package com.federated.client.ui.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import androidx.hilt.navigation.compose.hiltViewModel
import com.federated.client.ui.screens.onboarding.RegistrationScreen
import com.federated.client.ui.screens.onboarding.SplashScreen
import com.federated.client.ui.screens.onboarding.WelcomeCarouselScreen
import com.federated.client.ui.screens.home.HomeScreen
import com.federated.client.ui.screens.camera.CameraScreen
import com.federated.client.ui.screens.label.ImageLabelScreen
import com.federated.client.ui.screens.gallery.GalleryScreen
import com.federated.client.ui.screens.predict.PredictScreen
import com.federated.client.ui.screens.models.ModelsScreen

/**
 * Main navigation graph for the app.
 * Defines all routes and their corresponding screens.
 *
 * @param navController Navigation controller
 * @param innerPadding Padding from scaffold
 * @param startDestination Initial destination
 */
@Composable
fun NavGraph(
    navController: NavHostController,
    innerPadding: PaddingValues,
    startDestination: String = Route.Splash.route
) {
    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = Modifier.padding(innerPadding)
    ) {
        // Onboarding flow
        composable(Route.Splash.route) {
            SplashScreen(
                onNavigateNext = {
                    navController.navigate(Route.Welcome.route) {
                        popUpTo(Route.Splash.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Route.Welcome.route) {
            WelcomeCarouselScreen(
                onComplete = {
                    navController.navigate(Route.Registration.route) {
                        popUpTo(Route.Welcome.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Route.Registration.route) {
            RegistrationScreen(
                onRegistrationComplete = {
                    navController.navigate(Route.Home.route) {
                        popUpTo(Route.Registration.route) { inclusive = true }
                    }
                }
            )
        }
        
        // Main screens with bottom navigation
        composable(Route.Home.route) {
            HomeScreen(
                onNavigateToCamera = {
                    navController.navigate(Route.Train.route)
                },
                onNavigateToGallery = {
                    navController.navigate(Route.Gallery.route)
                },
                onNavigateToLabel = {
                    navController.navigate(Route.Label.route)
                },
                onNavigateToImageDetail = { imageId ->
                    navController.navigate(Route.ImageDetail.createRoute(imageId.toString()))
                }
            )
        }
        
        // Train Screen (renamed from Camera - for collecting training data)
        composable(Route.Train.route) {
            CameraScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onImageCaptured = {
                    // Navigate back to home after capture
                    navController.popBackStack()
                }
            )
        }
        
        // Predict Screen (new - for model predictions)
        composable(Route.Predict.route) {
            PredictScreen(
                viewModel = hiltViewModel()
            )
        }
        
        // Models Screen (renamed from Training - for model management)
        composable(Route.Models.route) {
            ModelsScreen(
                viewModel = hiltViewModel()
            )
        }
        
        composable(Route.Label.route) {
            ImageLabelScreen(
                navController = navController,
                viewModel = hiltViewModel()
            )
        }
        
        composable(Route.Settings.route) {
            // TODO: Implement SettingsScreen
            PlaceholderScreen("Settings Screen")
        }
        
        // Detail screens
        composable(
            route = Route.ImageDetail.route,
            arguments = listOf(
                navArgument("imageUri") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val imageUri = backStackEntry.arguments?.getString("imageUri")
            // TODO: Implement ImageDetailScreen
            PlaceholderScreen("Image Detail Screen: $imageUri")
        }
        
        composable(
            route = Route.TrainingDetail.route,
            arguments = listOf(
                navArgument("sessionId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val sessionId = backStackEntry.arguments?.getString("sessionId")
            // TODO: Implement TrainingDetailScreen
            PlaceholderScreen("Training Detail: $sessionId")
        }
        
        composable(Route.Gallery.route) {
            GalleryScreen(
                navController = navController,
                viewModel = hiltViewModel()
            )
        }
        
        composable(Route.LiveDetection.route) {
            // TODO: Implement LiveDetectionScreen
            PlaceholderScreen("Live Detection Screen")
        }
        
        composable(Route.TrainingHistory.route) {
            // TODO: Implement TrainingHistoryScreen
            PlaceholderScreen("Training History Screen")
        }
        
        composable(Route.Privacy.route) {
            // TODO: Implement PrivacyScreen
            PlaceholderScreen("Privacy Screen")
        }
        
        composable(Route.About.route) {
            // TODO: Implement AboutScreen
            PlaceholderScreen("About Screen")
        }
    }
}

/**
 * Temporary placeholder screen for development.
 */
@Composable
private fun PlaceholderScreen(title: String) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.headlineMedium
        )
    }
}
