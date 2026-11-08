plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.serialization)
}
android {
    namespace = "com.via.core.storage"
    compileSdk = 36
    testOptions { unitTests.isIncludeAndroidResources = true }
    defaultConfig { minSdk = 26 }
}
dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.robolectric:robolectric:4.16.1")
    implementation(project(":core-model"))
    implementation(project(":core-crypto"))
    api(libs.datastore.preferences)
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.kotlinx.coroutines.android)
}
