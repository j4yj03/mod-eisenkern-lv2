# Probes — Konvention

Probenprogramme werden von Werkzeugen erzeugt (Block A4; Vorlage:
`../mod-1175-lv2/tools/make_probes.py` und das Diskriminierungsprogramm
`tools/make_discrimination_program.py` — Generatoren und Timeline-Muster
dort übernehmen, an Eisenkern-Reglerbereiche anpassen).

## Regeln

- Ein Programm = ein WAV + `manifest.json` + `README.md` im eigenen
  Unterordner (`Probes/<programm>/`).
- `manifest.json` enthält: Ablaufplan (Start s/frames, Dauer, Inhalt),
  Generatorkonstanten, SHA256 des WAV, Erzeuger (Werkzeug + Stand),
  48 kHz / Stereo / PCM 24 als Ziel.
- `README.md` beschreibt Ablaufplan und den Render-Auftrag inklusive
  verbindlicher Dateinamen (`matrix-<region>-<datetime>`, siehe
  `../testbench/README.md`).
- WAVs bleiben lokal (`.gitignore` schließt `*.wav` aus); im Repository
  landen nur die beiden Metadateien.
- Sync-Marker (Pilot-Chirps am Anfang/Ende) und stummes Lead-in gehören
  zu jedem Programm — sie sind die Basis der Render-Verifikation.
