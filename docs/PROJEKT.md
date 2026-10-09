# Eisenkern — Projektstand und Übergabe

## Zusammenfassung (Stand 2026-10-09)

- **Code-Trennung abgeschlossen (2026-10-09):** Solver-Header
  (`src/dsp/Transformer.hpp` + `Numeric.hpp`), Transformatorbank und
  Einfach-Ziel-Generator (`tools/transformer_model.py`, `generate.py`,
  `validate.py`, `Makefile`) sind übertragen; `data/model.json`
  startet bei **0.1.0**. Die Übertragung ist **bitgleich verifiziert**:
  Bank + generierte Konstanten gegen `mod-1175-lv2`
  (`tools/verify_transfer.py` PASS), C++-Bitvergleich beider
  Namespaces (12 Koeffizientensätze, 13 Core-/Stage-Läufe, max
  0,0e+00), eigenständiger Kompilatcheck mit/ohne Stats-Makro PASS,
  `make test` PASS. Details: `docs/DSP.md` („Übertragener Kern"),
  `docs/QUELLEN.md` (SHA256-Tabelle).
- **Sym-DC-Pumpen zurückgestellt (Benutzer 2026-10-09):** evtl.
  entfällt das Symmetric-Modell in Eisenkern; die Bank trägt vorerst
  weiter 4 Profile. Kein Blocker für A1–A3.
- **Grundgerüst angelegt:** eigenständiges Repository für das
  Transformator-Plugin **Eisenkern** (LV2 Mono/Stereo + JSFX). Struktur,
  `README.md`, `AGENTS.md` und Dokument-Stubs stehen; das
  Design-Asset `transformer-front.png` ist aus dem Geschwisterprojekt
  übernommen.
- **Beschlüsse (2026-10-08, aus der Planung in `mod-1175-lv2`):**
  Name Eisenkern; Bank als eigene übertragene Quelle (Herkunftsmagnet
  erhalten); Drive pur auf `source_volts_per_fs` mit eigenem
  Output-Regler; kein None-Wert (Bypass macht der Host); 4 Modelle als
  Factory-Presets, User-Presets über den Host; Expert-Regler nur in den
  Settings (Port-Gruppe „Expert"); Reihenfolge: erst Eisenkern (Block A),
  dann Entfernung der Transformatorstufe aus Green Stripe 76 (Block B,
  dort Version 0.6.0).
- **A1 abgeschlossen (2026-10-09, Revision 0.1.3):** normative
  `parameters.json`/`port_groups.json`/`presets.json`, Generator erzeugt
  den vollständigen Bundle-Satz (manifest, Mono/Stereo-TTL mit Port-
  Gruppen, presets.ttl, modgui.ttl, minimale Icon-Templates,
  JSFX-Wrappers + Presets-Include + RPL-Bänke, PRESETS.md; 15
  Artefakte). `validate.py` prüft Portzahlen (Mono 17/Stereo 19),
  Gruppen, Presetsemantik, TTL-Struktur; Makefile-Buildgerüst meldet
  A2, bis der LV2-Wrapper existiert. JSFX-Wrappers sind metadaten-
  vollständig, aber erst mit A3/A5 ladbar (Core-/UI-Includes fehlen
  bewusst). Verträge: `docs/DSP.md`, Abschnitt „A1-Verträge".
  **Benutzeraufträge 2026-10-09:** Profil-Wähler heißt `eisen`
  (Umbenennung von `model`, Indizes unverändert, 0.1.2); Presets
  englisch benannt/beschrieben (Warm Iron / Tight Coil / Open Core /
  Linear Reference, 0.1.3); das Design-Asset ist elementweise
  dokumentiert (`lv2/eisenkern.lv2/modgui/assets/README.md`).
- **Werkzeuge übernommen (2026-10-09):** die für Bau/Paketierung/GUI-
  Render benötigten Skripte wurden aus `../mod-1175-lv2/tools` kopiert
  und auf Eisenkern angepasst (`gui_preview.py`, `make_assets.py`,
  `check_abi.py`, `build_dwarf.sh`, `package.py`); Mess-/Gerätewerkzeuge
  bleiben im Geschwisterprojekt. Playwright/Chromium/Pillow sind auf
  diesem Rechner verfügbar; die MPB-Toolchain liegt nicht hier —
  `build_dwarf.sh` läuft wie bei GS76 **im** MOD Plugin Builder
  (moddwarf-new).
- **A5 modgui abgeschlossen (2026-10-09, keine Revision — nur `lv2/` +
  `tools/`):** Panel nach dem `transformer-front.png`-Design in HTML/CSS
  (Amp-Head/Variac), generierte Icon-Templates + statisches
  `eisenkern.css`, `modgui.ttl` mit stylesheet/screenshot/thumbnail,
  Screenshots/Thumbnails lokal gerendert (`tools/make_assets.py`,
  Playwright/Chromium; fehlende Systembibliotheken werden unter
  `/tmp/opencode/chrome-libs` nachgeladen). `make check-generated` +
  `validate.py` PASS. Details: `docs/DSP.md`, Abschnitt „modgui (A5)".
- **A5-Nacharbeit (2026-10-09):** Tragebügel sichtbar gemacht und lila
  Platte eingerückt; oberen Profil-Schriftzug, Variac-Skala und roten
  Ziertaster entfernt; EISEN ist ein großer **Chicken-Head-Drehknopf**
  als eigenes 65-Frame-Filmstreifen-Asset (`tools/make_eisen_knob.py`,
  Frames 0/21/43/64 ↔ −135°/−46,4°/+46,4°/+135°) — der Zeiger zeigt
  framegenau auf das gewählte Profil; Profilnamen größer ohne Punkte an
  den Rastpositionen; Bügel als U-Rohr in leichter Perspektive
  (vordere/hintere Rohrlage + Brücke + Schattenwurf). Produktbeschriftung
  neutral „Transformer". GS76-Meterassets übernommen und reproduzierbar
  auf `THD / %` umbeschriftet; Anzeige bleibt statisch, bis Messsemantik
  und die nötige Änderung des „kein Meter-Port"-Vertrags entschieden sind.
- **Nächster Schritt:** **A2** — `src/lv2_plugin.cpp` (LV2-C-ABI nach
  GS76-Muster) um die übertragenen Kerne; Signalpfad Host → OS →
  Drive → Netz → HF-Zweipol → Normalisierung → Output → Dezimation;
  Makros in `prepare()`, verallgemeinerter Linear-Fastpath — siehe
  `docs/TODO.md` (Block A).
- **Repository-Status:** Remote
  `https://github.com/j4yj03/mod-eisenkern-lv2.git` konfiguriert;
  Erst-Commit lokal auf `main` (2026-10-09, Benutzerauftrag):
  `a382dcb Eisenkern 0.1.3: Code-Trennung, Generator/Metadaten (A1),
  modgui (A5), Werkzeuge`. **Push ausstehend** — dieser Rechner hat
  keine GitHub-Zugangsdaten (weder SSH-Key noch `gh` noch
  Credential-Helper); Push nach Authentifizierung nachholen. Skill
  `.opencode/skills/audio-coding/SKILL.md` auf Stand 2026-10-09
  erweitert (modgui-Konventionen, Werkzeuge, Render-Pipeline, offene
  Punkte) und mitcommittet.
- **REAPER-Testbench** steht: `reaper/testbench/testbench.rpp`
  (GS76-Renderkonvention `$datetime\$region{1}\matrix-$regionname-$datetime`,
  48 kHz, Tracks Probe-Player/Referenz/Eisenkern; FX-Kette folgt mit
  A3) plus verbindliche Render-Disziplin in `reaper/testbench/README.md`
  — no_fx-Negativkontrolle zuerst, Verifikation vor Auswertung,
  verworfene Serien als Provenanz.

### Kompakte Kopfplatte und native Preset-Auswahl (2026-10-09)

- Kopfplatte um 70 px verkürzt, 13 Lüftungsschlitze erhalten.
  Profilknopf links, Preset-Dropdown rechts; „EISEN“-Unterzeile entfernt.
- Chicken-Head neu gezeichnet: flacher, vollständig deckender Sockel,
  durchgehender Griff mit kurzem Heck und Spitze; Licht/Sockel ortsfest.
  Rastframes 0/21/43/64 zeigen exakt auf −135°/−45°/+45°/+135°.
- Eigene SVG-Bügel `carry-handle.svg`: Frontansicht, durchgehendes
  Chromrohr mit Rückbögen oben/unten und leichter Wölbung nach außen.
- Preset-Dropdown nutzt MODs natives `mod-role="presets"` und
  `effect.presets` (Mustache); der Host lädt das gesamte LV2-Preset.
  Lokale Vorschau rendert die vier Factory-Presets aus den normativen Daten.
- Browserprüfung beider Varianten: 13 Schlitze, sechs Control-Widgets,
  vier ausgerichtete Raststellungen, variantengenaue Preset-URIs,
  kein Überlappen von Knopf/Dropdown PASS. Screenshots neu gerendert.
  Preset-Recall am Dwarf **noch nicht ausgeführt**. Keine Änderung unter
  `src/` oder `jsfx/`, Version bleibt 0.1.3.

## Gerätelandschaft

| Gerät | Stand |
|---|---|
| MOD Dwarf | OS 1.14 RC4 (build 3366), Teststand; Release-Verifikation an 1.13.5.3315 gebunden, bis 1.14 stable ist |
| Testrechner | REAPER- und Dwarf-Praxistests erfolgen auf einem anderen Rechner |

## Übergabe-Notizen

- Dieses Repo wird nach der sauberen Code-Trennung von einem eigenen
  Agent weiterentwickelt; Einstieg immer über `README.md`, `AGENTS.md`
  und `docs/TODO.md`.
- Der Solver ist in `mod-1175-lv2` bitgleich (C++/EEL2) und am Gerät
  validiert; Messhistorie und Messtechnik liegen dort und bleiben als
  Provenanz erhalten. Hier beginnt die Beweisführung neu: Parität,
  Anker, Geräte-CPU nach der Übertragung erneut fahren.
- Bankanker (1-%-THD-Anker −14/−8/−2 dBFS) gelten nur bei neutralen
  Makros; Makro-Bereiche vor dem Freeze am A35 messen.
