package com.via.terminal

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.via.core.model.FaceProfile
import com.via.core.ui.ViaColors

@Composable
internal fun ProfileNameEntry(name: String, onName: (String) -> Unit, onContinue: () -> Unit, onBack: () -> Unit) {
    val keyboard = androidx.compose.ui.platform.LocalSoftwareKeyboardController.current
    val continueAction = { if (name.isNotBlank()) { keyboard?.hide(); onContinue() } }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).imePadding().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(20.dp, Alignment.CenterVertically)) {
        Text("Profil nou", fontSize = 30.sp, fontWeight = FontWeight.Bold)
        OutlinedTextField(name, onName, label = { Text("Numele utilizatorului") }, singleLine = true,
            keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Words, imeAction = ImeAction.Next),
            keyboardActions = KeyboardActions(onNext = { continueAction() }), modifier = Modifier.widthIn(max = 440.dp).fillMaxWidth())
        Button(onClick = continueAction, enabled = name.isNotBlank()) { Text("Continuă") }
        TextButton(onClick = onBack) { Text("Înapoi") }
    }
}

@Composable
internal fun SavedProfiles(profiles: List<FaceProfile>, modifier: Modifier = Modifier) {
    Column(modifier.verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text("${profiles.size} " + if (profiles.size == 1) "utilizator salvat" else "utilizatori salvați", fontWeight = FontWeight.Bold, fontSize = 18.sp)
        profiles.forEach { profile ->
            Surface(color = MaterialTheme.colorScheme.surface, shape = MaterialTheme.shapes.medium) {
                Column(Modifier.fillMaxWidth().padding(14.dp)) {
                    Text(profile.displayName, fontWeight = FontWeight.SemiBold)
                    Text(if (profile.palmEmbedding.isNotEmpty()) "Față și palmă" else "Față", color = ViaColors.Muted, fontSize = 12.sp)
                }
            }
        }
    }
}
