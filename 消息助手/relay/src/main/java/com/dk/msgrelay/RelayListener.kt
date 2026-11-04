package com.dk.msgrelay

import android.app.Notification
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build
import android.os.PowerManager
import android.os.Process
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification

class RelayListener : NotificationListenerService() {
    private var screenRx: BroadcastReceiver? = null

    override fun onListenerConnected() {
        instance = this
        L.i(this, "监听已连接 | 进程=${Process.myPid()} | ${Cfg.describe(this)}")
        // 记录亮屏、灭屏的时刻，用来判断原通知有没有把屏幕点亮
        val rx = object : BroadcastReceiver() {
            override fun onReceive(c: Context, i: Intent) {
                L.i(c, "屏幕 | ${if (i.action == Intent.ACTION_SCREEN_ON) "亮" else "灭"}")
            }
        }
        val f = IntentFilter().apply { addAction(Intent.ACTION_SCREEN_ON); addAction(Intent.ACTION_SCREEN_OFF) }
        if (Build.VERSION.SDK_INT >= 33) registerReceiver(rx, f, Context.RECEIVER_NOT_EXPORTED) else registerReceiver(rx, f)
        screenRx = rx
    }

    override fun onListenerDisconnected() {
        instance = null
        L.i(this, "监听已断开")
        screenRx?.let { unregisterReceiver(it) }
        screenRx = null
    }

    override fun onDestroy() {
        L.i(this, "监听服务销毁")
        super.onDestroy()
    }

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        if (sbn.packageName == packageName || !Cfg.watches(this, sbn.packageName)) return
        val n = sbn.notification
        val ex = n.extras
        val title = ex.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
        val text = (ex.getCharSequence(Notification.EXTRA_BIG_TEXT) ?: ex.getCharSequence(Notification.EXTRA_TEXT))?.toString() ?: ""
        val label = try {
            packageManager.getApplicationLabel(packageManager.getApplicationInfo(sbn.packageName, 0)).toString()
        } catch (_: Exception) { sbn.packageName }
        val r = Ranking()
        val ch = if (currentRanking?.getRanking(sbn.key, r) == true) r.channel else null
        val effect = if (ch == null) "渠道=?" else
            "渠道=${ch.id} 重要性=${ch.importance} 有声音=${ch.sound != null} 震动=${ch.shouldVibrate()}"
        val screenOn = getSystemService(PowerManager::class.java).isInteractive
        val summary = n.flags and Notification.FLAG_GROUP_SUMMARY != 0
        val ongoing = n.flags and Notification.FLAG_ONGOING_EVENT != 0
        val entry = n.contentIntent?.let { "有 创建者=${it.creatorPackage}" } ?: "无"
        L.i(this, "收到 | $label | ${sbn.packageName} | 标题=$title | 正文=$text | 发出=${L.t(sbn.postTime)} | " +
            "key=${sbn.key} | $effect | 亮屏=$screenOn | 入口=$entry | 组摘要=$summary 常驻=$ongoing")

        if (ongoing || !Cfg.cancelOrig(this)) return
        cancelNotification(sbn.key)
        L.i(this, "已收起 | ${sbn.key} | 距发出 ${System.currentTimeMillis() - sbn.postTime}ms")
        if (summary) return
        val item = Item(Store.nextIdx++, sbn.packageName, label, title, text, sbn.postTime, sbn.key, n.contentIntent, System.currentTimeMillis())
        Store.items.add(item)
        Store.pending.add(item)
        L.i(this, "入队 | #${item.idx} | ${item.label} | ${item.title} | 待推 ${Store.pending.size} 条")
        Batch.onQueued(this)
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification, rankingMap: RankingMap, reason: Int) {
        if (sbn.packageName == packageName || !Cfg.watches(this, sbn.packageName)) return
        L.i(this, "被移除 | ${sbn.key} | 原因码=$reason")
    }

    companion object { var instance: RelayListener? = null }
}
