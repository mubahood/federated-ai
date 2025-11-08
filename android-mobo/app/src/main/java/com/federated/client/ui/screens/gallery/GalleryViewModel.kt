package com.federated.client.ui.screens.gallery

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.federated.client.data.local.db.dao.ImageDao
import com.federated.client.data.local.db.entities.ImageEntity
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for Gallery Screen
 * Manages image browsing, filtering, sorting, and deletion
 */
@HiltViewModel
class GalleryViewModel @Inject constructor(
    private val imageDao: ImageDao
) : ViewModel() {

    // Filter options
    private val _filterCategory = MutableStateFlow<String?>(null)
    private val _filterLabeled = MutableStateFlow<LabelFilter>(LabelFilter.ALL)
    private val _sortOrder = MutableStateFlow(SortOrder.NEWEST_FIRST)
    private val _searchQuery = MutableStateFlow("")

    // UI State
    private val _uiState = MutableStateFlow(GalleryUiState())
    val uiState: StateFlow<GalleryUiState> = _uiState.asStateFlow()

    // Category statistics
    private val _categoryStats = MutableStateFlow<Map<String, Int>>(emptyMap())
    val categoryStats: StateFlow<Map<String, Int>> = _categoryStats.asStateFlow()

    init {
        loadImages()
        loadCategoryStats()
    }

    /**
     * Load images based on current filters and sorting
     */
    private fun loadImages() {
        viewModelScope.launch {
            combine(
                _filterCategory,
                _filterLabeled,
                _sortOrder,
                _searchQuery
            ) { category, labeled, sort, query ->
                FilterState(category, labeled, sort, query)
            }.flatMapLatest { filter ->
                getFilteredImagesFlow(filter)
            }.catch { error ->
                _uiState.update { it.copy(
                    isLoading = false,
                    error = error.message ?: "Failed to load images"
                )}
            }.collect { images ->
                _uiState.update { it.copy(
                    images = images,
                    isLoading = false,
                    error = null
                )}
            }
        }
    }

    /**
     * Get filtered images flow based on current filters
     */
    private fun getFilteredImagesFlow(filter: FilterState): Flow<List<ImageEntity>> {
        // Base flow with category filter
        val baseFlow = if (filter.category != null) {
            imageDao.getByCategory(filter.category)
        } else {
            imageDao.getAllFlow()
        }

        return baseFlow.map { images ->
            var filtered = images

            // Apply labeled filter
            filtered = when (filter.labeled) {
                LabelFilter.LABELED_ONLY -> filtered.filter { it.isLabeled }
                LabelFilter.UNLABELED_ONLY -> filtered.filter { !it.isLabeled }
                LabelFilter.ALL -> filtered
            }

            // Apply search query
            if (filter.searchQuery.isNotBlank()) {
                filtered = filtered.filter {
                    it.category?.contains(filter.searchQuery, ignoreCase = true) == true ||
                    it.uri.contains(filter.searchQuery, ignoreCase = true)
                }
            }

            // Apply sorting
            when (filter.sortOrder) {
                SortOrder.NEWEST_FIRST -> filtered.sortedByDescending { it.capturedAt }
                SortOrder.OLDEST_FIRST -> filtered.sortedBy { it.capturedAt }
                SortOrder.BY_CATEGORY -> filtered.sortedBy { it.category ?: "" }
            }
        }
    }

    /**
     * Load category statistics
     */
    private fun loadCategoryStats() {
        viewModelScope.launch {
            imageDao.getAllFlow()
                .catch { error ->
                    // Silently fail for stats
                }
                .collect { images ->
                    // Build category stats map
                    val stats = images
                        .filter { it.category != null }
                        .groupBy { it.category!! }
                        .mapValues { it.value.size }
                    _categoryStats.value = stats
                }
        }
    }

    /**
     * Set category filter
     */
    fun filterByCategory(category: String?) {
        _filterCategory.value = category
    }

    /**
     * Set labeled filter
     */
    fun filterByLabeled(filter: LabelFilter) {
        _filterLabeled.value = filter
    }

    /**
     * Set sort order
     */
    fun setSortOrder(order: SortOrder) {
        _sortOrder.value = order
    }

    /**
     * Set search query
     */
    fun search(query: String) {
        _searchQuery.value = query
    }

    /**
     * Clear all filters
     */
    fun clearFilters() {
        _filterCategory.value = null
        _filterLabeled.value = LabelFilter.ALL
        _searchQuery.value = ""
    }

    /**
     * Delete an image
     */
    fun deleteImage(image: ImageEntity) {
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(isLoading = true) }
                imageDao.delete(image)
                // Flow will automatically update the list
                _uiState.update { it.copy(isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(
                    isLoading = false,
                    error = "Failed to delete image: ${e.message}"
                )}
            }
        }
    }

    /**
     * Delete multiple images
     */
    fun deleteImages(images: List<ImageEntity>) {
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(isLoading = true) }
                images.forEach { imageDao.delete(it) }
                _uiState.update { it.copy(isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(
                    isLoading = false,
                    error = "Failed to delete images: ${e.message}"
                )}
            }
        }
    }

    /**
     * Clear error
     */
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }

    /**
     * Get current filter summary text
     */
    fun getFilterSummary(): String {
        val parts = mutableListOf<String>()
        
        _filterCategory.value?.let { parts.add("Category: $it") }
        
        when (_filterLabeled.value) {
            LabelFilter.LABELED_ONLY -> parts.add("Labeled only")
            LabelFilter.UNLABELED_ONLY -> parts.add("Unlabeled only")
            LabelFilter.ALL -> {}
        }
        
        if (_searchQuery.value.isNotBlank()) {
            parts.add("Search: ${_searchQuery.value}")
        }

        return if (parts.isEmpty()) {
            "All images"
        } else {
            parts.joinToString(" • ")
        }
    }
}

/**
 * UI State for Gallery Screen
 */
data class GalleryUiState(
    val images: List<ImageEntity> = emptyList(),
    val isLoading: Boolean = true,
    val error: String? = null
) {
    val isEmpty: Boolean
        get() = images.isEmpty() && !isLoading && error == null
}

/**
 * Filter state container
 */
private data class FilterState(
    val category: String?,
    val labeled: LabelFilter,
    val sortOrder: SortOrder,
    val searchQuery: String
)

/**
 * Label filter options
 */
enum class LabelFilter {
    ALL,
    LABELED_ONLY,
    UNLABELED_ONLY
}

/**
 * Sort order options
 */
enum class SortOrder {
    NEWEST_FIRST,
    OLDEST_FIRST,
    BY_CATEGORY
}
