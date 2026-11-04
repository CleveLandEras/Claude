package com.dk.notitest

import android.Manifest
import android.app.Activity
import android.app.AlarmManager
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/** 发一条带编号 #k 的通知，点开落到 DetailActivity 并显示 #k。 */
object Poster {
    private const val CH = "test"

    fun post(ctx: Context, from: String, quiet: Boolean = false) {
        val p = ctx.getSharedPreferences("n", Context.MODE_PRIVATE)
        val k = p.getInt("k", 0) + 1
        p.edit().putInt("k", k).commit()
        val nm = ctx.getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(
            NotificationChannel(CH, "测试通知", NotificationManager.IMPORTANCE_HIGH).apply { enableVibration(true) }
        )
        val open = PendingIntent.getActivity(
            ctx, k,
            Intent(ctx, DetailActivity::class.java).putExtra("k", k)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        nm.createNotificationChannel(NotificationChannel("quiet", "测试通知（静音）", NotificationManager.IMPORTANCE_LOW))
        val now = SimpleDateFormat("HH:mm:ss", Locale.US).format(Date())
        val n = Notification.Builder(ctx, if (quiet) "quiet" else CH)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("测试通知 #$k")
            .setContentText("发出时间 $now（$from）")
            .setAutoCancel(true)
            .setContentIntent(open)
            .build()
        nm.notify(k, n)
        Log.i("NTEST", "发出 #$k | $now | $from")
    }

    fun later(ctx: Context, minutes: Int) {
        val pi = PendingIntent.getBroadcast(
            ctx, minutes,
            Intent(ctx, PostReceiver::class.java).putExtra("from", "${minutes}分钟定时"),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        ctx.getSystemService(AlarmManager::class.java)
            .setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, System.currentTimeMillis() + minutes * 60_000L, pi)
        Log.i("NTEST", "定时 | ${minutes} 分钟后发一条")
    }
}

class PostReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, i: Intent) {
        val later = i.getIntExtra("later", 0)
        if (later > 0) Poster.later(ctx, later) else Poster.post(ctx, i.getStringExtra("from") ?: "adb", i.getBooleanExtra("quiet", false))
    }
}

class MainActivity : Activity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(40, 40, 40, 40); fitsSystemWindows = true }
        root.addView(Button(this).apply { text = "发一条通知"; setOnClickListener { Poster.post(this@MainActivity, "按钮") } })
        root.addView(Button(this).apply { text = "30 分钟后发一条"; setOnClickListener { Poster.later(this@MainActivity, 30) } })
        setContentView(root)
    }
}

class DetailActivity : Activity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        val k = intent.getIntExtra("k", -1)
        setContentView(TextView(this).apply { textSize = 28f; setPadding(40, 200, 40, 40); text = "测试通知 #$k 的详情页" })
        Log.i("NTEST", "打开详情页 #$k")
    }
}
