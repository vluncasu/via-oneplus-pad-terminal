package com.via.mobile

import androidx.activity.ComponentActivity
import androidx.compose.runtime.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class MobileBackTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    @Test fun androidBackFromSessionReturnsHomeWithoutFinishingActivity() {
        var screen by mutableStateOf(MobileViewModel.Screen.SESSION)
        compose.setContent { MobileBackNavigation(screen) { screen = MobileViewModel.backDestination(screen) } }
        compose.runOnIdle { compose.activity.onBackPressedDispatcher.onBackPressed() }
        compose.runOnIdle {
            assertEquals(MobileViewModel.Screen.HOME, screen)
            assertFalse(compose.activity.isFinishing)
        }
    }
    @Test fun backFromPalmEnrollmentReturnsToSettings() {
        var screen by mutableStateOf(MobileViewModel.Screen.PALM_ENROLL)
        compose.setContent { MobileBackNavigation(screen) { screen = MobileViewModel.backDestination(screen) } }
        compose.runOnIdle { compose.activity.onBackPressedDispatcher.onBackPressed() }
        compose.runOnIdle {
            assertEquals(MobileViewModel.Screen.SETTINGS, screen)
            assertFalse(compose.activity.isFinishing)
        }
    }
}
