---
name: audio-coding
description: Arbeitsregeln und DSP-Erkenntnisse für Eisenkern, das eigenständige Transformator-Plugin (LV2 + JSFX, zwei Sprachpfade C++/EEL2 mit Bit-Parität). Nutzen bei allen Arbeiten in mod-eisenkern-lv2.
---

# Eisenkern — Skill (Stand 2026-10-09)

Dieses Repository ist aus dem Geschwisterprojekt
`../mod-1175-lv2` (Green Stripe 76) abgezweigt; der Transformator-Solver
wurde bitgleich übertragen und verifiziert. Einstieg immer über die
normativen Dokumente, dann diesen Skill.

## Normative Einstiege (jede Session)

1. `AGENTS.md` — verbindliche Regeln (Umfang, DSP-/Revisionsdisziplin,
   Zielgerät, Generierung, Commits nur auf Auftrag).
2. `docs/TODO.md` — Arbeitsplan mit Blockstatus (A1/A5 erledigt,
   A2/A3/A4/A7 offen, Block B im Geschwisterprojekt).
3. `docs/PROJEKT.md` — Stand und Übergabe inkl. GUI-Nacharbeit.
4. `docs/DSP.md` — A1-Verträge (Port-Dreieck LV2/JSFX/RPL, Port-Gruppen,
   Expert-Ports absolut), Parameter-Analyse, modgui-Abschnitt.
5. `docs/QUELLEN.md` — SHA256-Herkunftskette; `docs/MESSTECHNIK.md` —
   geplante Messplätze.

## Geteilte Disziplin (Quelle: GS76-Skill)

Die harte Paritätsdisziplin (C++/EEL2 bitgleich, echtes Rendern beider
Kerne, kein Fast-Math, `-ffp-contract=off`, EEL2-Caveats `===`/NaN/
negative Literale, PIL-Ebenenregeln, Render-Disziplin) ist im
**audio-coding-Skill des Geschwisterprojekts** ausführlich dokumentiert —
bei DSP-Arbeit zuerst dort nachschlagen statt Erkenntnisse zu duplizieren.
Wichtige Abschnitte dort: „Zwei-Sprachen-Parität", „Angehängte Ports",
„LV2 Port-Gruppen (pg)", „REAPER-Testbench — Konventionen", „Typische
Fallen".

## Stand der Blöcke (2026-10-09)

- **Erledigt:** Code-Trennung (bitgleich verifiziert), A1 Generator +
  Plugin-Metadaten (Revision 0.1.3), A5 modgui inkl. Nacharbeit
  (kompakte Kopfplatte, Chicken-Head, Preset-Dropdown), Werkzeugübernahme.
- **Offen:** A2 `src/lv2_plugin.cpp` (LV2-C-ABI-Wrapper, Signalpfad
  Host → OS → Drive → Netz → HF → Normalisierung → Output → Dezimation),
  A3 EEL2-Engine (`Eisenkern-Core.jsfx-inc`, `Eisenkern-UI.jsfx-inc` —
  die generierten Wrappers importieren sie bereits), A4 Tests (Parität,
  Anker, Extremecken), A7 Cross-Build/Gerät.
- **Zurückgestellt:** Sym-DC-Pumpen (Benutzerentscheidung); evtl. entfällt
  das Symmetric-Profil — Entscheidung vor Release, dann Bankrevision +
  Presets + Doku anpassen.

## MOD modgui-Konventionen (A5, erprobt)

- **Film-Widget:** 65 Frames à 128 px nebeneinander; CSS
  `background-size = 65 × Anzeigebreite`. MOD leitet die Schritte aus der
  background-size ab und mappt den Wertanteil × 64 (Preview-Formel in
  `tools/gui_preview.py`: `-round(64*(v-min)/(max-min))*frameWidth`,
  frameWidth via `getBoundingClientRect().width`). Integer-Port 0..3
  landet auf Frames 0/21/43/64 — Zwischenframes zeigt MOD beim Ziehen.
- **Chicken-Head-Streifen:** `tools/make_eisen_knob.py` (deterministisch,
  Pillow, Sockel/Licht ortsfest, nur der Griff rotiert). Rastframes
  0/21/43/64 ↔ −135°/−45°/+45°/+135°, stückweise Interpolation dazwischen
  (`angle()` im Skript). Label-Winkel im CSS müssen dieselben Winkel
  verwenden; Browserprüfung über atan2 im Screenshot-Skript möglich.
- **Mustache-Templates:** `{{{cns}}}` an jede CSS-Klasse (Scope) und an
  die Root-Klasse im HTML; `{{{ns}}}` an jede Asset-URL
  (`/resources/assets/name.png{{{ns}}}`). `gui_preview.py` ersetzt
  `{{{ns}}}` **vor** dem Asset-Inlining — Reihenfolge beachten.
- **Native Preset-Auswahl:** `<select mod-role="presets">` mit
  `<option value="{{uri}}">{{label}}</option>` aus
  `{{#effect.presets}}`; der MOD-Host lädt bei Änderung das komplette
  LV2-Preset (`options.presetLoad`), kein Extra-Port, keine eigene
  Recall-Logik. Lokale Vorschau: Optionen aus `data/presets.json`
  einsetzen (macht `gui_preview.py`). Am Gerät noch nicht verifiziert.
- **Drag-Ring:** 4 absolute Rails (top/left/right/bottom) + Fußplatten-
  Drag nach dem GS76-Muster; Maße hängen am Panel-Padding (hier 26/24/8)
  und stehen im CSS-Kommentar. Controls dürfen nie Nachfahren eines
  Handles sein.
- **Kein Meter-Port** im Portvertrag; die THD-Anzeige ist statisch
  vorbereitet (`thd-meter-*`-Assets aus GS76-VU-Ebenen, Face-Umbeschriftung
  via `tools/make_thd_meter.py`). Live-THD braucht zuerst Messsemantik
  (Grundfrequenz/Fenster/THD+N, Mono/Stereo) und eine bewusste
  Vertragsänderung.
- **Render-Pipeline:** `tools/make_assets.py` (Playwright/Chromium +
  Pillow) rendert screenshot/thumbnail je Variante. Auf diesem Rechner
  fehlen Chromium-Systemlibs:
  `LD_LIBRARY_PATH=/tmp/opencode/chrome-libs/root/usr/lib/x86_64-linux-gnu`
  (Debs liegen dort entpackt; Neuaufbau per `apt-get download` + `dpkg -x`
  ohne Root).

## Werkzeuge (Herkunft und Zweck)

- **Aus GS76 übernommen und angepasst:** `gui_preview.py`, `make_assets.py`,
  `check_abi.py` (unverändert), `build_dwarf.sh` (MPB moddwarf-new, läuft
  **im** Plugin-Builder), `package.py` (Eisenkern-Namen, nur existierende
  Docs). Bewusst **nicht** übernommen: Mess-/Gerätewerkzeuge (`dwarf_*`,
  `scarlett_*`, `analyze_*`), Offline-Fit, `make_probes.py` (Testrechner),
  `make_transformer_asset.py` (Asset existiert).
- **Eigen:** `make_thd_meter.py`, `make_eisen_knob.py`,
  `lv2/eisenkern.lv2/modgui/assets/carry-handle.svg` (eigene SVG-Bügel,
  Frontansicht mit Außenwölbung; rechter Bügel via `transform:scaleX(-1)`).
- Asset-Änderungen: Generator-Skript laufen lassen, Screenshots neu
  rendern, Herkunftsangaben in `modgui/assets/README.md` und
  `docs/QUELLEN.md` pflegen.

## Revisions- und Ablage-Disziplin (Erinnerung)

- Revisionsnummer = **dritte Stelle** der `version` in `data/model.json`;
  eine Sourcecodeänderung (nur `src/` oder `jsfx/`) = +1; ein Arbeitsblock
  = eine Revision. `tools/`, `lv2/`, `docs/`, GUI-Assets bumpen **nicht**.
- Nach jedem Bump `tools/generate.py` laufen lassen (Version erscheint in
  LV2-GUI-Fußzeile und JSFX-GFX).
- `make check-generated` + `tools/validate.py` nach jeder Generator- oder
  Datenänderung; Commits/Pushes nur auf ausdrücklichen Auftrag.
- Kein JSON-Laden im Audiothread; ein Bankrefit = neuer Build-/Include-
  Stand (Refit-Vertrag in `docs/DSP.md`).

## Offene Punkte (nicht vergessen)

- A2/A3/A4/A7 (siehe TODO); Preset-Recall des nativen Dropdowns am Dwarf
  verifizieren (OS 1.14 RC4 build 3366, Release-Bindung an 1.13.5.3315).
- THD-Meter-Semantik entscheiden (s. o.) oder Anzeige als Zierwerk
  deklarieren.
- Namenskollision „Eisenkern" (DreamForge-Miniaturen) vor Release prüfen
  und in `docs/QUELLEN.md` dokumentieren.
- REAPER-/Dwarf-Praxistests laufen auf dem anderen Rechner; Messwerte
  immer mit OS-Version labeln.
