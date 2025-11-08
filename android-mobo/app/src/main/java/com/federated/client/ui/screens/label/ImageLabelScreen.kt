package com.federated.client.ui.screens.label

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import coil.compose.AsyncImage
import com.federated.client.ui.components.ErrorMessage
import com.federated.client.ui.components.LoadingIndicator
import com.federated.client.ui.components.PrimaryButton
import com.federated.client.ui.components.TertiaryButton

/**
 * Image Labeling Screen
 * Allows users to assign categories to unlabeled images
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImageLabelScreen(
    navController: NavController,
    viewModel: ImageLabelViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { androidx.compose.material3.SnackbarHostState() }
    
    // Handle success messages
    LaunchedEffect(uiState.successMessage) {
        uiState.successMessage?.let {
            snackbarHostState.showSnackbar(
                message = it,
                duration = SnackbarDuration.Short
            )
            viewModel.dismissSuccess()
        }
    }
    
    // Handle error messages
    LaunchedEffect(uiState.error) {
        uiState.error?.let {
            snackbarHostState.showSnackbar(
                message = it,
                duration = SnackbarDuration.Long
            )
            viewModel.clearError()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Label Images",
                            style = MaterialTheme.typography.titleLarge
                        )
                        if (uiState.hasImages) {
                            Text(
                                text = "Progress: ${viewModel.getProgressText()}",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
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
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface
                )
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when {
                uiState.isLoading && !uiState.hasImages -> {
                    LoadingIndicator()
                }

                uiState.allLabeled -> {
                    AllLabeledState(
                        uiState = uiState,
                        viewModel = viewModel,
                        onBackToDashboard = { navController.navigateUp() }
                    )
                }

                uiState.hasImages && uiState.currentImage != null -> {
                    LabelingContent(
                        uiState = uiState,
                        viewModel = viewModel,
                        progress = viewModel.getProgress()
                    )
                }

                else -> {
                    EmptyState(
                        onBackToDashboard = { navController.navigateUp() }
                    )
                }
            }

            // Show error message if present
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
}

@Composable
private fun LabelingContent(
    uiState: LabelUiState,
    viewModel: ImageLabelViewModel,
    progress: Float
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Progress indicator
        LinearProgressIndicator(
            progress = progress,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            color = MaterialTheme.colorScheme.primary
        )

        // Image preview
        ImagePreview(
            imageUri = uiState.currentImage?.uri ?: "",
            modifier = Modifier
                .fillMaxWidth()
                .height(300.dp)
                .padding(bottom = 16.dp)
        )

        // Category selection label
        Text(
            text = "Select Category:",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 8.dp)
        )

        // Category selection chips
        CategorySelection(
            categories = viewModel.getCategories(),
            selectedCategory = uiState.selectedCategory,
            onCategorySelected = { viewModel.selectCategory(it) },
            modifier = Modifier.padding(bottom = 24.dp)
        )

        // Action buttons
        ActionButtons(
            canGoBack = uiState.currentIndex > 0,
            canAssignLabel = uiState.selectedCategory != null,
            isLoading = uiState.isLoading,
            onBack = { viewModel.previous() },
            onSkip = { viewModel.skip() },
            onAssignLabel = {
                uiState.selectedCategory?.let { category ->
                    viewModel.assignLabel(category)
                }
            }
        )
    }
}

@Composable
private fun ImagePreview(
    imageUri: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        AsyncImage(
            model = imageUri,
            contentDescription = "Image to label",
            modifier = Modifier
                .fillMaxSize()
                .clip(RoundedCornerShape(8.dp)),
            contentScale = ContentScale.Fit
        )
    }
}

@Composable
private fun CategorySelection(
    categories: List<String>,
    selectedCategory: String?,
    onCategorySelected: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyRow(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(categories) { category ->
            CategoryChip(
                category = category,
                isSelected = category == selectedCategory,
                onClick = { onCategorySelected(category) }
            )
        }
    }
}

@Composable
private fun CategoryChip(
    category: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    FilterChip(
        selected = isSelected,
        onClick = onClick,
        label = {
            Text(
                text = category,
                style = MaterialTheme.typography.bodyMedium
            )
        },
        leadingIcon = if (isSelected) {
            {
                Icon(
                    imageVector = Icons.Default.CheckCircle,
                    contentDescription = "Selected",
                    modifier = Modifier.size(18.dp)
                )
            }
        } else null,
        colors = FilterChipDefaults.filterChipColors(
            selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
            selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer
        )
    )
}

@Composable
private fun ActionButtons(
    canGoBack: Boolean,
    canAssignLabel: Boolean,
    isLoading: Boolean,
    onBack: () -> Unit,
    onSkip: () -> Unit,
    onAssignLabel: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Primary action: Assign Label
        PrimaryButton(
            text = if (isLoading) "Assigning..." else "Assign Label",
            onClick = onAssignLabel,
            enabled = canAssignLabel && !isLoading,
            modifier = Modifier.fillMaxWidth(),
            icon = Icons.Default.CheckCircle
        )

        // Secondary actions row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Back button
            if (canGoBack) {
                TertiaryButton(
                    text = "Back",
                    onClick = onBack,
                    enabled = !isLoading,
                    modifier = Modifier.weight(1f),
                    icon = Icons.Filled.ArrowBack
                )
            }

            // Skip button
            TertiaryButton(
                text = "Skip",
                onClick = onSkip,
                enabled = !isLoading,
                modifier = Modifier.weight(1f),
                icon = Icons.Default.SkipNext
            )
        }
    }
}

@Composable
private fun AllLabeledState(
    uiState: LabelUiState,
    viewModel: ImageLabelViewModel,
    onBackToDashboard: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.CheckCircle,
            contentDescription = "All labeled",
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "All Images Labeled!",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "Great job! All your captured images have been labeled and are ready for training.",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(32.dp))
        
        // Upload Statistics Card
        uiState.uploadStats?.let { stats ->
            UploadStatsCard(
                pending = stats.pending,
                success = stats.success,
                failed = stats.failed
            )
            Spacer(modifier = Modifier.height(24.dp))
        }
        
        // Upload Progress
        if (uiState.isUploading) {
            UploadProgressCard(
                progress = uiState.uploadProgress,
                activeUploads = uiState.activeUploads
            )
            Spacer(modifier = Modifier.height(24.dp))
        }
        
        // Upload Button
        if (!uiState.isUploading) {
            Button(
                onClick = { viewModel.uploadLabeledImages() },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary
                )
            ) {
                Icon(
                    imageVector = Icons.Default.CloudUpload,
                    contentDescription = null,
                    modifier = Modifier.padding(end = 8.dp)
                )
                Text("Upload Labeled Images")
            }
            Spacer(modifier = Modifier.height(12.dp))
        }
        
        // Retry Failed Button
        if (uiState.hasFailedUploads && !uiState.isUploading) {
            Button(
                onClick = { viewModel.retryFailedUploads() },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                Icon(
                    imageVector = Icons.Default.Refresh,
                    contentDescription = null,
                    modifier = Modifier.padding(end = 8.dp)
                )
                Text("Retry ${uiState.uploadStats?.failed ?: 0} Failed Uploads")
            }
            Spacer(modifier = Modifier.height(12.dp))
        }

        PrimaryButton(
            text = "Back to Dashboard",
            onClick = onBackToDashboard,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

@Composable
private fun EmptyState(
    onBackToDashboard: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Close,
            contentDescription = "No images",
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "No Images to Label",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "Capture some images first, then come back here to label them.",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(32.dp))

        PrimaryButton(
            text = "Back to Dashboard",
            onClick = onBackToDashboard,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

/**
 * Upload Statistics Card - shows pending, success, and failed upload counts
 */
@Composable
private fun UploadStatsCard(
    pending: Int,
    success: Int,
    failed: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Upload Statistics",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(
                    label = "Pending",
                    count = pending,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                StatItem(
                    label = "Success",
                    count = success,
                    color = Color(0xFF4CAF50) // Green
                )
                StatItem(
                    label = "Failed",
                    count = failed,
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
private fun StatItem(
    label: String,
    count: Int,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = count.toString(),
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

/**
 * Upload Progress Card - shows current upload progress
 */
@Composable
private fun UploadProgressCard(
    progress: Float,
    activeUploads: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    strokeWidth = 3.dp,
                    color = MaterialTheme.colorScheme.primary
                )
                Text(
                    text = "Uploading images...",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
            }
            
            LinearProgressIndicator(
                progress = progress,
                modifier = Modifier.fillMaxWidth(),
                color = MaterialTheme.colorScheme.primary
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "$activeUploads images in queue",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Text(
                    text = "${(progress * 100).toInt()}%",
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}
