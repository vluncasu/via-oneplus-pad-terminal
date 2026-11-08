@file:Suppress("DEPRECATION")
package com.via.core.hardware

import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.*
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.os.ParcelUuid
import java.util.UUID
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeout
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/** QR selects a unique service. Signed confirmation is verified by the receiver before final ACK. */
@SuppressLint("MissingPermission")
class LocalConfirmationReceiver(private val context: Context) : AutoCloseable {
    private val main = Handler(Looper.getMainLooper())
    private var server: BluetoothGattServer? = null
    private var advertiser: BluetoothLeAdvertiser? = null
    private var advertising: AdvertiseCallback? = null
    private val attempts = ReceiverAttempts()
    private var available = false
    private var watching = false
    private var desired: Request? = null
    private data class Request(val id: String, val accept: (String) -> Boolean, val error: (String) -> Unit, val ready: () -> Unit)
    private val adapterChanges = object : android.content.BroadcastReceiver() {
        override fun onReceive(context: Context, intent: android.content.Intent) {
            if (intent.action != BluetoothAdapter.ACTION_STATE_CHANGED || desired == null) return
            when (intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR)) {
                BluetoothAdapter.STATE_ON -> {
                    val epoch = attempts.current
                    main.postDelayed({ if (desired != null && !available && attempts.isCurrent(epoch)) restart() }, 750)
                }
                BluetoothAdapter.STATE_TURNING_OFF, BluetoothAdapter.STATE_OFF -> {
                    stopResources()
                    desired?.error?.invoke("Activează Bluetooth pe tabletă")
                }
            }
        }
    }
    fun start(sessionId: String, accept: (String) -> Boolean, error: (String) -> Unit, ready: () -> Unit = {}) {
        desired = Request(sessionId, accept, error, ready)
        if (!watching) {
            try {
                androidx.core.content.ContextCompat.registerReceiver(context, adapterChanges, android.content.IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED), androidx.core.content.ContextCompat.RECEIVER_EXPORTED)
                watching = true
            } catch (e: Exception) { error("Permite Bluetooth / Dispozitive din apropiere"); return }
        }
        restart()
    }
    private fun restart() {
        val request = desired ?: return
        stopResources()
        val epoch = attempts.current
        fun fail(message: String) { main.post { if (attempts.isCurrent(epoch) && desired === request) request.error(message) } }
        try {
            val manager = context.getSystemService(BluetoothManager::class.java)
            val adapter = requireNotNull(manager.adapter)
            check(adapter.isEnabled) { "Activează Bluetooth pe tabletă" }
            val adv = requireNotNull(adapter.bluetoothLeAdvertiser) { "Tableta nu oferă Bluetooth LE advertising" }
            advertiser = adv
            val buffers = mutableMapOf<String, ConfirmationFrames>()
            val callback = object : BluetoothGattServerCallback() {
                override fun onServiceAdded(status: Int, service: BluetoothGattService) {
                    if (!attempts.isCurrent(epoch)) return
                    if (status != BluetoothGatt.GATT_SUCCESS) { fail("Serviciul Bluetooth nu a pornit. Reîncearcă."); return }
                    val cb = object : AdvertiseCallback() {
                        override fun onStartSuccess(settingsInEffect: AdvertiseSettings) {
                            main.post { if (attempts.isCurrent(epoch) && desired === request) { available = true; request.ready() } }
                        }
                        override fun onStartFailure(errorCode: Int) { fail("Bluetooth indisponibil ($errorCode). Reîncearcă.") }
                    }
                    advertising = cb
                    runCatching { adv.startAdvertising(AdvertiseSettings.Builder().setAdvertiseMode(AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY).setConnectable(true).setTimeout(180000).build(), AdvertiseData.Builder().addServiceUuid(ParcelUuid(service.uuid)).addManufacturerData(LocalConfirmationAddress.MANUFACTURER, LocalConfirmationAddress.tag(request.id)).setIncludeDeviceName(false).build(), cb) }
                        .onFailure { fail("Permite Bluetooth / Dispozitive din apropiere") }
                }
                override fun onConnectionStateChange(device: BluetoothDevice, status: Int, newState: Int) { if (newState == BluetoothProfile.STATE_DISCONNECTED) synchronized(buffers) { buffers.remove(device.address) } }
                override fun onCharacteristicWriteRequest(device: BluetoothDevice, requestId: Int, characteristic: BluetoothGattCharacteristic, preparedWrite: Boolean, responseNeeded: Boolean, offset: Int, value: ByteArray) {
                    val gattServer = server ?: return
                    fun answer(ok: Boolean) { if (responseNeeded) runCatching { gattServer.sendResponse(device,requestId,if (ok) BluetoothGatt.GATT_SUCCESS else BluetoothGatt.GATT_FAILURE,0,null) } }
                    if (!attempts.isCurrent(epoch) || preparedWrite || offset != 0 || characteristic.uuid != CHARACTERISTIC || value.isEmpty()) { answer(false); return }
                    val complete: String?
                    synchronized(buffers) {
                        if (buffers.size >= 8 && device.address !in buffers) { answer(false); return }
                        val frame = buffers.getOrPut(device.address) { ConfirmationFrames() }
                        try { complete = frame.append(value) }
                        catch (_: Exception) { buffers.remove(device.address); answer(false); return }
                        if (complete != null) buffers.remove(device.address)
                    }
                    if (complete == null) answer(true)
                    else main.post { answer(attempts.isCurrent(epoch) && runCatching { request.accept(complete) }.getOrDefault(false)) }
                }
            }
            server = requireNotNull(manager.openGattServer(context, callback)) { "Bluetooth pornește încă. Reîncearcă." }
            val service = BluetoothGattService(LocalConfirmationAddress.SERVICE, BluetoothGattService.SERVICE_TYPE_PRIMARY)
            service.addCharacteristic(BluetoothGattCharacteristic(CHARACTERISTIC, BluetoothGattCharacteristic.PROPERTY_WRITE, BluetoothGattCharacteristic.PERMISSION_WRITE))
            check(server!!.addService(service)) { "Serviciul Bluetooth nu a fost creat. Reîncearcă." }
            main.postDelayed({
                if (attempts.isCurrent(epoch) && desired === request && !available) {
                    stopResources()
                    request.error("Bluetooth nu a pornit complet. Apasă Reîncearcă Bluetooth.")
                }
            }, 8000)
        } catch (e: Exception) { fail(e.message ?: "Permite dispozitivele din apropiere și activează Bluetooth") }
    }
    private fun stopResources() {
        available = false
        attempts.invalidate()
        advertising?.let { cb -> runCatching { advertiser?.stopAdvertising(cb) } }
        advertising = null; advertiser = null
        runCatching { server?.close() }; server = null
    }
    override fun close() {
        desired = null
        stopResources()
        if (watching) { runCatching { context.unregisterReceiver(adapterChanges) }; watching = false }
    }
    companion object { val CHARACTERISTIC: UUID = UUID.fromString("f8911568-6f70-4f20-8c72-1c98bf1be781") }
}

/** Guards queued callbacks from attempts invalidated by Bluetooth OFF or a manual retry. */
internal class ReceiverAttempts {
    @Volatile var current = 0; private set
    @Synchronized fun invalidate() { current++ }
    fun isCurrent(token: Int) = token == current
}

@SuppressLint("MissingPermission")
class LocalConfirmationSender(private val context: Context) {
    suspend fun send(sessionId: String, payload: String) = withTimeout(25000) {
        suspendCancellableCoroutine<Unit> { continuation ->
            val adapter = context.getSystemService(BluetoothManager::class.java).adapter
            var gatt: BluetoothGatt? = null
            var scanner: BluetoothLeScanner? = null
            var scan: ScanCallback? = null
            val done = java.util.concurrent.atomic.AtomicBoolean(false)
            val lock = Any()
            fun cleanup() { runCatching { scan?.let { scanner?.stopScan(it) } }; runCatching { gatt?.disconnect() }; runCatching { gatt?.close() } }
            fun finish(error: String? = null) = synchronized(lock) {
                if (done.compareAndSet(false, true)) {
                    cleanup()
                    if (continuation.isActive) {
                        if (error == null) continuation.resume(Unit) else continuation.resumeWithException(IllegalStateException(error))
                    }
                }
            }
            continuation.invokeOnCancellation { synchronized(lock) { done.set(true); cleanup() } }
            try {
                check(adapter != null && adapter.isEnabled) { "Activează Bluetooth pe telefon" }
                val serviceId = LocalConfirmationAddress.SERVICE
                val chunks = (payload + "\n").chunked(20).map { it.toByteArray(Charsets.US_ASCII) }
                var index = 0
                var characteristic: BluetoothGattCharacteristic? = null
                fun writeNext(connection: BluetoothGatt) {
                    if (done.get()) return
                    val target = characteristic ?: return finish("Serviciu Bluetooth invalid")
                    target.writeType = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
                    target.value = chunks[index]
                    if (!runCatching { connection.writeCharacteristic(target) }.getOrDefault(false)) finish("Transmiterea Bluetooth a eșuat")
                }
                val connectionCallback = object : BluetoothGattCallback() {
                    override fun onConnectionStateChange(connection: BluetoothGatt, status: Int, newState: Int) {
                        if (done.get()) return
                        if (status != BluetoothGatt.GATT_SUCCESS || newState == BluetoothProfile.STATE_DISCONNECTED) finish("Conexiunea cu tableta s-a întrerupt")
                        else if (newState == BluetoothProfile.STATE_CONNECTED && !runCatching { connection.discoverServices() }.getOrDefault(false)) finish("Serviciul tabletei nu răspunde")
                    }
                    override fun onServicesDiscovered(connection: BluetoothGatt, status: Int) {
                        if (status != BluetoothGatt.GATT_SUCCESS) return finish("Serviciu Bluetooth indisponibil")
                        characteristic = connection.getService(serviceId)?.getCharacteristic(LocalConfirmationReceiver.CHARACTERISTIC)
                        writeNext(connection)
                    }
                    override fun onCharacteristicWrite(connection: BluetoothGatt, target: BluetoothGattCharacteristic, status: Int) {
                        if (done.get()) return
                        if (status != BluetoothGatt.GATT_SUCCESS) return finish("Tableta nu a acceptat răspunsul")
                        index++
                        if (index == chunks.size) finish() else writeNext(connection)
                    }
                }
                scanner = requireNotNull(adapter.bluetoothLeScanner)
                scan = object : ScanCallback() {
                    private var found = false
                    override fun onScanResult(callbackType: Int, result: ScanResult) {
                        if (done.get() || found) return
                        found = true
                        try {
                            scanner?.stopScan(this)
                            gatt = result.device.connectGatt(context,false,connectionCallback,BluetoothDevice.TRANSPORT_LE)
                            if (gatt == null) finish("Tableta nu poate fi conectată")
                        } catch (_: Exception) { finish("Conexiune Bluetooth indisponibilă") }
                    }
                    override fun onScanFailed(errorCode: Int) { finish("Căutarea Bluetooth a eșuat ($errorCode)") }
                }
                scanner!!.startScan(listOf(ScanFilter.Builder().setServiceUuid(ParcelUuid(serviceId)).setManufacturerData(LocalConfirmationAddress.MANUFACTURER, LocalConfirmationAddress.tag(sessionId)).build()),ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build(),scan)
            } catch (e: Exception) { finish(e.message ?: "Permite dispozitivele din apropiere") }
        }
    }
}
