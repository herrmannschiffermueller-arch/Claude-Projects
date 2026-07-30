package com.example.calendarapp.data

/** Mirrors (a subset of) the Google Calendar API v3 "Event" resource JSON shape. */
data class EventDto(
    val id: String? = null,
    val summary: String? = null,
    val description: String? = null,
    val start: EventDateTimeDto? = null,
    val end: EventDateTimeDto? = null,
)

/**
 * Exactly one of [date] (all-day, format "yyyy-MM-dd") or [dateTime] (format
 * RFC3339, e.g. "2026-08-01T09:00:00+02:00") is set, per the Google Calendar API.
 */
data class EventDateTimeDto(
    val date: String? = null,
    val dateTime: String? = null,
    val timeZone: String? = null,
)

data class EventsListResponseDto(
    val items: List<EventDto> = emptyList(),
)
