package com.federated.client.ui.navigation

/**
 * Navigation routes for the app.
 * Sealed class ensures type-safe navigation.
 */
sealed class Route(val route: String) {
    // Onboarding
    object Splash : Route("splash")
    object Welcome : Route("welcome")
    object Registration : Route("registration")
    
    // Main navigation
    object Home : Route("home")
    object Train : Route("train") // Renamed from Camera - for training data collection
    object Predict : Route("predict") // New - for model prediction/inference
    object Label : Route("label")
    object Models : Route("models") // Renamed from Training - for model management
    object Stats : Route("stats")
    object Settings : Route("settings")
    
    // Detail screens
    object ImageDetail : Route("image_detail/{imageUri}") {
        fun createRoute(imageUri: String) = "image_detail/$imageUri"
    }
    object TrainingDetail : Route("training_detail/{sessionId}") {
        fun createRoute(sessionId: String) = "training_detail/$sessionId"
    }
    object Gallery : Route("gallery")
    object LiveDetection : Route("live_detection")
    object TrainingHistory : Route("training_history")
    object Privacy : Route("privacy")
    object About : Route("about")
}

/**
 * Bottom navigation items.
 */
enum class BottomNavItem(
    val route: String,
    val title: String,
    val icon: String // Using string for icon names, will use Material Icons
) {
    HOME(
        route = Route.Home.route,
        title = "Home",
        icon = "home"
    ),
    TRAIN(
        route = Route.Train.route,
        title = "Train",
        icon = "camera_alt"
    ),
    PREDICT(
        route = Route.Predict.route,
        title = "Predict",
        icon = "search"
    ),
    MODELS(
        route = Route.Models.route,
        title = "Models",
        icon = "model_training"
    ),
    SETTINGS(
        route = Route.Settings.route,
        title = "Settings",
        icon = "settings"
    )
}
