package com.federated.client.ui.screens.gallery

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import coil.compose.AsyncImage
import com.federated.client.data.local.db.entities.ImageEntity
import com.federated.client.ui.components.ComingSoonDialog
import com.federated.client.ui.components.ErrorMessage
import com.federated.client.ui.components.LoadingIndicator
import java.text.SimpleDateFormat
import java.util.*

/**
 * Gallery Screen
 * Browse, filter, and manage all captured images
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GalleryScreen(
    navController: NavController,
    viewModel: GalleryViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val categoryStats by viewModel.categoryStats.collectAsState()
    
    var showFilterSheet by remember { mutableStateOf(false) }
    var showSortSheet by remember { mutableStateOf(false) }
    var selectedImage by remember { mutableStateOf<ImageEntity?>(null) }
    var showSearchComingSoon by remember { mutableStateOf(false) }
    var showDeleteComingSoon by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Gallery",
                            style = MaterialTheme.typography.titleLarge
                        )
                        Text(
                            text = "${uiState.images.size} images",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(
                            imageVector = Icons.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                actions = {
                    // Search button
                    IconButton(onClick = { showSearchComingSoon = true }) {
                        Icon(
                            imageVector = Icons.Filled.Search,
                            contentDescription = "Search"
                        )
                    }
                    
                    // Filter button
                    IconButton(onClick = { showFilterSheet = true }) {
                        Icon(
                            imageVector = Icons.Filled.FilterList,
                            contentDescription = "Filter"
                        )
                    }
                    
                    // Sort button
                    IconButton(onClick = { showSortSheet = true }) {
                        Icon(
                            imageVector = Icons.Filled.Sort,
                            contentDescription = "Sort"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface
                )
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when {
                uiState.isLoading -> {
                    LoadingIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                
                uiState.isEmpty -> {
                    EmptyGalleryState(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                
                else -> {
                    GalleryContent(
                        images = uiState.images,
                        onImageClick = { image ->
                            selectedImage = image
                        },
                        onImageLongClick = { image ->
                            showDeleteComingSoon = true
                        }
                    )
                }
            }

            // Error message
            if (uiState.error != null) {
                ErrorMessage(
                    message = uiState.error!!,
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(16.dp)
                )
            }
        }
    }

    // Filter bottom sheet
    if (showFilterSheet) {
        FilterBottomSheet(
            categoryStats = categoryStats,
            onDismiss = { showFilterSheet = false },
            onFilterByCategory = { category ->
                viewModel.filterByCategory(category)
                showFilterSheet = false
            },
            onFilterByLabeled = { filter ->
                viewModel.filterByLabeled(filter)
                showFilterSheet = false
            },
            onClearFilters = {
                viewModel.clearFilters()
                showFilterSheet = false
            }
        )
    }

    // Sort bottom sheet
    if (showSortSheet) {
        SortBottomSheet(
            onDismiss = { showSortSheet = false },
            onSortOrderSelected = { order ->
                viewModel.setSortOrder(order)
                showSortSheet = false
            }
        )
    }

    // Image detail dialog
    selectedImage?.let { image ->
        ImageDetailDialog(
            image = image,
            onDismiss = { selectedImage = null },
            onDelete = {
                viewModel.deleteImage(image)
                selectedImage = null
            }
        )
    }
    
    // Coming Soon Dialogs
    if (showSearchComingSoon) {
        ComingSoonDialog(
            onDismiss = { showSearchComingSoon = false },
            title = "Search Feature",
            message = "Image search functionality is currently under development and will be available in a future update."
        )
    }
    
    if (showDeleteComingSoon) {
        ComingSoonDialog(
            onDismiss = { showDeleteComingSoon = false },
            title = "Bulk Delete",
            message = "Long-press multi-select and bulk delete is currently under development. You can delete individual images from the detail view."
        )
    }
}

/**
 * Gallery grid content
 */
@Composable
private fun GalleryContent(
    images: List<ImageEntity>,
    onImageClick: (ImageEntity) -> Unit,
    onImageLongClick: (ImageEntity) -> Unit
) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(3),
        contentPadding = PaddingValues(4.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        items(images, key = { it.id }) { image ->
            GalleryImageItem(
                image = image,
                onClick = { onImageClick(image) },
                onLongClick = { onImageLongClick(image) }
            )
        }
    }
}

/**
 * Individual gallery image item
 */
@Composable
private fun GalleryImageItem(
    image: ImageEntity,
    onClick: () -> Unit,
    onLongClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .aspectRatio(1f)
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onClick)
    ) {
        // Image
        AsyncImage(
            model = image.uri,
            contentDescription = image.category ?: "Image",
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        // Label badge
        if (image.isLabeled && image.category != null) {
            Surface(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(4.dp),
                color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.9f),
                shape = RoundedCornerShape(4.dp)
            ) {
                Text(
                    text = image.category,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }

        // Unlabeled indicator
        if (!image.isLabeled) {
            Surface(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(4.dp),
                color = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.9f),
                shape = RoundedCornerShape(4.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Warning,
                    contentDescription = "Unlabeled",
                    modifier = Modifier
                        .padding(2.dp)
                        .size(16.dp),
                    tint = MaterialTheme.colorScheme.onErrorContainer
                )
            }
        }
    }
}

/**
 * Empty gallery state
 */
@Composable
private fun EmptyGalleryState(
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.PhotoLibrary,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "No Images Yet",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "Capture some images to see them here",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center
        )
    }
}

/**
 * Filter bottom sheet
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FilterBottomSheet(
    categoryStats: Map<String, Int>,
    onDismiss: () -> Unit,
    onFilterByCategory: (String?) -> Unit,
    onFilterByLabeled: (LabelFilter) -> Unit,
    onClearFilters: () -> Unit
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Filter Images",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Label status filter
            Text(
                text = "Label Status",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Medium
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = false,
                    onClick = { onFilterByLabeled(LabelFilter.ALL) },
                    label = { Text("All") }
                )
                FilterChip(
                    selected = false,
                    onClick = { onFilterByLabeled(LabelFilter.LABELED_ONLY) },
                    label = { Text("Labeled") }
                )
                FilterChip(
                    selected = false,
                    onClick = { onFilterByLabeled(LabelFilter.UNLABELED_ONLY) },
                    label = { Text("Unlabeled") }
                )
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Category filter
            if (categoryStats.isNotEmpty()) {
                Text(
                    text = "Category",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                categoryStats.forEach { (category, count) ->
                    TextButton(
                        onClick = { onFilterByCategory(category) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = "$category ($count)",
                            modifier = Modifier.weight(1f),
                            textAlign = TextAlign.Start
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Clear filters button
            OutlinedButton(
                onClick = onClearFilters,
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(
                    imageVector = Icons.Default.Clear,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Clear All Filters")
            }
            
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

/**
 * Sort bottom sheet
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SortBottomSheet(
    onDismiss: () -> Unit,
    onSortOrderSelected: (SortOrder) -> Unit
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Sort By",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            SortOption(
                text = "Newest First",
                icon = Icons.Default.NewReleases,
                onClick = { onSortOrderSelected(SortOrder.NEWEST_FIRST) }
            )
            
            SortOption(
                text = "Oldest First",
                icon = Icons.Default.History,
                onClick = { onSortOrderSelected(SortOrder.OLDEST_FIRST) }
            )
            
            SortOption(
                text = "By Category",
                icon = Icons.Default.Category,
                onClick = { onSortOrderSelected(SortOrder.BY_CATEGORY) }
            )
            
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

/**
 * Sort option item
 */
@Composable
private fun SortOption(
    text: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    onClick: () -> Unit
) {
    TextButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = text,
            modifier = Modifier.weight(1f),
            textAlign = TextAlign.Start
        )
    }
}

/**
 * Image detail dialog
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ImageDetailDialog(
    image: ImageEntity,
    onDismiss: () -> Unit,
    onDelete: () -> Unit
) {
    var showDeleteConfirm by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss
    ) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp)
            ) {
                // Image
                AsyncImage(
                    model = image.uri,
                    contentDescription = image.category ?: "Image",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(300.dp)
                        .clip(RoundedCornerShape(8.dp)),
                    contentScale = ContentScale.Fit
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Metadata
                ImageMetadataRow(
                    label = "Category",
                    value = image.category ?: "Not labeled"
                )
                
                ImageMetadataRow(
                    label = "Captured",
                    value = formatDate(image.capturedAt)
                )
                
                ImageMetadataRow(
                    label = "Dimensions",
                    value = "${image.width} × ${image.height}"
                )
                
                ImageMetadataRow(
                    label = "Size",
                    value = formatFileSize(image.fileSize ?: 0L)
                )
                
                ImageMetadataRow(
                    label = "Status",
                    value = if (image.isLabeled) "Labeled" else "Unlabeled"
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Actions
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Close")
                    }
                    
                    Button(
                        onClick = { showDeleteConfirm = true },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.error
                        )
                    ) {
                        Icon(
                            imageVector = Icons.Default.Delete,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Delete")
                    }
                }
            }
        }
    }

    // Delete confirmation dialog
    if (showDeleteConfirm) {
        AlertDialog(
            onDismissRequest = { showDeleteConfirm = false },
            title = { Text("Delete Image?") },
            text = { Text("This action cannot be undone.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        onDelete()
                        showDeleteConfirm = false
                    }
                ) {
                    Text("Delete", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteConfirm = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

/**
 * Image metadata row
 */
@Composable
private fun ImageMetadataRow(
    label: String,
    value: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
    }
}

/**
 * Format date
 */
private fun formatDate(timestamp: Long): String {
    val sdf = SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault())
    return sdf.format(Date(timestamp))
}

/**
 * Format file size
 */
private fun formatFileSize(bytes: Long): String {
    return when {
        bytes < 1024 -> "$bytes B"
        bytes < 1024 * 1024 -> "${bytes / 1024} KB"
        else -> "${bytes / (1024 * 1024)} MB"
    }
}
