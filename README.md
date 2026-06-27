# Ethan Mathias — Embedded / Firmware Engineering

I'm a Computer Engineering student at the University of Virginia (GPA 4.0, grad 2028) focused on **embedded software and firmware** — the layer where code meets silicon, sensors, and motors. I like getting real hardware to *do something* fast: write a driver, put it on a logic analyzer, find out where reality disagrees with the datasheet, and close the loop. My bias is toward **end-to-end bring-up and tight build/test cycles — working hardware in days, not months.**

**Tech:** C, C++, Python · STM32 (G4) · FreeRTOS / RTOS abstraction · CAN / CAN-FD, UART (RS422), I²C, SPI, analog · real-time ISR-driven drivers · DMA · hardware bring-up & signal-integrity validation (Analog Discovery) · Bazel / CMake / Docker

📫 ethanmathias@gmail.com

---

## Selected Projects

### 1. [archibald-moteus](archibald-moteus/) — Real-time STM32 encoder driver for a next-gen servo actuator
> End-to-end bring-up of an absolute-encoder driver in the open-source [moteus](https://github.com/mjbots/moteus) motor-controller firmware.

I added support for the **Mosrac S-series 17-bit absolute magnetic encoder** to the moteus brushless-servo firmware (STM32G4): an **ISR-driven, DMA-backed RS422/UART driver** that polls the encoder and decodes its 6-byte frames inside the real-time control loop. I wanted to understand a production motor-control firmware from the inside — so rather than bolt on a sensor, I integrated it the way moteus does, behind its `aux_port` encoder abstraction, modeled on the existing AksIM-2 driver. The decision I'm most happy with is the **validator** I wrote alongside the driver: instead of trusting the first reading, it only marks the encoder "active" after several consecutive CRC-valid readings that agree with each other, and drops it on timeout — so a noisy power-on or a yanked cable can't feed garbage into commutation. This is the genuinely shareable part of a larger actuator project.

> ⚠️ This was firmware work for **Archibald Corporation**. The encoder driver documented here is Apache-2.0-licensed within the moteus fork and is fully shareable; the Mosrac actuator design itself is proprietary and is **not** reproduced.

**Stack:** C++ · STM32G4 · moteus firmware · RS422/UART · DMA · ISR-context drivers · Bazel
**Repo:** [Archibald-Corp/archibald-moteus](https://github.com/Archibald-Corp/archibald-moteus)

---

### 2. [solarcar-Rivanna3S](solarcar-Rivanna3S/) — Multi-board embedded firmware + a C++ RTOS layer for UVA Solar Car
> Five STM32 boards on CAN, running C++ firmware over a custom FreeRTOS abstraction, brought up and verified on the bench.

This is the on-vehicle firmware for UVA Solar Car's **Rivanna3S** platform: five STM32G4 boards (motor, relay, telemetry, and two distribution boards) that coordinate over a shared **CAN** bus. I worked on the **C++ driver and RTOS-abstraction layer** that the boards share — `Thread`, `MessageQueue`, locks, and timeouts wrapping FreeRTOS so application code reads as plain concurrent tasks instead of raw RTOS calls, plus the **CAN / UART / analog** drivers underneath. I built it because I wanted to own the OS layer rather than treat FreeRTOS as a black box; wrapping it forced me to reason concretely about priorities, shared peripherals, and where timing budget goes. The interesting tradeoff was uniformity vs. footprint — one shared driver/RTOS layer across five very different boards keeps the codebase coherent and testable, at the cost of carrying abstraction each board doesn't strictly need. I used **COBS-framed UART** for reliable host logging and verified bus signal integrity on real hardware with an Analog Discovery.

**Stack:** C++ · STM32G474 · FreeRTOS (custom C++ abstraction) · CAN · UART (COBS) · I²C · SPI · analog · CMake + Docker · Analog Discovery
**Repo:** [solarcaratuva/Rivanna3S](https://github.com/solarcaratuva/Rivanna3S)

---

### 3. [openpilot-hcc](openpilot-hcc/) — Cooperative cruise control, from simulation to a real car
> A vehicle-to-vehicle longitudinal controller on comma.ai openpilot, validated up a six-rung ladder from MetaDrive to an in-car field test.

I built **hCCC — Human-in-the-loop Cooperative Cruise Control** — on comma.ai's openpilot (Comma 3X): the lead car broadcasts its speed and acceleration over a 50 Hz UDP **V2V** link, and the ego car's controller uses a constant time-headway gap plus a **lead-lag feedforward** on the lead's acceleration to follow it without amplifying stop-and-go waves. I built it for UVA **Link Lab** research because controllers that look safe in simulation rarely survive real timing, networks, and vehicle hardware unchanged — so I designed the whole thing around a **testing ladder** (identical V2V plumbing from MetaDrive sim → cloud relay → bench → in-car) that finds each defect in the cheapest place it can be found. Two decisions I'd call out: **UDP with a 100 ms staleness cutoff** instead of TCP, because for control data late is worse than lost; and **discretizing the feedforward compensator in closed form (bilinear transform)** to keep SciPy out of the real-time loop. On the bench it ran **1750/1750 packets at 50 Hz, 0% loss**, catching a crash that would have hit mid-drive; in a real Kia Sportage the V2V link and hCCC produced smooth, correctly-signed acceleration on hardware — the only blocker was the test car lacking the cruise hardware to actuate, not the software.

**Stack:** Python · comma.ai openpilot (Comma 3X) · MetaDrive · UDP V2V · longitudinal control / CACC · cyber-physical systems
**Repo:** [ethanmathias/openpilot-hcc](https://github.com/ethanmathias/openpilot-hcc) (branch `hcc-ego`)

---

*Suggested pin order: **archibald-moteus** → **solarcar-Rivanna3S** → **openpilot-hcc** (embedded relevance first).*
