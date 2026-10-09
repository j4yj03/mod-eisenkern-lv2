# Eisenkern — REAPER-Testbench

Renderplatz für alle REAPER-basierten Messreihen. Die Konventionen sind 1:1
aus dem Geschwisterprojekt
[`mod-1175-lv2`](https://github.com/j4yj03/mod-1175-lv2)
(`reaper/testbench/`, `docs/MESSTECHNIK.md`) übernommen — dieselbe
Disziplin gilt hier, damit Messwerte vergleichbar und gerichtsfest sind.

## Projekt

- `testbench.rpp`: 48 kHz, Stereo, WAV 24 bit, Render-Muster
  `$datetime\$region{1}\matrix-$regionname-$datetime` — je Render entsteht
  ein Sitzungsordner `YYYY-MM-DD HH_MM_SS\matrix-<region>-<datetime>`.
  Dies ist die **verbindliche Namensgebung** für alle Serien.
- Tracks: **C Probe-Player** (Proben-WAV-Items), **B Referenz
  (Dry/Bypass)**, **A Eisenkern Stereo** (FX-Kette kommt mit A3/A4, wenn
  die JSFX existiert; Muster wie GS76: JSFX-Kette inklusive Bypass-Track).
- `Media/` nimmt Renderings auf, die über den Projekt-Record-Pfad laufen;
  WAVs werden durch `.gitignore` aus dem Repository gehalten.

## Probes

Probenprogramme liegen unter `Probes/` und werden von Werkzeugen erzeugt
(siehe `Probes/README.md`). WAVs bleiben lokal (`*.wav` ist gitignored);
im Repository landen nur `manifest.json` und `README.md` je Programm.

## Verbindliche Render-Disziplin (aus MESSTECHNIK/1k.2-Erfahrung)

1. **Negativkontrolle zuerst:** immer zuerst eine `no_fx`-Variante
   rendern (Track B oder FX gebypasst) und die Programmstruktur
   verifizieren — die GS76-Serie `2026-10-08 23_03_38` war kontaminiert
   (Probenkopien an falschen Offsets, −6,38 dB auf nur einem Kanal,
   Oszillation im Lead-in) und musste verworfen werden. Erst die
   verifizierte Serie `23_21_15` zählte.
2. **Verifikation vor Auswertung:** Lead-in stumm, L=R prüfen,
   Sync-Marker (Pilot-Chirps) an den erwarteten Frames, keine Clips,
   PDC-Offset dokumentieren (GS76: −3 Samples). Erst danach Wertung.
3. **Eine Render-Session je Zustandsserie**, Label mit OS-/Build-/Datei-
   Stand; SHA256 der Renders in das Serien-README (Muster:
   `test-results/<serie>/RENDERS.md` im GS76-Projekt).
4. **Verworfene Serien bleiben liegen** und werden in der Doku als
   verworfen markiert — sie sind Provenanz, kein Müll.
5. Nicht ausgeführte Messungen niemals als bestanden melden (AGENTS).

## Geplante Serien (Block A4)

- Bankanker: 20-Hz-Pegelreihe je Profil (−26/−20/−14/−8/−2 dBFS),
  **neutrale Makros**; Anker nur dort gültig.
- Makro-Sweeps: drive (−18…+24 dB), saturation (0…150 %),
  remanence (0…150 %), bass (0,5…2×) als A/B gegen Profil.
- Solver-Corner: p=13 × Saturation 150 %, DC-Asymmetrie (Sym-DC-Pumpen-
  Nachprüfung), Extremtests ±256 FS.
- PDC/OS-Wechsel: 0/3/4 Frames bei Off/2x/4x, Modellblend-Übergänge.
