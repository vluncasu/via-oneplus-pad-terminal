package com.via.terminal

import android.content.Context
import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.background
import androidx.compose.ui.graphics.Color
import androidx.compose.material3.*
import androidx.compose.ui.unit.dp
import androidx.compose.ui.Alignment
import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.FocusMeteringAction
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.core.SurfaceOrientedMeteringPointFactory
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.via.core.vision.FaceDescriptor
import com.via.core.vision.FramingState
import com.via.core.vision.PalmLandmarkerEngine
import com.via.core.vision.SmartFramingEngine
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

enum class CameraMode { SMART, SMILE, ENROLL, SETUP }

@Composable
private fun SmartCameraContent(
    vm: TerminalViewModel,
    mode: CameraMode,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val mainExecutor = remember { ContextCompat.getMainExecutor(context) }
    val lifecycleOwner = LocalLifecycleOwner.current
    val executor = remember { Executors.newSingleThreadExecutor() }
    val disposed = remember { java.util.concurrent.atomic.AtomicBoolean(false) }
    val cleanup = remember { mutableStateOf<(() -> Unit)?>(null) }
    val cameraError = remember { mutableStateOf(false) }
    if (cameraError.value) {
        Box(modifier.background(Color(0xFF152A38)), contentAlignment = Alignment.Center) { Text("Camera nu este disponibilă. Revino și încearcă din nou.", color = Color.White) }
        return
    }
    val zoomExecutor = remember { mutableStateOf<java.util.concurrent.ScheduledExecutorService?>(null) }

    AndroidView(
        modifier = modifier,
        factory = { ctx ->
            val previewView = PreviewView(ctx).apply {
                scaleType = PreviewView.ScaleType.FILL_CENTER
            }
            val providerFuture = ProcessCameraProvider.getInstance(ctx)
            providerFuture.addListener({
                if (disposed.get()) return@addListener
                try {
                val provider = providerFuture.get()
                val preview = Preview.Builder().build().also {
                    it.surfaceProvider = previewView.surfaceProvider
                }

                val descriptorCallback: ((List<Float>) -> Unit)? = when (mode) {
                    CameraMode.ENROLL -> { d -> vm.onEnrollDescriptor(d) }
                    CameraMode.SETUP -> { d -> vm.onSetupDescriptor(d) }
                    CameraMode.SMART -> { d -> vm.onFaceRecognized(d) }
                    CameraMode.SMILE -> { d -> vm.onFaceRecognized(d) }
                }

                val engine = SmartFramingEngine(
                    onFramingUpdate = { state -> mainExecutor.execute { if (!disposed.get()) {
                        vm.onFramingUpdate(state)
                        if (mode == CameraMode.SMILE || mode == CameraMode.SETUP) {
                            state.activeFace?.let { face ->
                                vm.onSmileProgress(
                                    progress = if (face.smileProbability > 0.7f) 1f
                                    else (face.smileProbability / 0.7f).coerceIn(0f, 0.95f),
                                    rawSmile = face.smileProbability,
                                )
                            }
                        }
                    } } },
                    onSmileConfirmed = if (mode == CameraMode.SMILE || mode == CameraMode.SETUP) {
                        { mainExecutor.execute { if (!disposed.get()) vm.onSmileConfirmed() } }
                    } else null,
                    onFaceDescriptor = { d -> mainExecutor.execute { if (!disposed.get()) descriptorCallback?.invoke(d) } },
                )

                if (mode == CameraMode.SMILE || mode == CameraMode.SETUP) {
                    engine.startSmileDetection()
                }

                val analysis = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .build()

                cleanup.value = { analysis.clearAnalyzer(); provider.unbind(preview, analysis); executor.execute { engine.close() } }
                analysis.setAnalyzer(executor, engine)

                provider.unbindAll()
                val camera = provider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_FRONT_CAMERA,
                    preview, analysis,
                )

                zoomExecutor.value = startZoomController(camera, vm)

                } catch (e: Exception) { cameraError.value = true }
            }, ContextCompat.getMainExecutor(ctx))
            previewView
        },
    )

    DisposableEffect(Unit) {
        onDispose {
            disposed.set(true)
            cleanup.value?.invoke()
            zoomExecutor.value?.shutdownNow()
            executor.shutdown()
        }
    }
}

private fun startZoomController(camera: Camera, vm: TerminalViewModel): java.util.concurrent.ScheduledExecutorService {
    val executor = Executors.newSingleThreadScheduledExecutor()
    var zoomVel = 0f
    var lastFocusMs = 0L
    val stiffness = 80f
    val damping = 18f

    executor.scheduleAtFixedRate({
        try {
            val state = vm.ui.value
            val currentZoom = camera.cameraInfo.zoomState.value?.zoomRatio ?: 1f
            val maxZoom = camera.cameraInfo.zoomState.value?.maxZoomRatio ?: 3f
            val target = state.targetZoom.coerceIn(1f, maxZoom)
            val dt = 0.033f

            val displacement = currentZoom - target
            val springForce = -stiffness * displacement
            val dampForce = -damping * zoomVel
            zoomVel += (springForce + dampForce) * dt
            val rawZoom = currentZoom + zoomVel * dt
            val newZoom = rawZoom.coerceIn(1f, maxZoom)
            if (newZoom != rawZoom) zoomVel = 0f

            if (kotlin.math.abs(newZoom - currentZoom) > 0.005f) {
                camera.cameraControl.setZoomRatio(newZoom)
            }

            val now = System.currentTimeMillis()
            if (state.faceCount > 0 && now - lastFocusMs > 2000) {
                lastFocusMs = now
                val factory = SurfaceOrientedMeteringPointFactory(1f, 1f)
                val point = factory.createPoint(0.5f, 0.4f)
                val action = FocusMeteringAction.Builder(point)
                    .setAutoCancelDuration(3, TimeUnit.SECONDS)
                    .build()
                camera.cameraControl.startFocusAndMetering(action)
            }
        } catch (_: Exception) {}
    }, 50, 33, TimeUnit.MILLISECONDS)
    return executor
}

@Composable
private fun PalmCameraContent(
    modifier: Modifier = Modifier,
    onDescriptor: (List<Float>) -> Unit,
    onError: (Throwable) -> Unit,
) {
    val latestDescriptor = rememberUpdatedState(onDescriptor)
    val latestError = rememberUpdatedState(onError)
    val context = LocalContext.current
    val mainExecutor = remember { ContextCompat.getMainExecutor(context) }
    val lifecycleOwner = LocalLifecycleOwner.current
    val executor = remember { Executors.newSingleThreadExecutor() }
    val disposed = remember { java.util.concurrent.atomic.AtomicBoolean(false) }
    val cleanup = remember { mutableStateOf<(() -> Unit)?>(null) }
    val cameraError = remember { mutableStateOf(false) }
    if (cameraError.value) {
        Box(modifier.background(Color(0xFF152A38)), contentAlignment = Alignment.Center) { Text("Camera nu este disponibilă. Revino și încearcă din nou.", color = Color.White) }
        return
    }

    AndroidView(
        modifier = modifier,
        factory = { ctx ->
            val previewView = PreviewView(ctx).apply {
                scaleType = PreviewView.ScaleType.FILL_CENTER
            }
            val providerFuture = ProcessCameraProvider.getInstance(ctx)
            providerFuture.addListener({
                if (disposed.get()) return@addListener
                try {
                val provider = providerFuture.get()
                val preview = Preview.Builder().build().also {
                    it.surfaceProvider = previewView.surfaceProvider
                }
                val analysis = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                    .build()

                val palmEngine = PalmLandmarkerEngine(
                    ctx,
                    onDescriptor = { descriptor, _, _ -> mainExecutor.execute { if (!disposed.get()) latestDescriptor.value(descriptor) } },
                    onError = { error -> mainExecutor.execute { if (!disposed.get()) latestError.value(error) } },
                )
                cleanup.value = { analysis.clearAnalyzer(); provider.unbind(preview, analysis); executor.execute { palmEngine.close() } }
                analysis.setAnalyzer(executor, palmEngine)

                provider.unbindAll()
                provider.bindToLifecycle(lifecycleOwner, CameraSelector.DEFAULT_FRONT_CAMERA, preview, analysis)
                } catch (e: Exception) { cameraError.value = true }
            }, ContextCompat.getMainExecutor(ctx))
            previewView
        },
    )

    DisposableEffect(Unit) {
        onDispose { disposed.set(true); cleanup.value?.invoke(); executor.shutdown() }
    }
}

@Composable
fun SmartCameraView(vm: TerminalViewModel, mode: CameraMode, modifier: Modifier = Modifier) {
    CameraPermissionGate(modifier) { SmartCameraContent(vm, mode, Modifier.fillMaxSize()) }
}

@Composable
fun PalmCameraView(modifier: Modifier = Modifier, onDescriptor: (List<Float>) -> Unit, onError: (Throwable) -> Unit) {
    CameraPermissionGate(modifier) { PalmCameraContent(Modifier.fillMaxSize(), onDescriptor, onError) }
}

@Composable
private fun CameraPermissionGate(modifier: Modifier, content: @Composable () -> Unit) {
    val context = LocalContext.current
    val mainExecutor = remember { ContextCompat.getMainExecutor(context) }
    val allowed = remember { mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) }
    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { allowed.value = it }
    Box(modifier.background(Color(0xFF152A38)), contentAlignment = Alignment.Center) {
        if (allowed.value) content() else Column(Modifier.padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text("Camera este necesară pentru acest pas.", color = Color.White)
            Spacer(Modifier.height(16.dp))
            Button(onClick = { launcher.launch(Manifest.permission.CAMERA) }) { Text("Permite accesul la cameră") }
            Text("Demo-ul ghidat funcționează și fără cameră.", color = Color.White)
        }
    }
}
