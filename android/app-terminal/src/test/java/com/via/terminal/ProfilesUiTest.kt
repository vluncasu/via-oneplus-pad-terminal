package com.via.terminal

import androidx.activity.ComponentActivity
import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.foundation.layout.*
import androidx.compose.ui.Modifier
import com.via.core.model.FaceProfile
import com.via.core.ui.ViaTheme
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35], qualifiers = "w1280dp-h800dp-land-mdpi")
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class ProfilesUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    @Test fun nameRequiredBeforeStartingCamera() {
        var continued = false
        compose.setContent { ViaTheme {
            var name by remember { mutableStateOf("") }
            ProfileNameEntry(name, { name = it }, { continued = true }, {})
        } }
        compose.onNodeWithText("Continuă").assertIsNotEnabled()
        compose.onNodeWithText("Numele utilizatorului").performTextInput("Ștefan")
        compose.onNodeWithText("Continuă").assertIsEnabled().performClick()
        assertTrue(continued)
    }
    @Test fun experiencesDisplaysAllProfilesAndUpdatesCount() {
        val profiles = mutableStateOf(listOf(FaceProfile("1", "Ana", emptyList(), emptyList(), 1)))
        compose.setContent { ViaTheme { SavedProfiles(profiles.value, Modifier.fillMaxSize()) } }
        compose.onNodeWithText("1 utilizator salvat").assertIsDisplayed()
        compose.runOnIdle { profiles.value = profiles.value + listOf(FaceProfile("2", "Mihai", emptyList(), emptyList(), 2), FaceProfile("3", "Ștefan", emptyList(), emptyList(), 3)) }
        compose.onNodeWithText("3 utilizatori salvați").assertIsDisplayed()
        listOf("Ana","Mihai","Ștefan").forEach { compose.onNodeWithText(it).assertIsDisplayed() }
    }
}
