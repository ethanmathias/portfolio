# openpilot-hcc

**Cooperative cruise control, sim to road.**

hCCC (Human-in-the-loop Cooperative Cruise Control) on comma.ai openpilot, running on a Comma 3X. A lead car transmits its speed and acceleration over a 50 Hz UDP link, and the following car uses that to hold a time-headway gap without amplifying stop-and-go waves. I took it from a MetaDrive sim up to a test on real hardware in a car. Work for UVA Link Lab.

The code is on the `hcc-ego` branch; the lead device runs `hcc-lead`. Full write-up is in [`HCC_PROJECT_GUIDE.md`](https://github.com/ethanmathias/openpilot-hcc/blob/hcc-ego/HCC_PROJECT_GUIDE.md).

## What it is

Normal adaptive cruise only sees the gap to the car ahead. hCCC also hears it. The lead broadcasts its own speed and acceleration, so the follower reacts to what the lead is doing instead of waiting for the gap to change. The data path is the same wherever it runs.

```
lead --UDP--> relay --UDP--> ego --> hCCC --> gas/brake   (50 Hz)
```

It is a fork of [openpilot](https://github.com/commaai/openpilot), which gives me production car interfaces, a vetted safety model, and replay tooling, so the only things I had to write were the controller and the V2V layer.

## Why I built it

Plenty of controllers look fine in a simulator and come apart on hardware. I wanted to find where mine would. So I didn't stop at the sim. I built the controller, the V2V transport, and the field tooling to run the same code on a moving car, and kept notes on everything that broke.

## The controller

`selfdrive/controls/lib/hccc_controller.py`. A time-headway spacing law (`t_h = 1.5 s`, `beta = 0.65`) plus a lead-lag feedforward on the lead's acceleration, tuned against a BeamNG reference.

```
a_cmd = beta*(v_lead - v_ego) + F(s)*a_lead
F(s)  = (tau*s + (1 - beta*th_bar)) / (th_bar*s + 1)
```

`controlsd` sits in the real-time path and I didn't want SciPy in it. So I worked out the bilinear (Tustin) discretization of `F(s)` by hand and run it as a three-tap difference equation with scalar state, `y[n] = b0*x[n] + b1*x[n-1] - a1*y[n-1]`.

## Architecture and the test ladder

The idea is to catch each bug in the cheapest place it can show up. Nothing moves up a rung until the one below passes, and because the V2V plumbing is byte-for-byte identical at every rung, a passing rung actually says something about the next.

```mermaid
flowchart TB
    R1["Rung 1. Sim, sensed lead (MetaDrive, controller only)"]
    R2["Rung 2. Sim, V2V lead (two openpilot + relay)"]
    R3["Rung 3. Sim, cloud relay (WAN transport)"]
    R4["Rung 4. Bench (two real Comma 3X, no car)"]
    R5["Rung 5. Phase-1 in-car (ego drives; lead device replays a profile)"]
    R6["Rung 6. Phase-2, two cars"]
    R1 --> R2 --> R3 --> R4 --> R5 --> R6
    classDef done fill:#1f7a1f,color:#fff,stroke:#0d3d0d;
    classDef next fill:#b58900,color:#fff,stroke:#6b5200;
    class R1,R2,R3,R4 done
    class R5 next
```

The sim is MetaDrive, fed to openpilot through a bridge that fakes camera and vehicle signals in the format a real car produces, so the code under test is the production code. Mode 1 follows a sensed lead and isolates the controller. Mode 2 runs two openpilot instances through a relay, the full V2V path. When Mode 2 misbehaves I rerun it in Mode 1 to tell a controller bug from a comms bug.

## Decisions worth explaining

**UDP, not TCP, with a 100 ms cutoff.** For control data, stale is worse than missing. TCP would hold a fresh packet behind a retransmitted old one; UDP just drops the old one and the next arrives 20 ms later. If nothing arrives for 100 ms the follower marks the signal stale and stops commanding. Silence always means do less, never guess.

**A relay in the middle, not lead-to-ego.** It is the one place every packet gets logged, the one address to change when I move between laptop, car, and cloud, and it is how the eventual cellular version has to work anyway. Two cars can't reach each other directly, but both can reach a server.

**No HIL.** I tried hardware-in-the-loop and dropped it for a hardware reason. The Comma 3X's USB-C goes to its safety MCU (the panda), not the main SoC, so the high-bandwidth PC link HIL needs isn't physically there. The bench test took its place and caught everything I'd hoped HIL would.

## Field tooling

`tools/real_world_testing/` is the laptop side of a road test. Most of it exists because something bit me once.

- A 14-check preflight that won't let a run start until both devices answer, the relay is up, the flags are right, and the two clocks agree. The lead can't reach the internet on the test network, its clock drifts, and a skew over 500 ms makes the follower drop every packet silently.
- Runs that outlive the laptop. The device-side processes detach on launch, so if the laptop's WiFi drops mid-run, one `collect` afterward pulls the data back. Each run writes to its own timestamped folder that never gets overwritten.
- `abort` cuts the data feed and the staleness rule stops hCCC within 100 ms, but it is not the emergency stop. The brake is. The tooling never touches engage or disengage; only the driver does.

## Testing

About 29 unit tests over the controller, the V2V core, and the tooling (`test_hccc_controller.py`, `test_hcc_v2v.py`, `test_virtual_lead.py`, `test_launcher_common.py`, `test_field_test.py`), on top of the sim and bench rungs.

## Results

**Bench, 2026-06-12, no car.** Set up to fully validated in a day, after shaking out three real bugs. One was a type mismatch in code that also runs in the vehicle control process and would have killed the controller mid-drive. Transport held 1750/1750 packets at 50 Hz, zero loss, worst gap 51 ms against the 100 ms budget.

**In-car, 2023 Kia Sportage, 2026-06-14.** First run of the whole loop on a real car.

- V2V in the car matched the bench, 2000/2000 packets, zero loss at 50 Hz, about 20 ms median spacing.
- hCCC engaged and put out smooth, correctly-signed commands, ramping roughly -0.1 to -2.0 m/s^2 as it tracked the lead. The feedforward stayed stable.
- The car never actuated. This base-trim Sportage doesn't have the Smart Cruise Control package openpilot needs to inject acceleration, so the commands had nowhere to land. Joystick mode, which skips hCCC entirely, didn't move it either, which puts the fault in the car, not the stack. Nothing in the code is car-specific, so the fix is a different car (radar-SCC), not a rewrite.

Rungs 1 to 4 pass. The in-car test cleared everything but that last actuation link. Next is a radar-SCC car, then two real vehicles; the lead-side publisher already runs on `hcc-lead`.

## Tech stack

- **Language** &nbsp; Python
- **Platform** &nbsp; comma.ai openpilot on Comma 3X (AGNOS)
- **Simulation** &nbsp; MetaDrive (controller originally tuned against a BeamNG reference)
- **Transport** &nbsp; UDP V2V with relay, 50 Hz, 100 ms staleness rule
- **Domain** &nbsp; cooperative longitudinal control (CACC), cyber-physical systems (UVA Link Lab)

## Build and run

This is an openpilot fork, so full setup follows [upstream openpilot](https://github.com/commaai/openpilot). Quick paths.

```bash
# Simulation (Mode 1, controller against a sensed lead in MetaDrive)
tools/sim/launch_openpilot_ego.sh          # see tools/sim/README.md for Mode 2 (V2V)

# Bench or field V2V check on real devices
tools/hcc_v2v/scripts/setup_v2v_network.sh # one-time per device
python tools/real_world_testing/field_test.py check   # 14-point preflight
python tools/real_world_testing/field_test.py run --scenario 48
```

See [`HCC_PROJECT_GUIDE.md`](https://github.com/ethanmathias/openpilot-hcc/blob/hcc-ego/HCC_PROJECT_GUIDE.md), `tools/real_world_testing/README.md`, and `tools/sim/README.md` for the full procedures.

**Contact** &nbsp; ethanmathias@gmail.com
