# Eisenkern — DSP-Architektur und Modell (Aufbau)

Dieses Dokument wird bei der Code-Trennung aus
[`mod-1175-lv2`](https://github.com/j4yj03/mod-1175-lv2) aufgebaut. Die
Migrationsquelle ist dort `docs/DSP.md`, Teil 3 („Transformatorstufe und
spätere Refits — seit 0.4.0") inklusive Refit-Vertrag, HF-Diskretisierung
und Grenzen.

## Inhalt nach der Trennung (Plan)

1. **Signalpfad:** Host → Off/2x/4x-Interpolation → Drive (pur:
   Skalierung von `source_volts_per_fs`) → lastgekoppeltes Netz
   (Primär-/Sekundärwiderstände, Quelle, Last) → Sättigungskennlinie
   (`law()`: Potenzgesetz p bzw. regularisierter Fröhlich-Kern mit
   C1-Hochfeld-Fortsetzung) → 14 Stop-Zweige (Hysterese) → RL-Relaxation
   → HF-Zweipol → feste `fixed_output_normalization` → Output-Trim →
   Dezimation.
2. **Zustandsmodell:** Flussverkettung `lambda` je Kanal/Richtung,
   14 Stop-Zustände, HF-Historien; Solver: implizite Trapez-Form,
   maximal 40 Newton-/Bisektionsschritte, Prädikator (`px2`),
   Konvergenztoleranz 1e-6 relativ; Sym-Fastpath verallgemeinert
   (`saturation == 0` und `remanence == 0` → linear).
3. **Makro-Vertrag (neu):** `drive`/`saturation`/`bass`/`remanence`/
   `output` als `prepare()`-Größen mit Reglerglättung (GS76-Muster);
   `eisen`/`family`/`exponent` über 2-ms-Blend; Bereiche und
   Klemmen der Expert-Regler; Anker nur bei neutralen Makros.
4. **Refit-Vertrag:** übernommen aus `mod-1175-lv2` — Bank ist
   normativ, `schema_version=1`, Revision/SHA256-Herkunft, Import über
   `tools/transformer_model.py`; kein JSON-Laden im Audiothread; ein
   Refit ändert bestehende Projektklänge (Revision/Herkunft/Tests
   erneuern).
5. **Grenzen:** HF-Diskretisierung (max. Amplitudenfehler 0,3081 dB,
   Phasendifferenz 67,91° gegenüber dem analogen Surrogat), OS Off ist
   kein aliasfreier Betrieb, keine Hardwarekalibrierung.

## Übertragener Kern (2026-10-09, Code-Trennung)

Der Solver wurde aus `mod-1175-lv2` übertragen; die Rechengeometrie ist
unverändert und **bitgleich gegen die GS76-Quelle verifiziert** (siehe
unten). Prüfsummen und Quellen: `docs/QUELLEN.md`, Abschnitt
„Übertragene Dateien".

| Element | GS76 (Quelle) | Eisenkern (hier) |
|---|---|---|
| Numerische Kerne | `src/dsp/GreenStripe.hpp`, Zeilen 15–77 (im Namespace `greenstripe`) | `src/dsp/Numeric.hpp` (Namespace `eisenkern`), Code unverändert |
| Solver | `src/dsp/Transformer.hpp` (ohne eigenen Guard, inkludiert innerhalb des GS76-Namespace) | `src/dsp/Transformer.hpp` (eigener Guard, eigener Namespace, inkludiert `Numeric.hpp` + `TransformerModels.hpp` selbstständig) |
| Bank-Include (generiert) | `src/dsp/TransformerModels.hpp`, Guard `GREEN_STRIPE_TRANSFORMER_MODELS_HPP`, `namespace greenstripe` | `src/dsp/TransformerModels.hpp`, Guard `EISENKERN_TRANSFORMER_MODELS_HPP`, `namespace eisenkern` |
| Bank-Include (EEL2, generiert) | `jsfx/GreenStripe76-Transformers.jsfx-inc`, Funktionen `gs_xf_model`/`gs_xf_thresholds` | `jsfx/Eisenkern-Transformers.jsfx-inc`, Funktionen `ek_xf_model`/`ek_xf_thresholds` |
| Diagnosemakro | `GS76_TRANSFORMER_STATS` | `EISENKERN_TRANSFORMER_STATS` (gleiche Semantik: compile-time-guard, Zähler audioneutral) |
| Bank | `data/transformers.json`, `revision gs76-input-2026-10-05-v1` | `data/transformers.json`, `revision eisenkern-2026-10-09-v1`, `source_revision gs76-input-2026-10-05-v1`, Profildaten bitgleich |

Unverändert übernommen (Rechenpfad): `TransformerCoefficients::prepare()`
(OS-Faktor `1u<<os`, Kehrwerte aus 0.5.2, 00s-Hochfeld-Hoists),
`law()` (Familien 0/1, `saturation_strength==0`-Fastpath),
`TransformerCore::current()/process()` (Prädikator `px2`, Toleranz
1e-6 relativ, 40er-Cap, konvergierte Zustands-Commit ohne erneute
Auswertung), `TransformerStage` (2-ms-Modellblend). Die
`TransformerStage`-Semantik mit `model=0` (Durchreich) ist ein GS76-
Erbe; Eisenkern hat keinen None-Wert — die Anpassung an den
Eisenkern-Signalpfad (Drive → Netz → Normalisierung → Output-Trim)
erfolgt in A2.

**Verifikation der Übertragung (2026-10-09):**

- `tools/verify_transfer.py`: Profildaten, Stop-Schwellen und die
  numerischen Payloads beider generierten Artefakte bitgleich gegen
  `mod-1175-lv2` — PASS.
- C++-Bitvergleich in einer Übersetzungseinheit (beide Namespaces,
  identische Bankvorbereitung bei 48 kHz): 12 vorbereitete
  Koeffizientensätze (3 OS × 4 Profile) feldweise bitidentisch; 12
  Core-Läufe über 48 000 Samples je (Signalprogramm: 997 Hz −12 dBFS,
  20 Hz −12 dBFS mit Burst ×4, DC-Segment, Polaritätswechsel) plus ein
  Stage-Lauf mit Modellwechsel 1→3 — **max Abweichung 0,0e+00, alle
  Samples bitgleich** — PASS.
- Eigenständiger Kompilatcheck des Headers (ohne GS76-Quellen, g++
  `-std=c++11 -O2 -ffp-contract=off`): mit und ohne
  `EISENKERN_TRANSFORMER_STATS` identische Summe (`capped=0`) — PASS.
- `make test` (Bank-/Modellvalidierung, `generate.py --check`) PASS.

Dies ist eine Übertragungsverifikation, **keine** Geräteabnahme; die
eigenständige Beweisführung (Parität C++/EEL2 im neuen Bundle, Anker,
Geräte-CPU) folgt mit A4/A7.

## A1-Verträge (2026-10-09, Revision 0.1.1)

### Port-Dreieck LV2 / JSFX / RPL

LV2-Portreihenfolge (nach den Audio-Ports): 13 Controls in normativer
Ordnung (`eisen`, `drive`, `saturation`, `bass`, `remanence`, `output`,
`load`, `source`, `hf_frequency`, `hf_q`, `family`, `exponent`,
`enabled`), dann der Latenz-Output-Port, dann der angehängte
`oversampling`-Port. Portzahlen: Mono 17 (2 Audio + 13 + 1 + 1),
Stereo 19 (4 Audio + 13 + 1 + 1). Kein GR-/Meter-Output, kein
Stereo-Link, kein Input-Gain.

JSFX-Slider: 1–13 = die Controls in derselben Ordnung, **14 =
Profil-Preset-Selektor**, 15 = Oversampling (angehängt, nimmt an der
Änderungsdetektion und `ek_set` teil — sonst bliebe ein manuell
veränderter Port mit stale Selektor stehen). `ek_apply_preset`
schreibt Slider 1–13 plus 15; der Selektor wird vom Wrapper gesetzt.
RPL-State: 15 Werte in Slider-Reihenfolge (Selektorposition 0) +
`-`-Auffüllung auf 64 Token.

`appended_value()` ist die einzige Quelle für Recall-Werte angehängter
Ports: Oversampling startet bei jedem Recall auf **Off** (Qualitäts-/
CPU-Wahl, nicht Klangwert) — LV2-Presets, JSFX-Presets und RPL-Bänke
können so nicht auseinanderlaufen.

### Port-Gruppen (LV2 pg)

`core` (eisen, drive, saturation, bass, remanence), `level` (output),
`expert` (load, source, hf_frequency, hf_q, family, exponent),
`system` (enabled, oversampling); Audio-Paare als `pg:MonoGroup`/
`pg:StereoGroup` (`audio_in`/`audio_out`) mit `pg:mainInput`/
`pg:mainOutput`. Gruppensymbole sind portfrei (Generator-Assert),
`validate.py` prüft Zuordnung, Definitionsblöcke und Variantentypen.
`enabled` sitzt in Eisenkern bewusst in `system` (GS76 hält es
gruppierungsfrei — bewusste Abweichung nach Parameterplan).

### Expert-Ports: absolute Semantik (Entscheidung A1)

Die sechs Expert-Ports sind **absolute Werte**, Defaults = die
`60s`-Profilwerte (`load` 10 kΩ, `source` 600 Ω, `hf_frequency`
26 kHz, `hf_q` 0,7071, `family` Power, `exponent` 3):

- `load`/`source` sind über alle vier Profile identisch — absolut
  unproblematisch.
- `hf_frequency`/`hf_q`/`family`/`exponent` folgen **nicht** automatisch
  einem Modellwechsel am Paneel; die **Factory-Presets tragen die
  profilgenauen Werte**, ein Preset-Recall reproduziert also exakt die
  Profilcharakteristik. Ein manueller Modellwechsel kombiniert die
  Kurve des neuen Modells mit dem eingestellten Netz — das ist Teil
  des Klangmaterials, nicht ein Defekt.
- `exponent` trägt Bereich 2…13; das 00s-Profil führt `exponent=1`
  nur als Platzhalter (Familie Fröhlich ignoriert ihn) — das
  00s-Preset trägt daher 3 (unwirksam, aber bereichskonform).
- `hf_q`-Portbereich 0,4…1,5 ist bewusst breiter als die
  Bankvalidierung (.51…1): die Bank begrenzt Profile, der Port
  erlaubt Klangmaterial; obere Grenze klemmt Ringing (A2).
- „log“-Taper für `load`/`source`/`hf_frequency` ist GUI-/A2-Sache;
  der LV2-Port ist linear über den Bereich.

### Presets und GUI-Stand

Vier Factory-Presets (60s/80s/00s/Symmetric) mit neutralen Makros
(Drive 0 dB, Saturation/Remanenz 100 %, Bass 1,0, Output 0 dB) —
nur bei dieser Stellung gelten die 1-%-THD-Bankanker. Symmetric
bleibt wegen Profilkonstanten (`saturation_strength=0`,
`hysteresis_enabled=0`) bei jeder Makrostellung linear. Die JSFX-Wrappers
sind metadatenvollständig, importieren aber `Eisenkern-Core.jsfx-inc`/
`Eisenkern-UI.jsfx-inc` erst mit A3 — bis dahin nicht ladbar
(Validierung meldet das als Hinweis, nicht als Fehler).

### modgui (A5, 2026-10-09)

Nacharbeit: Kopfplatte 70 px niedriger, 13 Schlitze erhalten; Profilknopf
links, natives Preset-Dropdown rechts (`mod-role="presets"`, Optionen
aus `effect.presets` per Mustache, vollständiger Recall durch den Host).
Kein zusätzlicher DSP-Port. EISEN-Unterzeile entfernt. Chicken-Head mit
ortsfestem Sockel/Licht und durchgehendem Griff; Rastframes 0/21/43/64
zeigen auf −135°/−45°/+45°/+135°. Bügel als eigene SVG-Chromrohre mit
leichten Außenbögen in Frontansicht. Geräte-Recall noch zu prüfen.

Das Panel baut das `transformer-front.png`-Design in HTML/CSS nach
(Amp-Head/Variac; Elementkarte in `modgui/assets/README.md`): schmalere
Kopfplatte zwischen sichtbaren Tragebügeln, Grillschlitze und der
EISEN-Wähler als großer gestufter Film-Drehknopf mit den vier Profilnamen
an den Rastpositionen; Basisreihe mit vorbereitetem THD-Messwerk, fünf
Film-Knobs, Bypass-Kippschalter mit Kontrolllampe. Aktive
Steuerelemente sind nur die sechs Panel-Regler; `modgui.ttl` trägt
stylesheet/screenshot/thumbnail, kein JavaScript (nichts zu monitoren).
CSS ist statisch (`modgui/eisenkern.css`), Icons generiert
(`tools/generate.py`), Screenshots/Thumbnails entwicklungsseitig via
`tools/make_assets.py` gerendert (kein Dwarf-Screenshot).

Die THD-Anzeige ist **vorbereitet, aber noch nicht live**: Face/Nadel/Nabe
stammen als übertragene Assets aus GS76, das Face ist reproduzierbar über
`tools/make_thd_meter.py` auf `THD / %` umbeschriftet. Ein Messwert wird
erst angebunden, wenn die Semantik festgelegt ist. Breitband-THD ist bei
beliebigem Musikmaterial ohne definierte Grundfrequenz und Zeitfenster
nicht eindeutig; außerdem verbietet der aktuelle Portvertrag einen
Meter-Port. Für eine Live-Anzeige wären Messdefinition, DSP-/UI-Port und
beide Varianten zu versionieren.

Die Produktbeschriftung lautet neutral **Transformer**. Die übertragene
Bank stammt weiterhin aus einer Eingangstransformator-Referenz. Ein
Ausgangstransformator würde u. a. anderes Übersetzungsverhältnis,
Quell-/Lastnetz, Leistungs-/Kernauslegung und ggf. DC-Vormagnetisierung
erfordern; die neutrale Plugin-Rolle macht aus der Bank daher nicht
automatisch ein Ausgangstrafo-Modell.

### Nachträge (2026-10-09, Revision 0.1.2/0.1.3, Benutzeraufträge)

- **Profil-Wähler heißt `eisen` (0.1.2):** der bisherige `model`-Port
  wurde in Symbol und Anzeige zu **`eisen`** umbenannt („Eisen" wählt
  das Transformatorprofil). Semantik unverändert; Indizes, Bereiche,
  Labels und Presetwerte blieben gleich — vor jedem Release ist das
  portvertragsfrei, die Umbenennung ist hier Benutzerauftrag.
  Betroffen: TTL, JSFX slider1, RPL-State, GUI-Select, Presetschlüssel.
- **Presetnamen/Beschreibungen englisch (0.1.3):** die vier Factory-
  Presets heißen **01 Warm Iron** (60s), **02 Tight Coil** (80s),
  **03 Open Core** (00s), **04 Linear Reference** (Symmetric); die
  `note`-Felder sind englisch, das generierte `docs/PRESETS.md` damit
  durchgängig englisch (Produktdaten). Die Projektdokumentation bleibt
  deutsch (AGENTS); die Profilnamen 60s/80s/00s/Symmetric bleiben als
  Bankidentität erhalten.
- **Asset-Dokumentation:** `lv2/eisenkern.lv2/modgui/assets/README.md`
  beschreibt `transformer-front.png` elementweise mit der jeweiligen
  Vorlage (Mini-Amp-Head-/Variac-Archetypen); Herkunft und Abgrenzung
  in `docs/QUELLEN.md`.

## Parameter-Analyse (2026-10-08, Grundlage der Reglerwahl)

Befunde aus dem Quellcode (`src/dsp/Transformer.hpp` in `mod-1175-lv2`)
und der Bank `data/transformers.json` — sie begründen, welche Parameter
als Regler taugen und welche nicht:

**Kennlinie `law()` — zwei Familien:**

- **Familie 0 (Potenzgesetz, 60s p=3 / 80s p=5 / Sym p=3):**
  `i = (λ/Lm)·(1 + s·u^(p−1))`, Steigung
  `(1 + p·s·u^(p−1))/Lm` mit `u = |λ|/flux_scale_vs`. Der `exponent`
  läuft in einer `(unsigned)`-Schleife `exponent−1`-fach — er ist
  **ganzzahlig** (Regler: Integer 2…13, nicht kontinuierlich). `p=1`
  entartet zu `u^0` = konstanter Zusatzstrom, deshalb Untergrenze 2.
- **Familie 1 (regularisierter Fröhlich, 00s):**
  `i = (λ/Lm)·(1 + s·u/(1−u))` für `u < 0,98`, oberhalb C1-stetige
  Hochfeld-Fortsetzung (0.5.2-Hoists `hf_knee/fk/sk/target/width`).
  **`exponent` ist hier unwirksam** (00s trägt `exponent=1` als
  Platzhalter) — ein Exponent-Regler wäre auf Fröhlich-Profilen
  wirkungslos.
- **Symmetric:** `hysteresis_enabled = 0` und `saturation_strength = 0`
  sind normative Profilkonstanten; `law()` kehrt direkt
  `x·inv_lm_h` zurück. Daraus der verallgemeinerte Fastpath: jedes
  Profil mit Makro `saturation == 0` **und** `remanence == 0` ist
  linear.

**Linearitäten — warum Makro-Skalierung sauber ist:**

- Die 14 Stop-Gewichte sind **linear** in
  `hysteresis_stiffness_a_per_vs`:
  `weights[j] = hysteresis_enabled · stiffness · seriesExp(hysteresis_slope ·
  log(threshold_j/1mV))`; `memoryBound` skaliert mit. Remanenz-Makro =
  ein Multiplikator auf stiffness, Stop-Netz bleibt konsistent.
- Alle vier Profile haben **dasselbe** Verhältnis
  `relax_l_h / lm_h = 2,704` (deshalb ist `relax_frequency_hz`
  profilübergreifend identisch 0,2657 Hz). Bass-Makro skaliert beide
  proportional — die Netztopologie bleibt erhalten.

**Pegelvertrag (feste Parameter):**

- `source_volts_per_fs = 14,438 V` je Full Scale: 0 dBFS → 14,44 V an
  der Quelle; der Fit-Anker „−18 dBFS Peak → ≈ +4 dBu Primärpegel
  (1 kHz, Referenzbeschaltung)" hängt daran. Skalierung = „Drive pur":
  Pegel **und** Sättigung steigen gemeinsam (Benutzerentscheid).
- `fixed_output_normalization` = 1,36122…1,36124 über alle Profile —
  Pegel-Identität, kein Klanganteil; als Regler wäre er ein
  redundanter Linear-Gain (Output-Trim existiert).

**Expert-Regler-Einordnung:**

- `hf_q`: Q-Faktor des HF-Zweipols (0,707 Butterworth bei 60s/80s,
  0,663 bei 00s) — Resonanzüberhöhung vor der HF-Kante; kein
  Solver-Risiko (getrennter Zweipol), obere Grenze klemmen (Ringing).
- `load`/`source`: echte Netzgrößen — verändern Kopplung und
  Sättigungsgrad physikalisch, klanglich lohnend.
- `family`/`exponent`: als Expert-Regler ausdrücklich gewollte
  „ungeprüfte Kennlinien als Klangmaterial"; Bedingungen: Wechsel über
  den 2-ms-Modellblend (nicht samplegeglättet), Solver-Bench der
  Extremecken, Extremtests ±256 FS, Anker nur bei neutralen Makros.

## Sym-DC-Pumpen (zurückgestellt, 2026-10-09)

~~Offene Blocker vor dem ersten Signalimport:~~

~~**Sym-DC-Pumpen:** akkumulierender Zustand unter DC
(−0,058 → −0,165 FS in der GS76-Diskriminierungsserie,
MESSERGEBNISSE 12.3 dort). Verdacht: Integrator-/Stop-Zustandsdrift
im Solver. Befund und ggf. Fix zuerst dokumentieren — Eisenkern erbt
den Solver unverändert sonst mit dem Defekt.~~

**Benutzerentscheidung 2026-10-09:** die Sym-DC-Pumpen werden
zunächst **ignoriert** — möglicherweise entfällt das Symmetric-Modell
in Eisenkern ganz (Entscheidung offen). Konsequenzen:

- Der Solver wurde unverändert übertragen; das Verhalten ist bekannt
  und in der GS76-Messhistorie dokumentiert (MESSERGEBNISSE 12.3 dort).
- Die Bank enthält Symmetric vorerst weiter (4 Profile, stabile
  Reihenfolge im Validator); ob es Factory-Preset wird, entscheidet
  sich vor A5/A7. Falls es entfällt: Bankrevision erneuern,
  Profilordnung im Validator anpassen, Presetplan und Doku anpassen.
- Kein Blocker für die Code-Trennung oder A1–A3.
