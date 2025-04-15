package info.nightscout.androidaps.queue

import android.os.CountDownTimer
import info.nightscout.androidaps.plugins.source.OpenAPIPlugin
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException

class APICommander {
    companion object {

        private var initBasal: Double = 0.1
        private var timer: Thread? = null

        private fun sendInfoToAPI(insulin: Double, carbs: Double, path: String) {
            val client = OkHttpClient()

            val formBody = FormBody.Builder()
                .add("insulin", insulin.toString())
                .add("carbs", carbs.toString())
                .build()
            val request = Request.Builder()
                .url(OpenAPIPlugin.serverIP+path)
                .post(formBody)
                .build()

            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) throw IOException("Unexpected code $response")
            }
        }

        public fun BasalToAPI(insulinH: Double? = null) {
            if (insulinH == null){
                timer?.interrupt()
            }
            else{
                initBasal = insulinH
            }
            sendInfoToAPI(initBasal, 0.0, "/basal")
        }

        public fun TempBasalToAPI(absoluteRate: Double, durationInMinutes: Int) {
            if(absoluteRate == initBasal) {
                BasalToAPI()
            }
            else{
                timer?.interrupt()
                sendInfoToAPI(absoluteRate, 0.0, "/basal")
                timer = Thread{
                        try {
                            Thread.sleep(durationInMinutes.toLong() * 60000)
                            BasalToAPI()
                        }catch (e: InterruptedException){
                            timer = null
                        }
                    }
                timer?.start()
            }
        }

        public fun BolusToAPI(insulin: Double, carbs: Double) {
            sendInfoToAPI(insulin, carbs, "/bolus")
        }
    }
}