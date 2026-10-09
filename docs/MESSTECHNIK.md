# Eisenkern — Messtechnik (Aufbau)

Messplätze, Prüfungen und Referenzkanziffern werden beim Aufbau von
Block A (A4) konkreter. Vorlage und Provenanz liegen im
Geschwisterprojekt [`mod-1175-lv2`](https://github.com/j4yj03/mod-1175-lv2):
`docs/MESSTECHNIK.md` (Teil 1b–1f Transformator-Matrix, 1k.2
Diskriminierung) sowie die dortigen Messwerkzeuge
(`tools/transformer_bench.cpp`, `tools/dwarf_loadtest.py`,
`tools/make_probes.py`).

## Geplante Messplätze (vorläufig)

1. **Parität C++/EEL2** (echtes Rendern beider Kerne, Erwartungen aus
   dem Artefakt) — Voraussetzung für jede weitere Aussage.
2. **Bankanker:** 20-Hz-THD 1 % bei −14/−8/−2 dBFS je Profil — **nur
   bei neutralen Makros** (drive 0 dB, Saturation/Remanenz 100 %,
   Bass 1,0); Makro-Sweeps werden als A/B-Dokumentation geführt.
3. **Solver-Corner:** p=13 × Saturation 150 %, Iterationslast und
   Konvergenz; Extremtests ±256 FS ohne NaN/Inf.
4. **Gerät (MOD Dwarf):** CPU-Matrix der 4 Profile × OS × Colour-frei,
   mit OS-Build label (Teststand 1.14 RC4 build 3366; Release-Verifikation
   an 1.13.5.3315 gebunden); xruns-Delta; Install-SHA256-Verifikation.
5. **REAPER:** PDC-Anzeige bei OS-Wechsel (0/3/4 Frames), Presets,
   User-Presets, Zustands-Recall.
