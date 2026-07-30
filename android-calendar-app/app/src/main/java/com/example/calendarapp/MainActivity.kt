package com.example.calendarapp

import android.content.IntentSender
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.IntentSenderRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.lifecycle.lifecycleScope
import com.example.calendarapp.ui.CalendarRoute
import com.example.calendarapp.ui.theme.CalendarAppTheme
import com.example.calendarapp.viewmodel.CalendarViewModel
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private val viewModel: CalendarViewModel by viewModels { CalendarViewModel.factory(this) }

    private val consentLauncher = registerForActivityResult(
        ActivityResultContracts.StartIntentSenderForResult(),
    ) { result ->
        viewModel.onConsentResult(result.data)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.consentRequests.collect { request: IntentSenderRequest ->
                try {
                    consentLauncher.launch(request)
                } catch (e: IntentSender.SendIntentException) {
                    // Consent screen could not be shown; user can retry via the sign-in button.
                }
            }
        }

        setContent {
            CalendarAppTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    CalendarRoute(viewModel = viewModel)
                }
            }
        }
    }
}
