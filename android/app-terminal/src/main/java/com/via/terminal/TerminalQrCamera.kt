package com.via.terminal

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import com.via.core.vision.PalmLandmarkerEngine
import com.via.core.vision.QrAnalyzer
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

@Composable
fun TerminalQrCamera(owner: LifecycleOwner, modifier: Modifier, onPayload: (String) -> Unit) {
    val callback = rememberUpdatedState(onPayload)
    CameraHost(owner, modifier, false) { context, deliver -> QrAnalyzer { payload -> deliver { callback.value(payload) } } }
}

@Composable
fun UnusedPalmCamera(owner: LifecycleOwner, modifier: Modifier, onDescriptor: (List<Float>) -> Unit, onError: (Throwable) -> Unit) {
    val descriptor = rememberUpdatedState(onDescriptor)
    val error = rememberUpdatedState(onError)
    CameraHost(owner, modifier, true) { context, deliver -> PalmLandmarkerEngine(context,
        onDescriptor = { d, _, _ -> deliver { descriptor.value(d) } }, onError = { e -> deliver { error.value(e) } }) }
}

@Composable
private fun CameraHost(owner: LifecycleOwner, modifier: Modifier, rgba: Boolean, factory: (android.content.Context, (() -> Unit) -> Unit) -> ImageAnalysis.Analyzer) {
    val context = LocalContext.current
    var allowed by remember { mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) }
    val permission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { allowed = it }
    var error by remember { mutableStateOf(false) }
    val executor = remember { Executors.newSingleThreadExecutor() }
    val disposed = remember { AtomicBoolean(false) }
    var cleanup by remember { mutableStateOf<(() -> Unit)?>(null) }
    DisposableEffect(Unit) { onDispose { disposed.set(true); cleanup?.invoke(); executor.shutdown() } }
    Box(modifier.background(Color(0xFF172E32)), contentAlignment = Alignment.Center) {
        if (!allowed || error) Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            Text(if (error) "Camera nu este disponibilă. Revino și încearcă din nou." else "Permite accesul la cameră pentru acest pas.", color = Color.White)
            if (!allowed) Button(onClick = { permission.launch(Manifest.permission.CAMERA) }) { Text("Permite camera") }
        } else AndroidView(modifier = Modifier.fillMaxSize(), factory = { ctx ->
            val view = PreviewView(ctx).apply { scaleType = PreviewView.ScaleType.FILL_CENTER }
            val main = ContextCompat.getMainExecutor(ctx)
            val future = ProcessCameraProvider.getInstance(ctx)
            future.addListener({
                if (!disposed.get()) try {
                    val provider = future.get()
                    val preview = Preview.Builder().build().also { it.surfaceProvider = view.surfaceProvider }
                    val builder = ImageAnalysis.Builder().setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    if (rgba) builder.setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                    val analysis = builder.build()
                    val analyzer = factory(ctx) { action -> main.execute { if (!disposed.get()) action() } }
                    cleanup = { analysis.clearAnalyzer(); provider.unbind(preview, analysis); executor.execute { (analyzer as? AutoCloseable)?.close() } }
                    analysis.setAnalyzer(executor, analyzer)
                    provider.bindToLifecycle(owner, CameraSelector.DEFAULT_FRONT_CAMERA, preview, analysis)
                } catch (e: Exception) { error = true }
            }, main)
            view
        })
    }
}
