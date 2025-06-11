package com.surendramaran.yolov8tflite.api

import retrofit2.http.Body
import retrofit2.http.POST

interface PredictionService {
    @POST("predict")
    suspend fun predict(@Body request: PredictionRequest): PredictionResponse
}

data class PredictionRequest(
    val image_base64: String,
    val target_class: String
)

sealed class PredictionResponse {
    data class Success(
        val `class`: String,
        val confidence: Double,
        val bbox: List<Int>
    ) : PredictionResponse()

    data class Error(
        val message: String
    ) : PredictionResponse()
} 