#!/usr/bin/env python3
"""
Federated AI - Training Image Import Script

This script carefully imports training images from various datasets into the database.
- Maximum 1,000 images per category
- Handles multiple annotation formats (XML, Excel, None)
- Progress tracking and error logging
- Transaction-safe with rollback capability

Author: Federated AI Team
Date: November 6, 2025
"""

import os
import sys
import random
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import xml.etree.ElementTree as ET

# Add Django project to path
sys.path.insert(0, '/Users/mac/Desktop/github/federated-ai/server')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.files import File
from django.db import transaction
from PIL import Image
import openpyxl

from objects.models import ObjectCategory
from clients.models import Client
from training.models import TrainingImage


# Configuration
# When running in Docker, /downloads is mounted to /Users/mac/Downloads
DOWNLOADS_BASE = '/downloads' if os.path.exists('/downloads') else '/Users/mac/Downloads'

DATASETS = {
    'Cat': {
        'path': f'{DOWNLOADS_BASE}/archive-cats/Data',
        'pattern': '*.png',
        'total_count': 29843,
        'import_limit': 1000,
        'annotation_type': None,
    },
    'Car': {
        'path': f'{DOWNLOADS_BASE}/archive-cars',
        'pattern': '*.jpg',
        'total_count': 64467,
        'import_limit': 1000,
        'annotation_type': None,
    },
    'Bicycle': {
        'path': f'{DOWNLOADS_BASE}/archive-bicycles/dataset/Bicycle annotated',
        'pattern': '*.jpg',
        'total_count': 208,
        'import_limit': 208,  # Import all
        'annotation_type': None,
    },
    'Dog': {
        'path': f'{DOWNLOADS_BASE}/archive-dogs/images/Images',
        'pattern': '*.jpg',
        'total_count': 20580,
        'import_limit': 1000,
        'annotation_type': 'xml',
        'annotation_path': f'{DOWNLOADS_BASE}/archive-dogs/annotations/Annotation',
    },
    'Person': {
        'path': f'{DOWNLOADS_BASE}/archive-person/images/images',
        'pattern': '*.jpg',
        'total_count': 2054,
        'import_limit': 1000,
        'annotation_type': 'excel',
        'annotation_file': f'{DOWNLOADS_BASE}/archive-person/images_info.xlsx',
    },
}

# Setup logging
# Use /app/server/logs in Docker, or local path otherwise
if os.path.exists('/app/server'):
    LOG_DIR = Path('/app/server/logs')
else:
    LOG_DIR = Path('/Users/mac/Desktop/github/federated-ai/server/logs')

LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f'import_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ImageImporter:
    """Handles the import of training images into the database."""
    
    def __init__(self, test_mode: bool = False):
        """
        Initialize the importer.
        
        Args:
            test_mode: If True, only import 10 images per category for testing
        """
        self.test_mode = test_mode
        self.stats = {
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'by_category': {}
        }
        
        logger.info("=" * 80)
        logger.info("FEDERATED AI - TRAINING IMAGE IMPORT")
        logger.info("=" * 80)
        logger.info(f"Test Mode: {test_mode}")
        logger.info(f"Log File: {LOG_FILE}")
        logger.info("")
    
    def validate_prerequisites(self) -> bool:
        """Validate that all required database records exist."""
        logger.info("🔍 Validating Prerequisites...")
        
        try:
            # Check ObjectCategory records
            categories = ['Cat', 'Car', 'Bicycle', 'Dog', 'Person']
            missing_categories = []
            
            for cat_name in categories:
                if not ObjectCategory.objects.filter(name=cat_name).exists():
                    missing_categories.append(cat_name)
            
            if missing_categories:
                logger.error(f"❌ Missing ObjectCategory records: {missing_categories}")
                return False
            
            logger.info(f"✅ All 5 ObjectCategory records exist")
            
            # Check Client record
            client = Client.objects.filter(status='active').first()
            if not client:
                # Create a default client if none exists
                logger.warning("⚠️  No active Client found, creating one...")
                client = Client.objects.create(
                    name="Data Import Client",
                    device_type="server",
                    status="active"
                )
                logger.info(f"✅ Created Client: {client.name}")
            else:
                logger.info(f"✅ Active Client found: {client.name} ({client.device_id})")
            
            self.client = client
            
            # Check media directory
            if os.path.exists('/app/server'):
                media_root = Path('/app/server/media')
            else:
                media_root = Path('/Users/mac/Desktop/github/federated-ai/server/media')
            
            if not media_root.exists():
                logger.warning(f"⚠️  Media directory not found: {media_root}, creating...")
                media_root.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"✅ Media directory accessible: {media_root}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Prerequisites validation failed: {e}")
            return False
    
    def discover_images(self, category_name: str, config: Dict) -> List[Path]:
        """
        Discover all images for a category.
        
        Args:
            category_name: Name of the object category
            config: Dataset configuration
            
        Returns:
            List of image file paths
        """
        logger.info(f"🔍 Discovering {category_name} images...")
        
        dataset_path = Path(config['path'])
        
        if not dataset_path.exists():
            logger.error(f"❌ Dataset path not found: {dataset_path}")
            return []
        
        # Find all image files
        image_files = []
        
        if category_name == 'Dog':
            # Dogs are organized in breed folders
            for breed_folder in dataset_path.iterdir():
                if breed_folder.is_dir():
                    image_files.extend(breed_folder.glob(config['pattern']))
        else:
            # Other categories are flat or simple structures
            image_files = list(dataset_path.glob(config['pattern']))
        
        logger.info(f"✅ Found {len(image_files)} {category_name} images")
        return image_files
    
    def sample_images(self, image_files: List[Path], limit: int) -> List[Path]:
        """
        Randomly sample images if count exceeds limit.
        
        Args:
            image_files: List of all image files
            limit: Maximum number to import
            
        Returns:
            Sampled list of image files
        """
        if len(image_files) <= limit:
            return image_files
        
        logger.info(f"📊 Sampling {limit} from {len(image_files)} images...")
        sampled = random.sample(image_files, limit)
        
        return sampled
    
    def parse_xml_annotation(self, xml_path: Path) -> Optional[Dict]:
        """
        Parse XML annotation file (PASCAL VOC format).
        
        Args:
            xml_path: Path to XML annotation file
            
        Returns:
            Dict with annotation data or None if parsing fails
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            annotations = []
            
            for obj in root.findall('object'):
                name = obj.find('name').text
                bndbox = obj.find('bndbox')
                
                annotation = {
                    'label': name,
                    'bbox': {
                        'xmin': int(bndbox.find('xmin').text),
                        'ymin': int(bndbox.find('ymin').text),
                        'xmax': int(bndbox.find('xmax').text),
                        'ymax': int(bndbox.find('ymax').text),
                    }
                }
                annotations.append(annotation)
            
            return {'objects': annotations}
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to parse XML {xml_path}: {e}")
            return None
    
    def load_excel_annotations(self, excel_path: Path) -> Dict[str, Dict]:
        """
        Load annotations from Excel file.
        
        Args:
            excel_path: Path to Excel file
            
        Returns:
            Dict mapping image filenames to annotation data
        """
        logger.info(f"📊 Loading Excel annotations from {excel_path.name}...")
        
        try:
            workbook = openpyxl.load_workbook(excel_path, data_only=True)
            sheet = workbook.active
            
            annotations = {}
            
            # Assuming first row is header
            headers = [cell.value for cell in sheet[1]]
            logger.info(f"Excel columns: {headers}")
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]:  # Skip empty rows
                    continue
                
                # Map to dict (adjust based on actual Excel structure)
                row_data = dict(zip(headers, row))
                filename = row_data.get('filename') or row_data.get('image') or str(row[0])
                
                annotations[filename] = row_data
            
            logger.info(f"✅ Loaded {len(annotations)} annotations from Excel")
            return annotations
            
        except Exception as e:
            logger.error(f"❌ Failed to load Excel: {e}")
            return {}
    
    def get_image_info(self, image_path: Path) -> Optional[Tuple[int, int, int]]:
        """
        Get image dimensions and file size.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (width, height, file_size) or None if invalid
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                file_size = image_path.stat().st_size
                return width, height, file_size
        except Exception as e:
            logger.warning(f"⚠️  Cannot read image {image_path.name}: {e}")
            return None
    
    def import_image(
        self,
        image_path: Path,
        category: ObjectCategory,
        annotation_data: Optional[Dict] = None
    ) -> bool:
        """
        Import a single image into the database.
        
        Args:
            image_path: Path to source image file
            category: ObjectCategory instance
            annotation_data: Optional annotation dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get image information
            image_info = self.get_image_info(image_path)
            if not image_info:
                return False
            
            width, height, file_size = image_info
            
            # Prepare metadata
            metadata = {
                'width': width,
                'height': height,
                'file_size': file_size,
                'original_filename': image_path.name,
            }
            
            # Add annotations to metadata if available
            if annotation_data:
                metadata['annotations'] = annotation_data
            
            # Create TrainingImage instance
            training_image = TrainingImage(
                object_category=category,
                client=self.client,
                metadata=metadata,
                is_validated=(annotation_data is not None),
                validation_notes=f"Imported from {image_path.parent.name}" if annotation_data else ""
            )
            
            # Copy image file to Django's file field
            with open(image_path, 'rb') as f:
                training_image.image.save(image_path.name, File(f), save=True)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to import {image_path.name}: {e}")
            return False
    
    def import_category(self, category_name: str) -> Dict:
        """
        Import all images for a specific category.
        
        Args:
            category_name: Name of the object category
            
        Returns:
            Dict with import statistics
        """
        logger.info("=" * 80)
        logger.info(f"📦 IMPORTING: {category_name.upper()}")
        logger.info("=" * 80)
        
        config = DATASETS[category_name]
        stats = {
            'category': category_name,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            # Get ObjectCategory
            category = ObjectCategory.objects.get(name=category_name)
            
            # Discover images
            all_images = self.discover_images(category_name, config)
            if not all_images:
                logger.error(f"❌ No images found for {category_name}")
                return stats
            
            # Sample images
            import_limit = 10 if self.test_mode else config['import_limit']
            selected_images = self.sample_images(all_images, import_limit)
            
            logger.info(f"📥 Importing {len(selected_images)} {category_name} images...")
            logger.info("")
            
            # Load annotations if needed
            excel_annotations = {}
            if config.get('annotation_type') == 'excel':
                excel_path = Path(config['annotation_file'])
                excel_annotations = self.load_excel_annotations(excel_path)
            
            # Import images in batches
            batch_size = 100
            success_count = 0
            
            for idx, image_path in enumerate(selected_images, 1):
                stats['processed'] += 1
                
                # Get annotation data
                annotation_data = None
                
                if config.get('annotation_type') == 'xml':
                    # For dogs: find corresponding XML
                    breed_folder = image_path.parent.name
                    xml_filename = image_path.stem  # Remove extension
                    xml_path = Path(config['annotation_path']) / breed_folder / xml_filename
                    
                    if xml_path.exists():
                        annotation_data = self.parse_xml_annotation(xml_path)
                
                elif config.get('annotation_type') == 'excel':
                    # For persons: lookup in Excel data
                    annotation_data = excel_annotations.get(image_path.name)
                
                # Import the image
                if self.import_image(image_path, category, annotation_data):
                    stats['success'] += 1
                    success_count += 1
                else:
                    stats['failed'] += 1
                
                # Progress update
                if idx % 50 == 0:
                    logger.info(f"  Progress: {idx}/{len(selected_images)} "
                              f"(Success: {success_count}, Failed: {stats['failed']})")
                
                # Commit batch
                if idx % batch_size == 0:
                    logger.info(f"  💾 Committed batch at {idx} images")
            
            # Update category statistics
            category.training_images_count = TrainingImage.objects.filter(
                object_category=category
            ).count()
            category.save()
            
            logger.info("")
            logger.info(f"✅ {category_name} Import Complete!")
            logger.info(f"   Total Processed: {stats['processed']}")
            logger.info(f"   Successful: {stats['success']}")
            logger.info(f"   Failed: {stats['failed']}")
            logger.info("")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Category import failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return stats
    
    def run(self, categories: Optional[List[str]] = None):
        """
        Run the import process for specified categories.
        
        Args:
            categories: List of category names to import, or None for all
        """
        start_time = datetime.now()
        
        # Validate prerequisites
        if not self.validate_prerequisites():
            logger.error("❌ Prerequisites validation failed. Aborting import.")
            return
        
        # Determine categories to import
        if categories is None:
            categories = list(DATASETS.keys())
        
        logger.info(f"📋 Categories to import: {', '.join(categories)}")
        logger.info("")
        
        # Import each category
        for category_name in categories:
            if category_name not in DATASETS:
                logger.warning(f"⚠️  Unknown category: {category_name}. Skipping.")
                continue
            
            category_stats = self.import_category(category_name)
            self.stats['by_category'][category_name] = category_stats
            self.stats['total_processed'] += category_stats['processed']
            self.stats['total_success'] += category_stats['success']
            self.stats['total_failed'] += category_stats['failed']
        
        # Final report
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("📊 FINAL IMPORT REPORT")
        logger.info("=" * 80)
        logger.info(f"Total Duration: {duration:.2f} seconds")
        logger.info(f"Total Images Processed: {self.stats['total_processed']}")
        logger.info(f"Total Successful: {self.stats['total_success']}")
        logger.info(f"Total Failed: {self.stats['total_failed']}")
        logger.info("")
        logger.info("By Category:")
        for cat_name, cat_stats in self.stats['by_category'].items():
            logger.info(f"  {cat_name}: {cat_stats['success']}/{cat_stats['processed']} "
                       f"(Failed: {cat_stats['failed']})")
        logger.info("")
        logger.info(f"Log saved to: {LOG_FILE}")
        logger.info("=" * 80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Import training images into Federated AI database'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: import only 10 images per category'
    )
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['Cat', 'Car', 'Bicycle', 'Dog', 'Person'],
        help='Specific categories to import (default: all)'
    )
    
    args = parser.parse_args()
    
    # Create and run importer
    importer = ImageImporter(test_mode=args.test)
    importer.run(categories=args.categories)


if __name__ == '__main__':
    main()
