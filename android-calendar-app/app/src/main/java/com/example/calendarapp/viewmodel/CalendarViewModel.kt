package com.example.calendarapp.viewmodel

import android.content.Context
import android.content.Intent
import androidx.activity.result.IntentSenderRequest
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.example.calendarapp.auth.AuthOutcome
import com.example.calendarapp.auth.GoogleAuthManager
import com.example.calendarapp.data.CalendarEvent
import com.example.calendarapp.data.CalendarRepository
import java.time.DayOfWeek
import java.time.LocalDate
import java.time.LocalTime
import java.time.YearMonth
import java.time.temporal.TemporalAdjusters
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException

class CalendarViewModel(
    private val authManager: GoogleAuthManager,
    private val repository: CalendarRepository = CalendarRepository(authManager),
) : ViewModel() {

    data class UiState(
        val isAuthorizing: Boolean = true,
        val isAuthorized: Boolean = false,
        val currentMonth: YearMonth = YearMonth.now(),
        val selectedDate: LocalDate = LocalDate.now(),
        val eventsByDate: Map<LocalDate, List<CalendarEvent>> = emptyMap(),
        val isLoadingEvents: Boolean = false,
        val errorMessage: String? = null,
    )

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    /** Emits a consent screen request the UI must launch via ActivityResultLauncher. */
    private val _consentRequests = MutableSharedFlow<IntentSenderRequest>(extraBufferCapacity = 1)
    val consentRequests: SharedFlow<IntentSenderRequest> = _consentRequests.asSharedFlow()

    init {
        attemptAuthorization()
    }

    fun attemptAuthorization() {
        viewModelScope.launch {
            _uiState.update { it.copy(isAuthorizing = true, errorMessage = null) }
            handleAuthOutcome(authManager.authorize())
        }
    }

    /** Feed the Intent returned by the launched consent screen back in here. */
    fun onConsentResult(data: Intent?) {
        handleAuthOutcome(authManager.onConsentResult(data))
    }

    private fun handleAuthOutcome(outcome: AuthOutcome) {
        when (outcome) {
            is AuthOutcome.Authorized -> {
                _uiState.update { it.copy(isAuthorizing = false, isAuthorized = true) }
                refresh()
            }
            is AuthOutcome.ConsentRequired -> {
                _uiState.update { it.copy(isAuthorizing = false) }
                _consentRequests.tryEmit(outcome.intentSenderRequest)
            }
            is AuthOutcome.Failed -> {
                _uiState.update {
                    it.copy(isAuthorizing = false, isAuthorized = false, errorMessage = outcome.message)
                }
            }
        }
    }

    fun goToPreviousMonth() = setMonth(_uiState.value.currentMonth.minusMonths(1))

    fun goToNextMonth() = setMonth(_uiState.value.currentMonth.plusMonths(1))

    private fun setMonth(month: YearMonth) {
        _uiState.update { it.copy(currentMonth = month) }
        refresh()
    }

    fun selectDate(date: LocalDate) {
        _uiState.update { it.copy(selectedDate = date) }
    }

    /** Re-fetches events for the currently displayed month grid (including spillover days). */
    fun refresh() {
        if (!_uiState.value.isAuthorized) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingEvents = true, errorMessage = null) }
            val month = _uiState.value.currentMonth
            val gridStart = month.atDay(1).with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY))
            val gridEnd = month.atEndOfMonth().with(TemporalAdjusters.nextOrSame(DayOfWeek.SUNDAY))
            runCatching { repository.fetchEvents(gridStart, gridEnd) }
                .onSuccess { events ->
                    _uiState.update {
                        it.copy(
                            isLoadingEvents = false,
                            eventsByDate = events
                                .groupBy { event -> event.date }
                                .mapValues { (_, dayEvents) ->
                                    dayEvents.sortedBy { it.startTime ?: LocalTime.MIN }
                                },
                        )
                    }
                }
                .onFailure { error -> onEventLoadFailure(error) }
        }
    }

    private fun onEventLoadFailure(error: Throwable) {
        _uiState.update { it.copy(isLoadingEvents = false, errorMessage = error.toUserMessage()) }
    }

    fun saveEvent(event: CalendarEvent, onSaved: () -> Unit = {}) {
        viewModelScope.launch {
            val result = runCatching {
                if (event.id == null) repository.createEvent(event) else repository.updateEvent(event)
            }
            result
                .onSuccess {
                    refresh()
                    onSaved()
                }
                .onFailure { error -> _uiState.update { it.copy(errorMessage = error.toUserMessage()) } }
        }
    }

    fun deleteEvent(event: CalendarEvent, onDeleted: () -> Unit = {}) {
        val id = event.id ?: return
        viewModelScope.launch {
            runCatching { repository.deleteEvent(id) }
                .onSuccess {
                    refresh()
                    onDeleted()
                }
                .onFailure { error -> _uiState.update { it.copy(errorMessage = error.toUserMessage()) } }
        }
    }

    fun dismissError() {
        _uiState.update { it.copy(errorMessage = null) }
    }

    private fun Throwable.toUserMessage(): String = when {
        this is HttpException && (code() == 401 || code() == 403) ->
            "Sitzung abgelaufen – bitte erneut anmelden."
        this is HttpException -> "Serverfehler (${code()})"
        else -> message ?: "Unbekannter Fehler"
    }

    companion object {
        fun factory(context: Context): ViewModelProvider.Factory = viewModelFactory {
            initializer { CalendarViewModel(GoogleAuthManager(context.applicationContext)) }
        }
    }
}
