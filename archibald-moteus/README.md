# archibald-moteus

Real-time firmware support for the Mosrac S-series absolute magnetic encoder in the open-source [moteus](https://github.com/mjbots/moteus) brushless-servo controller (STM32G4). This fork adds an ISR-driven RS422/UART encoder driver and a robustness validator behind moteus's existing `aux_port` encoder abstraction.

This firmware was developed for Archibald Corporation. The encoder driver documented here lives in the moteus firmware tree under its Apache-2.0 license and is fully shareable. The Mosrac actuator design itself is proprietary and is not described here; this README covers only the open driver and integration contribution.

## What it is

[moteus](https://github.com/mjbots/moteus) is a widely used open-source brushless servo controller. It supports several encoders behind a common `aux_port` interface. This contribution adds a new one, the Mosrac S, a 17-bit absolute magnetic ring encoder polled over RS422 UART.

My contribution ([commit `dce0392`](https://github.com/Archibald-Corp/archibald-moteus/commit/dce0392)) adds the following.

| File | Role |
|------|------|
| `fw/mosrac_s.h` | ISR-driven, DMA-backed RS422 driver that polls the encoder (command `0x31`), decodes the 6-byte response, and handles timeouts and resync |
| `fw/mosrac_s_validator.h` | Startup and disconnect state machine that gates when the encoder is trusted |
| `fw/aux_port.h`, `fw/aux_common.h`, `fw/motor_position.h`, `fw/BUILD` | Wiring the new encoder into moteus's auxiliary-port and motor-position framework |


- **MCU** &nbsp; STM32G4
- **Language** &nbsp; C++
- **Firmware** &nbsp; moteus (Apache-2.0)
- **Interface** &nbsp; RS422/UART with DMA
- **Encoder** &nbsp; Mosrac S, 17-bit absolute (`kCpr = 131072`)
- **Build** &nbsp; Bazel (moteus toolchain)

## Build

This builds as part of the moteus firmware. See the upstream [moteus docs](https://github.com/mjbots/moteus/blob/main/docs/) for the toolchain.
