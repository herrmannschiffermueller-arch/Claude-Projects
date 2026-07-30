package com.example.calendarapp.data

import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.PUT
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor

/** Thin REST client for the parts of the Google Calendar API v3 this app needs. */
interface GoogleCalendarApi {

    @GET("calendars/primary/events")
    suspend fun listEvents(
        @Header("Authorization") authorization: String,
        @Query("timeMin") timeMin: String,
        @Query("timeMax") timeMax: String,
        @Query("singleEvents") singleEvents: Boolean = true,
        @Query("orderBy") orderBy: String = "startTime",
    ): EventsListResponseDto

    @POST("calendars/primary/events")
    suspend fun insertEvent(
        @Header("Authorization") authorization: String,
        @Body event: EventDto,
    ): EventDto

    @PUT("calendars/primary/events/{eventId}")
    suspend fun updateEvent(
        @Header("Authorization") authorization: String,
        @Path("eventId") eventId: String,
        @Body event: EventDto,
    ): EventDto

    @DELETE("calendars/primary/events/{eventId}")
    suspend fun deleteEvent(
        @Header("Authorization") authorization: String,
        @Path("eventId") eventId: String,
    ): Response<Unit>

    companion object {
        private const val BASE_URL = "https://www.googleapis.com/calendar/v3/"

        fun create(): GoogleCalendarApi {
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BASIC
            }
            val client = OkHttpClient.Builder()
                .addInterceptor(logging)
                .build()
            return Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(GoogleCalendarApi::class.java)
        }
    }
}
