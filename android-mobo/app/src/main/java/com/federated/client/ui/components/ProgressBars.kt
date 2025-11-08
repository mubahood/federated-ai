package com.federated.client.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

/**
 * Linear progress bar with label.
 *
 * @param progress Progress value (0.0 to 1.0)
 * @param modifier Modifier for styling
 * @param label Optional label text
 * @param showPercentage Whether to show percentage
 * @param color Progress bar color
 */
@Composable
fun LabeledProgressBar(
    progress: Float,
    modifier: Modifier = Modifier,
    label: String? = null,
    showPercentage: Boolean = true,
    color: Color = MaterialTheme.colorScheme.primary
) {
    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (label != null) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }
            
            if (showPercentage) {
                Text(
                    text = "${(progress * 100).toInt()}%",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        LinearProgressIndicator(
            progress = progress.coerceIn(0f, 1f),
            modifier = Modifier.fillMaxWidth(),
            color = color,
            trackColor = color.copy(alpha = 0.2f)
        )
    }
}

/**
 * Training progress bar with round information.
 */
@Composable
fun TrainingProgressBar(
    currentRound: Int,
    totalRounds: Int,
    modifier: Modifier = Modifier
) {
    val progress = if (totalRounds > 0) {
        currentRound.toFloat() / totalRounds.toFloat()
    } else {
        0f
    }
    
    LabeledProgressBar(
        progress = progress,
        label = "Round $currentRound of $totalRounds",
        modifier = modifier
    )
}

/**
 * Download progress bar for model downloads.
 */
@Composable
fun DownloadProgressBar(
    downloadedBytes: Long,
    totalBytes: Long,
    modifier: Modifier = Modifier
) {
    val progress = if (totalBytes > 0) {
        (downloadedBytes.toFloat() / totalBytes.toFloat())
    } else {
        0f
    }
    
    val downloadedMB = downloadedBytes / (1024f * 1024f)
    val totalMB = totalBytes / (1024f * 1024f)
    
    LabeledProgressBar(
        progress = progress,
        label = "Downloaded: ${"%.1f".format(downloadedMB)} / ${"%.1f".format(totalMB)} MB",
        modifier = modifier
    )
}

/**
 * Simple indeterminate progress indicator.
 */
@Composable
fun IndeterminateProgressBar(
    modifier: Modifier = Modifier,
    label: String? = null,
    color: Color = MaterialTheme.colorScheme.primary
) {
    Column(modifier = modifier.fillMaxWidth()) {
        if (label != null) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
            Spacer(modifier = Modifier.height(8.dp))
        }
        
        LinearProgressIndicator(
            modifier = Modifier.fillMaxWidth(),
            color = color,
            trackColor = color.copy(alpha = 0.2f)
        )
    }
}

/**
 * Metric progress with label and value.
 */
@Composable
fun MetricProgressBar(
    label: String,
    value: Float,
    target: Float,
    modifier: Modifier = Modifier,
    unit: String = "",
    color: Color = MaterialTheme.colorScheme.primary
) {
    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Text(
                text = "${"%.2f".format(value)} / ${"%.2f".format(target)} $unit",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        LinearProgressIndicator(
            progress = if (target > 0) (value / target).coerceIn(0f, 1f) else 0f,
            modifier = Modifier.fillMaxWidth(),
            color = color,
            trackColor = color.copy(alpha = 0.2f)
        )
    }
}
