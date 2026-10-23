# Beginner walkthrough

## 1. Understand the question

We want to see what changes when a fault starts and a breaker opens. Begin with a healthy circuit and verify it before adding the fault.

## 2. Build the healthy circuit

Create a case project. Add these Master Library components:

| Library name | Purpose |
|---|---|
| `source3` | Three-phase source, 11 kV and 50 Hz |
| `ground` | Ground the source neutral |
| `breaker3` | Disconnect the feeder |
| `tbreakn` | Schedule a breaker opening command |
| `datalabel` | Name its output `BRK_FEEDER`, matching the breaker name |
| `rtcbranch` | Represent feeder resistance and inductance |
| `Yload` | Three equal phase loads with grounded neutral |

Connect source → breaker → feeder → load. Apply the values in the README. For a healthy switching test, run without the fault branch. Normal phase current should be about 63 A RMS (89 A peak), then stop after the opening command.

## 3. Add the fault and its timer

Use `tpflt`, set all three phases and ground enabled, and attach it as a side branch at the load bus. Use `tfaultn` (Timed Fault Logic) for a start time of 0.50 s and a duration of 1 s. Connect its signal output to the fault's control input. Keep electrical connections separate from control signals.

## 4. Add measurements

Enable `I_Feeder` under the feeder's Internal Outputs. Generate an output channel and graph. For voltage, place `nodeloop` over the load-bus wire and connect it to `rms3ph`, then connect the meter's signal output to a `pgb` Output Channel. Set the meter base to 11 kV and output channel scale to 1; label it `V_Load_RMS_pu`, unit `pu`.

Some old graph menu options display an obsolete-option message. Instead, copy the Output Channel, create a Graph Frame and an Overlay Graph, then paste the channel into the plotting area. No electrical component needs replacement for this message.

## 5. Read the plots

Use 0–1 s for both horizontal axes. Use approximately ±15 kA for current and 0–1.2 pu for voltage. Clipped fault waves mean the display range is too narrow. They do not by themselves indicate a failed simulation.

Build, check messages, then run. Building successfully does not prove the circuit is physically correct; verify magnitudes and timing against expected behaviour.

## 6. Compare delays

Set the breaker command to 0.55, 0.60 and 0.65 s. Run after each change, then export all data from both graphs. Confirm the current burst lasts until shortly after the intended command before naming the export. File names alone do not establish which settings produced the data.

## 7. Check the time step

Repeat the 100 ms command-delay case at 25 µs solution step. Leave the export interval at 250 µs. Restore the baseline (50 µs, command at 0.60 s) before saving the final native model.

## 8. Explain the result

The fault initially reduces the load-bus impedance sharply, increasing current and collapsing voltage. Earlier breaker opening reduces current exposure. The first peak remains unchanged because it occurs before any of the compared opening commands.
