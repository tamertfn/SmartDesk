package com.surendramaran.yolov8tflite

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Matrix
import android.os.Bundle
import android.os.Vibrator
import android.os.VibrationEffect
import android.util.Base64
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.AspectRatio
import androidx.camera.core.Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.surendramaran.yolov8tflite.Constants.LABELS_PATH
import com.surendramaran.yolov8tflite.Constants.MODEL_PATH
import com.surendramaran.yolov8tflite.api.PredictionRequest
import com.surendramaran.yolov8tflite.api.PredictionResponse
import com.surendramaran.yolov8tflite.api.RetrofitClient
import com.surendramaran.yolov8tflite.databinding.ActivityMainBinding
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.InputStreamReader
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import org.json.JSONObject

class MainActivity : AppCompatActivity(), Detector.DetectorListener {
    private lateinit var binding: ActivityMainBinding
    private val isFrontCamera = false
    private var isObjectNameEntered = false
    private var targetObjectName: String = ""
    private var availableLabels: List<String> = emptyList()
    private var isTargetObjectFound = false
    private var isServerMode = false
    private var serverModeJob: Job? = null
    private var isServerModeObjectFound = false
    private var isAutoServerMode = false
    private val CONFIDENCE_THRESHOLD = 0.7f
    private var consecutiveNoDetections = 0
    private val MAX_CONSECUTIVE_NO_DETECTIONS = 30
    private var consecutiveLowConfidenceFrames = 0
    private val requiredLowConfidenceFrames = 30

    // Sadece server modunda aranacak class'lar
    private val serverOnlyClasses = setOf(
        "Apple-Pencil",
        "Calculator",
        "Charging-cable",
        "Keys",
        "Markers",
        "StudentID_card",
        "Wallet"
    )

    // Sadece edge modunda aranacak class'lar
    private val edgeOnlyClasses = setOf(
        "Flashlight",
        "Mug",
        "Bowl",
        "Camera",
        "Coin",
        "Personal care",
        "Fork",
        "Kitchen knife",
        "Spoon",
        "Glove",
        "IPod",
        "Necklace",
        "Snack"
    )

    private var preview: Preview? = null
    private var imageAnalyzer: ImageAnalysis? = null
    private var camera: Camera? = null
    private var cameraProvider: ProcessCameraProvider? = null
    private var detector: Detector? = null

    private lateinit var cameraExecutor: ExecutorService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        cameraExecutor = Executors.newSingleThreadExecutor()

        // Label dosyasını oku
        loadLabels()

        cameraExecutor.execute {
            detector = Detector(baseContext, MODEL_PATH, LABELS_PATH, this)
        }

        setupObjectInputDialog()
        setupServerMode()

        if (allPermissionsGranted()) {
            startCamera()
        } else {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS)
        }

        bindListeners()
    }

    private fun loadLabels() {
        try {
            val inputStream = assets.open("label.txt")
            val reader = BufferedReader(InputStreamReader(inputStream))
            availableLabels = reader.readLines().map { it.trim() }
            reader.close()
            Log.d(TAG, "Yüklenen etiketler: $availableLabels")
        } catch (e: Exception) {
            Log.e(TAG, "Label dosyası okunamadı", e)
        }
    }

    private fun setupObjectInputDialog() {
        binding.objectInputDialog.visibility = View.VISIBLE
        binding.confirmButton.setOnClickListener {
            val objectName = binding.objectNameInput.text.toString().trim()
            if (objectName.isNotEmpty()) {
                // Server-only class kontrolü
                if (serverOnlyClasses.any { it.equals(objectName, ignoreCase = true) }) {
                    isObjectNameEntered = true
                    targetObjectName = objectName
                    binding.objectInputDialog.visibility = View.GONE
                    isAutoServerMode = true
                    binding.serverModeSwitch.isChecked = true
                    Toast.makeText(this, "Bu nesne sadece server modunda aranabilir", Toast.LENGTH_LONG).show()
                }
                // Edge-only veya diğer class'lar için normal kontrol
                else if (availableLabels.any { it.equals(objectName, ignoreCase = true) }) {
                    isObjectNameEntered = true
                    targetObjectName = objectName
                    binding.objectInputDialog.visibility = View.GONE
                    Toast.makeText(this, "Aranacak nesne: $objectName", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Modelde bu nesne bulunmamaktadır", Toast.LENGTH_LONG).show()
                }
            } else {
                Toast.makeText(this, "Lütfen bir nesne ismi giriniz", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setupServerMode() {
        binding.serverModeSwitch.setOnCheckedChangeListener { _, isChecked ->
            // Edge-only class kontrolü
            if (isChecked && edgeOnlyClasses.any { it.equals(targetObjectName, ignoreCase = true) }) {
                // Edge-only class için server moduna geçişi engelle
                binding.serverModeSwitch.isChecked = false
                Toast.makeText(this, "Bu nesne sadece edge cihazda aranabilir", Toast.LENGTH_LONG).show()
                return@setOnCheckedChangeListener
            }

            isServerMode = isChecked
            if (isChecked) {
                startServerMode()
            } else {
                stopServerMode()
            }
        }
    }

    private fun startServerMode() {
        if (!isObjectNameEntered) {
            Toast.makeText(this, "Lütfen önce bir nesne ismi giriniz", Toast.LENGTH_SHORT).show()
            binding.serverModeSwitch.isChecked = false
            return
        }

        serverModeJob = CoroutineScope(Dispatchers.IO).launch {
            while (isServerMode) {
                try {
                    val bitmap = withContext(Dispatchers.Main) {
                        binding.viewFinder.bitmap
                    }
                    
                    if (bitmap != null) {
                        val outputStream = ByteArrayOutputStream()
                        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, outputStream)
                        val base64Image = Base64.encodeToString(outputStream.toByteArray(), Base64.DEFAULT)

                        val request = PredictionRequest(
                            image_base64 = base64Image,
                            target_class = targetObjectName
                        )
                        val response = RetrofitClient.predictionService.predict(request)
                        
                        when (response) {
                            is PredictionResponse.Success -> {
                                withContext(Dispatchers.Main) {
                                    drawServerModeBoundingBox(response)
                                    if (!isServerModeObjectFound) {
                                        isServerModeObjectFound = true
                                        Toast.makeText(this@MainActivity, "Nesne bulundu!", Toast.LENGTH_SHORT).show()
                                        // Telefonu titreştir
                                        val vibrator = getSystemService(VIBRATOR_SERVICE) as Vibrator
                                        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                                            vibrator.vibrate(VibrationEffect.createOneShot(500, VibrationEffect.DEFAULT_AMPLITUDE))
                                        } else {
                                            vibrator.vibrate(500)
                                        }
                                    }
                                }
                            }
                            is PredictionResponse.Error -> {
                                withContext(Dispatchers.Main) {
                                    if (isServerModeObjectFound) {
                                        isServerModeObjectFound = false
                                    }
                                }
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Server modu hatası: ${e.message}")
                }
                delay(2000) // 2 saniye bekle
            }
        }
    }

    private fun drawServerModeBoundingBox(response: PredictionResponse.Success) {
        val bbox = response.bbox
        if (bbox.size == 4) {
            val x1 = bbox[0].toFloat()
            val y1 = bbox[1].toFloat()
            val x2 = bbox[2].toFloat()
            val y2 = bbox[3].toFloat()

            // Görüntü boyutlarına göre normalize et
            val viewWidth = binding.viewFinder.width.toFloat()
            val viewHeight = binding.viewFinder.height.toFloat()

            val normalizedBox = BoundingBox(
                x1 = x1 / viewWidth,
                y1 = y1 / viewHeight,
                x2 = x2 / viewWidth,
                y2 = y2 / viewHeight,
                cx = (x1 + x2) / (2 * viewWidth),
                cy = (y1 + y2) / (2 * viewHeight),
                w = (x2 - x1) / viewWidth,
                h = (y2 - y1) / viewHeight,
                cnf = response.confidence.toFloat(),
                cls = 0,
                clsName = response.`class`,
                boxColor = Color.GREEN
            )

            binding.overlay.apply {
                setResults(listOf(normalizedBox))
                invalidate()
            }
        }
    }

    private fun stopServerMode() {
        serverModeJob?.cancel()
        serverModeJob = null
        isServerModeObjectFound = false
        isAutoServerMode = false
        consecutiveNoDetections = 0
        binding.overlay.clear()
    }

    private fun bindListeners() {
        binding.apply {
            isGpu.setOnCheckedChangeListener { buttonView, isChecked ->
                cameraExecutor.submit {
                    detector?.restart(isGpu = isChecked)
                }
                if (isChecked) {
                    buttonView.setBackgroundColor(ContextCompat.getColor(baseContext, R.color.orange))
                } else {
                    buttonView.setBackgroundColor(ContextCompat.getColor(baseContext, R.color.gray))
                }
            }
        }
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        cameraProviderFuture.addListener({
            cameraProvider  = cameraProviderFuture.get()
            bindCameraUseCases()
        }, ContextCompat.getMainExecutor(this))
    }

    private fun bindCameraUseCases() {
        val cameraProvider = cameraProvider ?: throw IllegalStateException("Camera initialization failed.")

        val rotation = binding.viewFinder.display.rotation

        val cameraSelector = CameraSelector
            .Builder()
            .requireLensFacing(CameraSelector.LENS_FACING_BACK)
            .build()

        preview = Preview.Builder()
            .setTargetRotation(rotation)
            .build()

        imageAnalyzer = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .setTargetRotation(binding.viewFinder.display.rotation)
            .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
            .build()

        imageAnalyzer?.setAnalyzer(cameraExecutor) { imageProxy ->
            val bitmapBuffer =
                Bitmap.createBitmap(
                    imageProxy.width,
                    imageProxy.height,
                    Bitmap.Config.ARGB_8888
                )
            imageProxy.use { bitmapBuffer.copyPixelsFromBuffer(imageProxy.planes[0].buffer) }
            imageProxy.close()

            val matrix = Matrix().apply {
                postRotate(imageProxy.imageInfo.rotationDegrees.toFloat())

                if (isFrontCamera) {
                    postScale(
                        -1f,
                        1f,
                        imageProxy.width.toFloat(),
                        imageProxy.height.toFloat()
                    )
                }
            }

            val rotatedBitmap = Bitmap.createBitmap(
                bitmapBuffer, 0, 0, bitmapBuffer.width, bitmapBuffer.height,
                matrix, true
            )

            detector?.detect(rotatedBitmap)
        }

        cameraProvider.unbindAll()

        try {
            camera = cameraProvider.bindToLifecycle(
                this,
                cameraSelector,
                preview,
                imageAnalyzer
            )

            preview?.setSurfaceProvider(binding.viewFinder.surfaceProvider)
        } catch(exc: Exception) {
            Log.e(TAG, "Use case binding failed", exc)
        }
    }

    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()) {
        if (it[Manifest.permission.CAMERA] == true) { startCamera() }
    }

    override fun onDestroy() {
        super.onDestroy()
        stopServerMode()
        detector?.close()
        cameraExecutor.shutdown()
    }

    override fun onResume() {
        super.onResume()
        if (allPermissionsGranted()){
            startCamera()
        } else {
            requestPermissionLauncher.launch(REQUIRED_PERMISSIONS)
        }
    }

    companion object {
        private const val TAG = "Camera"
        private const val REQUEST_CODE_PERMISSIONS = 10
        private val REQUIRED_PERMISSIONS = mutableListOf (
            Manifest.permission.CAMERA
        ).toTypedArray()
    }

    override fun onEmptyDetect() {
        runOnUiThread {
            binding.overlay.clear()
        }
    }

    override fun onDetect(boundingBoxes: List<BoundingBox>, inferenceTime: Long) {
        runOnUiThread {
            binding.inferenceTime.text = "${inferenceTime}ms"
            
            // Eğer server-only bir class aranıyorsa edge modunda tespit yapma
            if (serverOnlyClasses.any { it.equals(targetObjectName, ignoreCase = true) }) {
                return@runOnUiThread
            }
            
            // Hedef nesneyi kontrol et
            val targetBoxes = boundingBoxes.filter { 
                it.clsName.equals(targetObjectName, ignoreCase = true) 
            }
            
            if (targetBoxes.isNotEmpty()) {
                // En yüksek güven skoruna sahip kutuyu al
                val bestBox = targetBoxes.maxByOrNull { it.cnf }
                
                if (bestBox != null) {
                    consecutiveNoDetections = 0 // Tespit yapıldığında sayacı sıfırla
                    
                    if (!isTargetObjectFound) {
                        isTargetObjectFound = true
                        Toast.makeText(this, "Nesne bulundu!", Toast.LENGTH_SHORT).show()
                        // Telefonu titreştir
                        val vibrator = getSystemService(VIBRATOR_SERVICE) as Vibrator
                        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                            vibrator.vibrate(VibrationEffect.createOneShot(500, VibrationEffect.DEFAULT_AMPLITUDE))
                        } else {
                            vibrator.vibrate(500)
                        }

                        // Güven skoru düşükse, edge-only değilse ve server modu aktif değilse, server moduna geç
                        if (bestBox.cnf < CONFIDENCE_THRESHOLD && 
                            !edgeOnlyClasses.any { it.equals(targetObjectName, ignoreCase = true) } && 
                            !isServerMode && 
                            !isAutoServerMode) {
                            isAutoServerMode = true
                            binding.serverModeSwitch.isChecked = true
                            Toast.makeText(this, "Düşük güven skoru nedeniyle server moduna geçiliyor...", Toast.LENGTH_LONG).show()
                        }
                    }
                }
            } else {
                // Hedef nesne bulunamadı
                if (isTargetObjectFound) {
                    isTargetObjectFound = false
                    // Eğer otomatik geçiş yapıldıysa ve nesne kaybolduysa, server modunu kapat
                    if (isAutoServerMode) {
                        isAutoServerMode = false
                        binding.serverModeSwitch.isChecked = false
                    }
                } else {
                    // Hedef nesne bulunamadı ve daha önce de bulunamamıştı
                    consecutiveNoDetections++
                    
                    // Belirli sayıda ardışık tespit yapılamazsa ve edge-only değilse server moduna geç
                    if (consecutiveNoDetections >= MAX_CONSECUTIVE_NO_DETECTIONS && 
                        !edgeOnlyClasses.any { it.equals(targetObjectName, ignoreCase = true) } && 
                        !isServerMode && 
                        !isAutoServerMode) {
                        isAutoServerMode = true
                        binding.serverModeSwitch.isChecked = true
                        Toast.makeText(this, "Nesne tespit edilemediği için server moduna geçiliyor...", Toast.LENGTH_LONG).show()
                    }
                }
            }

            // Tüm kutuları güncelle
            val updatedBoxes = boundingBoxes.map { box ->
                if (box.clsName.equals(targetObjectName, ignoreCase = true)) {
                    box.copy(boxColor = Color.RED)
                } else {
                    box
                }
            }

            binding.overlay.apply {
                setResults(updatedBoxes)
                invalidate()
            }
        }
    }
}
