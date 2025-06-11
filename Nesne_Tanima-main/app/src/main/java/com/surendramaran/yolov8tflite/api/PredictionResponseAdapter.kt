package com.surendramaran.yolov8tflite.api

import com.google.gson.*
import java.lang.reflect.Type

class PredictionResponseAdapter : JsonDeserializer<PredictionResponse> {
    override fun deserialize(
        json: JsonElement,
        typeOfT: Type,
        context: JsonDeserializationContext
    ): PredictionResponse {
        val jsonObject = json.asJsonObject
        
        return if (jsonObject.has("message")) {
            PredictionResponse.Error(jsonObject.get("message").asString)
        } else {
            PredictionResponse.Success(
                `class` = jsonObject.get("class").asString,
                confidence = jsonObject.get("confidence").asDouble,
                bbox = jsonObject.get("bbox").asJsonArray.map { it.asInt }
            )
        }
    }
} 