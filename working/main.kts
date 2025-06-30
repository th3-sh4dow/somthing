package com.sh4dow.jarvis_test

import android.Manifest
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.content.Intent
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.core.app.ActivityCompat
import coil.compose.rememberAsyncImagePainter
import java.util.Locale
import kotlinx.coroutines.*
import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject
import android.widget.Toast
import android.content.pm.PackageManager
import android.speech.tts.TextToSpeech
import android.util.Log
import android.speech.tts.UtteranceProgressListener
import okhttp3.*
import java.io.IOException
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody

class MainActivity : ComponentActivity() {
    private var speechRecognizer: SpeechRecognizer? = null
    private lateinit var tts: TextToSpeech

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 1)
        }

        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts.language = Locale.US
            }
        }

        tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onDone(utteranceId: String?) {
                runOnUiThread {
                    // Uncomment to auto-listen
                    // isListening = true
                }
            }
            override fun onError(utteranceId: String?) {}
            override fun onStart(utteranceId: String?) {}
        })

        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    VoiceInputUI()
                }
            }
        }
    }

    override fun onDestroy() {
        speechRecognizer?.destroy()
        if (::tts.isInitialized) {
            tts.stop()
            tts.shutdown()
        }
        super.onDestroy()
    }

    private suspend fun isServerAvailable(): Boolean {
        return try {
            val url = URL("http://192.168.31.74:5000/ask")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "OPTIONS"
            connection.connectTimeout = 3000
            connection.responseCode == 200 || connection.responseCode == 405
        } catch (e: Exception) {
            false
        }
    }

    private fun checkServerConnection(onResult: (Boolean) -> Unit) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val url = URL("http://192.168.31.74:5000/connect")
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "GET"
                val responseCode = connection.responseCode
                connection.disconnect()

                withContext(Dispatchers.Main) {
                    onResult(responseCode == 200)
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    onResult(false)
                }
            }
        }
    }

    @Composable
    fun ServerStatusBar() {
        var serverOnline by remember { mutableStateOf(false) }
        var connecting by remember { mutableStateOf(false) }

        LaunchedEffect(Unit) {
            connecting = true
            checkServerConnection { success ->
                serverOnline = success
                connecting = false
            }
        }

        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp)
        ) {
            Text("Server Status: ", color = Color.White)
            Box(
                modifier = Modifier
                    .size(16.dp)
                    .padding(start = 8.dp, end = 16.dp)
                    .background(
                        if (serverOnline) Color.Green else Color.Red,
                        shape = CircleShape
                    )
            )
            Button(
                onClick = {
                    connecting = true
                    checkServerConnection { success ->
                        serverOnline = success
                        connecting = false
                    }
                },
                enabled = !connecting
            ) {
                Text(if (serverOnline) "Connected ✅" else "Connect 🔌")
            }
        }
    }

    @Composable
    fun VoiceInputUI() {
        var spokenText by remember { mutableStateOf("Press button to speak") }
        var isListening by remember { mutableStateOf(false) }
        var result by remember { mutableStateOf("") }
        val context = this

        val speechRecognizer = remember {
            SpeechRecognizer.createSpeechRecognizer(context)
        }
        val speechIntent = remember {
            Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            }
        }

        DisposableEffect(Unit) {
            onDispose {
                speechRecognizer.destroy()
            }
        }

        LaunchedEffect(isListening) {
            if (isListening) {
                speechRecognizer.setRecognitionListener(object : RecognitionListener {
                    override fun onReadyForSpeech(params: Bundle?) {}
                    override fun onBeginningOfSpeech() {}
                    override fun onRmsChanged(rmsdB: Float) {}
                    override fun onBufferReceived(buffer: ByteArray?) {}
                    override fun onEndOfSpeech() {}
                    override fun onError(error: Int) {
                        isListening = false
                        spokenText = "Error recognizing speech: $error"
                    }
                    override fun onResults(results: Bundle?) {
                        isListening = false
                        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        if (!matches.isNullOrEmpty()) {
                            spokenText = matches[0]
                            Log.d("JARVIS_APP", "Recognized voice input: $spokenText")
                            sendToServer(spokenText) { replyText ->
                                spokenText = replyText
                                result = replyText
                                handleServerResponse(replyText)
                                tts.speak(replyText, TextToSpeech.QUEUE_FLUSH, null, "jarvis_response")
                            }
                        }
                    }
                    override fun onPartialResults(partialResults: Bundle?) {}
                    override fun onEvent(eventType: Int, params: Bundle?) {}
                })
                speechRecognizer.startListening(speechIntent)
            }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black)
                .padding(16.dp),
            verticalArrangement = Arrangement.Center
        ) {
            ServerStatusBar()
            Text(text = spokenText, style = MaterialTheme.typography.titleLarge, color = Color.White)
            Spacer(modifier = Modifier.height(20.dp))
            if (isListening) {
                Image(
                    painter = rememberAsyncImagePainter(model = "file:///android_asset/Jarvis.gif"),
                    contentDescription = "Listening Animation",
                    modifier = Modifier.size(96.dp)
                )
                Spacer(modifier = Modifier.height(20.dp))
            }
            Button(
                onClick = { isListening = true },
                enabled = !isListening
            ) {
                Text("🎙 Start Listening")
            }
            Spacer(modifier = Modifier.height(20.dp))
            if (result.isNotEmpty()) {
                Text("Response:\n$result", color = Color.White)
            }
        }
    }

    private fun handleServerResponse(response: String) {
        when {
            response.startsWith("open", ignoreCase = true) -> {
                val app = response.removePrefix("open").trim().lowercase()
                openApp(app)
            }
            else -> { /* Default: handled in UI */ }
        }
    }

    private fun openApp(appName: String) {
        val appPackageMap = mapOf(
            "chrome" to "com.android.chrome",
            "youtube" to "com.google.android.youtube",
            "gmail" to "com.google.android.gm",
            "whatsapp" to "com.whatsapp",
            "settings" to "com.android.settings",
            "camera" to "com.android.camera"
        )
        val key = appPackageMap.keys.find { appName.contains(it, ignoreCase = true) }
        val pkg = key?.let { appPackageMap[it] }
        if (pkg != null) {
            val intent = packageManager.getLaunchIntentForPackage(pkg)
            if (intent != null) {
                startActivity(intent)
            } else {
                Toast.makeText(this, "App not found", Toast.LENGTH_SHORT).show()
            }
        } else {
            Toast.makeText(this, "Unknown app: $appName", Toast.LENGTH_SHORT).show()
        }
    }

    private fun sendToServer(prompt: String, onResult: (String) -> Unit) {
        val client = OkHttpClient()
        val url = "http://192.168.31.74:5000/ask"
        val json = JSONObject().put("query", prompt)
        val body = json.toString().toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url(url)
            .post(body)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    val errorMsg = "❌ Failed to connect:\n${e.localizedMessage}"
                    Log.e("JARVIS", errorMsg, e)
                    Toast.makeText(applicationContext, errorMsg, Toast.LENGTH_LONG).show()
                    onResult(errorMsg)
                }
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
                    val raw = try {
                        response.body?.string()?.trim()
                    } catch (e: Exception) {
                        Log.e("JARVIS", "Error reading response", e)
                        null
                    }

                    runOnUiThread {
                        if (raw.isNullOrEmpty()) {
                            val msg = "⚠️ Empty or null response from server."
                            Log.w("JARVIS", msg)
                            onResult(msg)
                            return@runOnUiThread
                        }

                        try {
                            if (!raw.startsWith("{") || !raw.endsWith("}")) {
                                val msg = "⚠️ Invalid JSON response:\n$raw"
                                Log.e("JARVIS", msg)
                                onResult(msg)
                                return@runOnUiThread
                            }

                            val json = JSONObject(raw)
                            val replyText = json.optString("response", "⚠️ 'response' key not found.")
                            Log.d("JARVIS_RESPONSE", replyText)
                            onResult(replyText)
                        } catch (e: Exception) {
                            val msg = "⚠️ Failed to parse JSON:\n${e.localizedMessage}\nRaw: $raw"
                            Log.e("JARVIS_PARSE", msg, e)
                            onResult(msg)
                        }
                    }
                }
            }
        })
    }
}

