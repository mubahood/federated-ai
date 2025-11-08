package com.federated.client.ui.screens.onboarding

import android.util.Patterns
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.federated.client.data.local.db.dao.UserProfileDao
import com.federated.client.data.local.db.entities.UserProfileEntity
import com.federated.client.data.local.preferences.PreferencesDataStore
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

/**
 * ViewModel for registration screen.
 */
@HiltViewModel
class RegistrationViewModel @Inject constructor(
    private val userProfileDao: UserProfileDao,
    private val preferencesDataStore: PreferencesDataStore
) : ViewModel() {

    private val _uiState = MutableStateFlow(RegistrationUiState())
    val uiState: StateFlow<RegistrationUiState> = _uiState.asStateFlow()

    /**
     * Update username field.
     */
    fun updateUsername(username: String) {
        _uiState.update { it.copy(username = username, usernameError = null) }
    }

    /**
     * Update email field.
     */
    fun updateEmail(email: String) {
        _uiState.update { it.copy(email = email, emailError = null) }
    }

    /**
     * Update terms acceptance.
     */
    fun updateTermsAcceptance(accepted: Boolean) {
        _uiState.update { it.copy(acceptedTerms = accepted, termsError = null) }
    }

    /**
     * Validate and register user.
     */
    fun register() {
        if (!validateInputs()) {
            return
        }

        _uiState.update { it.copy(isLoading = true, generalError = null) }

        viewModelScope.launch {
            try {
                // Generate device ID
                val deviceId = generateDeviceId()

                // Create user profile
                val profile = UserProfileEntity(
                    deviceId = deviceId,
                    username = _uiState.value.username.trim(),
                    email = _uiState.value.email.trim(),
                    createdAt = System.currentTimeMillis()
                )

                // Save to database
                userProfileDao.insert(profile)

                // Mark onboarding as complete
                preferencesDataStore.setOnboardingComplete(true)

                // Update UI state
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        isRegistrationComplete = true
                    ) 
                }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        generalError = "Registration failed: ${e.message}"
                    ) 
                }
            }
        }
    }

    /**
     * Validate all input fields.
     */
    private fun validateInputs(): Boolean {
        var isValid = true
        val currentState = _uiState.value

        // Validate username
        if (currentState.username.isBlank()) {
            _uiState.update { it.copy(usernameError = "Username is required") }
            isValid = false
        } else if (currentState.username.length < 3) {
            _uiState.update { it.copy(usernameError = "Username must be at least 3 characters") }
            isValid = false
        } else if (currentState.username.length > 20) {
            _uiState.update { it.copy(usernameError = "Username must be less than 20 characters") }
            isValid = false
        } else if (!currentState.username.matches(Regex("^[a-zA-Z0-9_]+$"))) {
            _uiState.update { it.copy(usernameError = "Username can only contain letters, numbers, and underscores") }
            isValid = false
        }

        // Validate email
        if (currentState.email.isBlank()) {
            _uiState.update { it.copy(emailError = "Email is required") }
            isValid = false
        } else if (!Patterns.EMAIL_ADDRESS.matcher(currentState.email).matches()) {
            _uiState.update { it.copy(emailError = "Please enter a valid email address") }
            isValid = false
        }

        // Validate terms acceptance
        if (!currentState.acceptedTerms) {
            _uiState.update { it.copy(termsError = "You must accept the Terms & Conditions") }
            isValid = false
        }

        return isValid
    }

    /**
     * Generate unique device ID.
     */
    private fun generateDeviceId(): String {
        return "device_${UUID.randomUUID()}"
    }
}

/**
 * UI state for registration screen.
 */
data class RegistrationUiState(
    val username: String = "",
    val email: String = "",
    val acceptedTerms: Boolean = false,
    val usernameError: String? = null,
    val emailError: String? = null,
    val termsError: String? = null,
    val generalError: String? = null,
    val isLoading: Boolean = false,
    val isRegistrationComplete: Boolean = false
)
