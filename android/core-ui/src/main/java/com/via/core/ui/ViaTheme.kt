package com.via.core.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

object ViaColors {
    val Background = Color(0xFFF5F5F7)
    val Surface = Color.White
    val Ink = Color(0xFF111111)
    val Muted = Color(0xFF747477)
    val Blue = Color(0xFF1769E0)
    val Green = Color(0xFF2FBF63)
    val Red = Color(0xFFE84C4C)
    val Hairline = Color(0x14000000)
}

private val scheme = lightColorScheme(
    primary = ViaColors.Blue,
    background = ViaColors.Background,
    surface = ViaColors.Surface,
    onBackground = ViaColors.Ink,
    onSurface = ViaColors.Ink,
    error = ViaColors.Red,
)

@Composable
fun ViaTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = scheme,
        typography = Typography(
            displayLarge = MaterialTheme.typography.displayLarge.copy(fontWeight = FontWeight.Bold, letterSpacing = (-3).sp),
            headlineLarge = MaterialTheme.typography.headlineLarge.copy(fontWeight = FontWeight.Bold),
            titleLarge = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.SemiBold),
            bodyLarge = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Normal),
        ),
        content = content,
    )
}

@Composable
fun ViaLogo(modifier: Modifier = Modifier, markOnly: Boolean = false) {
    Canvas(modifier = modifier) {
        if (markOnly) drawViaMark()
        else drawViaWordmark()
    }
}

private fun DrawScope.drawViaMark() {
    val w = size.width
    val h = size.height
    val v = Path().apply {
        moveTo(w * 0.08f, h * 0.18f)
        lineTo(w * 0.28f, h * 0.18f)
        lineTo(w * 0.50f, h * 0.82f)
        lineTo(w * 0.72f, h * 0.18f)
        lineTo(w * 0.92f, h * 0.18f)
        lineTo(w * 0.60f, h * 0.94f)
        lineTo(w * 0.40f, h * 0.94f)
        close()
    }
    drawPath(v, ViaColors.Ink)
    val tri = Path().apply {
        moveTo(w * 0.35f, h * 0.02f)
        lineTo(w * 0.65f, h * 0.02f)
        lineTo(w * 0.50f, h * 0.30f)
        close()
    }
    drawPath(tri, ViaColors.Blue)
}

private fun DrawScope.drawViaWordmark() {
    val gap = size.width * .03f
    val third = (size.width - gap * 2) / 3f
    // V mark in first third
    val v = Path().apply {
        moveTo(third * .06f, size.height * .18f)
        lineTo(third * .28f, size.height * .18f)
        lineTo(third * .50f, size.height * .80f)
        lineTo(third * .72f, size.height * .18f)
        lineTo(third * .94f, size.height * .18f)
        lineTo(third * .61f, size.height * .94f)
        lineTo(third * .39f, size.height * .94f)
        close()
    }
    drawPath(v, ViaColors.Ink)
    val tri = Path().apply {
        moveTo(third * .35f, size.height * .01f)
        lineTo(third * .65f, size.height * .01f)
        lineTo(third * .50f, size.height * .29f)
        close()
    }
    drawPath(tri, ViaColors.Blue)

    // I
    val ix = third + gap
    drawRect(ViaColors.Ink, topLeft = Offset(ix + third * .35f, size.height * .17f), size = Size(third * .30f, size.height * .77f))
    drawRect(ViaColors.Blue, topLeft = Offset(ix + third * .35f, size.height * .17f), size = Size(third * .30f, size.height * .20f))

    // A
    val ax = (third + gap) * 2
    val a = Path().apply {
        moveTo(ax + third * .08f, size.height * .94f)
        lineTo(ax + third * .40f, size.height * .17f)
        lineTo(ax + third * .65f, size.height * .17f)
        lineTo(ax + third * .94f, size.height * .94f)
        lineTo(ax + third * .72f, size.height * .94f)
        lineTo(ax + third * .53f, size.height * .43f)
        lineTo(ax + third * .34f, size.height * .94f)
        close()
    }
    drawPath(a, ViaColors.Ink)
    drawRect(ViaColors.Blue, topLeft = Offset(ax + third * .31f, size.height * .62f), size = Size(third * .42f, size.height * .16f))
}

@Composable
fun ViaSurface(
    modifier: Modifier = Modifier,
    radius: Dp = 32.dp,
    content: @Composable BoxScope.() -> Unit,
) {
    Surface(modifier = modifier, shape = RoundedCornerShape(radius), tonalElevation = 0.dp, shadowElevation = 5.dp, content = { Box(content = content) })
}

enum class RailDestination(val icon: ImageVector) {
    HOME(Icons.Outlined.Home),
    PAY(Icons.Outlined.CreditCard),
    VALIDATE(Icons.Outlined.VerifiedUser),
    DOWNLOAD(Icons.Outlined.Download),
}

@Composable
fun ViaSidebar(
    current: RailDestination,
    onSelect: (RailDestination) -> Unit,
    modifier: Modifier = Modifier,
    onLogoTap: () -> Unit = {},
) {
    Column(
        modifier = modifier
            .width(92.dp)
            .fillMaxHeight()
            .background(Color.White.copy(alpha = .80f))
            .padding(vertical = 20.dp, horizontal = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        ViaLogo(Modifier.width(58.dp).height(38.dp).clickable(onClick = onLogoTap))
        Spacer(Modifier.height(26.dp))
        RailButton(RailDestination.HOME, current, onSelect)
        Spacer(Modifier.height(10.dp))
        RailButton(RailDestination.PAY, current, onSelect)
        Spacer(Modifier.height(10.dp))
        RailButton(RailDestination.VALIDATE, current, onSelect)
        Spacer(Modifier.weight(1f))
        RailButton(RailDestination.DOWNLOAD, current, onSelect)
    }
}

@Composable
private fun RailButton(item: RailDestination, current: RailDestination, onSelect: (RailDestination) -> Unit) {
    val selected = current == item
    FilledIconButton(
        onClick = { onSelect(item) },
        modifier = Modifier.size(58.dp),
        shape = RoundedCornerShape(18.dp),
        colors = IconButtonDefaults.filledIconButtonColors(
            containerColor = if (selected) ViaColors.Ink else Color.Transparent,
            contentColor = if (selected) Color.White else Color(0xFF86868B),
        ),
    ) { Icon(item.icon, contentDescription = item.name) }
}
