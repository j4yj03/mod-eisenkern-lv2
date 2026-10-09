# transformer-front.png — Elemente und Vorlagen

Designbasis für das Eisenkern-modgui (800 × 350 px, transparent,
4× gerendert und auf 800 px heruntergerechnet). Gezeichnet von
`../mod-1175-lv2/tools/make_transformer_asset.py` (dort gepflegt);
die Datei ist byteidentisch zur Quelle (SHA256 `b7ac607f42f578b8…a893f5`,
siehe `docs/QUELLEN.md`). Das Asset trägt bewusst **keine Beschriftung
und kein Fremd-Branding** (GUI-Regel „keine Produktnamen aus
Fremdquellen"); Text ergänzt die HTML/CSS-Fassung (A5).

**Grundidee:** Mischung aus **Mini-Amp-Head** (silbernes Chassis,
gebürstete Frontplatte, Grillschlitze, chrom Tragebügel, Kippschalter
mit LED) und **Variac** (Stelltrafo-Bedienfeld: schwarzes Zifferblatt
mit Skala und rotem Endbereich, Analog-Messwerk, roter Taster,
Buchsen an den Basiskanten). Beides **allgemeine Gerätearchetypen**
als optische Vorlagen — keine konkreten Fremdprodukte, keine
Markenelemente.

## Elemente (Schichtfolge der Komposition)

| # | Element | Ausführung im Asset | Vorlage / Beispiel |
|---|---|---|---|
| 1 | **Chrom-Tragebügel** (2, seitlich, volle Höhe) | Abgerundete Rohre mit Chromprofil (hell–dunkel–hell über die Rohrbreite), dunkle Kontur | Rack-/Tragegriffe kleiner Amp-Heads (seitliche Bügel über Gerätehöhe) |
| 2 | **Silbernes Chassis** (Basisbox + Kopfrahmen) | Zwei abgerundete Rechtecke mit vertikalem Silberverlauf, dunkler Kontur und heller Oberkante | Silbernes, eloxiertes Amp-Head-Chassis |
| 3 | **Gummifüße** (2, unten) | Dunkle abgerundete Balken an den Basisecken | Gummifüße von Kopfgeräten |
| 4 | **Gebürstete Frontplatte** (lila) | Abgerundetes Feld mit Lila-Verlauf plus horizontale Bürstlinien (hell/dunkel im Wechsel) | Gebürstete Frontplatten kleiner Amps (hier lila statt Aluminium) |
| 5 | **Grillschlitze** (13, vertikal, oberer Plattenbereich) | Dunkle, abgerundete Vertikalschlitze in Reihe | Lüftungs-/Grillschlitze von Amp-Heads |
| 6 | **Variac-Zifferblatt** (zentral) | Schwarze Kreisskala, 25 Striche über 240° (lang/kurz im Wechsel), roter Endbogen (letzte 20°) | Stelltrafo-(Variac-)Zifferblatt mit Gefahren-Endbereich |
| 7 | **Mittelknopf mit Zeiger** (Stellung ≈ 10 Uhr) | Dunkler Knopf, heller Zeiger, metallische Nabe | Variac-Drehsteller |
| 8 | **Plattenschrauben** (4: 2 oben flankierend, 2 unten) | Chromköpfe mit Kreuzschlitz | Frontplatten-Kreuzschlitzschrauben (Motiv wie im GS76-Paneel) |
| 9 | **Analog-Messwerk (V-Meter)** auf der Basis | Dunkler Rahmen, cremeweißes Zifferblatt, grüner + roter Bogenbereich, dunkle Nadel (≈ 78°), Glasreflex-Kante | Analoges Volt-/VU-Werk, wie es Variac-Bedienfelder tragen („wie am Variac", Renderer-Kommentar) |
| 10 | **Drei Bedienknöpfe** (schwarz, weißer Zeiger, Winkel 118/95/66°) | Knopfringe mit Glanzbogen | Amp-Panel-Knöpfe |
| 11 | **Beschriftungsleiste** unter den Knöpfen | Dunkle Leiste als Platzhalter | Reserviert für HTML/CSS-Beschriftung (Asset bleibt textfrei) |
| 12 | **Roter Taster** mit Chromring | Chromring, rote runde Fläche, Glanzbogen | Variac-Reset-/Auslösetaster („Variac-Reset-Zitat", Renderer-Kommentar) |
| 13 | **Seitliche Audioanschlüsse** (2, an den Basiskanten) | Chrombuchsen mit dunklem Bohrloch und Glasreflex, seitlich statt frontal | Klinken-/Buchsenfelder, seitlich am Geräterahmen |
| 14 | **Kippschalter + LED** (rechts) | Chromfassung, heller Kipphebel, bernsteinfarbene LED | Netz-Kippschalter mit Kontrollleuchte an Amp-Heads |
| 15 | **Weiche Bodenverschattung** | Unscharfe Ellipse unter dem Gerät | Produktfoto-Standbild (weicher Schattenwurf) |

## Abgrenzung

- Die Referenzen sind **Archetypen** (Gerätetypen), keine konkreten
  Produkte; es gibt keine Logos, Schriftzüge oder kopierten Details.
- Das Asset ist die **Designbasis**; die modgui-Umsetzung (A5, 2026-10-09)
  baut das Panel als HTML/CSS nach diesem Erscheinungsbild
  (`modgui/eisenkern.css`, generierte `icon-{mono,stereo}.html`) und
  ergänzt die Beschriftung.
- In der A5-Nacharbeit wurde die lila Platte zwischen sichtbar
  hervortretenden Tragebügeln eingerückt; die Bügel sind als U-Rohr in
  leichter Perspektive gezeichnet (vordere Rohrlage, hintere dunkle Lage,
  Brücke oben, weicher Schattenwurf). Der EISEN-Wähler ist ein großer
  Chicken-Head-Drehknopf (`eisen-knob.png`); die Profilnamen stehen
  ohne Punkte an den vier Rastpositionen, keine umlaufende Variac-Skala.
  Der rote Ziertaster aus der Vorlage wird in der GUI nicht mehr
  dargestellt.
- Änderungen am Asset laufen über das Renderer-Skript im
  Geschwisterprojekt (eine Quelle, kein Abweichungsduplikat);
  nach einer Änderung Herkunfts-SHA256 hier und in `QUELLEN.md`
  erneuern.

## Weitere Dateien in diesem Verzeichnis

Aktueller Nacharbeitsstand: kompakte Kopfplatte mit nativer MOD-Preset-
Auswahl rechts und Profilknopf links; keine EISEN-Unterzeile.
`carry-handle.svg` ist eine eigene Eisenkern-Zeichnung eines durchgehend
gebogenen Chromrohrs in Frontansicht mit leichter Außenwölbung. Die
frühere CSS-Konstruktion mit parallelen Rohrlagen wurde dadurch ersetzt.
`eisen-knob.png` wird nun mit ortsfestem, vollständig deckendem Sockel
und Licht sowie einem durchgehenden Griff mit Spitze und kurzem Heck
gerendert. Die Rastframes 0/21/43/64 zeigen genau auf
−135°/−45°/+45°/+135° (Zwischenframes stückweise interpoliert).

`aluminium.png`, `toggle.png`, `pilot_on.svg`, `pilot_off.svg` sind
die vom Benutzer bereitgestellten Basis-Assets des GS76-Panels
(seit A5 aktiv im Panel genutzt: Knob-Filmstreifen, Bypass-Kippschalter,
Kontrolllampe; Herkunftsangabe wie
in `mod-1175-lv2/docs/QUELLEN.md`: „Vom Benutzer im Projekt
bereitgestellte Assets — als Vorlagen übernommen, keine zusätzliche
Urheber-/Lizenzherkunft behauptet").

`eisen-knob.png` ist ein **eigenes Eisenkern-Asset** (keine Übernahme):
Chicken-Head-Drehknopf für den EISEN-Wähler, erzeugt von
`tools/make_eisen_knob.py` (deterministisch, Vektor-render in Pillow,
65 Frames je 128×128 im 8320×128-Streifen, MOD-Filmkonvention). Die
ganzzahligen Portwerte 0..3 landen auf den Frames 0/21/43/64 mit
−135°/−45°/+45°/+135°; Zwischenframes interpolieren stückweise. Der Zeiger zeigt damit
auf das gewählte Profil-Label (60s unten links, 80s oben links,
00s oben rechts, Symmetric unten rechts). Nach einer Änderung des
Skripts den Streifen neu erzeugen und die Screenshots neu rendern.

`thd-meter-base.png`, `thd-meter-needle.png` und `thd-meter-hub.png`
stammen byteidentisch aus den GS76-VU-Ebenen; SHA256 und Quellpfade
stehen in `docs/QUELLEN.md`. `tools/make_thd_meter.py` erzeugt daraus
`thd-meter-face.png` mit der Beschriftung `THD / %`. Die Nadel ist bis
zur Festlegung des Messverfahrens statisch; das Bild behauptet keinen
laufenden Messwert.
