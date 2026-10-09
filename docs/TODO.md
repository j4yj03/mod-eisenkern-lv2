# Eisenkern — TODO

Plan-Stand: 2026-10-09 (Beschlüsse aus der Planungs-Session im
Geschwisterprojekt `mod-1175-lv2` übernommen; dieses Repo ist das
eigenständige Plugin-Ziel).

## Offen — Grundgerüst und Trennung (Startblock)

- [x] **Grundgerüst angelegt (2026-10-08):** Verzeichnisstruktur
  (`data/`, `docs/`, `jsfx/`, `lv2/eisenkern.lv2/modgui/assets/`,
  `src/dsp/`, `tests/`, `tools/`), `.gitignore`, `LICENSE` (MIT),
  `README.md`, `AGENTS.md`, Dokument-Stubs; Designbasis-Asset
  `transformer-front.png` aus `mod-1175-lv2` kopiert; **REAPER-Testbench
  aufgesetzt** (`reaper/testbench/`: `testbench.rpp` mit der
  GS76-Renderkonvention `$datetime\$region{1}\matrix-$regionname-$datetime`,
  48 kHz, drei Tracks Probe-Player/Referenz/Eisenkern — FX-Kette kommt
  mit A3; `README.md` mit verbindlicher Render-Disziplin inkl.
  no_fx-Negativkontrolle zuerst; `Probes/README.md` mit Manifest-Regeln).
- [x] **Code-Trennung aus `../mod-1175-lv2` (2026-10-09, sauber,
  bitgleich verifiziert):**
  1. `src/dsp/Transformer.hpp` + numerische Kerne übertragen —
     Namespace `eisenkern`, eigener Header-Guard, `Numeric.hpp`
     (Helferblock aus `GreenStripe.hpp`), Diagnosemakro
     `EISENKERN_TRANSFORMER_STATS`; Rechengeometrie unverändert.
  2. Bank `data/transformers.json` übertragen — **Herkunftsmagnet
     erhalten**: `schema_version=1`, `source_revision
     gs76-input-2026-10-05-v1`, `source_sha256 d5a19f41…524a6`,
     `source_fit_sha256 4408c92b…6db91`; eigene Revision
     **`eisenkern-2026-10-09-v1`** vergeben; Profildaten bitgleich
     (Vollwerte und Datei-SHA256 in `docs/QUELLEN.md`).
  3. Offline-Fit-Referenzen: Werkzeuge bleiben in `mod-1175-lv2`
     (`docs/transformer/offline_fit/`); hier nur SHA256 + Zeiger
     (QUELLEN.md), nichts dupliziert.
  4. Generator als **Einfach-Ziel** aufgebaut: `tools/transformer_model.py`
     (Validator + Erzeugung, ohne Fit-Import), `tools/generate.py`
     (`--check`), `tools/validate.py` (Bank + model.json), `Makefile`
     (`check-generated`, `test`); generiert
     `src/dsp/TransformerModels.hpp` und
     `jsfx/Eisenkern-Transformers.jsfx-inc` (`ek_xf_*`-Namen).
  5. Modellkonstanten: `data/model.json` **0.1.0** — nur
     Solver-/Gerätekonstanten (`oversampling`, `default_oversampling`,
     Latenzrahmen, Bankverweis); Kompressorkonstanten bewusst nicht
     übernommen.
  **Verifikation:** `tools/verify_transfer.py` PASS (Bank + generierte
  Konstanten bitgleich gegen GS76); C++-Bitvergleich beider Namespaces
  in einer TU — 12 Koeffizientensätze + 13 Core-/Stage-Läufe über
  48 000 Samples (Burst/DC/Polarität) **max 0,0e+00**; eigenständiger
  Kompilatcheck mit/ohne Stats-Makro PASS; `make test` PASS. Details:
  `docs/DSP.md`, Abschnitt „Übertragener Kern".
- [x] **A1 Generator + Plugin-Metadaten (2026-10-09, Revision 0.1.3):**
  `data/parameters.json` (14 Controls in LV2-Ordnung), `data/port_groups.json`
  (core/level/expert/system + Audio-Gruppen), `data/presets.json` (4
  Factory-Profile, neutrale Makros, profilgenaue Expert-Werte). Der
  Generator erzeugt 15 Artefakte (TTL-Satz, presets, modgui.ttl,
  minimale Icon-Templates, JSFX-Wrappers, Presets-Include, RPL-Bänke,
  PRESETS.md); `validate.py` prüft Portzahlen (Mono 17/Stereo 19),
  Gruppenzuordnung/Disjunktion, Presetsemantik (Recall→Off), TTL-Struktur;
  Makefile-Buildgerüst meldet Block A2 bis der Wrapper existiert. Details
  und Verträge: `docs/DSP.md`, Abschnitt „A1-Verträge". **Benutzer-
  aufträge im Block:** Profil-Wähler `model` → **`eisen`** umbenannt
  (Semantik/Indizes unverändert, 0.1.2); Presets englisch benannt/
  beschrieben — 01 Warm Iron / 02 Tight Coil / 03 Open Core /
  04 Linear Reference (0.1.3); `assets/README.md` beschreibt
  transformer-front.png elementweise mit Vorlagenbezug. **Offen:**
  JSFX-Wrappers importieren Core/UI-Includes (A3/A5) — bis dahin
  Metadaten komplett, aber nicht ladbar; rdflib-Vollprüfung Testrechner.
- [x] **Werkzeuge aus `../mod-1175-lv2` übernommen (2026-10-09, nur
  benötigte):** `tools/gui_preview.py` (HTML-Vorschau, Pfade/CSS auf
  `eisenkern` umgestellt), `tools/make_assets.py` (Screenshot-/Thumbnail-
  Renderer, Playwright/Chromium lokal vorhanden), `tools/check_abi.py`
  (projektneutral, unverändert), `tools/build_dwarf.sh` (MPB-Crossbuild,
  Bundle-Namen `eisenkern.lv2`/`eisenkern.so`), `tools/package.py`
  (Paketierung, nur hier existierende Dokumente referenziert). Verifikation:
  Syntax/Import-Checks PASS. **Nicht** übernommen: Mess-/Gerätewerkzeuge
  (Laufwerk auf dem Testrechner), Offline-Fit, Probe-/Asset-Generatoren.
- [ ] ~~**Sym-DC-Pumpen klären (Blocker):**~~ *(zurückgestellt,
  Benutzerentscheidung 2026-10-09 — evtl. entfällt das Symmetric-Modell;
  siehe Risiken und `docs/DSP.md`.)*

## Offen — Eisenkern bauen (Block A, 3–4 Sitzungen)

- [x] **A1 Generator + Bank:** erledigt — siehe Startblock oben
  (Generator Einfach-Ziel, Bank in der Code-Trennung übertragen,
  Plugin-Metadaten + Bundle-Satz generiert, Revision 0.1.1).
- [ ] **A2 DSP-Kern:** Signalpfad Host → OS → Drive → gekoppeltes Netz
  → HF-Zweipol → feste Normalisierung → Output → Dezimation; Makros in
  `prepare()`; Fastpath verallgemeinert (`saturation == 0` **und**
  `remanence == 0` → linear für jedes Profil); Familien-/Exponent-Wechsel
  über 2-ms-Blend; C++11, kein `-ffast-math`, `-ffp-contract=off`.
- [ ] **A3 JSFX-Standalone:** EEL2-Solver (Includes wie GS76:
  Core/Model/Numeric/TransformerCore/Transformers/Presets/UI),
  Slider-/State-Mapping, PDC (`pdc_delay`, `pdc_bot_ch=0`,
  `pdc_top_ch=2` bei OS-Wechsel), EEL2-Caveats (`===` für gleichartige
  Zweige, geordnete NaN-Vergleichsfunktion, keine negativen
  Literale/Klammer nach `?`).
- [ ] **A4 Tests:** Parität C++/EEL2 ab Tag 1 (Erwartungen aus dem
  Artefakt, keine hartkodierten Zahlen); Solver-Corner (p=13 ×
  Saturation 150 %), Extremtests ±256 FS, Blockinvarianz, OS-Wechsel,
  Modell-/Familienblend, Makro-Sweeps offline (A/B, kein NaN/Inf,
  Konvergenz); 20-Hz-Pegelreihe gegen die Bankanker — **Anker gelten
  nur bei neutralen Makros**; Testprobes können aus
  `../mod-1175-lv2/tools/make_probes.py` abgeleitet werden,
  1k.2-Kanziffern (MESSERGEBNISSE 12 dort) als Referenz.
- [x] **A5 GUI (2026-10-09):** modgui nach dem `transformer-front.png`-
  Design (HTML/CSS nach dem GS76-Muster; `/resources/…{{{ns}}}`-Form):
  silbernes Chassis mit sichtbaren Tragebügeln/Füßen, schmalere lila
  Kopfplatte mit 13 Grillschlitzen, EISEN-Wähler als großer gestufter
  Film-Drehknopf; Profilnamen stehen nur an den vier Rastpositionen,
  keine umlaufende Skala. Basisreihe mit vorbereitetem THD-Messwerk
  (GS76-Face/Nadel/Nabe übernommen, `tools/make_thd_meter.py`; noch
  statisch — Messdefinition/Portvertrag offen), fünf Film-Knobs mit
  Min/Max-Beschriftung und Wertauffeld, Powerfeld (Bypass-Kippschalter +
  Kontrolllampe; roter Ziertaster entfernt), Fußleiste mit Version,
  Drag-Ring + Fußleisten-
  Drag wie GS76. Nur die 6 Panel-Regler sind aktiv; Expert in den
  Settings. Dateien: `modgui/eisenkern.css` (statisch), generierte
  `icon-{mono,stereo}.html`, `modgui.ttl` mit stylesheet/screenshot/
  thumbnail; Screenshots/Thumbnails via `tools/make_assets.py`
  (Playwright/Chromium lokal, Systembibliotheken unter
  `/tmp/opencode/chrome-libs`). Port-Gruppen unverändert aus A1
  (MOD 1.14 grouped controls). **Kein Revisions-Bump** (nur `lv2/` +
  `tools/`).
- [ ] **THD-Meter semantisch entscheiden:** für Live-Anzeige Grundfrequenz-
  Erkennung/Messfenster/Skala definieren und den verbindlichen Vertrag
  „kein Meter-Port" bewusst versionieren; bis dahin statische vorbereitete
  Anzeige, nicht als Messwert ausgeben.
- [ ] **A6 Doku:** `docs/DSP.md` ausbauen (Laufzeitmodell, Refit-Vertrag,
  Makro-Vertrag — Migrationsquelle: `mod-1175-lv2/docs/DSP.md` §11),
  `docs/QUELLEN.md` vervollständigen, `docs/MESSTECHNIK.md` (Testplan,
  Messplätze, Scarlett-Workflow kann später übernommen werden),
  README/PROJEKT fortschreiben.
- [ ] **A7 Build/Abnahme:** Cross-Build aarch64 (moddwarf-new-MPB,
  Symbolfloor); CPU am Gerät (1.14 RC4, mit OS-Build labeln); nur
  Transformator ist billiger als GS76, 4x OS multipliziert weiterhin;
  Extremecken-CPU (p=13 × 150 %, 4x OS) messen, bevor Reglerbereiche
  eingefroren werden; REAPER-Verifikation (PDC, OS-Wechsel, Presets)
  auf dem Testrechner.

## Offen — Block B: Transformator aus Green Stripe 76 entfernen (in `../mod-1175-lv2`, 2 Sitzungen, GS76 → 0.6.0)

- [ ] **B1 Port-Entfernung (Interface-Bruch, begründete Versionierung):**
  `transformer`-Port + Stufe + `TransformerModels.hpp`/
  `GreenStripe76-Transformers.jsfx-inc` + Bankreferenz aus GS76
  entfernen; `gr_db`-Index verschiebt sich; Hosts ignorieren das
  `transformer`-Symbol in alten States; Version **0.6.0**.
- [ ] **B2 Presets:** 6 GS76-Presets verlieren ihre Färbung (11/12→60s,
  13/19/24→80s, 20→00s) — Preset-Audit neu; „08 Vocal Transformer"
  behält Nummer/URI, Name mit Fußnote; Klangänderung ist
  Benutzerauftrag (2026-10-08).
- [ ] **B3 Folgearbeiten:** Port-Gruppen schrumpfen, CPU-Matrix am
  1.14-Gerät neu (GS76 wird deutlich leichter), JSFX-Selektor/RPL ohne
  Transformator, Testreduktion.
- [ ] **B4 Doku dort:** DSP.md §11 verweist dann auf dieses Repo;
  AGENTS „Verbindlicher Umfang" nur mit Benutzerfreigabe anpassen.

- [x] **GUI-Nacharbeit: kompakte Kopfplatte (2026-10-09):** 70 px
  niedriger, Lüftungsschlitze erhalten; überarbeiteter Chicken-Head mit
  vollständigem Sockel und durchgehendem Griff, keine EISEN-Unterzeile.
  SVG-Chrombügel in Frontansicht mit leichter Außenwölbung.
  Preset-Dropdown über MODs `mod-role="presets"` und `effect.presets`;
  Browsergeometrie und vier Raststellungen für Mono/Stereo geprüft.
- [ ] **Preset-Dropdown am Dwarf prüfen:** Factory- und Host-User-Presets,
  vollständiger Recall inklusive Expert-Werten und Oversampling Off;
  Teststand OS 1.14 RC4 build 3366, Release-Verifikation gesondert.

## Risiken / offene Punkte

- **Sym-DC-Pumpen: zurückgestellt (Benutzer 2026-10-09)** — evtl.
  entfällt das Symmetric-Modell in Eisenkern ganz; bis dahin kein
  Blocker. Der Solver wurde unverändert übertragen (Verhalten bekannt,
  GS76-MESSERGEBNISSE 12.3); falls Symmetric entfällt: Bankrevision
  erneuern, Profilordnung/Presets/Doku anpassen.
- Generator-Erstaufbau (A1) ist der unbekannteste Posten —
  kleinstmögliche erste Version (Model + Output + OS) end-to-end, dann
  Makros.
- CPU der Extremecken am A35 vor dem Regler-Freeze messen, nicht
  theoretisieren.
- Namenskollision „Eisenkern" (DreamForge-Miniaturen) vor Release
  prüfen und dokumentieren.
- Keine Commits/Pushes/Veröffentlichung ohne ausdrücklichen Auftrag.
- Revisionszähler: dritte Stelle der `version` in `data/model.json`
  (Start 0.1.0); „ein Arbeitsblock = eine Revision".

## Erledigt

- [x] Grundgerüst mit Verzeichnissen, README, AGENTS, Dokument-Stubs und
  Design-Asset (2026-10-08).
- [x] Code-Trennung: Solver-Header, Bank (bitgleich), Einfach-Ziel-
  Generator, `model.json` 0.1.0, Übertragungsverifikation (2026-10-09).
- [x] A1: Plugin-Metadaten + Bundle-Satz (TTL/presets/modgui/JSFX-
  Wrappers/RPL), Validierungserweiterung, Buildgerüst; Benutzeraufträge
  `eisen`-Umbenennung, englische Presets, Asset-Doku; Revision 0.1.3
  (2026-10-09).
