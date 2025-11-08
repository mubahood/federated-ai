package com.federated.client.ui.screens.home

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.federated.client.ui.components.ComingSoonDialog
import com.federated.client.ui.components.ErrorMessage
import com.federated.client.ui.components.LoadingIndicator
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Home Dashboard Screen - Main screen after onboarding.
 * Displays inventory metrics, storage usage, categories, and quick actions.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToCamera: () -> Unit,
    onNavigateToGallery: () -> Unit,
    onNavigateToLabel: () -> Unit,
    onNavigateToImageDetail: (Long) -> Unit,
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val lifecycleOwner = LocalLifecycleOwner.current
    val scope = rememberCoroutineScope()
    var isManualRefreshing by remember { mutableStateOf(false) }
    var showComingSoonDialog by remember { mutableStateOf(false) }

    // Auto-refresh when screen becomes visible (user returns from Camera/Gallery)
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                viewModel.refresh()
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Welcome Header
            item {
                WelcomeHeader(
                    greeting = viewModel.getGreeting(),
                    username = uiState.userProfile?.username ?: "User"
                )
            }

            // Loading State
            if (uiState.isLoading && !isManualRefreshing) {
                item {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(32.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        LoadingIndicator()
                    }
                }
            }

            // Error State
            if (uiState.error != null && !uiState.isLoading) {
                item {
                    ErrorMessage(
                        message = uiState.error ?: "Unknown error",
                        onRetry = { viewModel.refresh() },
                        modifier = Modifier.padding(horizontal = 16.dp)
                    )
                }
            }

            // Content - Only show if not loading and no error
            if (!uiState.isLoading && uiState.error == null) {
                // Inventory Summary Card
                item {
                    InventorySummaryCard(
                        total = uiState.totalImages,
                        labeled = uiState.labeledImages,
                        unlabeled = uiState.unlabeledImages,
                        todayCaptures = uiState.todayCaptures,
                        modifier = Modifier.padding(horizontal = 16.dp)
                    )
                }

                // Storage Usage Card
                item {
                    StorageCard(
                        used = uiState.storageUsed,
                        formatted = uiState.storageFormatted,
                        percentage = uiState.storagePercentage,
                        imageCount = uiState.imageFileCount,
                        isNearlyFull = uiState.isStorageNearlyFull,
                        modifier = Modifier.padding(horizontal = 16.dp)
                    )
                }

                // Category Breakdown
                if (uiState.categoryCounts.isNotEmpty()) {
                    item {
                        CategoryBreakdownSection(
                            categories = uiState.categoryCounts,
                            getCategoryIcon = viewModel::getCategoryIcon
                        )
                    }
                }

                // Recent Captures
                if (uiState.recentImages.isNotEmpty()) {
                    item {
                        RecentCapturesSection(
                            images = uiState.recentImages,
                            onImageClick = onNavigateToImageDetail,
                            onViewAllClick = onNavigateToGallery
                        )
                    }
                }

                // Quick Actions
                item {
                    QuickActionsGrid(
                        onCaptureClick = onNavigateToCamera,
                        onGalleryClick = onNavigateToGallery,
                        onLabelClick = onNavigateToLabel,
                        onSyncClick = {
                            showComingSoonDialog = true
                        },
                        unlabeledCount = uiState.unlabeledImages,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                }

                // Empty State
                if (!uiState.hasImages) {
                    item {
                        EmptyInventoryState(
                            onCaptureClick = onNavigateToCamera,
                            modifier = Modifier.padding(horizontal = 16.dp)
                        )
                    }
                }

                // Bottom spacing
                item {
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
        }
        
        // Floating refresh button
        FloatingActionButton(
            onClick = {
                scope.launch {
                    isManualRefreshing = true
                    viewModel.refresh()
                    delay(500)
                    isManualRefreshing = false
                }
            },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Refresh,
                contentDescription = "Refresh"
            )
        }
        
        // Show refreshing indicator
        if (isManualRefreshing) {
            CircularProgressIndicator(
                modifier = Modifier
                    .align(Alignment.Center)
            )
        }
    }
    
    // Coming Soon Dialog for Sync feature
    if (showComingSoonDialog) {
        ComingSoonDialog(
            onDismiss = { showComingSoonDialog = false },
            title = "Sync Feature",
            message = "Cloud synchronization is currently under development. Your data is safely stored locally and this feature will be available in a future update."
        )
    }
}

/**
 * Welcome header with greeting and username.
 */
@Composable
private fun WelcomeHeader(
    greeting: String,
    username: String,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
    ) {
        Text(
            text = "$greeting,",
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = username,
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}

/**
 * Empty state when user has no images.
 */
@Composable
private fun EmptyInventoryState(
    onCaptureClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "📸",
                style = MaterialTheme.typography.displayMedium
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "No Images Yet",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "Start building your inventory by capturing images of objects around you.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Button(
                onClick = onCaptureClick,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Capture First Image")
            }
        }
    }
}
