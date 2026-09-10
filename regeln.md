all# Tennis Spielplan — Regeln, Präferenzen und Systemarchitektur (Stand: 2026)

Dieses Dokument fasst alle geschäftlichen Regeln, Spielerpräferenzen, Blackout-Zeiten und technischen Anforderungen zusammen, die für die Generierung und den Betrieb des Tennis-Spielplans (`generate_html.py` und `index.html`) gelten.

---

## 1. Allgemeiner Geltungsbereich & Zeitrahmen
- **Datenbasis (Excel-Quelle)**: Die Datei `Tennis_Spielplan_Google_Drive_Native_Fix.xlsx` (Tabellenblatt `Gesamt-Spielplan`) dient als fundamentale Rohdatenquelle.
  - Spalte A: Spieltag-Nummer (1 bis 30)
  - Spalte B: Datum des Spieltags
  - Spalten C bis M: Platz 1 (Einzel-Matches zu den Zeiten 19:00, 20:00, 21:00)
  - Spalten N bis S: Platz 2 (Doppel-Match mit 4 Spielern um 20:30)
- **Saison-Einschränkung**: Der Spielplan wird für die Anwendung exklusiv auf das Jahr 2026 eingeschränkt (**Spieltage 1 bis 13**).
- **Sonder-Spieltag (Spieltag 13)**: Der Termin am **29.12.2026** ist als „Reserviert für alle“ definiert. Es sind hierbei keine festen Spieler vorgesehen oder vorzuplanen.

---

## 2. Kader & Spieler-Pool
- **Basis**: Einlesen der Rohdaten aus der Excel-Datei (`Tennis_Spielplan_Google_Drive_Native_Fix.xlsx`).
- **Alle in der Excel-Quelle enthaltenen Spieler (Rohdaten)**:
  - Beumer, Dedores, Hansmann, Heyn, Hinz, Höttinger, Knust, Kuhlhoff, Marschollek, Mönning, Nolte, Prodehl, Redieker, Rumpf, Trojanski, Weber, Wojtanowtisch, van de Loo.
- **Bereinigung / Roster-Anpassungen**:
  - Entfernte Spieler: *Knust*, *Höttinger*.
  - Hinzugefügte Spieler: *Kissner*.
  - Aktiver bereinigter Spieler-Pool (16 Spieler): Beumer, Dedores, Hansmann, Heyn, Hinz, Kissner, Kuhlhoff, Marschollek, Mönning, Nolte, Prodehl, Redieker, Rumpf, Trojanski, Weber, Wojtanowtisch, van de Loo.
- **Eindeutigkeit**: Pro Spielabend nehmen exakt 10 unique Spieler teil (keine Doppelbelegungen pro Spieler an demselben Abend).

---

## 3. Verschachteltes Regelwerk pro Spieler (`PLAYER_RULES`)

### Hansmann
- **Slot-Präferenz**: Wunsch nach ca. 70% Einzel / 30% Doppel (`ratio: 0.3`).
- **Blackout-Tage**: Kann an **Spieltag 9** (01.12.2026) nicht teilnehmen.

### Dedores
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).
- **Blackout-Tage**: 20.10.26 (#3), 27.10.26 (#4), 24.11.26 (#8), 29.12.26 (#13).

### Hinz
- **Slot-Präferenz**: Wunsch nach ca. 50% Doppel / 50% Einzel (`ratio: 0.5`).
- **Blackout-Tage**: Kann vor dem 01.01.2027 (Spieltage 1–13) und am 27.04.2027 (Spieltag 30) nicht spielen.

### Beumer
- **Slot-Präferenz**: Wunsch nach ca. 50% Doppel / 50% Einzel (`ratio: 0.5`).

### Mönning
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).

### Prodehl
- **Slot-Präferenz**: Wunsch nach ca. 60% Doppel (`ratio: 0.6`).
- **Urlaub**: In den ersten beiden Novemberwochen (**Spieltag 5 & 6**) abwesend.

### Marschollek
- **Slot-Präferenz**: Wunsch nach ca. 90% Doppel (`ratio: 0.9`).
- **Blackout-Tage**: 13.10.26 (#2), 20.10.26 (#3), 03.11.26 (#5), 08.12.26 (#10), 19.01.27 (#16), 16.03.27 (#24).

### Kissner
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).

### Heyn
- **Slot-Präferenz**: Wunsch nach ca. 50% Doppel / 50% Einzel (`ratio: 0.5`).
- **Blackout-Tage**: 13.10.26 (#2), 27.10.26 (#4), 03.11.26 (#5), 10.11.26 (#6), 08.12.26 (#10), 29.12.26 (#13).

### Trojanski
- **Frequenz**: 2-Wochen-Rhythmus (mindestens 1 Spieltag Pause zwischen Einsätzen).
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).
- **Blackout-Tage**: 13.10.26 (#2), 03.11.26 (#5), 08.12.26 (#10).

### Kuhlhoff
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).
- **Blackout-Tage**: 10.11.26 (#6), 17.11.26 (#7), 24.11.26 (#8), 08.12.26 (#10), 29.12.26 (#13).

### van de Loo
- **Frequenz**: Einmal im Monat (mindestens 3 Spieltage Pause / 4 Wochen Abstand).
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).

---

## 4. Kostenberechnung & Spielerstatistik
In der UI-Spielerstatistik wird eine Spalte **Kosten** geführt, basierend auf folgender Formel:
$$\text{Kosten} = (\text{Einzel-Spiele} \times 0.5) + (\text{Doppel-Spiele} \times \frac{1.5}{4})$$
Die Werte werden über alle gespielten Spieltage hinweg aufsummiert.

---

## 5. Paarungs-Optimierung (Matchmaking)
- **Vermeidung von Wiederholungen**: Ein Algorithmus (Randomized Local Search über Platz-Permutationen) minimiert die Wiederholung gleicher Paarungen (Head-to-Head) über die Saison hinweg (maximal ca. 3–4 Wiederholungen pro Paarung).
- **Slot-Zuordnung**:
  - Platz 1 (Zeiten 19:00, 20:00, 21:00): Einzel-Matches.
  - Platz 2 (Zeit 20:30): Doppel-Matches (4 Spieler).

---

## 6. Technische Bauanleitung & Architektur von `generate_html.py`

Das Python-Skript `generate_html.py` ist der zentrale Generator für den interaktiven Spielplan (`index.html`). Es integriert die Daten aus der Excel-Quelle und baut ein vollständiges, responsives Frontend auf.

### A. Excel-Struktur & Mapping (`Tennis_Spielplan_Google_Drive_Native_Fix.xlsx`)
- **Tabellenblatt**: `Gesamt-Spielplan` (aktiv).
- **Tabellenkopf**: Zeilen 1–5 (Titel, Gesamtübersichten).
- **Datenbereich**: Ab Zeile 7 (`raw_rows`).
- **Spalten-Mapping (0-basiert im Python-Skript / openpyxl)**:
  - `r[0]` (Spalte A): Spieltagsnummer (`spieltag`)
  - `r[1]` (Spalte B): Datum (`date_val`)
  - `r[2]` bis `r[12]` (Spalten C–M): Platz 1 (Einzel-Slots für Match 1, Match 2, Match 3 mit Zeiten 19:00, 20:00, 21:00)
  - `r[14]` bis `r[18]` (Spalten O–S): Platz 2 (Doppel-Slots für Team 1 und Team 2 um 20:30)
  - `r[19]` (Spalte T): Status des Spieltags (z. B. `Geplant`, `Reserviert für alle`, `Abgeschlossen`)

### B. Kader-Bereinigung & Initialisierung
1. **Automatisches Einlesen**: Alle in den Spalten befindlichen Spielernamen werden gesammelt (`all_excel_players`).
2. **Manuelle Modifikationen**:
   - Hinzufügen von *Kissner*.
   - Vollständiger Ausschluss/Bereinigung von inaktiven oder ausgeschiedenen Spielern (*Knust*, *Höttinger*).
3. **Spieler-Pool**: Sortierte Liste aller bereinigten aktiven Spieler als Substitutionsbasis.

### C. Regel-Engine & Status-Tracking pro Spieltag
Für jeden Spieltag (beschränkt auf Saison 2026, Spieltage 1–13) läuft folgende Pipeline ab:
1. **Sonder-Spieltag (Spieltag 13 / 29.12.2026)**:
   - Kurzschluss/Short-Circuit: Keine festen Zuweisungen, Status wird als `Reserviert für alle` gesetzt.
2. **Vorab-Prüfung von Hard-Ratio-Regeln**:
   - Spieler mit 100% Doppel (`ratio >= 1.0`) oder 0% Doppel (`ratio <= 0.0`) werden vorab in die korrekten Kategorien (Einzel vs. Doppel) gelenkt.
3. **Regel-Applikation (`PLAYER_RULES`)**:
   - **Blackout-Tage**: Abgleich mit den spezifischen Spieltags-IDs je Spieler. Bei Abwesenheit wird automatisch ein valider Ersatzspieler (`get_substitute`) ermittelt.
   - **Frequenz & Pausen (`max_frequency_gap`, `tshirt_size_frequency`)**: Einhaltung von Mindestabständen (z. B. Trojanski im 2-Wochen-Rhythmus, van de Loo monatlich).
   - **Slot-Präferenzen & Quoten (`ratio`)**: Dynamischer Ausgleich von Einzel- und Doppelspielen basierend auf kumulierten Ist-Zahlen.
4. **Doppelbuchungs-Schutz & Auffüllung**:
   - Prüfung auf Mehrfachbelegung (`occupied_today`) und automatisches Ersetzen durch freie Spieler unter Berücksichtigung der Slot-Typen (Einzel/Doppel).

### D. Matchmaking & Paarungs-Optimierung
- **Randomized Local Search**: Pro Spieltag werden die 10 aktiven Spieler in 300 Iterationen permutiert, um die Paarungen (Head-to-Head) über die Saison optimal zu verteilen (Vermeidung häufiger Wiederholungen).

### E. Statistik- & Kostenberechnung
- Nach Durchlauf aller Spieltage werden die Gesamtspiele, Einzel-/Doppel-Quoten und Kosten je Spieler über die Formel:
  $$\text{Kosten} = (\text{Einzel} \times 0.5) + (\text{Doppel} \times \frac{1.5}{4})$$
  berechnet und als JSON-Struktur übergeben.

### F. Frontend-Generierung (Vue.js 3 & Tailwind CSS)
Das Skript generiert eine eigenständige HTML-Datei mit folgenden integrierten Features:
- **Responsive UI**: Tailwind CSS Styling im modernen Clean-Design.
- **Interaktive Filter**: Klickbare Spieler-Badges zum Filtern von Spieltagen.
- **Statistik-Matrix**: Sortierbare Tabelle aller Spieler inklusive Kostenübersicht.
- **Regel-Legende**: Übersichtliche Darstellung aller aktiven Spielerregeln direkt im UI.
- **ICS Kalender-Export**: Generierung von `.ics`-Kalenderdateien für einzelne Spieler.
- **Zustandsverwaltung**: Vue.js 3 Reactive State (Suchfilter, Vergangenheits-Toggle, Nächster-Spieltag-Highlight).


