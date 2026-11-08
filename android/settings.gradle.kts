pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "VIA"
include(
    ":app-terminal",
    ":app-mobile",
    ":core-model",
    ":core-crypto",
    ":core-network",
    ":core-ui",
    ":core-vision",
    ":core-hardware",
    ":core-storage",
)
