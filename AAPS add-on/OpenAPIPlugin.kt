package info.nightscout.androidaps.plugins.source

import android.content.Context
import android.net.Uri
import android.os.Handler
import android.os.HandlerThread
import dagger.android.HasAndroidInjector
import info.nightscout.androidaps.Constants
import info.nightscout.androidaps.R
import info.nightscout.androidaps.database.AppRepository
import info.nightscout.androidaps.database.entities.GlucoseValue
import info.nightscout.androidaps.database.entities.TherapyEvent
import info.nightscout.androidaps.database.entities.UserEntry
import info.nightscout.androidaps.database.entities.ValueWithUnit
import info.nightscout.androidaps.database.transactions.CgmSourceTransaction
import info.nightscout.androidaps.interfaces.BgSource
import info.nightscout.androidaps.interfaces.PluginBase
import info.nightscout.androidaps.interfaces.PluginDescription
import info.nightscout.androidaps.interfaces.PluginType
import info.nightscout.shared.logging.AAPSLogger
import info.nightscout.shared.logging.LTag
import info.nightscout.androidaps.logging.UserEntryLogger
import info.nightscout.androidaps.utils.DateUtil
import info.nightscout.androidaps.utils.FabricPrivacy
import info.nightscout.androidaps.utils.T
import info.nightscout.androidaps.utils.XDripBroadcast
import info.nightscout.androidaps.interfaces.ResourceHelper
import info.nightscout.shared.sharedPreferences.SP
import io.reactivex.rxjava3.disposables.CompositeDisposable
import okhttp3.*
import java.io.IOException
import java.net.URL
import java.time.Instant
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OpenAPIPlugin @Inject constructor(
    injector: HasAndroidInjector,
    resourceHelper: ResourceHelper,
    aapsLogger: AAPSLogger,
    private val sp: SP,
    private val context: Context,
    private val repository: AppRepository,
    private val xDripBroadcast: XDripBroadcast,
    private val dateUtil: DateUtil,
    private val uel: UserEntryLogger,
    private val fabricPrivacy: FabricPrivacy
) : PluginBase(
    PluginDescription()
        .mainType(PluginType.BGSOURCE)
        .fragmentClass(BGSourceFragment::class.java.name)
        .pluginIcon(R.drawable.ic_generic_cgm)
        .pluginName(R.string.openapi)
        .shortName(R.string.openapi_short)
        .preferencesId(R.xml.pref_bgsource)
        .description(R.string.openapi),
    aapsLogger, resourceHelper, injector
), BgSource {

    private val sensor = GlucoseValue.SourceSensor.DEXCOM_G5_NATIVE

    private val handler = Handler(HandlerThread(this::class.java.simpleName + "Handler").also { it.start() }.looper)
    private lateinit var refreshLoop: Runnable

    private val contentUri: Uri = Uri.parse("content://$AUTHORITY/$TABLE_NAME")

    init {
        refreshLoop = Runnable {
            try {
                handleNewData()
            } catch (e: Exception) {
                fabricPrivacy.logException(e)
                aapsLogger.error("Error while processing data", e)
            }
            val lastReadTimestamp = sp.getLong(R.string.key_last_processed_glunovo_timestamp, 0L)
            val differenceToNow = INTERVAL - (dateUtil.now() - lastReadTimestamp) % INTERVAL + T.secs(10).msecs()
            handler.postDelayed(refreshLoop, T.mins(5L).msecs())
        }
    }

    private val disposable = CompositeDisposable()

    override fun onStart() {
        super.onStart()
        try {
            val client = OkHttpClient()
            val formBody = FormBody.Builder()
                .add("name", "currentTimeStamp")
                .build()
            val request = Request.Builder()
                .url(serverIP + "/initialize")
                .post(formBody)
                .build()
            var bg = ""
            val thread = Thread(Runnable {
                client.newCall(request).execute().use { response ->
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")
                }
            })
            thread.start()
            thread.join()
        }
        catch (e:Exception)
        {
            println(e)
        }
        handler.postDelayed(refreshLoop, T.mins(5L).msecs()) // do not start immediately, app may be still starting
    }

    override fun onStop() {
        super.onStop()
        handler.removeCallbacks(refreshLoop)
        disposable.clear()
    }

    private fun makeBgRequest(): String {
        val client = OkHttpClient()
        val currentTimeStamp = Instant.now().getEpochSecond().toString()

        val formBody = FormBody.Builder()
            .add("timestamp", currentTimeStamp)
            .build()
        val request = Request.Builder()
            .url("$serverIP/getBG")
            .post(formBody)
            .build()
        var bg = ""

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response")
            else bg = response.body!!.string()
        }

        return bg
    }

    private fun handleNewData() {
        if (!isEnabled()) return
        try {
            val receivedData = makeBgRequest().split('|')
            val timestamp = receivedData[0].toLong()
            val value = receivedData[1].toDouble()

            val glucoseValues = mutableListOf<CgmSourceTransaction.TransactionGlucoseValue>()
            val calibrations = mutableListOf<CgmSourceTransaction.Calibration>()
            if (timestamp > dateUtil.now() || timestamp == 0L) {
                aapsLogger.error(LTag.BGSOURCE, "Error in received data date/time $timestamp")
                return
            }
            if (value < 35 || value > 450) {
                aapsLogger.error(LTag.BGSOURCE, "Error in received data value (value out of bounds) $value")
                return
            }
            glucoseValues += CgmSourceTransaction.TransactionGlucoseValue(
            timestamp = dateUtil.now(),
            value = value,
            raw = 0.0,
            noise = null,
            trendArrow = GlucoseValue.TrendArrow.NONE,
            sourceSensor = sensor
            )

            if (glucoseValues.isNotEmpty())
                repository.runTransactionForResult(CgmSourceTransaction(glucoseValues, calibrations, null))
                    .doOnError {
                        aapsLogger.error(LTag.DATABASE, "Error while saving values from the API", it)
                    }
                    .blockingGet()
                    .also { savedValues ->
                        savedValues.inserted.forEach {
                            xDripBroadcast.send(it)
                            aapsLogger.debug(LTag.DATABASE, "Inserted bg $it")
                        }
                        savedValues.calibrationsInserted.forEach { calibration ->
                            calibration.glucose?.let { glucosevalue ->
                                uel.log(
                                    UserEntry.Action.CALIBRATION,
                                    UserEntry.Sources.Dexcom,
                                    ValueWithUnit.Timestamp(calibration.timestamp),
                                    ValueWithUnit.TherapyEventType(calibration.type),
                                    ValueWithUnit.fromGlucoseUnit(glucosevalue, calibration.glucoseUnit.toString)
                                )
                            }
                            aapsLogger.debug(LTag.DATABASE, "Inserted calibration $calibration")
                        }
                    }

        }
        catch (e: SecurityException) {
            aapsLogger.error(LTag.CORE, "Exception", e)
        }
    }

    override fun shouldUploadToNs(glucoseValue: GlucoseValue): Boolean =
        glucoseValue.sourceSensor == GlucoseValue.SourceSensor.GLUNOVO_NATIVE && sp.getBoolean(R.string.key_dexcomg5_nsupload, false)

    companion object {

        const val serverIP: String = "http://172.16.100.1:5001"

        @Suppress("SpellCheckingInspection")
        const val AUTHORITY = "alexpr.co.uk.infinivocgm.cgm_db.CgmExternalProvider/"
        const val TABLE_NAME = "CgmReading"
        const val INTERVAL = 180000L // 3 min
    }
}
