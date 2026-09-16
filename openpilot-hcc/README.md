# openpilot-hcc

**Cooperative cruise control, sim to road.**

hCCC (Human-in-the-loop Cooperative Cruise Control) on comma.ai openpilot, running on a Comma 3X. A lead car transmits its speed and acceleration over a 50 Hz UDP link, and the following car uses that to hold a time-headway gap. This was done as part of work for UVA Link Lab.

The code is on the `hcc-ego` branch; the lead device runs `hcc-lead`.

## What it is

Normal adaptive cruise only sees the gap to the car ahead. The lead broadcasts its own speed and acceleration, so the follower reacts to what the lead is doing instead of waiting for the gap to change. The data path is the same wherever it runs.

```
lead --UDP--> relay --UDP--> ego --> hCCC --> gas/brake
```

It is a fork of [openpilot](https://github.com/commaai/openpilot), which gives me production car interfaces, a vetted safety model, and replay tooling, so the only things I had to write were the controller and the V2V layer.


## The controller

`selfdrive/controls/lib/hccc_controller.py`. The controller holds a fixed time-headway gap to the lead, about 1.5 seconds of following distance, and adds a feedforward term from the lead's acceleration so it starts reacting as the lead changes speed instead of waiting for the gap to open or close.


## Results

**In-car, 2023 Kia Sportage, 2026-06-14.**

- V2V in the car matched the bench, 2000/2000 packets, zero loss at 50 Hz.
- hCCC engaged and put out smooth, correctly-signed commands, ramping roughly -0.1 to -2.0 m/s^2 as it tracked the lead. The feedforward stayed stable.
- The car never actuated. This base-trim Sportage doesn't have the Smart Cruise Control package openpilot needs to inject acceleration, so the commands had no effect

**In-car, 2024 Hyundai Tucson, 2026-07-11.**

- The ego drove the full scenario-48 profile: SET engage, feet off, tracked to 14.66 m/s (32.8 mph) peak, commanded-vs-achieved accel ~1:1 including hard braking. Scenarios 49 and 50 also ran.
- Still have bugs regarding braking + acceleration within the car as the car only reports on or off values for the pedal. 

## Tech stack

- **Language** &nbsp; Python
- **Platform** &nbsp; comma.ai openpilot on Comma 3X (AGNOS)
- **Simulation** &nbsp; MetaDrive (controller originally tuned against a BeamNG reference)
- **Transport** &nbsp; UDP V2V with relay
- **Domain** &nbsp; cooperative longitudinal control (CACC), cyber-physical systems (UVA Link Lab)

## Build and run

This is an openpilot fork, so full setup follows [upstream openpilot](https://github.com/commaai/openpilot).

See [`HCC_PROJECT_GUIDE.md`](https://github.com/ethanmathias/openpilot-hcc/blob/hcc-ego/HCC_PROJECT_GUIDE.md), `tools/real_world_testing/README.md`, and `tools/sim/README.md` for the full procedures.

**Contact** &nbsp; ethanmathias@gmail.com
