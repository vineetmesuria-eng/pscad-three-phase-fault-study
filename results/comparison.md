# Measured results

Command delay is measured from fault inception at 0.50 s. These are educational model results.

| Command delay | Command time | Largest sampled peak | Last sample above 1 A | Mean phase I²t |
|---|---|---|---|---|
| 50 ms | 0.55 s | 8.562 kA | 0.55950 s | 1.603 kA²s |
| 100 ms | 0.60 s | 8.562 kA | 0.60950 s | 3.050 kA²s |
| 150 ms | 0.65 s | 8.562 kA | 0.65950 s | 4.497 kA²s |

I²t: trapezoidal integration of instantaneous phase current squared over 0.50–0.70 s, followed by averaging the three phase integrals. This is current exposure, not measured temperature or a protection rating.

The next sample (250 µs later) is below 1 A. This threshold-based interval is an observation from the exports, not an exact contact-opening time.

Reducing command delay from 150 to 50 ms reduces mean phase I²t by 64.3%.

## Time-step sensitivity

For the 100 ms case, reducing the calculation step from 50 to 25 µs changes largest sampled peak by -0.0116% and mean phase I²t by -0.0333%. The 250 µs exported sampling remains unchanged.

See [methodology](../docs/methodology.md) for calculation windows, assumptions and limitations.
