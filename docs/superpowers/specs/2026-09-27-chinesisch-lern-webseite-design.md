# Design: Interaktive Chinesisch-Lernwebseite aus "五百字說華語"

Datum: 2026-09-27
Status: Freigegeben (Design-Phase)

## Ausgangslage

Quelle: `D:\(x)Taiwan CN DE Lernen\500MPDF-s_G-H-Y.pdf` — offizielles taiwanesisches
Lehrbuch "五百字說華語 / Mit 500 Wörtern Chinesisch sprechen" (Kommission für
Überseechinesen-Angelegenheiten, chinesisch-deutsche Ausgabe), 237 Seiten, 30 Lektionen.

Jede Lektion folgt einem festen 4-Teile-Schema:
1. 課文 (Text/Dialog)
2. 字與詞 (Schriftzeichen und Wörter)
3. 溫習 (Wiederholung, Text ohne Lautschrift)
4. 應用 (Anwendung, weitere Dialogbeispiele)

Jede chinesische Zeile ist mit Zhuyin (Bopomofo), Pinyin und deutscher Übersetzung
versehen. Im PDF sind zusätzlich **echte MP3-Audiodateien mit nativer Aussprache**
eingebettet (verifiziert: ca. 494 Sound-Clips, benannt `<lektion>-<nummer>.mp3`,
z.B. `01-01.mp3`). Diese sind über PDF-Rendition-Objekte referenziert und lassen sich
mit PyMuPDF (`xref_stream`) als echte MP3-Dateien extrahieren.

Bekanntes Problem: Der extrahierte Rohtext enthält kaputte Zeichen aus einer alten
Font-Kodierung (z.B. „㆗" statt „中", „㈤" statt „五", „㊢" statt „寫"). Diese müssen
beim Parsen über eine Ersetzungstabelle korrigiert werden.

## Ziel

Eine interaktive, moderne Lernwebseite für alle 30 Lektionen, die den Original-Content
1:1 abbildet und um digitale Übungsformen erweitert. Design lehnt sich an die
PDF-Vorlage an (rot/gold-Akzente, gleiche Struktur), wirkt aber zeitgemäßer
(Karten-Layout, klare Typografie, responsive).

## Architektur

Rein statische Website (HTML/CSS/Vanilla JavaScript), kein Build-Tool, kein Backend.
Hosting: GitHub Pages. Begründung: Der Content ist der komplexe Teil, nicht die
Interaktivität — ein Framework würde nur Overhead bringen. Reine Static-Site lässt
sich ohne Build-Pipeline direkt auf GitHub Pages deployen.

```
ChinesischLernApp/
├── index.html                  # Lektionsübersicht
├── lektion.html                # Lektionsansicht (per ?id=05 oder #/lektion/5)
├── css/
│   └── style.css
├── js/
│   ├── app.js                  # Routing, Lektionsübersicht, Fortschritt laden/speichern
│   ├── lektion.js               # Rendering der 4 Teile + Audio-Player
│   ├── uebungen.js              # Karteikarten, Satzbau, Hörverständnis, Aussprache
│   └── srs.js                   # Spaced-Repetition-Logik (vereinfachtes SM-2)
├── data/
│   ├── lektion-01.json … lektion-30.json
│   └── vokabular.json           # Aggregierte Vokabelliste über alle Lektionen (für Karteikarten)
├── audio/
│   └── 01-01.mp3 … 30-xx.mp3     # Aus PDF extrahierte Original-Aussprache
├── extraction/                  # Einmaliges Python-Tooling, nicht Teil der Live-Seite
│   ├── extract_audio.py
│   ├── extract_lessons.py
│   └── zeichen_fix_tabelle.py    # Ersetzungstabelle für kaputte Zeichen
└── docs/superpowers/specs/…
```

### Datenmodell (`lektion-NN.json`)

```json
{
  "nummer": 1,
  "titel_zh": "您早",
  "titel_de": "Guten Morgen!",
  "text": [
    {
      "sprecher": "李太太",
      "zh": "王先生，您早。",
      "zhuyin": "...",
      "pinyin": "Wáng xiān shēng, nín zǎo.",
      "de": "Herr Wang, guten Morgen!",
      "audio": "audio/01-01.mp3"
    }
  ],
  "woerter": [
    {
      "zh": "先生",
      "zhuyin": "ㄒㄧㄢ ㄕㄥ",
      "pinyin": "xiān sheng",
      "de": "der Mann, der Herr",
      "beispiele": [{"zh": "王先生", "pinyin": "Wáng xiān shēng", "de": "Herr Wang"}]
    }
  ],
  "wiederholung": ["..."],
  "anwendung": [ /* wie text[] */ ]
}
```

Die Audiozuordnung erfolgt über die Reihenfolge der Sound-Clips pro Lektion
gegen die Anzahl der Dialogzeilen in Text/Anwendung. Da dies heuristisch ist,
wird es pro Lektion stichprobenartig gegengehört/verifiziert statt blind
übernommen.

## Datenextraktion (einmalig, `extraction/`)

- `extract_audio.py`: iteriert über alle PDF-Xrefs, findet Filespec-Objekte mit
  `.mp3`-Namen, extrahiert die zugehörigen Streams nach `audio/`.
- `extract_lessons.py`: liest den Text lektionsweise (PyMuPDF `get_text` pro Seite),
  erkennt die 4 Abschnitts-Marker (一 課文 / 二 字與詞 / 三 溫習 / 四 應用),
  bereinigt kaputte Zeichen, zerlegt in Dialogzeilen/Vokabeleinträge, schreibt JSON.
- Da automatisches Parsen bei 30 Lektionen unterschiedlicher Textmuster nicht
  100% fehlerfrei sein wird, ist ein manueller Kontrollschritt eingeplant: nach
  dem automatischen Lauf werden alle 30 JSON-Dateien kurz durchgesehen (Text neben
  PDF-Original), auffällige Lektionen werden gezielt korrigiert.

## Frontend

### Startseite (`index.html`)
- Kachel-Grid mit allen 30 Lektionen (chinesischer Titel + deutscher Titel + kurzer
  Fortschrittsbalken pro Lektion, aus localStorage)
- Gesamtfortschritt oben (z.B. "X von 500 Vokabeln gelernt")

### Lektionsseite (`lektion.html`)
- Tabs für die 4 Original-Abschnitte, jede Dialogzeile mit Play-Button (Original-Audio)
- Vierter Tab "Übungen" mit den 4 Übungsformen:
  1. **Karteikarten**: vereinfachtes SM-2-Intervallsystem, Vokabular kommt aus
     `vokabular.json` gefiltert auf die aktuelle Lektion (oder global "alle fälligen")
  2. **Satzbau (Drag & Drop)**: Dialogsätze der Lektion werden in Wortblöcke zerlegt,
     Nutzer bringt sie in korrekte Reihenfolge
  3. **Hörverständnis-Quiz**: Original-Audio abspielen, Nutzer wählt passende
     Übersetzung/Lektionszeile aus Multiple-Choice-Optionen
  4. **Ausspracheübung**: Web Speech API (`SpeechRecognition`) nimmt Nutzeräußerung
     auf, vergleicht (grob, über Pinyin-Ähnlichkeit) mit erwartetem Satz. Nur in
     Chrome/Edge zuverlässig verfügbar — im UI wird das transparent kommuniziert,
     mit Fallback-Hinweis für andere Browser statt eines stillen Fehlers.

### Design-Sprache
- Angelehnt an Original: rot/gold-Akzentfarben (wie klassische chinesische
  Lehrmaterialien), aber moderner: viel Weißraum, Karten mit sanften Schatten,
  abgerundete Ecken
- Schrift: Noto Sans TC (chinesische Zeichen) + eine ruhige serifenlose Schrift
  für Deutsch/Pinyin
- Responsive: Mobile-first, da Vokabellernen oft unterwegs stattfindet

## Fortschritt & Daten-Persistenz

- localStorage: Karteikarten-Status (Intervall, nächste Fälligkeit pro Vokabel),
  "gelesen/gehört"-Status pro Lektion
- Export-Button: lädt den kompletten localStorage-Zustand als
  `fortschritt-YYYY-MM-DD.json` herunter
- Import-Button: liest eine solche Datei ein und überschreibt/merged den
  aktuellen Zustand (mit Bestätigungsdialog vor Überschreiben)

## Deployment

1. Lokales Git-Repo ist bereits initialisiert (`D:\_Projekte\Claude\ChinesischLernApp`)
2. Anleitung für Nutzer: GitHub-Repo erstellen, Remote hinzufügen, pushen
3. GitHub Pages im Repo aktivieren (Branch `main`, Root-Verzeichnis)
4. Alle Pfade relativ halten, damit es sowohl lokal (`file://` bzw. lokaler Server)
   als auch unter der GitHub-Pages-Unterpfad-URL funktioniert

## Out of Scope (bewusst nicht Teil dieses Projekts)

- Kein Nutzer-Login/Cloud-Sync (nur Datei-Export/Import)
- Keine automatische Bewertung der Ausspracheübung über einfachen Textvergleich
  hinaus (keine echte Phonetik-Analyse)
- Keine Übersetzung/Vertonung zusätzlicher, im Buch nicht enthaltener Sätze

## Offene Risiken

- **Textparsing-Qualität**: Die 30 Lektionen sind nicht alle exakt gleich
  formatiert (siehe Seite 118 mit Bild-Vokabular „毛筆"-Dialog). Automatisches
  Parsen kann bei Einzelfällen scheitern; wird durch Stichprobenkontrolle
  abgefangen, nicht durch perfekte Automatisierung vorausgesetzt.
- **Audio-Zuordnung**: Reihenfolge-basiertes Matching von Sound-Clips zu
  Dialogzeilen ist eine Annahme, keine Garantie aus der PDF-Struktur. Wird beim
  Testen gegengehört.
- **Web Speech API**: Browserabhängig (im Wesentlichen nur Chrome/Edge), das wird
  im UI klar kommuniziert statt als Vollfunktion versprochen.
