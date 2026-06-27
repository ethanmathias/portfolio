# Ethan Mathias

Embedded / Firmware Engineering

Computer Engineering at the University of Virginia (GPA 4.0, expected 2028), focused on embedded software and firmware: real-time drivers, hardware bring-up, and validation on real hardware. I like short build-and-test loops, working firmware in days, not months.

**Tech:** C, C++, Python, STM32 (G4), FreeRTOS and custom RTOS layers, CAN/CAN-FD, UART/RS422, I2C, SPI, analog, ISR-driven drivers, DMA, hardware bring-up, signal-integrity validation (Analog Discovery), Bazel, CMake, Docker.

**Contact:** ethanmathias@gmail.com

## Selected Projects

### 1. [archibald-moteus](archibald-moteus/): real-time STM32 encoder driver for a servo actuator

An absolute-encoder driver in the open-source [moteus](https://github.com/mjbots/moteus) motor-controller firmware (STM32G4). I added support for the Mosrac S 17-bit absolute magnetic encoder: an ISR-driven, DMA-backed RS422/UART driver that polls the encoder and decodes its frames inside the real-time control loop, behind moteus's `aux_port` abstraction like its existing AksIM-2 driver. Alongside it I wrote a validator that trusts the encoder only after several consecutive CRC-valid readings agree, and drops it on timeout, so a noisy power-on or a pulled cable can't push bad position into commutation.

This was firmware work for Archibald Corporation. The encoder driver here is Apache-2.0 within the moteus fork and fully shareable; the Mosrac actuator itself is proprietary and isn't reproduced.

**Stack:** C++, STM32G4, moteus firmware, RS422/UART, DMA, ISR-context drivers, Bazel
**Repo:** [Archibald-Corp/archibald-moteus](https://github.com/Archibald-Corp/archibald-moteus)

### 2. [solarcar-Rivanna3S](solarcar-Rivanna3S/): multi-board firmware and a C++ RTOS layer for UVA Solar Car

On-vehicle firmware for UVA Solar Car's Rivanna3S: five STM32G4 boards (motor, relay, telemetry, two distribution) talking over a shared CAN bus. I worked on the shared C++ driver and RTOS layer: `Thread`, `MessageQueue`, locks, and timeouts over FreeRTOS so each board's code reads as plain concurrent tasks, plus the CAN, UART, and analog drivers under it. One shared layer across five different boards keeps things coherent and testable, at the cost of some abstraction each board doesn't need. UART logging is COBS-framed, and I checked bus signal integrity on hardware with an Analog Discovery.

**Stack:** C++, STM32G474, FreeRTOS (custom C++ abstraction), CAN, UART (COBS), I2C, SPI, analog, CMake, Docker, Analog Discovery
**Repo:** [solarcaratuva/Rivanna3S](https://github.com/solarcaratuva/Rivanna3S)

### 3. [openpilot-hcc](openpilot-hcc/): cooperative cruise control, sim to road

A vehicle-to-vehicle longitudinal controller on comma.ai openpilot, taken from a MetaDrive sim up to an in-car test. The lead car transmits its speed and acceleration over a 50 Hz UDP link, and the follower holds a time-headway gap with a lead-lag feedforward on the lead's acceleration, so it doesn't amplify stop-and-go waves. I built it around a test ladder with identical V2V plumbing at every rung (sim, cloud relay, bench, car), so each bug shows up in the cheapest place it can. Two calls I'd defend: UDP with a 100 ms staleness cutoff instead of TCP, since stale control data is worse than missing data; and hand-deriving the feedforward's bilinear discretization to keep SciPy out of the real-time loop. The bench ran 1750/1750 packets at 50 Hz with zero loss and caught a bug that would have hit mid-drive; in a Kia Sportage the V2V link and controller worked on hardware, blocked only by the test car lacking the cruise hardware to actuate. For UVA Link Lab.

**Stack:** Python, comma.ai openpilot (Comma 3X), MetaDrive, UDP V2V, longitudinal control (CACC), cyber-physical systems
**Repo:** [ethanmathias/openpilot-hcc](https://github.com/ethanmathias/openpilot-hcc) (branch `hcc-ego`)
