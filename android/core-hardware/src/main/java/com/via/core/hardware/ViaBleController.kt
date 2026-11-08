package com.via.core.hardware

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.util.UUID

class ViaBleController(private val context: Context) {
    companion object {
        val SERVICE_UUID: UUID = UUID.fromString("7c8d0001-4d2b-4c1f-9c0a-0d7b2c6e1001")
        val STATE_UUID: UUID = UUID.fromString("7c8d0002-4d2b-4c1f-9c0a-0d7b2c6e1001")
        const val DEVICE_NAME = "VIA-HW"
    }

    enum class LinkState { DISCONNECTED, SCANNING, CONNECTING, CONNECTED }
    enum class LedState(val wire: String) { IDLE("idle"), ACTIVE("active"), SCAN("scan"), SUCCESS("success"), ERROR("error"), OFF("off") }

    private val manager = context.getSystemService(BluetoothManager::class.java)
    private val adapter get() = manager.adapter
    private var gatt: BluetoothGatt? = null
    private var stateCharacteristic: BluetoothGattCharacteristic? = null
    private val _link = MutableStateFlow(LinkState.DISCONNECTED)
    val link: StateFlow<LinkState> = _link

    fun hasPermissions(): Boolean {
        if (Build.VERSION.SDK_INT < 31) return ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        return ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED &&
            ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED
    }

    @SuppressLint("MissingPermission")
    fun connect() {
        if (!hasPermissions() || adapter == null || !adapter.isEnabled) return
        if (_link.value == LinkState.CONNECTED || _link.value == LinkState.SCANNING) return
        _link.value = LinkState.SCANNING
        adapter.bluetoothLeScanner.startScan(scanCallback)
    }

    @SuppressLint("MissingPermission")
    fun disconnect() {
        runCatching { adapter.bluetoothLeScanner.stopScan(scanCallback) }
        gatt?.disconnect(); gatt?.close(); gatt = null; stateCharacteristic = null
        _link.value = LinkState.DISCONNECTED
    }

    @SuppressLint("MissingPermission")
    fun setLedState(state: LedState) {
        val c = stateCharacteristic ?: return
        val bytes = state.wire.encodeToByteArray()
        if (Build.VERSION.SDK_INT >= 33) {
            gatt?.writeCharacteristic(c, bytes, BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT)
        } else {
            @Suppress("DEPRECATION")
            run { c.value = bytes; c.writeType = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT; gatt?.writeCharacteristic(c) }
        }
    }

    private val scanCallback = object : ScanCallback() {
        @SuppressLint("MissingPermission")
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            val name = result.device.name ?: result.scanRecord?.deviceName
            if (name != DEVICE_NAME) return
            adapter.bluetoothLeScanner.stopScan(this)
            _link.value = LinkState.CONNECTING
            gatt = result.device.connectGatt(context, false, gattCallback, BluetoothDevice.TRANSPORT_LE)
        }
        override fun onScanFailed(errorCode: Int) { _link.value = LinkState.DISCONNECTED }
    }

    private val gattCallback = object : BluetoothGattCallback() {
        @SuppressLint("MissingPermission")
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                this@ViaBleController.gatt = gatt
                gatt.discoverServices()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                stateCharacteristic = null
                _link.value = LinkState.DISCONNECTED
                runCatching { gatt.close() }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status != BluetoothGatt.GATT_SUCCESS) { _link.value = LinkState.DISCONNECTED; return }
            stateCharacteristic = gatt.getService(SERVICE_UUID)?.getCharacteristic(STATE_UUID)
            _link.value = if (stateCharacteristic != null) LinkState.CONNECTED else LinkState.DISCONNECTED
        }
    }
}
