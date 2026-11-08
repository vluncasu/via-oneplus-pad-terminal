plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.serialization)
}
android {
    namespace = "com.via.core.model"
    compileSdk = 36
    defaultConfig { minSdk = 26 }
}
dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation(libs.zxing.core)
    implementation(libs.kotlinx.serialization.json)
}
