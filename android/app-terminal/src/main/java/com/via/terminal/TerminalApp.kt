package com.via.terminal

import androidx.compose.animation.*
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.via.core.model.ConfirmationMethod
import com.via.core.model.ViaDomain
import com.via.core.ui.*
import kotlin.math.min

@Composable
fun TerminalApp(vm: TerminalViewModel, modifier: Modifier = Modifier) {
    val state by vm.ui.collectAsStateWithLifecycle()
    val config = LocalConfiguration.current
    val isLandscape = config.screenWidthDp > config.screenHeightDp
    val isTablet = min(config.screenWidthDp, config.screenHeightDp) >= 600

    Box(modifier.background(ViaColors.Background)) {
        if (isLandscape && isTablet) {
            TabletLayout(vm, state)
        } else if (isLandscape) {
            CompactLandscapeLayout(vm, state)
        } else {
            PortraitLayout(vm, state)
        }
        state.resultTitle?.let {
            ResultOverlay(it, state.resultSubtitle, state.resultKind == TerminalViewModel.ResultKind.SUCCESS)
        }
    }
}

@Composable
private fun TabletLayout(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    Row(Modifier.fillMaxSize().clickable(indication = null, interactionSource = remember { MutableInteractionSource() }) { vm.userInteraction() }) {
        ViaSidebar(
            current = currentRailDest(state.screen),
            onLogoTap = { vm.onLogoTap() },
            onSelect = { handleRailSelect(it, vm) },
        )
        Box(Modifier.weight(1f).fillMaxHeight().padding(24.dp)) {
            ScreenRouter(vm, state)
        }
    }
}

@Composable
private fun CompactLandscapeLayout(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    Row(Modifier.fillMaxSize().clickable(indication = null, interactionSource = remember { MutableInteractionSource() }) { vm.userInteraction() }) {
        ViaSidebar(
            current = currentRailDest(state.screen),
            onLogoTap = { vm.onLogoTap() },
            onSelect = { handleRailSelect(it, vm) },
        )
        Box(Modifier.weight(1f).fillMaxHeight().padding(16.dp)) {
            ScreenRouter(vm, state)
        }
    }
}

@Composable
private fun PortraitLayout(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    Column(Modifier.fillMaxSize().clickable(indication = null, interactionSource = remember { MutableInteractionSource() }) { vm.userInteraction() }) {
        Box(Modifier.weight(1f).fillMaxWidth().padding(16.dp)) {
            ScreenRouter(vm, state)
        }
        BottomNavBar(
            current = currentRailDest(state.screen),
            onLogoTap = { vm.onLogoTap() },
            onSelect = { handleRailSelect(it, vm) },
        )
    }
}

@Composable
private fun BottomNavBar(
    current: RailDestination,
    onLogoTap: () -> Unit,
    onSelect: (RailDestination) -> Unit,
) {
    Surface(
        tonalElevation = 2.dp,
        shadowElevation = 8.dp,
    ) {
        Row(
            Modifier.fillMaxWidth().navigationBarsPadding().height(72.dp).padding(horizontal = 8.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            ViaLogo(
                Modifier.size(32.dp).clickable(onClick = onLogoTap)
            )
            for (dest in RailDestination.entries) {
                val selected = dest == current
                FilledIconButton(
                    onClick = { onSelect(dest) },
                    modifier = Modifier.size(52.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = if (selected) ViaColors.Ink else Color.Transparent,
                        contentColor = if (selected) Color.White else Color(0xFF86868B),
                    ),
                ) {
                    Icon(dest.icon, contentDescription = dest.name, modifier = Modifier.size(22.dp))
                }
            }
        }
    }
}

private fun currentRailDest(screen: TerminalViewModel.Screen): RailDestination = when (screen) {
    TerminalViewModel.Screen.HOME, TerminalViewModel.Screen.ENROLL, TerminalViewModel.Screen.PALM_ENROLL -> RailDestination.HOME
    TerminalViewModel.Screen.PAY, TerminalViewModel.Screen.SMILE, TerminalViewModel.Screen.PALM, TerminalViewModel.Screen.PHONE -> RailDestination.PAY
    TerminalViewModel.Screen.VALIDATE, TerminalViewModel.Screen.TAP -> RailDestination.VALIDATE
    TerminalViewModel.Screen.DOWNLOAD -> RailDestination.DOWNLOAD
    else -> RailDestination.HOME
}

private fun handleRailSelect(dest: RailDestination, vm: TerminalViewModel) {
    when (dest) {
        RailDestination.HOME -> vm.navigate(TerminalViewModel.Screen.HOME)
        RailDestination.PAY -> vm.beginPayment()
        RailDestination.VALIDATE -> vm.navigate(TerminalViewModel.Screen.VALIDATE)
        RailDestination.DOWNLOAD -> vm.navigate(TerminalViewModel.Screen.DOWNLOAD)
    }
}

@Composable
private fun ScreenRouter(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    AnimatedContent(
        targetState = state.screen,
        transitionSpec = {
            (fadeIn(tween(220)) + slideInHorizontally { it / 12 })
                .togetherWith(fadeOut(tween(180)))
        },
        label = "screen",
    ) { screen ->
        when (screen) {
            TerminalViewModel.Screen.HOME -> HomeScreen(vm, state)
            TerminalViewModel.Screen.PAY -> PayScreen(vm, state)
            TerminalViewModel.Screen.VALIDATE -> ValidateScreen(vm)
            TerminalViewModel.Screen.DOWNLOAD -> DownloadScreen(vm, state)
            TerminalViewModel.Screen.SMILE -> SmileScreen(vm, state)
            TerminalViewModel.Screen.PALM -> PalmScreen(vm, state)
            TerminalViewModel.Screen.PHONE -> PhoneScreen(vm, state)
            TerminalViewModel.Screen.TAP -> TapScreen(vm, state.validationDomain)
            TerminalViewModel.Screen.ENROLL -> EnrollScreen(vm, state)
            TerminalViewModel.Screen.PALM_ENROLL -> PalmEnrollScreen(vm, state)
            TerminalViewModel.Screen.PRESENTATION -> PresentationScreen(vm, state)
            TerminalViewModel.Screen.ENGINEERING -> EngineeringScreen(vm, state)
        }
    }
}

// --- Adaptive dimensions ---

@Composable
private fun adaptiveHeroFontSize(): Int {
    val w = LocalConfiguration.current.screenWidthDp
    return when {
        w >= 1200 -> 72
        w >= 900 -> 56
        w >= 600 -> 42
        else -> 32
    }
}

@Composable
private fun adaptiveRadius(): Dp {
    val w = LocalConfiguration.current.screenWidthDp
    return if (w >= 600) 38.dp else 24.dp
}

@Composable
private fun isCompact(): Boolean = LocalConfiguration.current.screenWidthDp < 600

@Composable
private fun isShortLandscape(): Boolean {
    val config = LocalConfiguration.current
    return config.screenWidthDp > config.screenHeightDp && config.screenHeightDp < 500
}

@Composable
private fun adaptiveAmountSize(): Int {
    val h = LocalConfiguration.current.screenHeightDp
    return when {
        h >= 700 -> 72
        h >= 500 -> 56
        else -> 42
    }
}

// --- Category Filter ---

private val HOME_CATEGORIES = listOf("Toate", "Locații", "Muzică", "Servicii", "Experiențe")

@Composable
private fun CategoryChipBar(selected: String, onSelect: (String) -> Unit) {
    Row(
        Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Spacer(Modifier.width(4.dp))
        HOME_CATEGORIES.forEach { cat ->
            val isSelected = cat == selected
            Surface(
                modifier = Modifier
                    .clickable { onSelect(cat) }
                    .then(if (!isSelected) Modifier.border(1.dp, Color(0xFFE0E0E0), RoundedCornerShape(20.dp)) else Modifier),
                color = if (isSelected) ViaColors.Ink else Color.Transparent,
                shape = RoundedCornerShape(20.dp),
            ) {
                Text(
                    cat,
                    color = if (isSelected) Color.White else ViaColors.Ink,
                    fontSize = 14.sp,
                    fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Medium,
                    modifier = Modifier.padding(horizontal = 18.dp, vertical = 10.dp),
                )
            }
        }
        Spacer(Modifier.width(4.dp))
    }
}

// --- Screens ---

@Composable
private fun HomeScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    val heroSize = adaptiveHeroFontSize()
    val radius = adaptiveRadius()
    val compact = isCompact()
    val greeting = state.recognizedProfile?.displayName
    var selectedCategory by remember { mutableStateOf("Toate") }

    Column(Modifier.fillMaxSize()) {
        CategoryChipBar(selected = selectedCategory, onSelect = { selectedCategory = it })
        AnimatedContent(
            targetState = selectedCategory,
            transitionSpec = { fadeIn(tween(200)).togetherWith(fadeOut(tween(150))) },
            label = "category",
            modifier = Modifier.weight(1f),
        ) { category ->
            if (compact) {
                HomeCompactContent(category, vm, state, greeting, heroSize, radius)
            } else {
                HomeLandscapeContent(category, vm, state, greeting, heroSize, radius)
            }
        }
    }
}

@Composable
private fun HomeCompactContent(
    category: String,
    vm: TerminalViewModel,
    state: TerminalViewModel.UiState,
    greeting: String?,
    heroSize: Int,
    radius: Dp,
) {
    Column(Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        when (category) {
            "Toate" -> {
                Box(Modifier.fillMaxWidth().clip(RoundedCornerShape(radius)).background(ViaColors.Ink).padding(28.dp)) {
                    Column {
                        if (greeting != null) Text(greeting, color = Color.White.copy(.6f), fontSize = 18.sp, fontWeight = FontWeight.Medium)
                        Text("Plătește.\nValidează.\nIntră.", color = Color.White, fontSize = heroSize.sp, lineHeight = (heroSize - 4).sp, fontWeight = FontWeight.Bold, letterSpacing = (-2).sp)
                        Spacer(Modifier.height(18.dp))
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            CompactAction("Plătește", Icons.Outlined.CreditCard, Modifier.weight(1f)) { vm.beginPayment() }
                            CompactAction("Validează", Icons.Outlined.VerifiedUser, Modifier.weight(1f)) { vm.navigate(TerminalViewModel.Screen.VALIDATE) }
                        }
                    }
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    CompactHomeCard(Icons.Outlined.PersonAdd, "Profil nou", Modifier.weight(1f)) { vm.startEnrollment() }
                    CompactHomeCard(Icons.Outlined.PanToolAlt, "Palmă", Modifier.weight(1f)) { vm.startPalmEnrollment() }
                }
                ViaSurface(Modifier.fillMaxWidth()) {
                    Row(Modifier.fillMaxWidth().padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Outlined.PhoneAndroid, null, Modifier.size(80.dp))
                        Spacer(Modifier.width(16.dp))
                        Column {
                            Text("VIA pe telefon", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                            Text("Instalează VIA Mobile local", color = ViaColors.Muted, fontSize = 13.sp)
                        }
                    }
                }
            }
            "Locații" -> {
                ViaSurface(Modifier.fillMaxWidth()) {
                    Column(Modifier.fillMaxWidth().padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Outlined.PhoneAndroid, null, Modifier.size(80.dp))
                        Spacer(Modifier.height(16.dp))
                        Text("VIA pe telefon", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                        Text("Instalează APK-ul VIA Mobile pe telefon.", color = ViaColors.Muted, fontSize = 14.sp)
                    }
                }
                ViaSurface(Modifier.fillMaxWidth()) {
                    Row(Modifier.fillMaxWidth().padding(20.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                        Surface(color = Color(0xFFF1F1F3), shape = RoundedCornerShape(14.dp)) { Icon(Icons.Outlined.LocationOn, null, modifier = Modifier.padding(10.dp).size(22.dp)) }
                        Column {
                            Text("Locații VIA", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                            Text("Disponibil în toată România.", color = ViaColors.Muted, fontSize = 13.sp)
                        }
                    }
                }
            }
            "Muzică" -> {
                Box(Modifier.fillMaxWidth().clip(RoundedCornerShape(24.dp)).background(Color(0xFF1A1A2E)).padding(32.dp)) {
                    Column {
                        Icon(Icons.Outlined.MusicNote, null, tint = ViaColors.Blue, modifier = Modifier.size(40.dp))
                        Spacer(Modifier.height(16.dp))
                        Text("Muzică", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.height(8.dp))
                        Text("Plătește abonamentul cu VIA.\nCurând disponibil.", color = Color.White.copy(.5f), fontSize = 15.sp, lineHeight = 22.sp)
                    }
                }
            }
            "Servicii" -> {
                Box(Modifier.fillMaxWidth().clip(RoundedCornerShape(radius)).background(ViaColors.Ink).padding(28.dp)) {
                    Column {
                        Text("Servicii VIA", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold, letterSpacing = (-1).sp)
                        Spacer(Modifier.height(6.dp))
                        Text("Plată, validare, acces.", color = Color.White.copy(.5f), fontSize = 15.sp)
                        Spacer(Modifier.height(24.dp))
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            CompactAction("Plătește", Icons.Outlined.CreditCard, Modifier.weight(1f)) { vm.beginPayment() }
                            CompactAction("Validează", Icons.Outlined.VerifiedUser, Modifier.weight(1f)) { vm.navigate(TerminalViewModel.Screen.VALIDATE) }
                        }
                    }
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    CompactHomeCard(Icons.Outlined.DirectionsBus, "Transport", Modifier.weight(1f)) { vm.beginValidation(ViaDomain.TRANSPORT) }
                    CompactHomeCard(Icons.Outlined.LocalParking, "Parcare", Modifier.weight(1f)) { vm.beginValidation(ViaDomain.PARKING) }
                }
            }
            "Experiențe" -> {
                Box(Modifier.fillMaxWidth().clip(RoundedCornerShape(radius)).background(ViaColors.Blue).padding(28.dp)) {
                    Column {
                        Text("Experiențe VIA", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold, letterSpacing = (-1).sp)
                        Spacer(Modifier.height(6.dp))
                        Text("Profil facial, palmă, personalizare.", color = Color.White.copy(.7f), fontSize = 15.sp)
                    }
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    CompactHomeCard(Icons.Outlined.PersonAdd, "Profil nou", Modifier.weight(1f)) { vm.startEnrollment() }
                    CompactHomeCard(Icons.Outlined.PanToolAlt, "Palmă", Modifier.weight(1f)) { vm.startPalmEnrollment() }
                }
                SavedProfiles(state.profiles, Modifier.fillMaxWidth().weight(1f))
                if (greeting != null) {
                    ViaSurface(Modifier.fillMaxWidth()) {
                        Row(Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                            Surface(color = ViaColors.Green.copy(.15f), shape = RoundedCornerShape(14.dp)) { Icon(Icons.Outlined.Check, null, tint = ViaColors.Green, modifier = Modifier.padding(10.dp).size(22.dp)) }
                            Column {
                                Text(greeting, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                                Text("Profil activ", color = ViaColors.Muted, fontSize = 13.sp)
                            }
                        }
                    }
                }
            }
        }
        Spacer(Modifier.weight(1f))
    }
}

@Composable
private fun HomeLandscapeContent(
    category: String,
    vm: TerminalViewModel,
    state: TerminalViewModel.UiState,
    greeting: String?,
    heroSize: Int,
    radius: Dp,
) {
    when (category) {
        "Toate" -> {
            Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                Box(Modifier.weight(1.7f).fillMaxHeight().clip(RoundedCornerShape(radius)).background(ViaColors.Ink).padding(44.dp)) {
                    Column(Modifier.fillMaxSize()) {
                        if (greeting != null) { Text(greeting, color = Color.White.copy(.6f), fontSize = 28.sp, fontWeight = FontWeight.Medium); Spacer(Modifier.height(4.dp)) }
                        Text("Plătește.\nValidează.\nIntră.", color = Color.White, fontSize = heroSize.sp, lineHeight = (heroSize - 6).sp, fontWeight = FontWeight.Bold, letterSpacing = (-3).sp)
                        Spacer(Modifier.weight(1f))
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            HeroAction("Plătește", Icons.Outlined.CreditCard, Modifier.weight(1f)) { vm.beginPayment() }
                            HeroAction("Validează", Icons.Outlined.VerifiedUser, Modifier.weight(1f)) { vm.navigate(TerminalViewModel.Screen.VALIDATE) }
                            HeroAction("Profil nou", Icons.Outlined.PersonAdd, Modifier.weight(1f)) { vm.startEnrollment() }
                        }
                    }
                }
                ViaSurface(Modifier.weight(.68f).fillMaxHeight()) {
                    Column(Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("VIA pe\ntelefon.", fontSize = 28.sp, lineHeight = 28.sp, fontWeight = FontWeight.Bold, letterSpacing = (-1).sp)
                        Spacer(Modifier.height(8.dp))
                        Icon(Icons.Outlined.PhoneAndroid, null, Modifier.size(80.dp))
                        Text("Android", color = ViaColors.Blue, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                    }
                }
            }
        }
        "Locații" -> {
            Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ViaSurface(Modifier.weight(1f).fillMaxHeight()) {
                    Column(Modifier.fillMaxSize().padding(36.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                        Icon(Icons.Outlined.PhoneAndroid, null, Modifier.size(80.dp))
                        Spacer(Modifier.height(20.dp))
                        Text("VIA pe telefon", fontSize = 32.sp, fontWeight = FontWeight.Bold)
                        Text("Instalează VIA Mobile local", color = ViaColors.Muted, fontSize = 16.sp)
                    }
                }
                Box(Modifier.weight(1f).fillMaxHeight().clip(RoundedCornerShape(radius)).background(ViaColors.Ink).padding(44.dp), contentAlignment = Alignment.CenterStart) {
                    Column {
                        Icon(Icons.Outlined.LocationOn, null, tint = ViaColors.Blue, modifier = Modifier.size(44.dp))
                        Spacer(Modifier.height(16.dp))
                        Text("Locații\nVIA.", color = Color.White, fontSize = 42.sp, lineHeight = 42.sp, fontWeight = FontWeight.Bold, letterSpacing = (-2).sp)
                        Spacer(Modifier.height(12.dp))
                        Text("Disponibil în toată România.", color = Color.White.copy(.5f), fontSize = 18.sp)
                    }
                }
            }
        }
        "Muzică" -> {
            Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                Box(Modifier.weight(1f).fillMaxHeight().clip(RoundedCornerShape(radius)).background(Color(0xFF1A1A2E)).padding(44.dp), contentAlignment = Alignment.CenterStart) {
                    Column {
                        Icon(Icons.Outlined.MusicNote, null, tint = ViaColors.Blue, modifier = Modifier.size(52.dp))
                        Spacer(Modifier.height(20.dp))
                        Text("Muzică.", color = Color.White, fontSize = 48.sp, fontWeight = FontWeight.Bold, letterSpacing = (-3).sp)
                        Spacer(Modifier.height(12.dp))
                        Text("Plătește abonamentul cu VIA.\nCurând disponibil.", color = Color.White.copy(.5f), fontSize = 18.sp, lineHeight = 26.sp)
                    }
                }
            }
        }
        "Servicii" -> {
            Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                Box(Modifier.weight(1.5f).fillMaxHeight().clip(RoundedCornerShape(radius)).background(ViaColors.Ink).padding(44.dp)) {
                    Column(Modifier.fillMaxSize()) {
                        Text("Servicii VIA", color = Color.White, fontSize = 42.sp, fontWeight = FontWeight.Bold, letterSpacing = (-2).sp)
                        Spacer(Modifier.height(8.dp))
                        Text("Plată, validare, acces.", color = Color.White.copy(.5f), fontSize = 18.sp)
                        Spacer(Modifier.weight(1f))
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            HeroAction("Plătește", Icons.Outlined.CreditCard, Modifier.weight(1f)) { vm.beginPayment() }
                            HeroAction("Validează", Icons.Outlined.VerifiedUser, Modifier.weight(1f)) { vm.navigate(TerminalViewModel.Screen.VALIDATE) }
                        }
                    }
                }
                ViaSurface(Modifier.weight(1f).fillMaxHeight()) {
                    Column(Modifier.fillMaxSize().padding(32.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        Text("Validare", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                        LandscapeServiceRow(Icons.Outlined.DirectionsBus, "Transport") { vm.beginValidation(ViaDomain.TRANSPORT) }
                        LandscapeServiceRow(Icons.Outlined.LocalParking, "Parcare") { vm.beginValidation(ViaDomain.PARKING) }
                        LandscapeServiceRow(Icons.Outlined.VerifiedUser, "Acces") { vm.beginValidation(ViaDomain.ACCESS) }
                        LandscapeServiceRow(Icons.Outlined.Redeem, "Beneficii") { vm.beginValidation(ViaDomain.BENEFIT) }
                    }
                }
            }
        }
        "Experiențe" -> {
            Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                Box(Modifier.weight(1f).fillMaxHeight().clip(RoundedCornerShape(radius)).background(ViaColors.Blue).padding(44.dp), contentAlignment = Alignment.CenterStart) {
                    Column {
                        Text("Experiențe\nVIA.", color = Color.White, fontSize = 48.sp, lineHeight = 48.sp, fontWeight = FontWeight.Bold, letterSpacing = (-3).sp)
                        Spacer(Modifier.height(12.dp))
                        Text("Profil facial, palmă, personalizare.", color = Color.White.copy(.7f), fontSize = 18.sp)
                        if (greeting != null) {
                            Spacer(Modifier.height(24.dp))
                            Surface(color = Color.White.copy(.15f), shape = RoundedCornerShape(18.dp)) {
                                Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                    Icon(Icons.Outlined.Check, null, tint = Color.White, modifier = Modifier.size(20.dp))
                                    Text(greeting, color = Color.White, fontWeight = FontWeight.SemiBold)
                                }
                            }
                        }
                    }
                }
                ViaSurface(Modifier.weight(1f).fillMaxHeight()) {
                    Column(Modifier.fillMaxSize().padding(28.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        Text("Biometrie", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                        SavedProfiles(state.profiles, Modifier.fillMaxWidth().weight(1f))
                        LandscapeServiceRow(Icons.Outlined.PersonAdd, "Profil nou") { vm.startEnrollment() }
                        LandscapeServiceRow(Icons.Outlined.PanToolAlt, "Înregistrare palmă") { vm.startPalmEnrollment() }
                    }
                }
            }
        }
    }
}

@Composable
private fun CompactHomeCard(icon: ImageVector, label: String, modifier: Modifier, onClick: () -> Unit) {
    ViaSurface(modifier) {
        Row(Modifier.clickable(onClick = onClick).padding(16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Icon(icon, null, modifier = Modifier.size(20.dp))
            Text(label, fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
        }
    }
}

@Composable
private fun LandscapeServiceRow(icon: ImageVector, label: String, onClick: () -> Unit) {
    Surface(Modifier.fillMaxWidth().clickable(onClick = onClick), color = Color(0xFFF4F4F6), shape = RoundedCornerShape(18.dp)) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Surface(color = Color.White, shape = RoundedCornerShape(12.dp)) { Icon(icon, null, modifier = Modifier.padding(8.dp).size(20.dp)) }
            Text(label, fontWeight = FontWeight.SemiBold, fontSize = 16.sp)
        }
    }
}

@Composable
private fun CompactAction(text: String, icon: ImageVector, modifier: Modifier, onClick: () -> Unit) {
    Surface(modifier.clickable(onClick = onClick), color = Color.White.copy(.09f), shape = RoundedCornerShape(18.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Color.White.copy(.07f))) {
        Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Icon(icon, null, tint = Color.White, modifier = Modifier.size(20.dp))
            Text(text, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
private fun HeroAction(text: String, icon: ImageVector, modifier: Modifier, onClick: () -> Unit) {
    Surface(modifier.clickable(onClick = onClick), color = Color.White.copy(.09f), shape = RoundedCornerShape(26.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Color.White.copy(.07f))) {
        Column(Modifier.height(126.dp).padding(20.dp), verticalArrangement = Arrangement.SpaceBetween) {
            Surface(color = Color.White.copy(.11f), shape = RoundedCornerShape(15.dp)) {
                Icon(icon, null, tint = Color.White, modifier = Modifier.padding(10.dp).size(23.dp))
            }
            Text(text, color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
private fun PayScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    val compact = isCompact()
    Column {
        ScreenTitle("Plătește") { vm.navigate(TerminalViewModel.Screen.HOME) }
        if (compact) {
            Column(Modifier.weight(1f).fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                ViaSurface(Modifier.fillMaxWidth()) {
                    Row(Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(40.dp).clip(RoundedCornerShape(12.dp)).background(ViaColors.Ink), contentAlignment = Alignment.Center) { Text("V", color = Color.White, fontWeight = FontWeight.Bold) }
                        Spacer(Modifier.width(12.dp))
                        Column {
                            Text(state.merchant, color = ViaColors.Muted, fontSize = 13.sp)
                            Text("${state.amountDisplay} lei", fontSize = 28.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
                Text("Confirmă cu", fontSize = 22.sp, fontWeight = FontWeight.Bold)
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    PortraitMethodCard("Zâmbet", Icons.Outlined.SentimentSatisfied, true, Modifier.weight(1f), "confirmare") { vm.navigate(TerminalViewModel.Screen.SMILE) }
                    PortraitMethodCard("Palmă", Icons.Outlined.PanToolAlt, false, Modifier.weight(1f), "pe dispozitiv") { vm.navigate(TerminalViewModel.Screen.PALM) }
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    PortraitMethodCard("Telefon", Icons.Outlined.PhoneAndroid, false, Modifier.weight(1f), "VIA") { vm.navigate(TerminalViewModel.Screen.PHONE) }
                    PortraitMethodCard("QR", Icons.Outlined.QrCode2, false, Modifier.weight(1f), "VIA Light") { vm.openQrExchange() }
                }
                Spacer(Modifier.weight(1f))
            }
        } else {
            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ViaSurface(Modifier.weight(.82f).fillMaxHeight()) {
                    Column(Modifier.fillMaxSize().padding(38.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(Modifier.size(48.dp).clip(RoundedCornerShape(16.dp)).background(ViaColors.Ink), contentAlignment = Alignment.Center) { Text("V", color = Color.White, fontWeight = FontWeight.Bold) }
                            Spacer(Modifier.width(14.dp)); Text(state.merchant, color = ViaColors.Muted, fontWeight = FontWeight.SemiBold)
                        }
                        Column(Modifier.weight(1f), verticalArrangement = Arrangement.Center) {
                            val amtSize = adaptiveAmountSize()
                            Text("Total", color = ViaColors.Muted)
                            Text(state.amountDisplay, fontSize = amtSize.sp, lineHeight = (amtSize + 4).sp, fontWeight = FontWeight.Bold, letterSpacing = (-3).sp)
                            Text("lei", color = ViaColors.Muted, fontSize = 18.sp)
                        }
                        HorizontalDivider(color = ViaColors.Hairline)
                        Text("VIA-01", color = ViaColors.Muted, modifier = Modifier.padding(top = 18.dp))
                    }
                }
                ViaSurface(Modifier.weight(1.22f).fillMaxHeight()) {
                    val shortL = isShortLandscape()
                    Column(Modifier.fillMaxSize().padding(if (shortL) 20.dp else 30.dp)) {
                        Text("Confirmă cu", fontSize = if (shortL) 26.sp else 34.sp, fontWeight = FontWeight.Bold, letterSpacing = (-1).sp)
                        Spacer(Modifier.height(if (shortL) 10.dp else 18.dp))
                        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                MethodCard("Zâmbet", "confirmare", Icons.Outlined.SentimentSatisfied, true, Modifier.weight(1f)) { vm.navigate(TerminalViewModel.Screen.SMILE) }
                                MethodCard("Palmă", "pe dispozitiv", Icons.Outlined.PanToolAlt, false, Modifier.weight(1f)) { vm.navigate(TerminalViewModel.Screen.PALM) }
                            }
                            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                MethodCard("Telefon", "VIA", Icons.Outlined.PhoneAndroid, false, Modifier.weight(1f)) { vm.navigate(TerminalViewModel.Screen.PHONE) }
                                MethodCard("QR", "VIA Light", Icons.Outlined.QrCode2, false, Modifier.weight(1f)) { vm.openQrExchange() }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SmallMethodCard(title: String, icon: ImageVector, dark: Boolean, modifier: Modifier, onClick: () -> Unit) {
    val bg = if (dark) ViaColors.Ink else Color(0xFFF4F4F6)
    val fg = if (dark) Color.White else ViaColors.Ink
    Surface(modifier.height(72.dp).clickable(onClick = onClick), color = bg, shape = RoundedCornerShape(18.dp)) {
        Row(Modifier.fillMaxSize().padding(horizontal = 16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Icon(icon, null, tint = fg, modifier = Modifier.size(22.dp))
            Text(title, color = fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
private fun PortraitMethodCard(title: String, icon: ImageVector, dark: Boolean, modifier: Modifier, subtitle: String? = null, onClick: () -> Unit) {
    val bg = if (dark) ViaColors.Ink else Color.White
    val fg = if (dark) Color.White else ViaColors.Ink
    val border = if (dark) null else androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE8E8ED))
    Surface(modifier.aspectRatio(1.6f).clickable(onClick = onClick), color = bg, shape = RoundedCornerShape(22.dp), border = border, shadowElevation = if (dark) 0.dp else 2.dp) {
        Column(Modifier.fillMaxSize().padding(18.dp), verticalArrangement = Arrangement.SpaceBetween) {
            Surface(color = if (dark) Color.White.copy(.11f) else Color(0xFFF2F2F5), shape = RoundedCornerShape(14.dp)) { Icon(icon, null, tint = fg, modifier = Modifier.padding(10.dp).size(22.dp)) }
            Column {
                Text(title, color = fg, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                if (subtitle != null) Text(subtitle, color = if (dark) Color.White.copy(.45f) else ViaColors.Muted, fontSize = 11.sp)
            }
        }
    }
}

@Composable
private fun MethodCard(title: String, subtitle: String, icon: ImageVector, dark: Boolean, modifier: Modifier, onClick: () -> Unit) {
    val bg = if (dark) ViaColors.Ink else Color(0xFFF4F4F6)
    val fg = if (dark) Color.White else ViaColors.Ink
    Surface(modifier.clickable(onClick = onClick), color = bg, shape = RoundedCornerShape(26.dp)) {
        Column(Modifier.fillMaxSize().padding(22.dp), verticalArrangement = Arrangement.SpaceBetween) {
            Surface(color = if (dark) Color.White.copy(.11f) else Color.White, shape = RoundedCornerShape(16.dp)) { Icon(icon, null, tint = fg, modifier = Modifier.padding(11.dp).size(25.dp)) }
            Column { Text(title, color = fg, fontSize = 22.sp, fontWeight = FontWeight.SemiBold); Text(subtitle, color = if (dark) Color.White.copy(.45f) else ViaColors.Muted, fontSize = 12.sp) }
        }
    }
}

@Composable
private fun ValidateScreen(vm: TerminalViewModel) {
    val compact = isCompact()
    Column {
        ScreenTitle("Validează") { vm.navigate(TerminalViewModel.Screen.HOME) }
        if (compact) {
            Column(Modifier.weight(1f).fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                CompactServiceCard("Transport", Icons.Outlined.DirectionsBus, Modifier.fillMaxWidth().weight(1f)) { vm.beginValidation(ViaDomain.TRANSPORT) }
                CompactServiceCard("Parcare", Icons.Outlined.LocalParking, Modifier.fillMaxWidth().weight(1f)) { vm.beginValidation(ViaDomain.PARKING) }
                CompactServiceCard("Acces", Icons.Outlined.VerifiedUser, Modifier.fillMaxWidth().weight(1f)) { vm.beginValidation(ViaDomain.ACCESS) }
                CompactServiceCard("Beneficii", Icons.Outlined.Redeem, Modifier.fillMaxWidth().weight(1f)) { vm.beginValidation(ViaDomain.BENEFIT) }
            }
        } else {
            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                ServiceCard("Transport", Icons.Outlined.DirectionsBus, Modifier.weight(1f)) { vm.beginValidation(ViaDomain.TRANSPORT) }
                ServiceCard("Parcare", Icons.Outlined.LocalParking, Modifier.weight(1f)) { vm.beginValidation(ViaDomain.PARKING) }
                ServiceCard("Acces", Icons.Outlined.VerifiedUser, Modifier.weight(1f)) { vm.beginValidation(ViaDomain.ACCESS) }
                ServiceCard("Beneficii", Icons.Outlined.Redeem, Modifier.weight(1f)) { vm.beginValidation(ViaDomain.BENEFIT) }
            }
        }
    }
}

@Composable
private fun CompactServiceCard(text: String, icon: ImageVector, modifier: Modifier, onClick: () -> Unit) {
    ViaSurface(modifier) {
        Row(Modifier.fillMaxSize().clickable(onClick = onClick).padding(horizontal = 20.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
            Surface(color = Color(0xFFF1F1F3), shape = RoundedCornerShape(14.dp)) { Icon(icon, null, modifier = Modifier.padding(10.dp).size(22.dp)) }
            Text(text, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
private fun ServiceCard(text: String, icon: ImageVector, modifier: Modifier, onClick: () -> Unit) {
    ViaSurface(modifier.fillMaxHeight().clickable(onClick = onClick)) {
        Column(Modifier.fillMaxSize().padding(28.dp)) {
            Surface(color = Color(0xFFF1F1F3), shape = RoundedCornerShape(18.dp)) { Icon(icon, null, modifier = Modifier.padding(13.dp).size(26.dp)) }
            Spacer(Modifier.weight(1f)); Text(text, fontSize = 25.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun SmileScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    val compact = isCompact()
    Column {
        ScreenTitle("Zâmbet") { vm.navigate(TerminalViewModel.Screen.PAY) }
        if (compact) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(Modifier.weight(1f).fillMaxWidth().clip(RoundedCornerShape(24.dp)).background(Color(0xFF15161A))) {
                    SmartCameraView(vm = vm, mode = CameraMode.SMILE, modifier = Modifier.fillMaxSize())
                    FaceGuide(Modifier.align(Alignment.Center))
                    LinearProgressIndicator(progress = { state.smileProgress.coerceIn(0f, 1f) }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(16.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                }
                ViaSurface(Modifier.fillMaxWidth()) {
                    Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(state.merchant, color = ViaColors.Muted, fontSize = 13.sp)
                            Text("${state.amountDisplay} lei", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                        }
                        Text(if (state.smileProgress > 0.5f) "Zâmbește." else "Privește camera.", fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        } else {
            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ViaSurface(Modifier.weight(.61f).fillMaxHeight()) {
                    val short = isShortLandscape()
                    val instrSize = if (short) 34 else 48
                    Column(Modifier.fillMaxSize().padding(if (short) 24.dp else 36.dp)) {
                        Text(state.merchant, color = ViaColors.Muted)
                        Text("${state.amountDisplay} lei", fontSize = if (short) 32.sp else 48.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.weight(1f))
                        Text(if (state.smileProgress > 0.5f) "Zâmbește." else "Privește camera.", fontSize = instrSize.sp, lineHeight = instrSize.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.weight(1f))
                    }
                }
                Box(Modifier.weight(1.39f).fillMaxHeight().clip(RoundedCornerShape(38.dp)).background(Color(0xFF15161A))) {
                    SmartCameraView(vm = vm, mode = CameraMode.SMILE, modifier = Modifier.fillMaxSize())
                    FaceGuide(Modifier.align(Alignment.Center))
                    LinearProgressIndicator(progress = { state.smileProgress.coerceIn(0f, 1f) }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(24.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                }
            }
        }
    }
}

@Composable
private fun PalmScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    var reference by remember { mutableStateOf<List<Float>?>(null) }
    var stable by remember { mutableIntStateOf(0) }
    val compact = isCompact()

    val palmCallback: (List<Float>) -> Unit = { d ->
        vm.onPalmVerify(d)
        val r = reference
        if (r == null) { reference = d; stable = 1; vm.onPalmProgress(.25f) }
        else {
            val sim = com.via.core.vision.PalmDescriptor.cosine(r, d)
            stable = if (sim > .88f) stable + 1 else (stable - 1).coerceAtLeast(0)
            vm.onPalmProgress((stable / 5f).coerceAtMost(1f), sim)
            if (stable >= 5) vm.confirmPayment(ConfirmationMethod.PALM)
        }
    }

    Column {
        ScreenTitle("Palmă") { vm.navigate(TerminalViewModel.Screen.PAY) }
        if (compact) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(Modifier.weight(1f).fillMaxWidth().clip(RoundedCornerShape(24.dp)).background(Color(0xFF15161A))) {
                    PalmCameraView(modifier = Modifier.fillMaxSize(), onDescriptor = palmCallback, onError = { vm.showResult("Palmă indisponibilă", null, false) })
                    HandGuide(Modifier.align(Alignment.Center))
                    LinearProgressIndicator(progress = { state.palmProgress }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(16.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                }
                ViaSurface(Modifier.fillMaxWidth()) {
                    Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(state.merchant, color = ViaColors.Muted, fontSize = 13.sp)
                            Text("${state.amountDisplay} lei", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                        }
                        Text(if (stable > 1) "Ține palma." else "Arată palma.", fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        } else {
            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ViaSurface(Modifier.weight(.61f).fillMaxHeight()) {
                    val short = isShortLandscape()
                    val instrSize = if (short) 34 else 48
                    Column(Modifier.fillMaxSize().padding(if (short) 24.dp else 36.dp)) {
                        Text(state.merchant, color = ViaColors.Muted)
                        Text("${state.amountDisplay} lei", fontSize = if (short) 32.sp else 48.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.weight(1f))
                        Text(if (stable > 1) "Ține palma." else "Arată palma.", fontSize = instrSize.sp, lineHeight = instrSize.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.weight(1f))
                    }
                }
                Box(Modifier.weight(1.39f).fillMaxHeight().clip(RoundedCornerShape(38.dp)).background(Color(0xFF15161A))) {
                    PalmCameraView(modifier = Modifier.fillMaxSize(), onDescriptor = palmCallback, onError = { vm.showResult("Palmă indisponibilă", null, false) })
                    HandGuide(Modifier.align(Alignment.Center))
                    LinearProgressIndicator(progress = { state.palmProgress }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(24.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                }
            }
        }
    }
}

@Composable
private fun PhoneScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) { OfflineExchangeScreen(vm, state) }

@Composable
private fun TapScreen(vm: TerminalViewModel, domain: ViaDomain) {
    val state by vm.ui.collectAsStateWithLifecycle()
    OfflineExchangeScreen(vm, state)
}

@Composable
private fun OfflineExchangeScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    val owner = androidx.lifecycle.compose.LocalLifecycleOwner.current
    var now by remember { mutableStateOf(System.currentTimeMillis()) }
    LaunchedEffect(state.currentSession?.id) { while (true) { kotlinx.coroutines.delay(1000); now = System.currentTimeMillis() } }
    val expired = (state.currentSession?.expiresAtEpochMs ?: 0) <= now
    Column(Modifier.fillMaxSize()) {
        ScreenTitle(if (state.currentSession?.domain == ViaDomain.PAYMENT) "Confirmare QR · demo" else "Validare QR · demo") { vm.navigate(TerminalViewModel.Screen.HOME) }
        Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(12.dp)) {
            when {
                expired -> { Text("Cod expirat"); Button(onClick = vm::renewQrSession) { Text("Generează alt cod") } }
                else -> {
                    state.qrRequest?.let { QrImage(it, Modifier.size(290.dp)) }
                    Text("Scanează cu VIA Mobile")
                    Text("Confirmarea apare automat", color = ViaColors.Muted)
                    Text("${((state.currentSession?.expiresAtEpochMs ?: now) - now) / 1000}s", color = ViaColors.Muted)
                    if (state.qrConnecting) Text("Se pornește Bluetooth…", color = ViaColors.Muted)
                    state.qrError?.let { Text(it, color = MaterialTheme.colorScheme.error)
                        TextButton(onClick = vm::startLocalReceiver) { Text("Reîncearcă Bluetooth") }
                    }
                    Text("NFC indisponibil în această versiune", color = ViaColors.Muted, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
private fun DownloadScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    val compact = isCompact()
    Column {
        ScreenTitle("VIA pentru Android") { vm.navigate(TerminalViewModel.Screen.HOME) }
        if (compact) {
            Column(Modifier.weight(1f).fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                Icon(Icons.Outlined.PhoneAndroid, null, Modifier.size(80.dp))
                Spacer(Modifier.height(20.dp))
                Text("Instalează APK-ul.", fontSize = 32.sp, fontWeight = FontWeight.Bold)
                Text("VIA Mobile · local", color = ViaColors.Muted)
            }
        } else {
            val short = isShortLandscape()
            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ViaSurface(Modifier.weight(1f).fillMaxHeight()) {
                    Column(Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                        Icon(Icons.Outlined.PhoneAndroid, null, Modifier.size(80.dp))
                        Spacer(Modifier.height(if (short) 12.dp else 20.dp))
                        Text("Instalează APK-ul.", fontSize = if (short) 32.sp else 48.sp, fontWeight = FontWeight.Bold)
                        Text("VIA Mobile · local", color = ViaColors.Muted)
                    }
                }
                Box(Modifier.weight(1f).fillMaxHeight().clip(RoundedCornerShape(if (short) 24.dp else 38.dp)).background(ViaColors.Ink).padding(if (short) 28.dp else 48.dp), contentAlignment = Alignment.CenterStart) {
                    Column {
                        Text("VIA\npe telefon.", color = Color.White, fontSize = if (short) 34.sp else 50.sp, lineHeight = if (short) 34.sp else 48.sp, fontWeight = FontWeight.Bold)
                        Text("Plată. Transport. Parcare. Acces.", color = Color.White.copy(.5f), modifier = Modifier.padding(top = if (short) 10.dp else 16.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun EnrollScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    val compact = isCompact()
    if (state.enteringProfileName) {
        ProfileNameEntry(state.enrollName, vm::setEnrollName, vm::beginNamedEnrollment) { vm.navigate(TerminalViewModel.Screen.HOME) }
        return
    }
    val step = state.setupStep
    val instruction = when (step) {
        TerminalViewModel.SetupStep.FACE -> "Privește camera."
        TerminalViewModel.SetupStep.SMILE -> "Zâmbește."
        TerminalViewModel.SetupStep.PALM -> "Arată palma."
        TerminalViewModel.SetupStep.DONE -> "Gata."
    }
    Column {
        ScreenTitle("Persoană nouă") { vm.navigate(TerminalViewModel.Screen.HOME) }
        if (compact) {
            Box(
                Modifier.weight(1f).fillMaxWidth()
                    .padding(horizontal = 8.dp)
                    .clip(RoundedCornerShape(28.dp))
                    .background(Color(0xFF15161A))
            ) {
                when (step) {
                    TerminalViewModel.SetupStep.FACE, TerminalViewModel.SetupStep.SMILE ->
                        androidx.compose.runtime.key(step) { SmartCameraView(vm = vm, mode = CameraMode.SETUP, modifier = Modifier.fillMaxSize()) }
                    TerminalViewModel.SetupStep.PALM ->
                        PalmCameraView(modifier = Modifier.fillMaxSize(), onDescriptor = { d -> vm.onSetupPalmDescriptor(d) }, onError = {})
                    TerminalViewModel.SetupStep.DONE ->
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            Icon(Icons.Outlined.CheckCircle, null, tint = ViaColors.Green, modifier = Modifier.size(80.dp))
                        }
                }
                when (step) {
                    TerminalViewModel.SetupStep.FACE, TerminalViewModel.SetupStep.SMILE -> FaceGuide(Modifier.align(Alignment.Center))
                    TerminalViewModel.SetupStep.PALM -> HandGuide(Modifier.align(Alignment.Center))
                    else -> {}
                }
                if (step == TerminalViewModel.SetupStep.SMILE) {
                    LinearProgressIndicator(progress = { state.smileProgress.coerceIn(0f, 1f) }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(16.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                }
                if (step == TerminalViewModel.SetupStep.PALM) {
                    LinearProgressIndicator(progress = { state.palmProgress }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(16.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                }
            }
            Column(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                AnimatedContent(targetState = instruction, transitionSpec = { fadeIn(tween(200)).togetherWith(fadeOut(tween(150))) }, label = "setup-instr") { text ->
                    Text(text, fontSize = 28.sp, fontWeight = FontWeight.Bold, letterSpacing = (-1).sp)
                }
                Spacer(Modifier.height(12.dp))
                SetupStepDots(step)
            }
        } else {
            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ViaSurface(Modifier.weight(.55f).fillMaxHeight()) {
                    val short = isShortLandscape()
                    Column(Modifier.fillMaxSize().padding(if (short) 24.dp else 36.dp), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
                        AnimatedContent(targetState = instruction, transitionSpec = { fadeIn(tween(200)).togetherWith(fadeOut(tween(150))) }, label = "setup-instr-l") { text ->
                            Text(text, fontSize = if (short) 34.sp else 48.sp, lineHeight = if (short) 36.sp else 50.sp, fontWeight = FontWeight.Bold, letterSpacing = (-2).sp, textAlign = TextAlign.Center)
                        }
                        Spacer(Modifier.height(24.dp))
                        SetupStepDots(step)
                    }
                }
                Box(
                    Modifier.weight(1.45f).fillMaxHeight()
                        .clip(RoundedCornerShape(38.dp))
                        .background(Color(0xFF15161A))
                ) {
                    when (step) {
                        TerminalViewModel.SetupStep.FACE, TerminalViewModel.SetupStep.SMILE ->
                            androidx.compose.runtime.key(step) { SmartCameraView(vm = vm, mode = CameraMode.SETUP, modifier = Modifier.fillMaxSize()) }
                        TerminalViewModel.SetupStep.PALM ->
                            PalmCameraView(modifier = Modifier.fillMaxSize(), onDescriptor = { d -> vm.onSetupPalmDescriptor(d) }, onError = {})
                        TerminalViewModel.SetupStep.DONE ->
                            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                Icon(Icons.Outlined.CheckCircle, null, tint = ViaColors.Green, modifier = Modifier.size(100.dp))
                            }
                    }
                    when (step) {
                        TerminalViewModel.SetupStep.FACE, TerminalViewModel.SetupStep.SMILE -> FaceGuide(Modifier.align(Alignment.Center))
                        TerminalViewModel.SetupStep.PALM -> HandGuide(Modifier.align(Alignment.Center))
                        else -> {}
                    }
                    if (step == TerminalViewModel.SetupStep.SMILE) {
                        LinearProgressIndicator(progress = { state.smileProgress.coerceIn(0f, 1f) }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(24.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                    }
                    if (step == TerminalViewModel.SetupStep.PALM) {
                        LinearProgressIndicator(progress = { state.palmProgress }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(24.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                    }
                }
            }
        }
    }
}

@Composable
private fun SetupStepDots(step: TerminalViewModel.SetupStep) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        repeat(3) { i ->
            Box(Modifier.size(8.dp).clip(CircleShape).background(if (step.ordinal >= i) ViaColors.Ink else Color(0xFFE0E0E0)))
        }
    }
}

@Composable
private fun PalmEnrollScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    val compact = isCompact()
    Column {
        ScreenTitle("Înregistrare palmă") { vm.navigate(TerminalViewModel.Screen.HOME) }
        if (compact) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(Modifier.weight(1f).fillMaxWidth().clip(RoundedCornerShape(24.dp)).background(Color(0xFF15161A))) {
                    PalmCameraView(modifier = Modifier.fillMaxSize(), onDescriptor = { d -> vm.onPalmEnrollDescriptor(d) }, onError = {})
                    HandGuide(Modifier.align(Alignment.Center))
                    LinearProgressIndicator(progress = { state.palmProgress }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(16.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                }
                ViaSurface(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Ține palma nemișcată.", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                        Text("Se scanează…", color = ViaColors.Muted, fontSize = 14.sp)
                    }
                }
            }
        } else {
            Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ViaSurface(Modifier.weight(.61f).fillMaxHeight()) {
                    val short = isShortLandscape()
                    val instrSize = if (short) 34 else 48
                    Column(Modifier.fillMaxSize().padding(if (short) 24.dp else 36.dp), verticalArrangement = Arrangement.Center) {
                        Text("Ține palma\nnemișcată.", fontSize = instrSize.sp, lineHeight = instrSize.sp, fontWeight = FontWeight.Bold)
                        Spacer(Modifier.height(16.dp))
                        Text("Se scanează palma ta.", color = ViaColors.Muted)
                        Spacer(Modifier.height(24.dp))
                        LinearProgressIndicator(progress = { state.palmProgress }, modifier = Modifier.fillMaxWidth(), color = ViaColors.Blue)
                    }
                }
                Box(Modifier.weight(1.39f).fillMaxHeight().clip(RoundedCornerShape(38.dp)).background(Color(0xFF15161A))) {
                    PalmCameraView(modifier = Modifier.fillMaxSize(), onDescriptor = { d -> vm.onPalmEnrollDescriptor(d) }, onError = {})
                    HandGuide(Modifier.align(Alignment.Center))
                    LinearProgressIndicator(progress = { state.palmProgress }, modifier = Modifier.align(Alignment.BottomCenter).fillMaxWidth().padding(24.dp), color = Color.White, trackColor = Color.White.copy(.15f))
                }
            }
        }
    }
}

// --- Presentation & Engineering (hidden) ---

@Composable
private fun PresentationScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        ScreenTitle("Presentation Mode") { vm.navigate(TerminalViewModel.Screen.HOME) }
        Row(Modifier.weight(1f), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Plată", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                var merchant by remember { mutableStateOf(state.merchant) }
                var amount by remember { mutableStateOf(state.amountMinor.toString()) }
                OutlinedTextField(merchant, { merchant = it }, label = { Text("Merchant") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(amount, { amount = it }, label = { Text("Sumă (bani)") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                Button(onClick = { vm.triggerPayment(merchant, amount.toLongOrNull() ?: 2490) }, modifier = Modifier.fillMaxWidth()) { Text("Trigger Payment") }
                HorizontalDivider(Modifier.padding(vertical = 8.dp))
                Text("Validare", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = { vm.triggerValidation(ViaDomain.TRANSPORT) }) { Text("Transport") }
                    Button(onClick = { vm.triggerValidation(ViaDomain.PARKING) }) { Text("Parcare") }
                }
            }
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Demo", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                Button(onClick = vm::fallbackSuccess, modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = ViaColors.Green)) { Text("Fallback Success") }
                Button(onClick = vm::fallbackDeny, modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = ViaColors.Red)) { Text("Fallback Deny") }
                Button(onClick = vm::resetDemo, modifier = Modifier.fillMaxWidth()) { Text("Reset Demo") }
                HorizontalDivider(Modifier.padding(vertical = 8.dp))
                Button(onClick = { vm.startEnrollment() }, modifier = Modifier.fillMaxWidth()) { Text("Enrollment nou") }
                TextButton(onClick = { vm.navigate(TerminalViewModel.Screen.ENGINEERING) }) { Text("Engineering Mode →") }
            }
        }
    }
}

@Composable
private fun EngineeringScreen(vm: TerminalViewModel, state: TerminalViewModel.UiState) {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        ScreenTitle("Engineering") { vm.navigate(TerminalViewModel.Screen.PRESENTATION) }
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            EngRow("Faces", "${state.engFaceCount}")
            EngRow("Active", state.activeFaceName ?: "none")
            EngRow("Recognition", "%.3f".format(state.engRecognitionScore))
            EngRow("Zoom", "%.2fx".format(state.engZoom))
            EngRow("Group mode", if (state.groupMode) "yes" else "no")
            EngRow("Smile raw", "%.3f".format(state.engSmileRaw))
            EngRow("Smile progress", "%.2f".format(state.smileProgress))
            EngRow("Palm similarity", "%.4f".format(state.palmSimilarity))
            EngRow("Backend", if (state.backendAvailable) "connected" else "disconnected")
            EngRow("BLE", vm.ble.link.collectAsStateWithLifecycle().value.name)
            EngRow("Session", state.currentSession?.id ?: "none")
            EngRow("App version", BuildConfig.VERSION_NAME)
        }
    }
}

// --- Common Components ---

@Composable
private fun ScreenTitle(text: String, onBack: () -> Unit) {
    Row(Modifier.height(48.dp), verticalAlignment = Alignment.CenterVertically) {
        IconButton(onClick = onBack) { Icon(Icons.Outlined.ArrowBackIosNew, null) }
        Text(text, fontSize = 22.sp, fontWeight = FontWeight.Bold)
    }
    Spacer(Modifier.height(12.dp))
}

@Composable
private fun ResultOverlay(title: String, subtitle: String?, success: Boolean) {
    val compact = isCompact()
    val animProgress = remember { Animatable(0f) }

    LaunchedEffect(Unit) {
        animProgress.animateTo(1f, spring(dampingRatio = 0.65f, stiffness = 600f))
    }

    val scaleVal = 0.6f + 0.4f * animProgress.value
    val alphaVal = animProgress.value.coerceIn(0f, 1f)

    Box(
        Modifier.fillMaxSize().background(Color.White.copy(alphaVal)).graphicsLayer { scaleX = scaleVal; scaleY = scaleVal; alpha = alphaVal },
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Box(Modifier.size(if (compact) 72.dp else 104.dp).clip(CircleShape).background(if (success) ViaColors.Green else ViaColors.Red), contentAlignment = Alignment.Center) {
                Icon(if (success) Icons.Outlined.Check else Icons.Outlined.Close, null, tint = Color.White, modifier = Modifier.size(if (compact) 36.dp else 50.dp))
            }
            Spacer(Modifier.height(20.dp))
            Text(title, fontSize = if (compact) 36.sp else 56.sp, fontWeight = FontWeight.Bold, letterSpacing = (-2).sp, textAlign = TextAlign.Center)
            subtitle?.let { Text(it, color = ViaColors.Muted, fontSize = if (compact) 14.sp else 18.sp) }
        }
    }
}

@Composable
private fun PulseIcon(icon: ImageVector) {
    val compact = isCompact()
    val outer = if (compact) 120.dp else 182.dp
    val inner = if (compact) 96.dp else 150.dp
    val iconSize = if (compact) 48.dp else 74.dp
    Box(contentAlignment = Alignment.Center) {
        Box(Modifier.size(outer).clip(RoundedCornerShape(if (compact) 36.dp else 55.dp)).background(ViaColors.Blue.copy(.08f)))
        Box(Modifier.size(inner).clip(RoundedCornerShape(if (compact) 30.dp else 46.dp)).background(ViaColors.Ink), contentAlignment = Alignment.Center) {
            Icon(icon, null, tint = Color.White, modifier = Modifier.size(iconSize))
        }
    }
}

@Composable
private fun FaceGuide(modifier: Modifier) {
    val compact = isCompact()
    val guideSize = if (compact) 200.dp else 320.dp
    Canvas(modifier.size(guideSize)) {
        drawOval(Color.White.copy(.50f), style = Stroke(1.5f))
        val len = 36f
        drawLine(Color.White, Offset(0f, 0f), Offset(len, 0f), 2.5f, StrokeCap.Round)
        drawLine(Color.White, Offset(0f, 0f), Offset(0f, len), 2.5f, StrokeCap.Round)
        drawLine(Color.White, Offset(size.width, 0f), Offset(size.width - len, 0f), 2.5f, StrokeCap.Round)
        drawLine(Color.White, Offset(size.width, 0f), Offset(size.width, len), 2.5f, StrokeCap.Round)
    }
}

@Composable
private fun HandGuide(modifier: Modifier) {
    Canvas(modifier.size(360.dp)) {
        drawRoundRect(Color.White.copy(.60f), cornerRadius = CornerRadius(90f, 90f), style = Stroke(2f))
    }
}

@Composable
private fun QrImage(content: String, modifier: Modifier) {
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
private fun EngRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Text(label, color = ViaColors.Muted, modifier = Modifier.weight(1f), fontSize = 14.sp)
        Text(value, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
    }
}
