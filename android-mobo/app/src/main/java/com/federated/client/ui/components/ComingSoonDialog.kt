package com.federated.client.ui.components

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign

/**
 * Reusable "Coming Soon" dialog for features under development.
 * 
 * @param onDismiss Callback when dialog is dismissed
 * @param title Optional custom title (defaults to "Coming Soon")
 * @param message Optional custom message (defaults to a generic message)
 * @param modifier Modifier for the dialog
 */
@Composable
fun ComingSoonDialog(
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier,
    title: String = "Coming Soon",
    message: String = "This feature is currently under development and will be available in a future update. Stay tuned!"
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge,
                textAlign = TextAlign.Center
            )
        },
        text = {
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("OK")
            }
        },
        containerColor = MaterialTheme.colorScheme.surface,
        tonalElevation = AlertDialogDefaults.TonalElevation,
        modifier = modifier
    )
}
