all# Tennis Spielplan — Regeln, Präferenzen und Systemarchitektur (Stand: 2026)

Dieses Dokument fasst alle geschäftlichen Regeln, Spielerpräferenzen, Abwesenheit-Zeiten und technischen Anforderungen zusammen, die für die Generierung und den Betrieb des Tennis-Spielplans (`generate_html.py` und `index.html`) gelten.

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
  - Beumer, Dedores, Hansmann, Heyn, Hinz, Höttinger, Knust, Kuhlhoff, Marschollek, Mönning, Nolte, Prodehl, Redieker, Rumpf, Trojanski, Weber, Wojtanowitsch, van de Loo.
- **Bereinigung / Roster-Anpassungen**:
  - Entfernte Spieler: *Höttinger*.
  - Übersicht-only Spieler: *Knust* (nimmt erst 2027 teil).
  - Hinzugefügte Spieler: *Kissner*, *Quante*.
  - Aktiver bereinigter Spieler-Pool: Beumer, Dedores, Hansmann, Heyn, Hinz, Kissner, Knust, Kuhlhoff, Marschollek, Mönning, Nolte, Prodehl, Quante, Redieker, Rumpf, Trojanski, Weber, Wojtanowitsch, van de Loo.
- **Eindeutigkeit**: Pro Spielabend nehmen exakt 10 unique Spieler teil (keine Doppelbelegungen pro Spieler an demselben Abend).

---

## 3. Verschachteltes Regelwerk pro Spieler (`PLAYER_RULES`)

### Hansmann
- **Slot-Präferenz**: Wunsch nach ca. 70% Einzel / 30% Doppel (`ratio: 0.3`).
- **Abwesenheiten**: Kann an **Spieltag 9** (Dienstag, 01.12. / 02.12.2026) nicht teilnehmen.

### Dedores
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).
- **Abwesenheiten**: 20.10.26 (#3), 27.10.26 (#4), 24.11.26 (#8), 29.12.26 (#13).

### Hinz
- **Slot-Präferenz**: Wunsch nach ca. 50% Doppel / 50% Einzel (`ratio: 0.5`).
- **Abwesenheiten**: Kann vor dem 01.01.2027 (Spieltage 1–13) und am 27.04.2027 (Spieltag 30) nicht spielen.

### Beumer
- **Slot-Präferenz**: Wunsch nach ca. 50% Doppel / 50% Einzel (`ratio: 0.5`).

### Mönning
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).
- **Abwesenheiten**: 13.10.26 (#2, Zeitraum 29.09.–13.10.), 03.11.26 (#5, Zeitraum 03.11.–10.11.), 10.11.26 (#6, Zeitraum 03.11.–10.11.), 01.12.26 (#9, Dienstag 02.12.).

### Prodehl
- **Slot-Präferenz**: Wunsch nach ca. 60% Doppel (`ratio: 0.6`).
- **Urlaub**: In den ersten beiden Novemberwochen im Zeitraum **03.11. – 10.11.2026** (Spieltag 5 & 6) abwesend.

### Marschollek
- **Slot-Präferenz**: Wunsch nach ca. 90% Doppel (`ratio: 0.9`).
- **Abwesenheiten**: 13.10.26 (#2, im Zeitraum 29.09.–13.10.), 20.10.26 (#3), 03.11.26 (#5, im Zeitraum 03.11.–10.11.), 08.12.26 (#10), 19.01.27 (#16), 16.03.27 (#24).

### Kissner
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).

### Heyn
- **Slot-Präferenz**: Wunsch nach ca. 50% Doppel / 50% Einzel (`ratio: 0.5`).
- **Abwesenheiten**: 13.10.26 (#2, Zeitraum 29.09.–13.10.), 27.10.26 (#4), 03.11.26 (#5, Zeitraum 03.11.–10.11.), 10.11.26 (#6, Zeitraum 03.11.–10.11.), 08.12.26 (#10), 29.12.26 (#13).

### Trojanski
- **Frequenz**: 2-Wochen-Rhythmus (mindestens 1 Spieltag Pause zwischen Einsätzen).
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).
- **Abwesenheiten**: 13.10.26 (#2, Zeitraum 29.09.–13.10.), 03.11.26 (#5, Zeitraum 03.11.–10.11.), 08.12.26 (#10).

### Kuhlhoff
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).
- **Abwesenheiten**: 13.10.26 (#2), 20.10.26 (#3), 10.11.26 (#6, Zeitraum 03.11.–10.11.), 17.11.26 (#7), 24.11.26 (#8), 08.12.26 (#10), 29.12.26 (#13).

### van de Loo
- **Frequenz**: Einmal im Monat (mindestens 3 Spieltage Pause / 4 Wochen Abstand).
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).

### Wojtanowitsch
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).

### Nolte
- **Slot-Präferenz**: Spielt ausschließlich **Einzel** (0% Doppel, `ratio: 0.0`).
- **Abwesenheiten**: Spieltag 3 (20.10.2026).

### Quante
- **Zeitvorgabe**: Für 2026 bleibt die Vorgabe von genau 2 Einsätzen um 21:00 Uhr bestehen; zusätzlich gelten für die zweite Saisonhälfte 2027 drei Doppel- und ein Einzel-Einsatz.

---

## 4. Regeln für die 2. Saisonhälfte (Spieltage 14–30)

**Zeitraum:** 05.01.2027 bis 27.04.2027. Die bisherigen dauerhaften Spiel- und Frequenzwünsche gelten weiter. Die folgenden bekannten Abwesenheiten sind bereits eingetragen; weitere Angaben werden ergänzt, sobald sie vorliegen.

### Beumer
- **Slot-Präferenz**: Wunsch nach 50% Einzel / 50% Doppel (`ratio: 0.5`).
- **Abwesenheit**: 02.03.2027 (Spieltag 22).

### Dedores
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Einsatzumfang**: Bis zu 7 Einsätze reichen.
- **Abwesenheiten**: 19.01.2027 (Spieltag 16), 26.01.2027 (Spieltag 17), 16.02.2027 (Spieltag 20), 23.02.2027 (Spieltag 21), 23.03.2027 (Spieltag 25), 30.03.2027 (Spieltag 26) und 13.04.2027 (Spieltag 28).
- **Zeitvorgabe (intern)**: Nur um 19:00 oder 20:00 Uhr.

### Allgemeine Zeitverteilung
- Für alle Spieler ohne persönliche Zeit-Sonderregel werden Einsätze über **19:00, 20:00, 21:00 und 20:30 Uhr** möglichst gleichmäßig verteilt.
- Ziel: Bei vier Einsätzen soll ein Spieler idealerweise je einmal zu jeder Uhrzeit spielen; bei drei Einsätzen auf drei verschiedene Uhrzeiten. Die Abweichung zwischen den Uhrzeiten soll je Spieler so klein wie möglich bleiben.
- Persönliche Zeitvorgaben haben Vorrang (derzeit: Dedores nur 19:00 oder 20:00 Uhr).

### Hansmann
- **Slot-Präferenz**: Ca. 70% Einzel / 30% Doppel (`ratio: 0.3`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Heyn
- **Slot-Präferenz**: Wunsch nach 70% Einzel / 30% Doppel (`ratio: 0.30`).
- **Abwesenheiten**: 12.01.2027 (Spieltag 15), 09.02.2027 (Spieltag 19), 09.03.2027 (Spieltag 23), 30.03.2027 (Spieltag 26), 13.04.2027 (Spieltag 28) und 27.04.2027 (Spieltag 30).

### Hinz
- **Slot-Präferenz**: Wunsch nach ca. 50% Doppel / 50% Einzel (`ratio: 0.5`).
- **Abwesenheit**: 27.04.2027 (Spieltag 30).
- **Hinweis**: Die bisherige Sperre für Spieltage 1–13 betrifft die erste Saisonhälfte; Hinz kann ab Spieltag 14 grundsätzlich berücksichtigt werden.

### Kissner
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Knust
- **Teilnahme**: Ab 2027 vorgesehen.
- **Weitere Regeln/Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Kuhlhoff
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Marschollek
- **Slot-Präferenz**: Wunsch nach ca. 90% Doppel (`ratio: 0.9`).
- **Abwesenheiten**: 19.01.2027 (Spieltag 16) und 16.03.2027 (Spieltag 24).

### Mönning
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Nolte
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Abwesenheiten**: 02.03.2027 (Spieltag 22), 23.03.2027 (Spieltag 25), 20.04.2027 (Spieltag 29) und 27.04.2027 (Spieltag 30).

### Prodehl
- **Slot-Präferenz**: Wunsch nach ca. 60% Doppel (`ratio: 0.6`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Quante
- **Einsatzvorgabe (intern)**: Genau 3 Einsätze als Doppel und 1 Einsatz als Einzel in der zweiten Saisonhälfte 2027.

### Redieker
- **Slot-Präferenz**: Bisher keine besondere Einzel-/Doppelquote festgelegt.
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Rumpf
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Trojanski
- **Frequenz**: 2-Wochen-Rhythmus (mindestens ein Spieltag Pause zwischen Einsätzen).
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### van de Loo
- **Frequenz**: Einmal im Monat (mindestens drei Spieltage Pause / ca. vier Wochen Abstand).
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Weber
- **Slot-Präferenz**: Bisher keine besondere Einzel-/Doppelquote festgelegt.
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

### Wojtanowitsch
- **Slot-Präferenz**: Ausschließlich Einzel (`ratio: 0.0`).
- **Weitere Abwesenheiten**: Bisher keine für Spieltage 14–30 gemeldet.

---

## 5. Kostenberechnung & Spielerstatistik
In der UI-Spielerstatistik wird eine Spalte **Kosten** geführt, basierend auf folgender Formel:
$$\text{Kosten} = (\text{Einzel-Spiele} \times 0.5) + (\text{Doppel-Spiele} \times \frac{1.5}{4})$$
Die Werte werden über alle gespielten Spieltage hinweg aufsummiert.

---

## 5. Paarungs-Optimierung (Matchmaking)
- **Vermeidung von Wiederholungen**: Ein Algorithmus (Randomized Local Search über Platz-Permutationen) minimiert die Wiederholung gleicher Paarungen (Head-to-Head) über die Saison hinweg (maximal ca. 3–4 Wiederholungen pro Paarung).
- **Slot-Zuordnung**:
  - Platz 1 (Zeiten 19:00, 20:00, 21:00): Einzel-Matches.
  - Platz 2 (Zeit 20:30): **Alternierend** (ungerade Spieltage = Doppel mit 4 Spielern, gerade Spieltage = Einzel mit 2 Spielern).

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
   - Vollständiger Ausschluss/Bereinigung von inaktiven oder ausgeschiedenen Spielern (*Höttinger*).
3. **Spieler-Pool**: Sortierte Liste aller bereinigten aktiven Spieler als Substitutionsbasis.

### C. Regel-Engine & Status-Tracking pro Spieltag
Für jeden Spieltag (beschränkt auf Saison 2026, Spieltage 1–13) läuft folgende Pipeline ab:
1. **Sonder-Spieltag (Spieltag 13 / 29.12.2026)**:
   - Kurzschluss/Short-Circuit: Keine festen Zuweisungen, Status wird als `Reserviert für alle` gesetzt.
2. **Vorab-Prüfung von Hard-Ratio-Regeln**:
   - Spieler mit 100% Doppel (`ratio >= 1.0`) oder 0% Doppel (`ratio <= 0.0`) werden vorab in die korrekten Kategorien (Einzel vs. Doppel) gelenkt.
3. **Regel-Applikation (`PLAYER_RULES`)**:
   - **Abwesenheiten**: Abgleich mit den spezifischen Spieltags-IDs je Spieler. Bei Abwesenheit wird automatisch ein valider Ersatzspieler (`get_substitute`) ermittelt.
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
- **Quick-Stats-Leiste**: Übersicht zu Spieltagen, aktiven Spielern und nächstbester Begegnung.
- **Interaktive Filter**: Klickbare Spieler-Badges zum Filtern von Spieltagen (nicht beteiligte Spiele werden dezent abgeblendet).
- **Statistik-Matrix**: Klickbare, sortierbare Tabellenköpfe für alle Spieler inklusive Kostenübersicht und Formel-Tooltip.
- **Regel-Legende**: Übersichtliche Darstellung aller aktiven Spielerregeln direkt im UI.
- **ICS Kalender-Export**: Sowohl personalisierter `.ics`-Download pro Spieler als auch globaler Gesamtkalender-Export für die gesamte Saison.
- **Sonder-Spieltag-Darstellung**: „Reserviert für alle“ erstreckt sich über die gesamte Tabellenzeile.
- **Zustandsverwaltung**: Vue.js 3 Reactive State (Suchfilter, Vergangenheits-Toggle, Nächster-Spieltag-Highlight).


