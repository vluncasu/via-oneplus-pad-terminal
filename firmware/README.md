# Optional VIA LED Controller Firmware

`via_terminal_controller/via_terminal_controller.ino` is the supplied ESP32 enclosure-lighting accessory firmware. It is independent of the tablet–phone BLE confirmation transport. Inspect its pin definitions and the actual driver electronics before use; firmware does not establish an electrically safe LED power stage.

Open the sketch with a compatible ESP32 Arduino toolchain and the libraries declared by the sketch. No board-specific binary is claimed tested in this release. Do not connect a 12 V LED load directly to an ESP32 GPIO. Use an appropriate real driver/power circuit and validate current, wiring and heat with the selected strip. This publication includes the source as an optional accessory, not as a prerequisite for the Android demo.
