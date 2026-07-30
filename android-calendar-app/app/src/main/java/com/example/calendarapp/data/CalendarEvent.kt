package com.example.calendarapp.data

import java.time.LocalDate
import java.time.LocalTime

/**
 * App-level model for a single-day calendar event. Deliberately simpler than the
 * Google Calendar "Event" resource (no multi-day spans, attendees, recurrence, ...) -
 * everything the sample UI needs, mapped to/from [EventDto] in CalendarMappers.kt.
 */
data class CalendarEvent(
    val id: String? = null,
    val title: String,
    val description: String = "",
    val date: LocalDate,
    val startTime: LocalTime? = null,
    val endTime: LocalTime? = null,
    val isAllDay: Boolean = startTime == null,
)
