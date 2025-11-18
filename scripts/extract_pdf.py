#!/usr/bin/env python3
"""
PDF Text Extraction Tool

This script provides multiple methods to extract text from PDF files:
1. PyPDF2 - Basic text extraction
2. pdfplumber - Better layout preservation
3. PyMuPDF (fitz) - Fast and accurate extraction

Usage:
    python extract_pdf.py <pdf_path> [--output output.txt] [--method pymupdf]
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List


def extract_with_pypdf2(pdf_path: str) -> str:
    """Extract text using PyPDF2."""
    try:
        import PyPDF2
        
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            print(f"📄 Total pages: {len(reader.pages)}")
            
            for i, page in enumerate(reader.pages, 1):
                print(f"⏳ Extracting page {i}...", end='\r')
                page_text = page.extract_text()
                text += f"\n\n{'='*60}\nPAGE {i}\n{'='*60}\n\n"
                text += page_text
            
            print(f"✅ Extracted {len(reader.pages)} pages using PyPDF2")
        
        return text
    except ImportError:
        print("❌ PyPDF2 not installed. Run: pip install PyPDF2")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error with PyPDF2: {e}")
        sys.exit(1)


def extract_with_pdfplumber(pdf_path: str) -> str:
    """Extract text using pdfplumber (better layout preservation)."""
    try:
        import pdfplumber
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Total pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages, 1):
                print(f"⏳ Extracting page {i}...", end='\r')
                page_text = page.extract_text()
                text += f"\n\n{'='*60}\nPAGE {i}\n{'='*60}\n\n"
                text += page_text if page_text else "[No text found on this page]"
            
            print(f"✅ Extracted {len(pdf.pages)} pages using pdfplumber")
        
        return text
    except ImportError:
        print("❌ pdfplumber not installed. Run: pip install pdfplumber")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error with pdfplumber: {e}")
        sys.exit(1)


def extract_with_pymupdf(pdf_path: str) -> str:
    """Extract text using PyMuPDF (fast and accurate)."""
    try:
        import fitz  # PyMuPDF
        
        text = ""
        doc = fitz.open(pdf_path)
        
        print(f"📄 Total pages: {len(doc)}")
        print(f"📖 Title: {doc.metadata.get('title', 'N/A')}")
        print(f"👤 Author: {doc.metadata.get('author', 'N/A')}")
        print(f"📅 Created: {doc.metadata.get('creationDate', 'N/A')}\n")
        
        num_pages = len(doc)
        for i in range(num_pages):
            page = doc[i]
            print(f"⏳ Extracting page {i+1}...", end='\r')
            page_text = page.get_text()
            text += f"\n\n{'='*60}\nPAGE {i+1}\n{'='*60}\n\n"
            text += page_text if page_text else "[No text found on this page]"
        
        doc.close()
        print(f"✅ Extracted {num_pages} pages using PyMuPDF (fitz)")
        
        return text
    except ImportError:
        print("❌ PyMuPDF not installed. Run: pip install pymupdf")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error with PyMuPDF: {e}")
        sys.exit(1)


def extract_pdf_metadata(pdf_path: str) -> dict:
    """Extract metadata from PDF."""
    try:
        import fitz
        
        doc = fitz.open(pdf_path)
        metadata = {
            'title': doc.metadata.get('title', 'N/A'),
            'author': doc.metadata.get('author', 'N/A'),
            'subject': doc.metadata.get('subject', 'N/A'),
            'keywords': doc.metadata.get('keywords', 'N/A'),
            'creator': doc.metadata.get('creator', 'N/A'),
            'producer': doc.metadata.get('producer', 'N/A'),
            'creationDate': doc.metadata.get('creationDate', 'N/A'),
            'modDate': doc.metadata.get('modDate', 'N/A'),
            'pages': len(doc)
        }
        doc.close()
        return metadata
    except Exception as e:
        print(f"⚠️  Could not extract metadata: {e}")
        return {}


def extract_pdf_images(pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
    """Extract images from PDF (requires PyMuPDF)."""
    try:
        import fitz
        from PIL import Image
        import io
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        doc = fitz.open(pdf_path)
        image_files = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            images = page.get_images()
            
            for img_idx, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Save image
                if output_dir:
                    image_filename = f"page{page_num + 1}_img{img_idx + 1}.{base_image['ext']}"
                    image_path = output_path / image_filename
                    
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    image_files.append(str(image_path))
                    print(f"💾 Saved: {image_filename}")
        
        doc.close()
        print(f"\n✅ Extracted {len(image_files)} images")
        return image_files
        
    except ImportError:
        print("❌ PyMuPDF or Pillow not installed")
        return []
    except Exception as e:
        print(f"❌ Error extracting images: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files using multiple methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract using PyMuPDF (recommended - fastest and most accurate)
  python extract_pdf.py document.pdf
  
  # Extract using specific method
  python extract_pdf.py document.pdf --method pdfplumber
  
  # Save to output file
  python extract_pdf.py document.pdf --output extracted_text.txt
  
  # Show metadata only
  python extract_pdf.py document.pdf --metadata
  
  # Extract images
  python extract_pdf.py document.pdf --extract-images --image-dir ./images
        """
    )
    
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('-o', '--output', help='Output text file path')
    parser.add_argument('-m', '--method', 
                       choices=['pypdf2', 'pdfplumber', 'pymupdf'],
                       default='pymupdf',
                       help='Extraction method (default: pymupdf)')
    parser.add_argument('--metadata', action='store_true',
                       help='Show PDF metadata only')
    parser.add_argument('--extract-images', action='store_true',
                       help='Extract images from PDF')
    parser.add_argument('--image-dir', help='Directory to save extracted images')
    
    args = parser.parse_args()
    
    # Check if PDF exists
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"📄 PDF Extraction Tool")
    print(f"{'='*60}")
    print(f"📁 File: {pdf_path.name}")
    print(f"📊 Size: {pdf_path.stat().st_size / 1024:.2f} KB")
    print(f"🔧 Method: {args.method}")
    print(f"{'='*60}\n")
    
    # Extract metadata if requested
    if args.metadata:
        print("📋 PDF Metadata:")
        print("="*60)
        metadata = extract_pdf_metadata(str(pdf_path))
        for key, value in metadata.items():
            print(f"{key:15s}: {value}")
        return
    
    # Extract images if requested
    if args.extract_images:
        image_dir = args.image_dir or f"{pdf_path.stem}_images"
        print(f"\n🖼️  Extracting images to: {image_dir}\n")
        extract_pdf_images(str(pdf_path), image_dir)
        return
    
    # Extract text using selected method
    print(f"\n🚀 Starting extraction...\n")
    
    if args.method == 'pypdf2':
        text = extract_with_pypdf2(str(pdf_path))
    elif args.method == 'pdfplumber':
        text = extract_with_pdfplumber(str(pdf_path))
    else:  # pymupdf (default)
        text = extract_with_pymupdf(str(pdf_path))
    
    # Save or display results
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(text, encoding='utf-8')
        print(f"\n💾 Saved to: {output_path}")
        print(f"📏 Size: {len(text):,} characters")
    else:
        # Display first 2000 characters
        print(f"\n{'='*60}")
        print("📖 EXTRACTED TEXT (Preview - first 2000 chars)")
        print(f"{'='*60}\n")
        print(text[:2000])
        if len(text) > 2000:
            print(f"\n... ({len(text) - 2000:,} more characters)")
            print("\n💡 Tip: Use --output to save full text to file")
    
    # Statistics
    print(f"\n{'='*60}")
    print("📊 Statistics:")
    print(f"{'='*60}")
    print(f"Total characters: {len(text):,}")
    print(f"Total words: {len(text.split()):,}")
    print(f"Total lines: {len(text.splitlines()):,}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
