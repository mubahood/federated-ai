package com.federated.client.ui.screens.predict

import android.graphics.BitmapFactory
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.federated.client.ui.components.ErrorMessage
import com.federated.client.ui.components.LoadingIndicator

/**
 * Predict Screen
 * Select an image and get ML model predictions
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PredictScreen(
    viewModel: PredictViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    // Gallery picker launcher
    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            try {
                val bitmap = context.contentResolver.openInputStream(it)?.use { stream ->
                    BitmapFactory.decodeStream(stream)
                }
                if (bitmap != null) {
                    viewModel.predictImage(it, bitmap)
                }
            } catch (e: Exception) {
                // Error handled in ViewModel
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Predict") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Model Status
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = if (viewModel.isModelReady()) {
                            MaterialTheme.colorScheme.primaryContainer
                        } else {
                            MaterialTheme.colorScheme.errorContainer
                        }
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = if (viewModel.isModelReady()) {
                                Icons.Default.CheckCircle
                            } else {
                                Icons.Default.Warning
                            },
                            contentDescription = null,
                            modifier = Modifier.padding(end = 12.dp)
                        )
                        Column {
                            Text(
                                text = if (viewModel.isModelReady()) {
                                    "Model Ready"
                                } else {
                                    "Model Loading..."
                                },
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "MobileNetV3 - 98.47% Accuracy",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                    }
                }

                // Image Preview
                if (uiState.selectedBitmap != null) {
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(300.dp),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Image(
                            bitmap = uiState.selectedBitmap!!.asImageBitmap(),
                            contentDescription = "Selected Image",
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Crop
                        )
                    }
                }

                // Prediction Result
                if (uiState.hasPrediction && uiState.prediction != null) {
                    val prediction = uiState.prediction!!
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.secondaryContainer
                        )
                    ) {
                        Column(
                            modifier = Modifier.padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            Text(
                                text = "Prediction Result",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Column {
                                    Text(
                                        text = "Detected",
                                        style = MaterialTheme.typography.bodyMedium
                                    )
                                    Text(
                                        text = prediction.predictedClass,
                                        style = MaterialTheme.typography.headlineMedium,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                                Column(horizontalAlignment = Alignment.End) {
                                    Text(
                                        text = "Confidence",
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                    Text(
                                        text = "${prediction.getConfidencePercentage()}%",
                                        style = MaterialTheme.typography.headlineSmall,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                            }

                            LinearProgressIndicator(
                                progress = prediction.confidence,
                                modifier = Modifier.fillMaxWidth()
                            )

                            Text(
                                text = "Inference Time: ${prediction.inferenceTimeMs}ms",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                    }
                }

                // Action Buttons
                if (!uiState.hasPrediction) {
                    Button(
                        onClick = { galleryLauncher.launch("image/*") },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = !uiState.isLoading && viewModel.isModelReady()
                    ) {
                        Icon(
                            imageVector = Icons.Default.PhotoLibrary,
                            contentDescription = null,
                            modifier = Modifier.padding(end = 8.dp)
                        )
                        Text("Select Image to Predict")
                    }
                } else {
                    OutlinedButton(
                        onClick = { viewModel.clearPrediction() },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = null,
                            modifier = Modifier.padding(end = 8.dp)
                        )
                        Text("Try Another Image")
                    }
                }

                // Error Message
                if (uiState.error != null) {
                    ErrorMessage(message = uiState.error!!)
                }

                // Loading
                if (uiState.isLoading) {
                    LoadingIndicator()
                }

                // Instructions
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "How to use",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "1. Tap 'Select Image' to choose a photo\n" +
                                    "2. The AI model will analyze and predict\n" +
                                    "3. Review the prediction and confidence score",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
        }
    }
}
