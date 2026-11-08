plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}
android {
    namespace = "com.via.core.vision"
    compileSdk = 36
    defaultConfig { minSdk = 26 }
}
dependencies {
    implementation(libs.camera.core)
    implementation(libs.mlkit.face)
    implementation(libs.mlkit.barcode)
    implementation(libs.mediapipe.vision)
    implementation(libs.kotlinx.coroutines.android)
}
