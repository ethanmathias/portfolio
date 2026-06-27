# Ethan Mathias

Embedded / Firmware Engineering

I am a Computer Engineering student at the University of Virginia (GPA 4.0, expected 2028), focused on embedded software and firmware: real-time driver development, hardware bring-up, and validation on real hardware. I work toward tight build-and-test cycles, getting working firmware onto hardware in days rather than months.

**Tech:** C, C++, Python, STM32 (G4), FreeRTOS and custom RTOS layers, CAN/CAN-FD, UART/RS422, I2C, SPI, analog interfaces, real-time ISR-driven drivers, DMA, hardware bring-up, signal-integrity validation (Analog Discovery), Bazel, CMake, Docker.

**Contact:** ethanmathias@gmail.com

## Selected Projects

### 1. [archibald-moteus](archibald-moteus/): Real-time STM32 encoder driver for a servo actuator

Bring-up of an absolute-encoder driver in the open-source [moteus](https://github.com/mjbots/moteus) motor-controller firmware.

I added support for the Mosrac S-series 17-bit absolute magnetic encoder to the moteus brushless-servo firmware (STM32G4): an ISR-driven, DMA-backed RS422/UART driver that polls the encoder and decodes its 6-byte frames inside the real-time control loop. Rather than bolt on a sensor, I integrated it behind moteus's `aux_port` encoder abstraction, modeled on the existing AksIM-2 driver. Alongside the driver I wrote a validator that marks the encoder active only after several consecutive CRC-valid readings that agree with each other, and drops it on timeout, so a noisy power-on or a disconnected cable cannot feed bad position into commutation.

This was firmware work for Archibald Corporation. The encoder driver documented here is Apache-2.0 licensed within the moteus fork and is fully shareable; the Mosrac actuator design itself is proprietary and is not reproduced.

**Stack:** C++, STM32G4, moteus firmware, RS422/UART, DMA, ISR-context drivers, Bazel
**Repo:** [Archibald-Corp/archibald-moteus](https://github.com/Archibald-Corp/archibald-moteus)

### 2. [solarcar-Rivanna3S](solarcar-Rivanna3S/): Multi-board embedded firmware and a C++ RTOS layer for UVA Solar Car

Five STM32 boards on CAN, running C++ firmware over a custom FreeRTOS abstraction, verified on the bench.

This is the on-vehicle firmware for UVA Solar Car's Rivanna3S platform: five STM32G4 boards (motor, relay, telemetry, and two distribution boards) that coordinate over a shared CAN bus. I worked on the shared C++ driver and RTOS-abstraction layer: `Thread`, `MessageQueue`, locks, and timeouts that wrap FreeRTOS so application code reads as plain concurrent tasks instead of raw RTOS calls, plus the CAN, UART, and analog drivers underneath. A single shared driver and RTOS layer across five different boards keeps the codebase coherent and testable, at the cost of carrying some abstraction each board does not strictly need. UART host logging uses COBS framing, and I verified bus signal integrity on real hardware with an Analog Discovery.

**Stack:** C++, STM32G474, FreeRTOS (custom C++ abstraction), CAN, UART (COBS), I2C, SPI, analog, CMake, Docker, Analog Discovery
**Repo:** [solarcaratuva/Rivanna3S](https://github.com/solarcaratuva/Rivanna3S)

### 3. [openpilot-hcc](openpilot-hcc/): Cooperative cruise control, from simulation to a real car

A vehicle-to-vehicle longitudinal controller on comma.ai openpilot, validated up a six-rung ladder from MetaDrive simulation to an in-car field test.

I built hCCC (Human-in-the-loop Cooperative Cruise Control) on comma.ai's openpilot (Comma 3X). The lead car broadcasts its speed and acceleration over a 50 Hz UDP V2V link, and the ego car's controller uses a constant time-headway gap plus a lead-lag feedforward on the lead's acceleration to follow it without amplifying stop-and-go waves. I designed the project around a testing ladder with identical V2V plumbing at every rung (MetaDrive simulation, cloud relay, bench, in-car) so each defect surfaces in the cheapest place it can. Two notable decisions: UDP with a 100 ms staleness cutoff rather than TCP, since for control data late is worse than lost; and discretizing the feedforward compensator in closed form (bilinear transform) to keep SciPy out of the real-time loop. On the bench it ran 1750/1750 packets at 50 Hz with 0% loss, catching a crash that would otherwise have occurred while driving. In a real Kia Sportage the V2V link and hCCC produced smooth, correctly-signed acceleration on hardware; the only blocker was the test car lacking the cruise hardware to actuate, not the software. Built for UVA Link Lab research.

**Stack:** Python, comma.ai openpilot (Comma 3X), MetaDrive, UDP V2V, longitudinal control (CACC), cyber-physical systems
**Repo:** [ethanmathias/openpilot-hcc](https://github.com/ethanmathias/openpilot-hcc) (branch `hcc-ego`)
