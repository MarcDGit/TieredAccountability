# Tiered Accountability Dashboard

Dieses Streamlit-Projekt stellt ein einfaches Eskalations- und Tier-Dashboard bereit, das typische Anforderungen aus dem Shop-Floor- und Office-Umfeld von Operational Excellence (OPEX) und Lean Management abbildet.

## Inhalt

1. Einleitung
2. Definitionen und Abkürzungen
3. Systemarchitektur
4. Installation & Start
5. Workflows
6. Ausblick

---

## 1  Einleitung

Die Anwendung visualisiert und verwaltet **Tier-Meetings** mit zugehörigen Eskalations-Aufgaben (‚Issues‘). Über ein Admin-Panel können neue Tiers (Ebenen) sowie Personen angelegt werden. Aufgaben, die nicht auf der eigenen Ebene gelöst werden können, werden an die nächsthöhere Ebene eskaliert. Nach Bearbeitung fließt das Ergebnis zurück, bis der ursprüngliche Melder das Issue schließt.

---

## 2  Definitionen und Abkürzungen

| Begriff / Kürzel | Bedeutung |
|------------------|-----------|
| Tier n           | Ebene n der Organisation (z. B. Tier 1 = Shopfloor-Team, Tier 2 = Abteilungsleitung) |
| Escalation       | Weitergabe eines Problems an die nächsthöhere Ebene, wenn es dort gelöst werden muss |
| Issue            | Ein einzelner Eintrag / Problem / Task im System |
| OPEX             | Operational Excellence |
| PDCA             | Plan-Do-Check-Act (Kontinuierlicher Verbesserungszyklus) |
| KPI              | Key Performance Indicator |
| SLA              | Service Level Agreement (hier sinngemäß Bearbeitungsziel) |
| Urgency          | Dringlichkeit (Low / Medium / High) |
| Days Open        | Anzahl Tage seit Erstellung des Issues |
| Admin Panel      | Verwaltungsoberfläche zum Anlegen von Tiers und Personen |

---

## 3  Systemarchitektur

* **Frontend**: [Streamlit](https://streamlit.io) single-page-app mit drei Hauptansichten: Dashboard, Neue Eskalation, Admin Panel.
* **Backend / Persistenz**: SQLite-Datenbank (`data.db`) mit drei Tabellen (tiers, people, tasks).
* **Python-Module**:  
  * `db.py` – Datenbank Helper (CRUD-Funktionen, Schema-Initialisierung)  
  * `app.py` – Streamlit-Application-Logic

---

## 4  Installation & Start

Voraussetzungen: Python ≥ 3.9

```bash
# Repository klonen
# git clone <URL> && cd repo

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
streamlit run app.py
```

Beim ersten Start wird die Datenbank automatisch initialisiert.

---

## 5  Workflows

### 5.1  Eskalation anlegen (Tier 1 → Tier 2)
1. Als Person aus Tier 1 einloggen.  
2. Menüpunkt „Neue Eskalation“ wählen.  
3. Titel, Beschreibung, Dringlichkeit eingeben und zuständige Person aus Tier 2 auswählen.  
4. „Eskalieren“ drücken – der Task erscheint sofort:  
   * Im Dashboard von Tier 1 unter „Meine Eskalationen“ (Status: *escalated*)  
   * Im Dashboard der zugewiesenen Person in Tier 2 unter „Aufgaben an mich“

### 5.2  Bearbeitung in Tier 2
1. Als Person aus Tier 2 einloggen.  
2. Unter „Aufgaben an mich“ das Issue öffnen.  
3. „Als erledigt markieren“ klicken – Status wechselt zu *resolved*.

### 5.3  Feedback & Abschluss in Tier 1
1. Melder in Tier 1 sieht sein Issue jetzt mit Hinweis „Eskalation bearbeitet“.  
2. Prüfung des Ergebnisses – bei Zufriedenheit „Schließen“ drücken – Status: *closed*.

---

## 6  Ausblick / Erweiterungen

* Authentifizierung (z. B. Single Sign-On)
* Mehrstufige Eskalationsketten (> Tier 2)
* Benachrichtigungen via E-Mail oder MS Teams
* KPI-Tracking (⌀ Durchlaufzeit, SLA-Erfüllung)
* Rollen- und Rechte-Management (Reviewer / Owner)