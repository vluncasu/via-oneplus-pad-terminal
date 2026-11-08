package com.via.mobile

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.via.core.model.ViaDomain
import com.via.core.ui.*
import com.via.core.vision.PalmEnrollmentAccumulator

@Composable
fun MobileApp(vm: MobileViewModel) {
    val state by vm.ui.collectAsStateWithLifecycle()
    MobileBackNavigation(state.screen, vm::goBack)
    Scaffold(
        containerColor = ViaColors.Background,
        bottomBar = {
            if (state.screen in listOf(MobileViewModel.Screen.HOME, MobileViewModel.Screen.WALLET, MobileViewModel.Screen.SCAN, MobileViewModel.Screen.SETTINGS)) {
                NavigationBar(containerColor = Color.White) {
                    NavItem("Acasă", Icons.Outlined.Home, state.screen == MobileViewModel.Screen.HOME) { vm.navigate(MobileViewModel.Screen.HOME) }
                    NavItem("Wallet", Icons.Outlined.AccountBalanceWallet, state.screen == MobileViewModel.Screen.WALLET) { vm.navigate(MobileViewModel.Screen.WALLET) }
                    NavItem("Scanează", Icons.Outlined.QrCodeScanner, state.screen == MobileViewModel.Screen.SCAN) { vm.navigate(MobileViewModel.Screen.SCAN) }
                    NavItem("Setări", Icons.Outlined.Settings, state.screen == MobileViewModel.Screen.SETTINGS) { vm.navigate(MobileViewModel.Screen.SETTINGS) }
                }
            }
        },
    ) { padding ->
        Box(Modifier.fillMaxSize().padding(padding)) {
            when (state.screen) {
                MobileViewModel.Screen.HOME -> MobileHome(vm, state)
                MobileViewModel.Screen.WALLET -> WalletScreen(state)
                MobileViewModel.Screen.SCAN -> ScannerScreen(vm)
                MobileViewModel.Screen.SETTINGS -> SettingsScreen(vm, state)
                MobileViewModel.Screen.SESSION -> SessionScreen(vm, state)
                MobileViewModel.Screen.PALM_ENROLL -> PalmEnrollScreen(vm, state)
            }
            state.message?.let { msg -> Surface(Modifier.align(Alignment.TopCenter).padding(top = 22.dp), color = ViaColors.Ink, contentColor = Color.White, shape = RoundedCornerShape(22.dp), shadowElevation = 8.dp) { Text(msg, Modifier.padding(horizontal = 18.dp, vertical = 12.dp), fontWeight = FontWeight.SemiBold) } }
        }
    }
}

@Composable
private fun RowScope.NavItem(label: String, icon: androidx.compose.ui.graphics.vector.ImageVector, selected: Boolean, onClick: () -> Unit) {
    NavigationBarItem(selected = selected, onClick = onClick, icon = { Icon(icon, null) }, label = { Text(label) }, colors = NavigationBarItemDefaults.colors(indicatorColor = ViaColors.Ink, selectedIconColor = Color.White, selectedTextColor = ViaColors.Ink))
}

@Composable
private fun MobileHome(vm: MobileViewModel, state: MobileViewModel.UiState) {
    Column(Modifier.fillMaxSize().padding(22.dp)) {
        ViaLogo(Modifier.width(110.dp).height(44.dp))
        Spacer(Modifier.height(28.dp))
        Text("Ce urmează.", fontSize = 38.sp, fontWeight = FontWeight.Bold, letterSpacing = (-1).sp)
        Spacer(Modifier.height(18.dp))
        val transport = state.credentials.firstOrNull { it.domain == ViaDomain.TRANSPORT }
        ViaSurface(Modifier.fillMaxWidth().height(190.dp)) {
            Column(Modifier.fillMaxSize().padding(24.dp)) {
                Text("Transport", color = ViaColors.Muted)
                Spacer(Modifier.weight(1f))
                Text(transport?.claims?.get("label") ?: "Niciun abonament", fontSize = 28.sp, fontWeight = FontWeight.Bold)
                TextButton(onClick = { vm.navigate(MobileViewModel.Screen.SCAN) }, contentPadding = PaddingValues(0.dp)) { Text("Validează") }
            }
        }
        Spacer(Modifier.height(14.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(14.dp)) {
            QuickCard("Parcare", Icons.Outlined.LocalParking, Modifier.weight(1f)) { vm.navigate(MobileViewModel.Screen.WALLET) }
            QuickCard("Acces", Icons.Outlined.VerifiedUser, Modifier.weight(1f)) { vm.navigate(MobileViewModel.Screen.WALLET) }
        }
    }
}

@Composable
private fun QuickCard(title: String, icon: androidx.compose.ui.graphics.vector.ImageVector, modifier: Modifier, onClick: () -> Unit) {
    ViaSurface(modifier.height(145.dp).clickable(onClick = onClick)) { Column(Modifier.fillMaxSize().padding(20.dp)) { Icon(icon, null); Spacer(Modifier.weight(1f)); Text(title, fontSize = 22.sp, fontWeight = FontWeight.Bold) } }
}

@Composable
private fun WalletScreen(state: MobileViewModel.UiState) {
    Column(Modifier.fillMaxSize().padding(22.dp)) {
        Text("Wallet", fontSize = 38.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(18.dp))
        state.credentials.forEach { c ->
            ViaSurface(Modifier.fillMaxWidth().padding(bottom = 12.dp)) {
                Row(Modifier.fillMaxWidth().padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.size(48.dp).clip(RoundedCornerShape(15.dp)).background(Color(0xFFF1F1F3)), contentAlignment = Alignment.Center) { Icon(when(c.domain){ViaDomain.TRANSPORT->Icons.Outlined.DirectionsBus;ViaDomain.PARKING->Icons.Outlined.LocalParking;ViaDomain.ACCESS->Icons.Outlined.VerifiedUser;else->Icons.Outlined.Redeem}, null) }
                    Spacer(Modifier.width(14.dp)); Column { Text(c.domain.name.lowercase().replaceFirstChar { it.uppercase() }, color = ViaColors.Muted, fontSize = 13.sp); Text(c.claims["label"] ?: c.type, fontWeight = FontWeight.Bold, fontSize = 19.sp); c.remainingUses?.let { Text("$it utilizări", color = ViaColors.Muted) } }
                }
            }
        }
    }
}

@Composable
private fun ScannerScreen(vm: MobileViewModel) {
    val owner = LocalLifecycleOwner.current
    Box(Modifier.fillMaxSize().background(Color.Black)) {
        MobileQrCamera(owner, Modifier.fillMaxSize(), vm::handleScannedPayload)
        Box(Modifier.align(Alignment.Center).size(250.dp).clip(RoundedCornerShape(34.dp)).background(Color.Transparent))
        Text("Scanează VIA", color = Color.White, fontSize = 26.sp, fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.TopCenter).padding(top = 28.dp))
    }
}

@Composable
private fun SettingsScreen(vm: MobileViewModel, state: MobileViewModel.UiState) {
    Column(Modifier.fillMaxSize().padding(22.dp)) {
        Text("Setări", fontSize = 38.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(24.dp))
        SettingRow("Zâmbet", state.smileEnabled) { vm.setSmile(it) }
        SettingRow("VIA Light", state.viaLightEnabled) { vm.setViaLight(it) }
        ViaSurface(Modifier.fillMaxWidth().padding(top = 12.dp)) {
            Row(Modifier.fillMaxWidth().padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) { Text("Palmă", fontWeight = FontWeight.Bold); Text(if(state.palmEnabled) "Adăugată" else "Neconfigurată", color = ViaColors.Muted, fontSize = 13.sp) }
                TextButton(onClick = { vm.navigate(MobileViewModel.Screen.PALM_ENROLL) }) { Text(if(state.palmEnabled) "Refă" else "Adaugă") }
                if(state.palmEnabled) TextButton(onClick = vm::clearPalm) { Text("Șterge", color = ViaColors.Red) }
            }
        }
        Spacer(Modifier.height(24.dp)); Text("VIA păstrează template-ul palmei criptat local pe dispozitiv. Operatorii nu primesc imaginea palmei.", color = ViaColors.Muted, fontSize = 13.sp)
    }
}

@Composable
private fun SettingRow(title: String, value: Boolean, onChange: (Boolean) -> Unit) {
    ViaSurface(Modifier.fillMaxWidth().padding(bottom = 12.dp)) { Row(Modifier.fillMaxWidth().padding(20.dp), verticalAlignment = Alignment.CenterVertically) { Text(title, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f)); Switch(value, onCheckedChange = onChange) } }
}

@Composable
private fun SessionScreen(vm: MobileViewModel, state: MobileViewModel.UiState) {
    val session = state.session ?: return
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(22.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(16.dp)) {
        TextButton(onClick = vm::goBack) { Text("Înapoi") }
        Text("${session.domain} · demo", color = ViaColors.Muted)
        Text(session.operatorName, fontSize = 24.sp, fontWeight = FontWeight.Bold)
        session.amount?.let { Text(it.display, fontSize = 32.sp) }
        if (state.delivered) Icon(Icons.Outlined.CheckCircle, null, Modifier.size(80.dp), tint = ViaColors.Ink)
        else if (state.busy) CircularProgressIndicator()
        else Button(onClick = vm::confirmPhone) { Text("Reîncearcă") }
        state.message?.let { Text(it) }
    }
}

@Composable
private fun PalmEnrollScreen(vm: MobileViewModel, state: MobileViewModel.UiState) {
    val owner = LocalLifecycleOwner.current
    val accumulator = remember { PalmEnrollmentAccumulator() }
    var done by remember { mutableStateOf(false) }
    Box(Modifier.fillMaxSize().background(Color.Black)) {
        if(!done) MobilePalmCamera(owner, Modifier.fillMaxSize(), onDescriptor = { d ->
            if(accumulator.offer(d)) vm.setPalmProgress(accumulator.progress)
            if(accumulator.ready && !done) { done = true; vm.savePalmTemplate(accumulator.template()) }
        }, onError = {})
        Column(Modifier.fillMaxSize().padding(24.dp)) {
            IconButton(onClick = { vm.navigate(MobileViewModel.Screen.SETTINGS) }) { Icon(Icons.Outlined.Close, null, tint = Color.White) }
            Spacer(Modifier.weight(1f)); Text(if(done) "Palmă adăugată." else "Arată palma.", color = Color.White, fontSize = 40.sp, fontWeight = FontWeight.Bold); Spacer(Modifier.height(14.dp)); LinearProgressIndicator(progress = { state.palmEnrollProgress }, modifier = Modifier.fillMaxWidth(), color = Color.White, trackColor = Color.White.copy(.2f)); if(done){Spacer(Modifier.height(16.dp)); Button(onClick={vm.navigate(MobileViewModel.Screen.SETTINGS)}){Text("Gata")}}; Spacer(Modifier.height(24.dp))
        }
    }
}

@Composable
private fun MobileResponseQr(content: String, modifier: Modifier) {
    val matrix = remember(content) {
        runCatching {
            com.google.zxing.qrcode.QRCodeWriter().encode(content, com.google.zxing.BarcodeFormat.QR_CODE, 0, 0, mapOf(com.google.zxing.EncodeHintType.MARGIN to 4))
        }.getOrNull()
    }
    if (matrix != null) {
        Canvas(modifier.background(Color.White).padding(12.dp)) {
            val w = matrix.width; val h = matrix.height
            val cellW = size.width / w; val cellH = size.height / h
            for (x in 0 until w) for (y in 0 until h) if (matrix.get(x, y)) drawRect(ViaColors.Ink, topLeft = Offset(x * cellW, y * cellH), size = Size(cellW, cellH))
        }
    } else {
        Box(modifier.background(Color.White), contentAlignment = Alignment.Center) { Text("QR", color = ViaColors.Muted) }
    }
}

@Composable
internal fun MobileBackNavigation(screen: MobileViewModel.Screen, onBack: () -> Unit) {
    androidx.activity.compose.BackHandler(enabled = screen != MobileViewModel.Screen.HOME, onBack = onBack)
}
