package com.federated.client.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.federated.client.data.local.db.dao.ImageDao
import com.federated.client.data.local.db.dao.UserProfileDao
import com.federated.client.data.local.db.entities.ImageEntity
import com.federated.client.data.local.db.entities.UserProfileEntity
import com.federated.client.data.local.storage.ImageStorageManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject
import kotlin.math.roundToInt

/**
 * ViewModel for the Home Dashboard screen.
 * Manages inventory state including image counts, storage, and recent captures.
 */
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val imageDao: ImageDao,
    private val userProfileDao: UserProfileDao,
    private val imageStorageManager: ImageStorageManager
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadDashboardData()
        observeProfile()
        observeImageChanges()
    }
    
    /**
     * Observe real-time changes to images in the database.
     */
    private fun observeImageChanges() {
        viewModelScope.launch {
            // Observe all images and update UI when changes occur
            imageDao.getAllFlow().collect { images ->
                // Only update if not currently loading (to avoid overwriting loading state)
                if (!_uiState.value.isLoading) {
                    updateDashboardMetrics(images)
                }
            }
        }
    }
    
    /**
     * Update dashboard metrics based on current images.
     */
    private suspend fun updateDashboardMetrics(images: List<ImageEntity>) {
        try {
            val totalImages = images.size
            val labeledImages = images.count { !it.category.isNullOrEmpty() }
            val unlabeledImages = totalImages - labeledImages
            
            // Get all categories and their counts
            val categoryCounts = images
                .filter { !it.category.isNullOrEmpty() }
                .groupBy { it.category!! }
                .mapValues { it.value.size }
            
            // Get storage usage
            val storageUsed = imageStorageManager.getStorageSize()
            val storageFormatted = formatBytes(storageUsed)
            val storagePercentage = (storageUsed.toDouble() / MAX_STORAGE_BYTES * 100).roundToInt()
            
            // Get recent images
            val recentImages = images.take(10)
            
            // Get image count for storage manager
            val imageFileCount = imageStorageManager.getImageCount()
            
            // Calculate daily capture rate (images captured today)
            val todayStart = Calendar.getInstance().apply {
                set(Calendar.HOUR_OF_DAY, 0)
                set(Calendar.MINUTE, 0)
                set(Calendar.SECOND, 0)
                set(Calendar.MILLISECOND, 0)
            }.timeInMillis
            
            val todayImages = images.count { it.capturedAt >= todayStart }
            
            _uiState.update {
                it.copy(
                    totalImages = totalImages,
                    labeledImages = labeledImages,
                    unlabeledImages = unlabeledImages,
                    categoryCounts = categoryCounts,
                    storageUsed = storageUsed,
                    storageFormatted = storageFormatted,
                    storagePercentage = storagePercentage,
                    recentImages = recentImages,
                    imageFileCount = imageFileCount,
                    todayCaptures = todayImages,
                    error = null
                )
            }
        } catch (e: Exception) {
            // Don't update error state during background updates
        }
    }

    /**
     * Load all dashboard data including inventory metrics.
     */
    fun loadDashboardData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            try {
                // Get total image count
                val totalImages = imageDao.getCount()
                
                // Get labeled and unlabeled counts
                val labeledImages = imageDao.getLabeledCount()
                val unlabeledImages = totalImages - labeledImages
                
                // Get all categories and their counts
                val categories = imageDao.getAllCategories()
                val categoryCounts = categories.associateWith { category ->
                    imageDao.getCountByCategory(category)
                }
                
                // Get storage usage
                val storageUsed = imageStorageManager.getStorageSize()
                val storageFormatted = formatBytes(storageUsed)
                val storagePercentage = (storageUsed.toDouble() / MAX_STORAGE_BYTES * 100).roundToInt()
                
                // Get recent images
                val recentImages = imageDao.getAll().take(10)
                
                // Get image count for storage manager
                val imageFileCount = imageStorageManager.getImageCount()
                
                // Calculate daily capture rate (images captured today)
                val todayStart = Calendar.getInstance().apply {
                    set(Calendar.HOUR_OF_DAY, 0)
                    set(Calendar.MINUTE, 0)
                    set(Calendar.SECOND, 0)
                    set(Calendar.MILLISECOND, 0)
                }.timeInMillis
                
                val todayImages = imageDao.getAll().count { it.capturedAt >= todayStart }
                
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        totalImages = totalImages,
                        labeledImages = labeledImages,
                        unlabeledImages = unlabeledImages,
                        categoryCounts = categoryCounts,
                        storageUsed = storageUsed,
                        storageFormatted = storageFormatted,
                        storagePercentage = storagePercentage,
                        recentImages = recentImages,
                        imageFileCount = imageFileCount,
                        todayCaptures = todayImages,
                        error = null
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "Failed to load dashboard: ${e.message}"
                    )
                }
            }
        }
    }

    /**
     * Observe user profile changes.
     */
    private fun observeProfile() {
        viewModelScope.launch {
            userProfileDao.getProfileFlow().collect { profile ->
                _uiState.update { it.copy(userProfile = profile) }
            }
        }
    }

    /**
     * Refresh dashboard data (for pull-to-refresh).
     */
    fun refresh() {
        loadDashboardData()
    }

    /**
     * Format bytes to human-readable format.
     */
    private fun formatBytes(bytes: Long): String {
        return when {
            bytes < 1024 -> "$bytes B"
            bytes < 1024 * 1024 -> "${(bytes / 1024.0).roundToInt()} KB"
            bytes < 1024 * 1024 * 1024 -> "${(bytes / (1024.0 * 1024.0)).roundToInt()} MB"
            else -> "${"%.2f".format(bytes / (1024.0 * 1024.0 * 1024.0))} GB"
        }
    }

    /**
     * Get formatted greeting based on time of day.
     */
    fun getGreeting(): String {
        val hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
        return when (hour) {
            in 0..11 -> "Good Morning"
            in 12..16 -> "Good Afternoon"
            else -> "Good Evening"
        }
    }

    /**
     * Get category icon name based on category.
     */
    fun getCategoryIcon(category: String): String {
        return when (category.lowercase()) {
            "person" -> "person"
            "car", "vehicle" -> "directions_car"
            "animal", "cat", "dog" -> "pets"
            "chair", "furniture" -> "chair"
            "book" -> "menu_book"
            "phone", "cell phone" -> "phone_android"
            "laptop", "computer" -> "laptop"
            "bottle" -> "local_drink"
            "cup" -> "coffee"
            else -> "category"
        }
    }

    companion object {
        // Maximum storage: 500MB (same as CacheManager)
        private const val MAX_STORAGE_BYTES = 500L * 1024 * 1024
    }
}

/**
 * UI state for Home Dashboard.
 */
data class HomeUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val userProfile: UserProfileEntity? = null,
    
    // Inventory metrics
    val totalImages: Int = 0,
    val labeledImages: Int = 0,
    val unlabeledImages: Int = 0,
    val todayCaptures: Int = 0,
    
    // Category breakdown
    val categoryCounts: Map<String, Int> = emptyMap(),
    
    // Storage metrics
    val storageUsed: Long = 0,
    val storageFormatted: String = "0 MB",
    val storagePercentage: Int = 0,
    val imageFileCount: Int = 0,
    
    // Recent images
    val recentImages: List<ImageEntity> = emptyList()
) {
    /**
     * Get completion percentage for labeling progress.
     */
    val labelingProgress: Int
        get() = if (totalImages > 0) {
            ((labeledImages.toDouble() / totalImages) * 100).roundToInt()
        } else 0

    /**
     * Check if storage is nearly full (>80%).
     */
    val isStorageNearlyFull: Boolean
        get() = storagePercentage > 80

    /**
     * Check if user has any images.
     */
    val hasImages: Boolean
        get() = totalImages > 0
}
