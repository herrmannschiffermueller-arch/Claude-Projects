package com.example.calendarapp.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.example.calendarapp.data.CalendarEvent
import com.example.calendarapp.ui.components.AddEditEventDialog
import com.example.calendarapp.ui.components.MonthGrid
import com.example.calendarapp.viewmodel.CalendarViewModel
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.TextStyle as JavaTextStyle
import java.util.Locale

@Composable
fun CalendarRoute(viewModel: CalendarViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    when {
        uiState.isAuthorizing -> LoadingScreen()
        !uiState.isAuthorized -> SignInScreen(
            errorMessage = uiState.errorMessage,
            onSignIn = viewModel::attemptAuthorization,
        )
        else -> CalendarScreen(
            uiState = uiState,
            onPreviousMonth = viewModel::goToPreviousMonth,
            onNextMonth = viewModel::goToNextMonth,
            onDaySelected = viewModel::selectDate,
            onSaveEvent = { viewModel.saveEvent(it) },
            onDeleteEvent = { viewModel.deleteEvent(it) },
            onDismissError = viewModel::dismissError,
        )
    }
}

@Composable
private fun LoadingScreen() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator()
    }
}

@Composable
private fun SignInScreen(errorMessage: String?, onSignIn: () -> Unit) {
    Column(
        Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text("Kalender", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(8.dp))
        Text(
            "Melde dich mit deinem Google-Konto an, um deinen Kalender zu sehen und zu bearbeiten.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(24.dp))
        Button(onClick = onSignIn) { Text("Mit Google anmelden") }
        errorMessage?.let { message ->
            Spacer(Modifier.height(16.dp))
            Text(message, color = MaterialTheme.colorScheme.error, textAlign = TextAlign.Center)
        }
    }
}

@Composable
private fun CalendarScreen(
    uiState: CalendarViewModel.UiState,
    onPreviousMonth: () -> Unit,
    onNextMonth: () -> Unit,
    onDaySelected: (LocalDate) -> Unit,
    onSaveEvent: (CalendarEvent) -> Unit,
    onDeleteEvent: (CalendarEvent) -> Unit,
    onDismissError: () -> Unit,
) {
    var dialogEvent by remember { mutableStateOf<CalendarEvent?>(null) }
    var showAddDialog by remember { mutableStateOf(false) }

    val monthTitle = remember(uiState.currentMonth) {
        val month = uiState.currentMonth
        val monthName = month.month.getDisplayName(JavaTextStyle.FULL, Locale.getDefault())
            .replaceFirstChar { it.titlecase(Locale.getDefault()) }
        "$monthName ${month.year}"
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(monthTitle) },
                navigationIcon = {
                    IconButton(onClick = onPreviousMonth) {
                        Icon(Icons.Default.ChevronLeft, contentDescription = "Vorheriger Monat")
                    }
                },
                actions = {
                    IconButton(onClick = onNextMonth) {
                        Icon(Icons.Default.ChevronRight, contentDescription = "Nächster Monat")
                    }
                },
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { showAddDialog = true }) {
                Icon(Icons.Default.Add, contentDescription = "Termin hinzufügen")
            }
        },
    ) { padding ->
        Column(Modifier.padding(padding).fillMaxSize()) {
            if (uiState.isLoadingEvents) {
                LinearProgressIndicator(Modifier.fillMaxWidth())
            }
            MonthGrid(
                month = uiState.currentMonth,
                selectedDate = uiState.selectedDate,
                today = LocalDate.now(),
                daysWithEvents = uiState.eventsByDate.keys,
                onDaySelected = onDaySelected,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            )
            HorizontalDivider()
            val dayEvents = uiState.eventsByDate[uiState.selectedDate].orEmpty()
            if (dayEvents.isEmpty()) {
                Box(Modifier.fillMaxWidth().padding(32.dp), contentAlignment = Alignment.Center) {
                    Text(
                        "Keine Termine an diesem Tag",
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            } else {
                LazyColumn(
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    items(dayEvents, key = { it.id ?: it.hashCode() }) { event ->
                        EventRow(event = event, onClick = { dialogEvent = event })
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        AddEditEventDialog(
            initialDate = uiState.selectedDate,
            existingEvent = null,
            onDismiss = { showAddDialog = false },
            onSave = {
                onSaveEvent(it)
                showAddDialog = false
            },
            onDelete = { showAddDialog = false },
        )
    }
    dialogEvent?.let { event ->
        AddEditEventDialog(
            initialDate = event.date,
            existingEvent = event,
            onDismiss = { dialogEvent = null },
            onSave = {
                onSaveEvent(it)
                dialogEvent = null
            },
            onDelete = {
                onDeleteEvent(it)
                dialogEvent = null
            },
        )
    }

    uiState.errorMessage?.let { message ->
        AlertDialog(
            onDismissRequest = onDismissError,
            confirmButton = { TextButton(onClick = onDismissError) { Text("OK") } },
            title = { Text("Fehler") },
            text = { Text(message) },
        )
    }
}

@Composable
private fun EventRow(event: CalendarEvent, onClick: () -> Unit) {
    val timeFormatter = remember { DateTimeFormatter.ofPattern("HH:mm") }
    Card(onClick = onClick, modifier = Modifier.fillMaxWidth()) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.width(64.dp)) {
                if (event.isAllDay) {
                    Text("Ganztägig", style = MaterialTheme.typography.labelSmall)
                } else {
                    Text(
                        event.startTime?.format(timeFormatter).orEmpty(),
                        style = MaterialTheme.typography.titleMedium,
                    )
                    event.endTime?.let { end ->
                        Text(end.format(timeFormatter), style = MaterialTheme.typography.labelSmall)
                    }
                }
            }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(event.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Medium)
                if (event.description.isNotBlank()) {
                    Text(event.description, style = MaterialTheme.typography.bodyMedium, maxLines = 2)
                }
            }
        }
    }
}
