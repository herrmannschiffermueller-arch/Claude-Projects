package com.example.calendarapp.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimePicker
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.calendarapp.data.CalendarEvent
import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

/** Create/edit dialog for a single [CalendarEvent]. Pass an existing event to edit it
 *  (enables the delete action); pass null to create a new one on [initialDate]. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddEditEventDialog(
    initialDate: LocalDate,
    existingEvent: CalendarEvent?,
    onDismiss: () -> Unit,
    onSave: (CalendarEvent) -> Unit,
    onDelete: (CalendarEvent) -> Unit,
) {
    var title by remember { mutableStateOf(existingEvent?.title.orEmpty()) }
    var description by remember { mutableStateOf(existingEvent?.description.orEmpty()) }
    var isAllDay by remember { mutableStateOf(existingEvent?.isAllDay ?: false) }
    var date by remember { mutableStateOf(existingEvent?.date ?: initialDate) }
    var startTime by remember { mutableStateOf(existingEvent?.startTime ?: LocalTime.of(9, 0)) }
    var endTime by remember { mutableStateOf(existingEvent?.endTime ?: LocalTime.of(10, 0)) }

    var showDatePicker by remember { mutableStateOf(false) }
    var showStartTimePicker by remember { mutableStateOf(false) }
    var showEndTimePicker by remember { mutableStateOf(false) }

    val dateFormatter = remember { DateTimeFormatter.ofPattern("EEEE, d. MMMM yyyy") }
    val timeFormatter = remember { DateTimeFormatter.ofPattern("HH:mm") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(if (existingEvent == null) "Neuer Termin" else "Termin bearbeiten") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = title,
                    onValueChange = { title = it },
                    label = { Text("Titel") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )
                OutlinedTextField(
                    value = description,
                    onValueChange = { description = it },
                    label = { Text("Beschreibung") },
                    minLines = 2,
                    modifier = Modifier.fillMaxWidth(),
                )
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Ganztägig", modifier = Modifier.weight(1f))
                    Switch(checked = isAllDay, onCheckedChange = { isAllDay = it })
                }
                OutlinedButton(onClick = { showDatePicker = true }, modifier = Modifier.fillMaxWidth()) {
                    Text(date.format(dateFormatter))
                }
                if (!isAllDay) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                        OutlinedButton(onClick = { showStartTimePicker = true }, modifier = Modifier.weight(1f)) {
                            Text("Von ${startTime.format(timeFormatter)}")
                        }
                        OutlinedButton(onClick = { showEndTimePicker = true }, modifier = Modifier.weight(1f)) {
                            Text("Bis ${endTime.format(timeFormatter)}")
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    onSave(
                        CalendarEvent(
                            id = existingEvent?.id,
                            title = title.trim(),
                            description = description.trim(),
                            date = date,
                            startTime = if (isAllDay) null else startTime,
                            endTime = if (isAllDay) null else endTime,
                            isAllDay = isAllDay,
                        ),
                    )
                },
                enabled = title.isNotBlank() && (isAllDay || !endTime.isBefore(startTime)),
            ) { Text("Speichern") }
        },
        dismissButton = {
            Row {
                if (existingEvent != null) {
                    TextButton(onClick = { onDelete(existingEvent) }) {
                        Text("Löschen", color = MaterialTheme.colorScheme.error)
                    }
                }
                TextButton(onClick = onDismiss) { Text("Abbrechen") }
            }
        },
    )

    if (showDatePicker) {
        val state = rememberDatePickerState(
            initialSelectedDateMillis = date.atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli(),
        )
        DatePickerDialog(
            onDismissRequest = { showDatePicker = false },
            confirmButton = {
                TextButton(onClick = {
                    state.selectedDateMillis?.let { millis ->
                        date = Instant.ofEpochMilli(millis).atZone(ZoneOffset.UTC).toLocalDate()
                    }
                    showDatePicker = false
                }) { Text("OK") }
            },
            dismissButton = { TextButton(onClick = { showDatePicker = false }) { Text("Abbrechen") } },
        ) {
            DatePicker(state = state)
        }
    }

    if (showStartTimePicker) {
        TimePickerDialogHost(
            initial = startTime,
            onDismiss = { showStartTimePicker = false },
            onConfirm = { startTime = it },
        )
    }
    if (showEndTimePicker) {
        TimePickerDialogHost(
            initial = endTime,
            onDismiss = { showEndTimePicker = false },
            onConfirm = { endTime = it },
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TimePickerDialogHost(
    initial: LocalTime,
    onDismiss: () -> Unit,
    onConfirm: (LocalTime) -> Unit,
) {
    val state = rememberTimePickerState(
        initialHour = initial.hour,
        initialMinute = initial.minute,
        is24Hour = true,
    )
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(onClick = {
                onConfirm(LocalTime.of(state.hour, state.minute))
                onDismiss()
            }) { Text("OK") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Abbrechen") } },
        text = { TimePicker(state = state) },
    )
}
