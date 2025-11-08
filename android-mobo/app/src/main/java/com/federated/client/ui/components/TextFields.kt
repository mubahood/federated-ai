package com.federated.client.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp

/**
 * Standard text field component.
 *
 * @param value Current text value
 * @param onValueChange Value change callback
 * @param label Label text
 * @param modifier Modifier for styling
 * @param placeholder Placeholder text
 * @param leadingIcon Leading icon
 * @param trailingIcon Trailing icon
 * @param isError Whether field has error
 * @param errorMessage Error message to display
 * @param keyboardType Keyboard type
 * @param imeAction IME action
 * @param keyboardActions Keyboard actions
 * @param singleLine Whether single line
 * @param maxLines Maximum lines
 * @param enabled Whether enabled
 */
@Composable
fun InputTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    leadingIcon: ImageVector? = null,
    trailingIcon: ImageVector? = null,
    isError: Boolean = false,
    errorMessage: String? = null,
    keyboardType: KeyboardType = KeyboardType.Text,
    imeAction: ImeAction = ImeAction.Next,
    keyboardActions: KeyboardActions = KeyboardActions.Default,
    singleLine: Boolean = true,
    maxLines: Int = 1,
    enabled: Boolean = true
) {
    Column(modifier = modifier) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            label = { Text(label) },
            placeholder = { Text(placeholder) },
            leadingIcon = if (leadingIcon != null) {
                { Icon(imageVector = leadingIcon, contentDescription = null) }
            } else null,
            trailingIcon = if (trailingIcon != null) {
                { Icon(imageVector = trailingIcon, contentDescription = null) }
            } else null,
            isError = isError,
            keyboardOptions = KeyboardOptions(
                keyboardType = keyboardType,
                imeAction = imeAction
            ),
            keyboardActions = keyboardActions,
            singleLine = singleLine,
            maxLines = maxLines,
            enabled = enabled,
            modifier = Modifier.fillMaxWidth()
        )
        
        if (isError && errorMessage != null) {
            Spacer(modifier = Modifier.height(4.dp))
            ErrorText(
                text = errorMessage,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

/**
 * Password text field with show/hide toggle.
 */
@Composable
fun PasswordTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    isError: Boolean = false,
    errorMessage: String? = null,
    imeAction: ImeAction = ImeAction.Done,
    keyboardActions: KeyboardActions = KeyboardActions.Default,
    enabled: Boolean = true
) {
    var passwordVisible by remember { mutableStateOf(false) }
    
    Column(modifier = modifier) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            label = { Text(label) },
            placeholder = { Text(placeholder) },
            visualTransformation = if (passwordVisible) {
                VisualTransformation.None
            } else {
                PasswordVisualTransformation()
            },
            trailingIcon = {
                IconButton(onClick = { passwordVisible = !passwordVisible }) {
                    Icon(
                        imageVector = if (passwordVisible) {
                            Icons.Default.Visibility
                        } else {
                            Icons.Default.VisibilityOff
                        },
                        contentDescription = if (passwordVisible) {
                            "Hide password"
                        } else {
                            "Show password"
                        }
                    )
                }
            },
            isError = isError,
            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Password,
                imeAction = imeAction
            ),
            keyboardActions = keyboardActions,
            singleLine = true,
            enabled = enabled,
            modifier = Modifier.fillMaxWidth()
        )
        
        if (isError && errorMessage != null) {
            Spacer(modifier = Modifier.height(4.dp))
            ErrorText(
                text = errorMessage,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

/**
 * Email text field with email keyboard type.
 */
@Composable
fun EmailTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String = "Email",
    modifier: Modifier = Modifier,
    placeholder: String = "your@email.com",
    isError: Boolean = false,
    errorMessage: String? = null,
    imeAction: ImeAction = ImeAction.Next,
    keyboardActions: KeyboardActions = KeyboardActions.Default,
    enabled: Boolean = true
) {
    InputTextField(
        value = value,
        onValueChange = onValueChange,
        label = label,
        placeholder = placeholder,
        isError = isError,
        errorMessage = errorMessage,
        keyboardType = KeyboardType.Email,
        imeAction = imeAction,
        keyboardActions = keyboardActions,
        enabled = enabled,
        modifier = modifier
    )
}

/**
 * Multiline text field for longer text input.
 */
@Composable
fun MultilineTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    minLines: Int = 3,
    maxLines: Int = 5,
    isError: Boolean = false,
    errorMessage: String? = null,
    enabled: Boolean = true
) {
    Column(modifier = modifier) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            label = { Text(label) },
            placeholder = { Text(placeholder) },
            isError = isError,
            minLines = minLines,
            maxLines = maxLines,
            enabled = enabled,
            modifier = Modifier.fillMaxWidth()
        )
        
        if (isError && errorMessage != null) {
            Spacer(modifier = Modifier.height(4.dp))
            ErrorText(
                text = errorMessage,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}
