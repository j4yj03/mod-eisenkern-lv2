# Eisenkern — Factory Profiles

> Four profiles as own voicing, not hardware measurements.
> The 1-%-THD anchors (−14/−8/−2 dBFS) hold only at neutral macros
> (Drive 0 dB, Saturation/Remanence 100 %, Bass 1.0).
> Oversampling is a separate quality/CPU choice and always recalls to Off.

| Preset | Eisen | Drive / Output dB | Saturation / Remanence % | Bass | Load / Source Ω | HF corner Hz / Q | Family / Exponent |
|---|---|---|---|---|---|---|---|
| 01 Warm Iron | 60s | 0 / 0 | 100 / 100 | 1 | 10000 / 600 | 26000 / 0.70710678118654746 | Power / 3 |
| 02 Tight Coil | 80s | 0 / 0 | 100 / 100 | 1 | 10000 / 600 | 48000 / 0.70710678118654746 | Power / 5 |
| 03 Open Core | 00s | 0 / 0 | 100 / 100 | 1 | 10000 / 600 | 108256.99342420955 / 0.66267210834206303 | Fröhlich / 3 |
| 04 Linear Reference | Symmetric | 0 / 0 | 100 / 100 | 1 | 10000 / 600 | 108256.99342420955 / 0.66267210834206303 | Power / 3 |

## 01 Warm Iron

60s profile at neutral macros: early, soft saturation, clearly warm with a noticeable bass loss. 1-%-THD anchor at −14 dBFS.


## 02 Tight Coil

80s profile at neutral macros: tight and punchy with less low-bass loss. 1-%-THD anchor at −8 dBFS.


## 03 Open Core

00s profile at neutral macros: open, saturation only at high levels (Fröhlich core with C1 high-field continuation). 1-%-THD anchor at −2 dBFS. The exponent has no effect with the Fröhlich family.


## 04 Linear Reference

Linear reference: no saturation, no remanence. Macros stay ineffective for this profile (profile constants are 0); the network (bass, load/source, HF corner) still acts.

