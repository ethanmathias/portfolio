# Ethan Mathias

Embedded / Firmware Engineering

Computer Engineering at the University of Virginia (expected 2028), focused on embedded software and firmware.

**Tech** &nbsp; C, C++, Python, STM32 (G4), FreeRTOS and custom RTOS layers, CAN/CAN-FD, UART/RS422, I2C, SPI, analog, ISR-driven drivers, DMA, hardware bring-up, signal-integrity validation (Analog Discovery), Bazel, CMake, Docker.

**Contact** &nbsp; ethanmathias@gmail.com

## Projects

### 1. [archibald-moteus](archibald-moteus/)

**Real-time encoder driver for a servo actuator.**

An absolute-encoder driver in the open-source [moteus](https://github.com/mjbots/moteus) motor-controller firmware (STM32G4). I added support for the Mosrac S 17-bit absolute magnetic encoder, an ISR-driven, DMA-backed RS422/UART driver that polls the encoder and decodes its frames inside the real-time control loop, behind moteus's `aux_port` abstraction like its existing AksIM-2 driver.

This was firmware work for Archibald Corporation. The encoder driver here is Apache-2.0 within the moteus fork and fully shareable; the Mosrac actuator itself is proprietary and isn't reproduced.

**Stack** &nbsp; C++, STM32G4, moteus firmware, RS422/UART, DMA, ISR-context drivers, Bazel

**Repo** &nbsp; [Archibald-Corp/archibald-moteus](https://github.com/Archibald-Corp/archibald-moteus)

### 2. [solarcar-Rivanna3S](solarcar-Rivanna3S/)

**Multi-board firmware and a C++ RTOS layer for UVA Solar Car.**

On-vehicle firmware for UVA Solar Car's Rivanna3S, five STM32G4 boards (motor, relay, telemetry, two distribution) talking over a shared CAN bus. I worked on the shared C++ driver and RTOS layer, the `Thread`, `MessageQueue`, lock, and timeout wrappers over FreeRTOS that let each board's code read as plain concurrent tasks, plus the CAN, UART, and analog drivers under it.

**Stack** &nbsp; C++, STM32G474, FreeRTOS (custom C++ abstraction), CAN, UART (COBS), I2C, SPI, analog, CMake, Docker, Analog Discovery

**Repo** &nbsp; [solarcaratuva/Rivanna3S](https://github.com/solarcaratuva/Rivanna3S)

### 3. [openpilot-hcc](openpilot-hcc/)

**Cooperative cruise control.**

A vehicle-to-vehicle longitudinal controller on comma.ai openpilot. The lead car transmits its speed and acceleration over a 50 Hz UDP link, and the follower holds a time-headway gap with a lead-lag feedforward on the lead's acceleration. The goal of this project is to test a custom CACC algorithm on read world cars. 

**Stack** &nbsp; Python, comma.ai openpilot (Comma 3X), MetaDrive, UDP V2V, longitudinal control (CACC), cyber-physical systems

**Repo** &nbsp; [ethanmathias/openpilot-hcc](https://github.com/ethanmathias/openpilot-hcc) (branch `hcc-ego`)
