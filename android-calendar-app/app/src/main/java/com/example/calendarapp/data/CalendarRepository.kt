package com.example.calendarapp.data

import com.example.calendarapp.auth.GoogleAuthManager
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter

/** Talks to the user's real Google Calendar ("primary") through [GoogleCalendarApi]. */
class CalendarRepository(
    private val authManager: GoogleAuthManager,
    private val api: GoogleCalendarApi = GoogleCalendarApi.create(),
) {
    /** Fetches all events overlapping the given inclusive date range, in ascending start order. */
    suspend fun fetchEvents(from: LocalDate, to: LocalDate): List<CalendarEvent> {
        val zone = ZoneId.systemDefault()
        val timeMin = from.atStartOfDay(zone).format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
        val timeMax = to.plusDays(1).atStartOfDay(zone).format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
        val response = api.listEvents(bearerToken(), timeMin, timeMax)
        return response.items.mapNotNull { it.toDomain() }
    }

    suspend fun createEvent(event: CalendarEvent): CalendarEvent =
        api.insertEvent(bearerToken(), event.toDto()).toDomain()
            ?: error("Ungültige Antwort vom Server beim Anlegen des Termins")

    suspend fun updateEvent(event: CalendarEvent): CalendarEvent {
        val id = requireNotNull(event.id) { "Termin ohne ID kann nicht aktualisiert werden" }
        return api.updateEvent(bearerToken(), id, event.toDto()).toDomain()
            ?: error("Ungültige Antwort vom Server beim Aktualisieren des Termins")
    }

    suspend fun deleteEvent(eventId: String) {
        api.deleteEvent(bearerToken(), eventId)
    }

    private fun bearerToken(): String {
        val token = requireNotNull(authManager.currentAccessToken()) { "Nicht angemeldet" }
        return "Bearer $token"
    }
}
