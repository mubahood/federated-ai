package com.federated.client.ui.screens.onboarding

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.federated.client.ui.components.*

/**
 * Registration screen for new users.
 * Collects username, email, and generates device ID.
 *
 * @param onRegistrationComplete Callback when registration succeeds
 * @param viewModel ViewModel for registration logic
 */
@Composable
fun RegistrationScreen(
    onRegistrationComplete: () -> Unit,
    viewModel: RegistrationViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(uiState.isRegistrationComplete) {
        if (uiState.isRegistrationComplete) {
            onRegistrationComplete()
        }
    }
    
    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(24.dp)
        ) {
            Spacer(modifier = Modifier.height(32.dp))
            
            // Header
            Text(
                text = "Create Your Profile",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "Join the FederatedAI community and start contributing",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(40.dp))
            
            // Username field
            InputTextField(
                value = uiState.username,
                onValueChange = { viewModel.updateUsername(it) },
                label = "Username",
                placeholder = "Choose a username",
                isError = uiState.usernameError != null,
                errorMessage = uiState.usernameError,
                enabled = !uiState.isLoading
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Email field
            EmailTextField(
                value = uiState.email,
                onValueChange = { viewModel.updateEmail(it) },
                label = "Email",
                placeholder = "your.email@example.com",
                isError = uiState.emailError != null,
                errorMessage = uiState.emailError,
                enabled = !uiState.isLoading
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Device ID info
            InfoCard(
                title = "Device ID",
                content = "A unique identifier will be generated for your device. This helps maintain privacy while tracking contributions.",
                icon = Icons.Default.Check
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Terms and conditions
            Row(
                verticalAlignment = Alignment.Top,
                modifier = Modifier.fillMaxWidth()
            ) {
                Checkbox(
                    checked = uiState.acceptedTerms,
                    onCheckedChange = { viewModel.updateTermsAcceptance(it) },
                    enabled = !uiState.isLoading
                )
                
                Spacer(modifier = Modifier.width(8.dp))
                
                Column {
                    Text(
                        text = "I agree to the Terms & Conditions",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    if (uiState.termsError != null) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = uiState.termsError!!,
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // Error message
            if (uiState.generalError != null) {
                ErrorMessage(
                    message = uiState.generalError!!,
                    onRetry = null
                )
                Spacer(modifier = Modifier.height(16.dp))
            }
            
            // Register button
            PrimaryButton(
                text = "Create Account",
                onClick = { viewModel.register() },
                enabled = !uiState.isLoading,
                modifier = Modifier.fillMaxWidth()
            )
            
            if (uiState.isLoading) {
                Spacer(modifier = Modifier.height(16.dp))
                LoadingIndicator()
            }
            
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}
