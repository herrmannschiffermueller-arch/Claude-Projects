package com.example.calendarapp.auth

import android.content.Context
import android.content.Intent
import androidx.activity.result.IntentSenderRequest
import com.google.android.gms.auth.api.identity.AuthorizationClient
import com.google.android.gms.auth.api.identity.AuthorizationRequest
import com.google.android.gms.auth.api.identity.AuthorizationResult
import com.google.android.gms.auth.api.identity.Identity
import com.google.android.gms.common.api.ApiException
import com.google.android.gms.common.api.Scope
import kotlinx.coroutines.tasks.await

/**
 * Wraps the Google Identity Services Authorization API to obtain an OAuth access
 * token scoped to the user's Google Calendar, without requiring a full Google
 * Sign-In (no profile/name is read - only the Calendar scope is requested).
 *
 * See app/README section "Google Cloud Konfiguration" for the one-time OAuth
 * client setup this depends on.
 */
class GoogleAuthManager(context: Context) {

    private val authorizationClient: AuthorizationClient = Identity.getAuthorizationClient(context)

    @Volatile
    private var cachedAccessToken: String? = null

    private val request: AuthorizationRequest =
        AuthorizationRequest.builder()
            .setRequestedScopes(listOf(Scope(SCOPE_CALENDAR_EVENTS)))
            .build()

    /**
     * Requests (or silently refreshes) an access token for the calendar scope.
     * If the user has not yet granted the scope, returns [AuthOutcome.ConsentRequired]
     * with an [IntentSenderRequest] the caller must launch; the result Intent from
     * that launch is then passed to [onConsentResult].
     */
    suspend fun authorize(): AuthOutcome {
        return try {
            handleResult(authorizationClient.authorize(request).await())
        } catch (e: ApiException) {
            AuthOutcome.Failed(e.message ?: "Autorisierung fehlgeschlagen (Code ${e.statusCode})")
        }
    }

    /** Call from the ActivityResultLauncher callback after showing the consent screen. */
    fun onConsentResult(data: Intent?): AuthOutcome {
        return try {
            handleResult(authorizationClient.getAuthorizationResultFromIntent(data))
        } catch (e: ApiException) {
            AuthOutcome.Failed(e.message ?: "Zugriff wurde nicht erteilt")
        }
    }

    private fun handleResult(result: AuthorizationResult): AuthOutcome {
        val pendingIntent = result.pendingIntent
        return if (result.hasResolution() && pendingIntent != null) {
            AuthOutcome.ConsentRequired(
                IntentSenderRequest.Builder(pendingIntent.intentSender).build()
            )
        } else {
            val token = result.accessToken
            if (token != null) {
                cachedAccessToken = token
                AuthOutcome.Authorized(token)
            } else {
                AuthOutcome.Failed("Kein Access Token erhalten")
            }
        }
    }

    fun currentAccessToken(): String? = cachedAccessToken

    fun signOut() {
        cachedAccessToken = null
    }

    companion object {
        /**
         * "calendar.events" is enough to read/create/edit/delete events on calendars the
         * user already has - it does not allow creating or deleting whole calendars.
         */
        const val SCOPE_CALENDAR_EVENTS = "https://www.googleapis.com/auth/calendar.events"
    }
}

sealed interface AuthOutcome {
    data class Authorized(val accessToken: String) : AuthOutcome
    data class ConsentRequired(val intentSenderRequest: IntentSenderRequest) : AuthOutcome
    data class Failed(val message: String) : AuthOutcome
}
