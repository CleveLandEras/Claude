package com.dk.msgrelay

import android.app.ActivityOptions
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Handler
import android.os.Looper
import android.provider.Telephony
import android.util.Log
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/** 日志：同时写 logcat（标签 RELAY，adb 读）和应用私有文件（日志页读）。 */
object L {
    private val fmt = SimpleDateFormat("MM-dd HH:mm:ss.SSS", Locale.US)
    fun t(ms: Long): String = synchronized(fmt) { fmt.format(Date(ms)) }

    fun i(ctx: Context, msg: String) {
        val line = "${t(System.currentTimeMillis())} | $msg"
        Log.i("RELAY", line)
        try { File(ctx.filesDir, "log.txt").appendText(line + "\n") } catch (_: Exception) {}
    }

    fun read(ctx: Context): String =
        try { File(ctx.filesDir, "log.txt").readText() } catch (_: Exception) { "" }

    fun clear(ctx: Context) { File(ctx.filesDir, "log.txt").delete() }
}

/** 设置：开关页和 adb 指令都改这里。 */
object Cfg {
    fun p(ctx: Context) = ctx.getSharedPreferences("cfg", Context.MODE_PRIVATE)
    fun mode(ctx: Context) = p(ctx).getString("mode", "A")!!
    fun windowSec(ctx: Context) = p(ctx).getInt("window", 30)
    fun batchCount(ctx: Context) = p(ctx).getInt("count", 3)
    fun cancelOrig(ctx: Context) = p(ctx).getBoolean("cancel", true)
    fun autoFlush(ctx: Context) = p(ctx).getBoolean("auto", true)

    fun watch(ctx: Context): Set<String> {
        val s = p(ctx).getString("watch", null)
        if (s != null) return s.split(",").map { it.trim() }.filter { it.isNotEmpty() }.toSet()
        return setOfNotNull("com.tencent.mm", "com.dk.notitest", Telephony.Sms.getDefaultSmsPackage(ctx))
    }

    /** 名单里写 *3 表示所有自装（非系统）应用都算。 */
    fun watches(ctx: Context, pkg: String): Boolean {
        val w = watch(ctx)
        if (pkg in w) return true
        if ("*3" !in w) return false
        return try {
            ctx.packageManager.getApplicationInfo(pkg, 0).flags and android.content.pm.ApplicationInfo.FLAG_SYSTEM == 0
        } catch (_: Exception) { false }
    }

    fun describe(ctx: Context) =
        "做法=${mode(ctx)} 批次=${windowSec(ctx)}秒或${batchCount(ctx)}条 收起原通知=${cancelOrig(ctx)} " +
            "自动推=${autoFlush(ctx)} 名单=${watch(ctx).joinToString(",")}"
}

/** 拦下的一条通知。入口（PendingIntent）只能存在内存里，进程被杀就没了。 */
class Item(
    val idx: Int, val pkg: String, val label: String, val title: String, val text: String,
    val postTime: Long, val key: String, val pi: PendingIntent?, val gotAt: Long,
) {
    var reposts = 0
}

object Store {
    val items = mutableListOf<Item>()
    val pending = mutableListOf<Item>()
    var nextIdx = 1
}

/** 攒批：第一条入队起计时，到时间或凑够条数就推一批。 */
object Batch {
    private val h = Handler(Looper.getMainLooper())
    private var appCtx: Context? = null
    private val timer = Runnable { appCtx?.let { flush(it, "到时间") } }

    fun onQueued(ctx: Context) {
        appCtx = ctx.applicationContext
        if (!Cfg.autoFlush(ctx)) return
        val n = Cfg.batchCount(ctx)
        if (Store.pending.size >= n) flush(ctx, "凑够${n}条")
        else if (Store.pending.size == 1) h.postDelayed(timer, Cfg.windowSec(ctx) * 1000L)
    }

    fun flush(ctx: Context, why: String) {
        h.removeCallbacks(timer)
        if (Store.pending.isEmpty()) { L.i(ctx, "推送一批 | $why | 没有待推的"); return }
        val mode = Cfg.mode(ctx)
        L.i(ctx, "推送一批 | $why | ${Store.pending.size} 条 | 做法$mode")
        Store.pending.forEach { Reposter.post(ctx, it, mode) }
        Store.pending.clear()
    }
}

/** 由我们重推。A：直接挂原通知的入口；B：挂我们的透明页，由它转发原入口。 */
object Reposter {
    private const val CH = "relay"

    fun post(ctx: Context, item: Item, mode: String) {
        val nm = ctx.getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(NotificationChannel(CH, "重推的通知", NotificationManager.IMPORTANCE_HIGH))
        val entry: PendingIntent? = if (mode == "A") item.pi else PendingIntent.getActivity(
            ctx, item.idx,
            Intent(ctx, TrampolineActivity::class.java).putExtra("idx", item.idx)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        val n = Notification.Builder(ctx, CH)
            .setSmallIcon(android.R.drawable.sym_action_chat)
            .setContentTitle("[${item.label}] ${item.title}")
            .setContentText(item.text)
            .setSubText("#${item.idx} 做法$mode")
            .setWhen(item.postTime).setShowWhen(true)
            .setAutoCancel(true)
            .setContentIntent(entry)
            .build()
        item.reposts++
        nm.notify(1000 + item.idx, n)
        L.i(ctx, "重推 | #${item.idx} | 做法$mode | ${item.label} | ${item.title} | 入口=${if (entry == null) "无" else "有"}")
    }

    /** 做法 B 的转发：带上「允许后台启动页面」选项（安卓 14 起要显式声明）。 */
    fun forward(ctx: Context, idx: Int) {
        val item = Store.items.find { it.idx == idx }
        val pi = item?.pi
        if (pi == null) {
            L.i(ctx, "B 跳转失败 | #$idx | ${if (item == null) "内存里没有这条（进程重启过）" else "原通知没有入口"}")
            return
        }
        try {
            val opts = ActivityOptions.makeBasic()
            if (android.os.Build.VERSION.SDK_INT >= 33) {
                opts.setPendingIntentBackgroundActivityStartMode(ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOWED)
            }
            pi.send(ctx, 0, null, null, null, null, opts.toBundle())
            L.i(ctx, "B 已发出原入口 | #$idx | ${item.label} | ${item.title}")
        } catch (e: PendingIntent.CanceledException) {
            L.i(ctx, "B 跳转失败 | #$idx | 原入口已作废")
        } catch (e: Exception) {
            L.i(ctx, "B 跳转失败 | #$idx | ${e.javaClass.simpleName}: ${e.message}")
        }
    }
}
