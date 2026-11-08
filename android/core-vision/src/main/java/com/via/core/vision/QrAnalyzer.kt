package com.via.core.vision

import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import java.util.concurrent.atomic.AtomicBoolean

class QrAnalyzer(private val onPayload: (String) -> Unit) : ImageAnalysis.Analyzer {
    private val busy = AtomicBoolean(false)
    private val scanner = BarcodeScanning.getClient(
        BarcodeScannerOptions.Builder().setBarcodeFormats(Barcode.FORMAT_QR_CODE).build(),
    )
    private var last: String? = null

    @androidx.annotation.OptIn(ExperimentalGetImage::class)
    override fun analyze(imageProxy: ImageProxy) {
        if (!busy.compareAndSet(false, true)) { imageProxy.close(); return }
        val media = imageProxy.image
        if (media == null) { busy.set(false); imageProxy.close(); return }
        scanner.process(InputImage.fromMediaImage(media, imageProxy.imageInfo.rotationDegrees))
            .addOnSuccessListener { codes ->
                codes.firstNotNullOfOrNull { it.rawValue }?.let { value ->
                    if (value != last) { last = value; onPayload(value) }
                }
            }
            .addOnCompleteListener { busy.set(false); imageProxy.close() }
    }

    fun reset() { last = null }
    fun close() = scanner.close()
}
