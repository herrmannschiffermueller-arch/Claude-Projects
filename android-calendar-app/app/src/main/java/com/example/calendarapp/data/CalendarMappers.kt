package com.example.calendarapp.data

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

private val zone: ZoneId = ZoneId.systemDefault()

fun CalendarEvent.toDto(): EventDto {
    val start: EventDateTimeDto
    val end: EventDateTimeDto
    if (isAllDay) {
        start = EventDateTimeDto(date = date.toString())
        end = EventDateTimeDto(date = date.plusDays(1).toString())
    } else {
        val from = requireNotNull(startTime) { "startTime fehlt für einen Termin mit Uhrzeit" }
        val to = endTime ?: startTime.plusHours(1)
        start = EventDateTimeDto(dateTime = offsetString(date, from), timeZone = zone.id)
        end = EventDateTimeDto(dateTime = offsetString(date, to), timeZone = zone.id)
    }
    return EventDto(id = id, summary = title, description = description, start = start, end = end)
}

fun EventDto.toDomain(): CalendarEvent? {
    val title = summary ?: return null
    val startDto = start ?: return null
    val endDto = end

    val allDayDate = startDto.date
    if (allDayDate != null) {
        return CalendarEvent(
            id = id,
            title = title,
            description = description.orEmpty(),
            date = LocalDate.parse(allDayDate),
            startTime = null,
            endTime = null,
            isAllDay = true,
        )
    }

    val startDateTime = startDto.dateTime?.let { parseToLocal(it) } ?: return null
    val endDateTime = endDto?.dateTime?.let { parseToLocal(it) }
    return CalendarEvent(
        id = id,
        title = title,
        description = description.orEmpty(),
        date = startDateTime.toLocalDate(),
        startTime = startDateTime.toLocalTime(),
        endTime = endDateTime?.toLocalTime(),
        isAllDay = false,
    )
}

private fun offsetString(date: LocalDate, time: java.time.LocalTime): String =
    LocalDateTime.of(date, time).atZone(zone).format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)

private fun parseToLocal(rfc3339: String): LocalDateTime =
    java.time.OffsetDateTime.parse(rfc3339).atZoneSameInstant(zone).toLocalDateTime()
