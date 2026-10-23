# Calculations and measurement method

## Hand calculation

Use RMS phasors for the balanced steady-state estimates. These calculations do not predict the first asymmetric current peak or exact breaker interruption.

Source phase-to-neutral RMS voltage:

```text
Vphase = 11,000 / sqrt(3) = 6,350.85 V
Xfeeder = 2 × pi × 50 × 0.003 = 0.94248 Ω
```

Normal operation, per-phase impedance:

```text
Znormal = (0.2 + 0.001 + 0.5 + 100) + j0.94248 Ω
Inormal = Vphase / |Znormal| ≈ 63.1 A RMS
```

During the balanced fault, the 0.01 Ω fault resistance is in parallel with the 100 Ω load resistor in each phase:

```text
Rparallel = 1 / (1/0.01 + 1/100) ≈ 0.009999 Ω
Zfault = (0.2 + 0.001 + 0.5 + Rparallel) + j0.94248 Ω
Ifault = Vphase / |Zfault| ≈ 5.38 kA RMS
Symmetrical peak ≈ sqrt(2) × Ifault ≈ 7.61 kA
```

The source ramp is nearly settled by 0.50 s. Small remaining startup effects and finite OFF-state resistances are neglected in the estimates. Source resistance and the feeder's inductance form a simple series network; no realistic source X/R ratio is claimed. The first sampled peak of 8.562 kA includes the switching transient, so it need not equal sqrt(2) times sustained RMS current.

## Input data

All exported files contain 4,001 records from 0 to 1 s, inclusive, at a 250 µs interval. The first column is time in seconds. Current exports have three instantaneous phase-current columns in kA, in their original export order. Voltage exports contain one combined analog RMS signal normalised to an 11 kV line-to-line base. It is not three separate phase RMS readings.

Raw data is preserved byte-for-byte from the supplied CSV files. Repeated current headers are retained; the script identifies columns by position. No interpolation, filtering or rescaling of the input data is performed before measurement.

## Metrics

- Normal RMS current: square root of the mean of squared samples in 0.40 ≤ t < 0.50 s.
- Fault RMS current: one 20 ms cycle, beginning 30 ms before each opening command and ending 10 ms before it. Windows are 0.52–0.54, 0.57–0.59 and 0.62–0.64 s. The earliest window may retain a small inception transient; do not infer that its small phase differences indicate a steady-state unbalanced network.
- Peak fault current: largest absolute exported sample at t ≥ 0.50 s. This is a sampled maximum, not a guarantee of the continuous-time maximum.
- Interruption observation: locate each phase's final sample above |I| = 0.001 kA (1 A) after fault inception, then report that time and the next exported sample. This avoids mistaking a normal zero crossing for permanent interruption. Finite OFF-state resistance permits tiny leakage currents.
- I²t: integrate instantaneous current squared by the trapezoidal rule over 0.50–0.70 s for each phase. Average the three integrals for the comparison metric. Units are kA²s; multiply by 1,000,000 for A²s. This metric indicates current exposure. Deriving heat requires resistance and a thermal model; no equipment withstand rating is asserted.

## Numerical sensitivity

Only the 100 ms case was repeated with a 25 µs solution step. The plotting/export interval remained 250 µs so the exported datasets can be compared at common times. Compare the largest sampled peak and mean phase I²t, and inspect each phase's threshold interval. Phase-specific results are in `results/metrics.json`.

The changes are small for the selected metrics. A fixed export interval can conceal changes shorter than 250 µs. More demanding switching-overvoltage or exact interruption-time studies would require finer recording and further numerical checks.

## Reproduction and limitations

The breaker opening is scheduled; no relay detects the fault. A common trip command does not make all phases interrupt at the same instant because they have different current zeros. The fault command remains active throughout the remainder of the one-second run. Load voltage does not recover when the feeder breaker opens.

No claims are made about real network compliance, protection coordination, device ratings, transformer grounding, line mutual coupling, distributed capacitance, motor load behaviour or arc dynamics. Asymmetric ground-fault extensions require a deliberate choice of sequence impedances and grounding assumptions.
