# Eisenkern — Quellen und Herkunft

Belege für Modellherkunft, Namensentscheidung und GUI-Vorlage. Das
Geschwisterprojekt [`mod-1175-lv2`](https://github.com/j4yj03/mod-1175-lv2)
(Repositorium „Green Stripe 76") ist die Herkunftsquelle des DSP; dessen
`docs/QUELLEN.md` bleibt die ausführliche Quellenarbeit, hier stehen die
für Eisenkern bindenden Verweise und Prüfsummen.

## Modellbank

- Normative Bank: `data/transformers.json` — `schema_version 1`,
  `revision eisenkern-2026-10-09-v1`, Herkunftsmagnet `source_revision
  gs76-input-2026-10-05-v1` (Übernahmestand aus dem Geschwisterprojekt;
  eine eigene Eisenkern-Revision ist mit der Übernahme vergeben).
- Die Profildaten wurden **bitgleich übertragen** (2026-10-09,
  `tools/verify_transfer.py`: alle Profilfelder, 14 Stop-Schwellen und
  die generierten C++/EEL2-Konstanten identisch gegen `mod-1175-lv2`).
- Quelle des Fits: partieller Datenblatt-Fit gegen die Jensen-JT-11P-1-
  Referenz (Whlock-Kapitel), Offline-Werkzeuge und Profile im
  Geschwisterprojekt unter `docs/transformer/offline_fit/` — bleiben
  dort, werden hier **nicht** dupliziert.
- Prüfsummen der Herkunft (unverändert aus der GS76-Bank):
  - `source_sha256` = `d5a19f41c68df1f27019ad3af0afc450919b37ba9118e82743c7616591b524a6`
  - `source_fit_sha256` = `4408c92bc418ac214d6fe4078794c3e434dd6a3f3bfc294fc6b4977f12a6db91`
- Grenzaussage (übernommen): eigener partieller Gray-Box-Fit (18/20
  zurückgehaltene Intervalle), **keine** Hardwarekalibrierung, keine
  Revisionstreue aus Literatur allein. Die Profile 60s/80s/00s/Symmetric
  sind eigene Klangabstimmungen, keine Bauteilnachbauten.

## Übertragene Dateien (Code-Trennung, 2026-10-09)

SHA256 zum Übernahmezeitpunkt; Änderungen nach der Trennung sind
Eigenentwicklungen dieses Repos und folgen der eigenen Revisionsregel.

| Datei (hier) | Quelle in `mod-1175-lv2` | SHA256 (Übernahmestand) |
|---|---|---|
| `src/dsp/Transformer.hpp` | `src/dsp/Transformer.hpp` | `635f3b178de101472a3fa7a1e815590862c2378af2cb969ffb20757d297bf6a3` |
| `src/dsp/Numeric.hpp` | Helferblock aus `src/dsp/GreenStripe.hpp` (Zeilen 15–77) | `c61c04ce9c383fa7093a2ebe44d9ced783faebb0596094b2dca0f9aaba097622` |
| `data/transformers.json` | `data/transformers.json` (Daten bitgleich; `revision`/`source_revision`/`status` angepasst) | `47f76b7c5b3c735f59de778841bb6555a99d78d293a5ef225b3bdb07003bbd60` |
| `data/model.json` | neu angelegt (0.1.0, Solver-/Gerätekonstanten; seit A1 Revision 0.1.1) | `deea679bc4235bd5b74e48b9069db8facc2618202c77d5eaceaa5a6d1f7b284d` (Übernahmestand 0.1.0) |
| `lv2/eisenkern.lv2/modgui/assets/transformer-front.png` | `lv2/green-stripe-76.lv2/modgui/assets/transformer-front.png` | `b7ac607f42f578b8dec94a99890e273fdf0faf539b1c5f7dc158c5b9e9a893f5` (identisch zur Quelle) |
| `lv2/eisenkern.lv2/modgui/assets/thd-meter-base.png` | `lv2/green-stripe-76.lv2/modgui/assets/vumeter-on.png` | `6f0d63bbf44b7b16e9604576cba2580c2277ee29c6ae7010a5430a16c528765f` (identisch; Ausgangsface für `make_thd_meter.py`) |
| `lv2/eisenkern.lv2/modgui/assets/thd-meter-needle.png` | `lv2/green-stripe-76.lv2/modgui/assets/vumeter-needle.png` | `a326535dadf6334a6cefa9540f05a72d3db7ba6d9cdd630d8c9f92d9aa2a873a` (identisch) |
| `lv2/eisenkern.lv2/modgui/assets/thd-meter-hub.png` | `lv2/green-stripe-76.lv2/modgui/assets/vumeter-hub.png` | `48ca763f7df02e2bccf856fef42246b6069f8530f88a1cb12818315a582f4f10` (identisch) |
| `reaper/testbench/testbench.rpp` | neu aufgesetzt (GS76-Renderkonvention) | `5dd3513dbfc2b1a6d7f391672dc535e816ca387bf95f298c7e20b38bfd5afe9b` |

Die generierten Artefakte (`src/dsp/TransformerModels.hpp`,
`jsfx/Eisenkern-Transformers.jsfx-inc`) stammen aus der hierigen
Einfach-Ziel-Generator-Kette (`tools/generate.py`); ihre numerischen
Payloads sind gegen die GS76-Artefakte bitgleich verifiziert
(`tools/verify_transfer.py`).

## Solver-Herkunft

- Laufzeitmodell: Fluss-Integrator mit impliziter Trapez-Zustandsform,
  monotoner Fröhlich-/Potenzkennlinie, 14 positiv gewichteten
  Stop-Zweigen, RL-Relaxation, HF-Zweipol — dokumentiert in
  `mod-1175-lv2/docs/DSP.md` (Teil 3, „Transformatorstufe und spätere
  Refits"); der Inhalt wandert bei der Trennung in `docs/DSP.md` hier.
- Validierungshistorie (bitgleiche C++/EEL2-Parität, Geräte-CPU-Matrix,
  20-Hz-Anker) liegt in `mod-1175-lv2` (MESSERGEBNISSE, PERFORMANCE,
  MESSTECHNIK) und bleibt dort als Provenanz; Eisenkern fährt die
  Nachweise nach der Übertragung eigenständig neu.

## Name „Eisenkern"

- Deutsch für „Iron Core" (magnetischer Kern) — neutraler Fachbegriff,
  keine Hardwarebehauptung.
- **Kollisionsprüfung offen:** „Eisenkern" ist zugleich eine
  Wargame-Miniaturlinie (DreamForge Games, „Eisenkern Stormtroopers").
  Anderer Markt, aber vor Release prüfen (Shops/Plugin-Datenbanken) und
  Ergebnis hier dokumentieren.

## GUI-Vorlage

- `lv2/eisenkern.lv2/modgui/assets/transformer-front.png` (800×350,
  transparent): Nano-Head-/Variac-Optik, gezeichnet von
  `../mod-1175-lv2/tools/make_transformer_asset.py` (dort gepflegt).
  **Elementweise Beschreibung mit Vorlagenbezug:**
  `lv2/eisenkern.lv2/modgui/assets/README.md` — Mischung aus
  Mini-Amp-Head- und Variac-Archetypen (allgemeine Gerätearten, keine
  konkreten Produkte). Optische Inspirationen (Kleinamp-/Variac-
  Referenzen des Benutzers) sind im Geschwisterprojekt dokumentiert.
  **Keine** Fremd-Branding-Elemente übernehmen; Beschriftung erst in
  der HTML/CSS-Fassung.
- Das THD-Meterface wird aus dem unveränderten übertragenen GS76-Face
  `thd-meter-base.png` mit `tools/make_thd_meter.py` erzeugt; nur die
  mittlere Beschriftung wird durch `THD / %` ersetzt. Nadel und Nabe
  bleiben bitidentische Ebenen. Die aktuelle GUI hält die Nadel statisch;
  dies ist keine behauptete Messung.
