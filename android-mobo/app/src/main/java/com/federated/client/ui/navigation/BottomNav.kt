package com.federated.client.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.ModelTraining
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavController
import androidx.navigation.compose.currentBackStackEntryAsState

/**
 * Bottom navigation bar component.
 * Shows main app navigation items.
 *
 * @param navController Navigation controller
 * @param onNavigate Navigation callback
 */
@Composable
fun BottomNavigationBar(
    navController: NavController,
    onNavigate: (String) -> Unit = { route ->
        navController.navigate(route) {
            // Pop up to the start destination to avoid building up a large stack
            popUpTo(navController.graph.startDestinationId) {
                saveState = true
            }
            // Avoid multiple copies of the same destination
            launchSingleTop = true
            // Restore state when reselecting a previously selected item
            restoreState = true
        }
    }
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route
    
    NavigationBar {
        bottomNavItems.forEach { item ->
            NavigationBarItem(
                icon = {
                    Icon(
                        imageVector = item.icon,
                        contentDescription = item.label
                    )
                },
                label = {
                    Text(
                        text = item.label,
                        style = MaterialTheme.typography.labelSmall
                    )
                },
                selected = currentRoute == item.route,
                onClick = {
                    if (currentRoute != item.route) {
                        onNavigate(item.route)
                    }
                }
            )
        }
    }
}

/**
 * Bottom navigation item data class.
 */
private data class BottomNavItemData(
    val route: String,
    val label: String,
    val icon: ImageVector
)

/**
 * List of bottom navigation items.
 */
private val bottomNavItems = listOf(
    BottomNavItemData(
        route = Route.Home.route,
        label = "Home",
        icon = Icons.Default.Home
    ),
    BottomNavItemData(
        route = Route.Train.route,
        label = "Train",
        icon = Icons.Default.CameraAlt
    ),
    BottomNavItemData(
        route = Route.Predict.route,
        label = "Predict",
        icon = Icons.Default.Search
    ),
    BottomNavItemData(
        route = Route.Models.route,
        label = "Models",
        icon = Icons.Default.ModelTraining
    ),
    BottomNavItemData(
        route = Route.Settings.route,
        label = "Settings",
        icon = Icons.Default.Settings
    )
)

/**
 * Check if current route should show bottom navigation.
 */
fun shouldShowBottomBar(currentRoute: String?): Boolean {
    return currentRoute in listOf(
        Route.Home.route,
        Route.Train.route,
        Route.Predict.route,
        Route.Models.route,
        Route.Settings.route
    )
}
