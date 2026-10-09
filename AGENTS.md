# Eisenkern — Arbeitsanweisungen

## Einstieg in eine neue Session

1. `README.md`, `docs/TODO.md` und `docs/PROJEKT.md` (Umfang, aktueller
   Stand, Übergabe) sowie `docs/DSP.md` und bei Performancearbeit
   `docs/PERFORMANCE.md` lesen.
2. `git status --short` prüfen; vorhandene Benutzeränderungen erhalten.
3. `docs/MESSTECHNIK.md` für die passenden Prüfungen und Messplätze
   verwenden.
4. Ergebnisse, offene Fragen und nächste Schritte in `docs/PROJEKT.md`
   (Stand) und `docs/TODO.md` aktualisieren. Nicht ausgeführte
   Geräte-/Hörtests niemals als bestanden melden.

## Verbindlicher Umfang

- Eigenständiges Transformator-Plugin, Name **Eisenkern**; Bundle
  `lv2/eisenkern.lv2/`, URIs `https://github.com/j4yj03/mod-eisenkern-lv2#eisenkern-mono`
  bzw. `#eisenkern-stereo`; `mod:brand "GreenStripe"`,
  `mod:label "Eisenkern"`. Der Anzeigename ist ohne Portvertragsrisiko
  änderbar, die URI nicht.
- LV2 Mono und Stereo; **kein** Stereo-Link (Fluss-/Kernzustände sind von
  Natur aus kanalgetrennt). Kein None-Modellwert — Bypass macht der Host.
- Vier Profile (`60s`/`80s`/`00s`/`Symmetric`) als Factory-Presets mit
  neutralen Makros; User-Presets über Host-Mechanik (LV2: Host-Presets;
  JSFX: REAPER-User-Presets neben der Factory-RPL-Bank).
- Panel: `eisen` (Profilwahl 60s/80s/00s/Symmetric), `drive`,
  `saturation`, `bass`, `remanence`, `output`.
  Expert-Regler (`load`, `source`, `hf_frequency`, `hf_q`, `family`,
  `exponent`) nur in den Host-Settings, mit Port-Gruppe „Expert"
  (LV2 pg — MOD OS 1.14 zeigt „Grouped plugin controls").
- Kein Input-Gain-Port (Drive ist die Eingangspegelung), kein Mix,
  kein Meter-Port. Latenz-Port meldet 0/3/4 Frames (Off/2x/4x).
- Zielgerät: MOD Dwarf OS **1.14 RC4 (build 3366)** — Teststand;
  Release-Verifikation bleibt an **1.13.5.3315** gebunden, bis 1.14
  stable ist. aarch64, Cortex-A35, Kernel 6.1.15-rt7-moddwarf,
  PREEMPT_RT; Betrieb bei 48 kHz. Gerätchecks (modgui-JS-Pfad,
  CPU-Matrix, Install-Verifikation) sind OS-gebunden und bei Wechsel
  neu zu fahren; Messwerte immer mit OS-Version labeln.
- REAPER- und Dwarf-Praxistests erfolgen auf einem **anderen Rechner**.

## DSP und Kompatibilität

- Normative Dateien: `data/model.json`, `data/parameters.json`,
  `data/port_groups.json`, **`data/transformers.json`** (übertragene Bank,
  Herkunft siehe `docs/QUELLEN.md`). Der Generator validiert beide
  Engines gemeinsam.
- C++11, LV2-C-ABI, keine GUI-/JUCE-/WebView-Abhängigkeit im DSP.
- `run()`/`@sample`: keine Allokationen, Datei-/Netzzugriffe oder
  unbeschränkten Schleifen. DSP arbeitet intern in double, Audioports
  in float.
- Kein `-ffast-math`; `-ffp-contract=off` für Parität.
- C++ und EEL2 bei DSP-Änderungen **zusammen** aktualisieren und Parität
  testen (echtes Rendern beider Kerne, nicht Textvergleich).
- Makro-Regler (`drive`, `saturation`, `bass`, `remanence`, `output`)
  wirken als `prepare()`-Größen; `eisen`/`family`/`exponent` wechseln
  über den 2-ms-Eingangsblend, nicht samplegeglättet.
- Verallgemeinerter Linear-Fastpath: `saturation == 0` **und**
  `remanence == 0` → linearer Pfad für jedes Profil.
- Die interne Rate umfasst die Transformatorstufe; Resamplerhistorien
  sind je Kanal/Richtung getrennt.
- Feste Parameter (nie als Regler): `source_volts_per_fs` (Pegelvertrag;
  nur via `drive` relativ), `fixed_output_normalization`,
  `stop_thresholds_vs`, `core_conductance_s`, `high_field_l_ratio`,
  `nonlinear_series_resistance_ohm`.
- Keine implizite Auto-Makeup-Funktion; Output ist ein ausdrücklicher
  Trim-Regler.
- EEL2 `==` vergleicht mit Toleranz; für gleichartige DSP-Zweige `===`
  nutzen. NaN-Sanierung nicht über `(x-x)===0` (x86-EEL behandelt
  unordered als gleich). Vorhandene geordnete Vergleichsfunktion
  beibehalten und NaN-Test wiederholen.
- **Bankanker gelten nur bei neutralen Makros** (drive 0 dB,
  Saturation/Remanenz 100 %, Bass 1,0): Makro-Skalierung verschiebt
  THD/GR-Anker bewusst — Änderungen der Anker müssen dokumentiert
  werden, nicht Testgrenzen gelockert.

## Revisionsnummer (verbindlich)

- Die Revisionsnummer ist die **dritte Stelle der Versionsnummer** in
  `data/model.json` (`version`, Start **0.1.0**). Mit **jeder
  Sourcecodeänderung** erhöht sich die dritte Stelle um **+1**; alle
  Änderungen zwischen zwei Nutzereingaben gelten als **eine**
  Sourcecodeänderung (ein Arbeitsblock = eine Revision). Sourcecode-
  änderung heißt: Dateien unter `src/` oder `jsfx/`. Änderungen an
  Werkzeugen (`tools/`), Metadaten, GUI-Assets oder Dokumentation
  zählen nicht.
- Nach dem Bump `tools/generate.py` laufen lassen; die Versionsnummer
  erscheint in der LV2-GUI (Fußzeile) und in der JSFX-GFX.

## Generierung und Validierung

- TTL, JSFX-Wrappers, Presets und GUI-Stücke werden von
  `tools/generate.py` erzeugt; `--check` vergleicht ohne Schreiben.
- `tools/validate.py` prüft Bundle, Portlayout, Port-Gruppen,
  Presetsemantik (Oversampling startet immer auf Off; Rest = Profilwert)
  und Imports. `make check-generated` fasst beide Prüfungen zusammen.
- Portindizes/-symbole/URIs nicht ohne begründete Versionierung ändern.
- Kein JSON wird vom Audiothread geladen; ein Refit ist ein neuer
  Build-/Include-Stand. Bestehende Projekte speichern Profilnummern —
  ein Bankrefit ändert bestehende Projektklänge; Revision/Herkunft und
  Tests erneuern (`docs/DSP.md`, Refit-Vertrag).

## Quellen und Provenanz

- Modellbank und Solver stammen aus dem Geschwisterprojekt
  `../mod-1175-lv2` (Green Stripe 76); die Offline-Fit-Werkzeuge und
  -Profile bleiben dort (`docs/transformer/offline_fit/`). SHA256 der
  Quellen in `docs/QUELLEN.md` sichern.
- Der Algorithmus ist ein reduziertes Gray-Box-Modell mit provisorischen
  Kennlinien; **keine** Hardwarekalibrierung, keine Revisionstreue aus
  Literatur allein. Namenskollision „Eisenkern" (DreamForge-Wargame-
  Miniaturen) vor Release prüfen und in QUELLEN dokumentieren.
- GUI-Optik basiert auf `lv2/eisenkern.lv2/modgui/assets/transformer-front.png`
  (aus `mod-1175-lv2` übernommen); keine Fremd-Branding-Elemente ins
  Asset oder die GUI.

## Build und Übergabe

- Native Build: `make`; Offline-Prüfung: `make test`.
- Dwarf: bevorzugt offizielle MPB-Toolchain `moddwarf-new`; andere
  Cross-Compiler-Artefakte eindeutig als solche dokumentieren;
  Architektur alleine ist kein ABI-/Gerätetest.
- Tests auf Signalverhalten, Blockinvarianz, Bypass, Solver-Konvergenz
  (Extremregler p=13 × Saturation 150 %) und Parität richten, nicht auf
  bloße Implementierungsduplikation.
- Keine Commits/Pushes/Veröffentlichung ohne ausdrücklichen Auftrag.
- Keine Unteragenten starten, sofern der aktuelle Benutzer dies nicht
  verlangt.
- Dokumentation deutsch, UTF-8; technische Symbole und Code englisch.
