# Kalender – Android-App mit Google-Kalender-Sync

Native Android-App (Kotlin + Jetpack Compose), die den **primären Google-Kalender**
des angemeldeten Nutzers anzeigt und bearbeitet: Monatsansicht, Termine anlegen,
bearbeiten und löschen – alles direkt über die Google Calendar REST API v3
synchronisiert (kein eigener Server, keine lokale Datenbank).

## Funktionsumfang

- Anmeldung per Google-Autorisierung (nur der Scope `calendar.events`, kein
  voller Google-Login/Profilzugriff)
- Monatsansicht mit Punkt-Markierung an Tagen mit Terminen
- Termine pro Tag als Liste, antippen zum Bearbeiten
- Neuer Termin über den "+"-Button: Titel, Beschreibung, ganztägig oder mit
  Start-/Endzeit
- Löschen bestehender Termine
- Alle Änderungen laufen 1:1 über die Google Calendar API – was hier passiert,
  taucht sofort im normalen Google-Kalender (Web/andere Geräte) auf

**Bewusste Vereinfachungen** (für einen ersten funktionsfähigen Stand):
Termine sind immer eintägig (kein mehrtägiges Spannen), keine Wiederholungen,
kein Offline-Cache, nur der primäre Kalender (nicht mehrere Kalender/Teilnehmer).

## Projektstruktur

```
app/src/main/java/com/example/calendarapp/
├── MainActivity.kt              Activity, Consent-Screen-Verdrahtung
├── auth/GoogleAuthManager.kt    OAuth-Autorisierung (Identity Authorization API)
├── data/
│   ├── CalendarEvent.kt         App-Datenmodell
│   ├── GoogleCalendarDto.kt     JSON-Modelle der Google-API
│   ├── CalendarMappers.kt       Mapping App-Modell ↔ Google-JSON
│   ├── GoogleCalendarApi.kt     Retrofit-Interface (REST-Client)
│   └── CalendarRepository.kt    fetch/create/update/delete
├── viewmodel/CalendarViewModel.kt
└── ui/
    ├── CalendarScreen.kt        Sign-in-Screen, Monatsscreen, Termin-Liste
    ├── components/              MonthGrid, AddEditEventDialog
    └── theme/                   Farben, Typografie, Theme
```

## Google-Cloud-Konfiguration (einmalig nötig)

Die App braucht ein eigenes OAuth-Setup in der Google Cloud Console, damit die
Autorisierung für den Calendar-Scope funktioniert. Ohne diese Schritte bleibt
die App beim Tippen auf "Mit Google anmelden" mit einem Fehler hängen.

1. **Projekt anlegen**: [console.cloud.google.com](https://console.cloud.google.com)
   → neues Projekt (oder bestehendes verwenden).
2. **Calendar API aktivieren**: „APIs & Dienste“ → „Bibliothek“ → nach
   *Google Calendar API* suchen → **Aktivieren**.
3. **OAuth-Consent-Screen einrichten**: „APIs & Dienste“ → „OAuth-Zustimmungsbildschirm“
   - Nutzertyp: *Extern* (reicht für Test-/Eigenbedarf)
   - App-Name, Support-E-Mail ausfüllen
   - Scope hinzufügen: `.../auth/calendar.events`
   - Unter „Testnutzer“ das eigene Google-Konto eintragen (solange die App nicht
     verifiziert ist, funktioniert die Anmeldung nur für eingetragene Testnutzer)
4. **SHA-1-Fingerabdruck des Debug-Keystores ermitteln**:
   ```
   keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
   ```
   Die Zeile `SHA1: XX:XX:...` kopieren.
5. **OAuth-Client-ID vom Typ „Android“ anlegen**: „APIs & Dienste“ → „Anmeldedaten“
   → „Anmeldedaten erstellen“ → „OAuth-Client-ID“ → Anwendungstyp *Android*
   - Paketname: `com.example.calendarapp` (siehe `app/build.gradle.kts` → `applicationId`,
     falls du ihn änderst, hier den neuen Wert eintragen)
   - SHA-1-Fingerabdruck: der Wert aus Schritt 4
   - **Wichtig**: Es wird hier keine Client-ID im Code hinterlegt – die
     Android-OAuth-Prüfung läuft rein über Paketname + Signatur (SHA-1), die
     bei Google Play Services hinterlegt sind. Kein `google-services.json`
     nötig, solange nur diese eine Scope-Autorisierung verwendet wird.
   - Für einen späteren Release-Build (eigener Signing-Key statt Debug-Keystore)
     denselben Schritt mit dem SHA-1 des Release-Keystores wiederholen.

## Bauen & Ausführen

Voraussetzung: **Android Studio** (aktuelle Version) mit installiertem Android
SDK, sowie ein Gerät/Emulator **mit Google Play Services** (die Autorisierung
läuft über Play Services – reine AOSP-Emulator-Images ohne Play Store
funktionieren nicht).

1. Projektordner `android-calendar-app/` in Android Studio öffnen ("Open").
2. Gradle-Sync abwarten (lädt Abhängigkeiten von Google- und Maven-Central-Repos
   herunter – Internetzugriff erforderlich).
3. „Run“ auf einem Gerät/Emulator mit Play Services.
4. Beim ersten Start: „Mit Google anmelden“ antippen → Google zeigt den
   Zustimmungsbildschirm für den Kalender-Zugriff → nach Bestätigung lädt die
   App den Monat mit den echten Terminen.

## Hinweis zu dieser Session

Diese Sandbox hat **keinen Zugriff auf das Android SDK** und **keinen
Netzwerkzugriff auf `dl.google.com`** (das Google-Maven-Repository, das die
Android-Gradle-Plugin- und AndroidX/Play-Services-Abhängigkeiten hostet).
Der Code wurde deshalb sorgfältig nach den offiziellen APIs geschrieben,
konnte hier aber **nicht kompiliert oder auf einem Gerät getestet werden**.
Der Gradle-Wrapper (`./gradlew`) ist einsatzbereit; der erste echte Build läuft
in Android Studio auf deinem eigenen Rechner.
