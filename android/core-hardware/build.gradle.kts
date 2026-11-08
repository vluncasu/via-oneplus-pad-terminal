plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}
android {
    namespace = "com.via.core.hardware"
    compileSdk = 36
    defaultConfig { minSdk = 26 }
}
dependencies {
    testImplementation("junit:junit:4.13.2")
    implementation(libs.androidx.core)
    implementation(libs.kotlinx.coroutines.android)
}
