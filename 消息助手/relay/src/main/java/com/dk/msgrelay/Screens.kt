package com.dk.msgrelay

import android.Manifest
import android.app.Activity
import android.app.NotificationManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Process
import android.provider.Settings
import android.text.InputType
import android.view.View
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.ScrollView
import android.widget.TextView

/** 开关页：授权状态、A/B 切换、批次参数、监听名单、立即推送、日志入口。 */
class MainActivity : Activity() {
    private lateinit var status: TextView

    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)

        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(40, 40, 40, 40) }
        status = TextView(this).apply { textSize = 15f }
        root.addView(status)
        root.addView(button("去授权通知读取") { startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)) })

        val group = RadioGroup(this)
        val a = RadioButton(this).apply { id = View.generateViewId(); text = "做法 A：直接挂原通知的入口" }
        val bb = RadioButton(this).apply { id = View.generateViewId(); text = "做法 B：先进透明页，再转发原入口" }
        group.addView(a); group.addView(bb)
        group.check(if (Cfg.mode(this) == "A") a.id else bb.id)
        group.setOnCheckedChangeListener { _, id -> save { putString("mode", if (id == a.id) "A" else "B") } }
        root.addView(group)

        root.addView(check("收起原通知", Cfg.cancelOrig(this)) { v -> save { putBoolean("cancel", v) } })
        root.addView(check("到批次自动推（关掉＝只存不推）", Cfg.autoFlush(this)) { v -> save { putBoolean("auto", v) } })
        val window = field("批次时间（秒）", Cfg.windowSec(this).toString(), true)
        val count = field("批次条数", Cfg.batchCount(this).toString(), true)
        val watch = field("监听的应用包名（逗号隔开）", Cfg.watch(this).joinToString(","), false)
        listOf(window, count, watch).forEach { root.addView(it) }
        root.addView(button("保存批次和名单") {
            save {
                putInt("window", window.text.toString().toIntOrNull() ?: 30)
                putInt("count", count.text.toString().toIntOrNull() ?: 3)
                putString("watch", watch.text.toString())
            }
        })
        root.addView(button("立即推送") { Batch.flush(this, "手动"); refresh() })
        root.addView(button("看日志") { startActivity(Intent(this, LogActivity::class.java)) })
        setContentView(ScrollView(this).apply { fitsSystemWindows = true; addView(root) })
    }

    override fun onResume() { super.onResume(); requestRebind(this, "打开开关页"); refresh() }

    private fun refresh() {
        val granted = Settings.Secure.getString(contentResolver, "enabled_notification_listeners")
            ?.contains(packageName) == true
        status.text = "通知读取：${if (granted) "已授权" else "未授权"}\n${Cfg.describe(this)}\n" +
            "已拦 ${Store.items.size} 条，待推 ${Store.pending.size} 条"
    }

    private fun save(block: android.content.SharedPreferences.Editor.() -> Unit) {
        Cfg.p(this).edit().apply(block).apply()
        L.i(this, "设置 | ${Cfg.describe(this)}")
        refresh()
    }

    private fun button(t: String, f: () -> Unit) = Button(this).apply { text = t; setOnClickListener { f() } }
    private fun check(t: String, v: Boolean, f: (Boolean) -> Unit) =
        CheckBox(this).apply { text = t; isChecked = v; setOnCheckedChangeListener { _, x -> f(x) } }
    private fun field(hint: String, v: String, number: Boolean) = EditText(this).apply {
        this.hint = hint; setText(v)
        if (number) inputType = InputType.TYPE_CLASS_NUMBER
    }
}

/** 本地日志页：最新的在最上面。 */
class LogActivity : Activity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        val tv = TextView(this).apply { textSize = 12f; setTextIsSelectable(true) }
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(24, 24, 24, 24) }
        root.addView(Button(this).apply {
            text = "清空日志"
            setOnClickListener { L.clear(this@LogActivity); tv.text = "" }
        })
        root.addView(tv)
        tv.text = L.read(this).lines().filter { it.isNotBlank() }.reversed().take(400).joinToString("\n")
        setContentView(ScrollView(this).apply { fitsSystemWindows = true; addView(root) })
    }
}

/** 做法 B 的透明页：不显示任何东西，转发原入口后立刻关掉。 */
class TrampolineActivity : Activity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        Reposter.forward(this, intent.getIntExtra("idx", -1))
        finish()
    }
}

/**
 * 调试指令（adb）：
 * am broadcast -n com.dk.msgrelay/.CmdReceiver --es cmd <set|flush|repost|list|status|clearours|clearlog> ...
 * set 可带 --es mode A|B --ei window 秒 --ei count 条 --es cancel 1|0 --es auto 1|0 --es watch 包名,包名
 * repost 带 --ei idx 第几条 [--es mode A|B]
 */
class CmdReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, i: Intent) {
        val c = ctx.applicationContext
        when (i.getStringExtra("cmd")) {
            "set" -> {
                val e = Cfg.p(c).edit()
                i.getStringExtra("mode")?.let { e.putString("mode", it) }
                if (i.hasExtra("window")) e.putInt("window", i.getIntExtra("window", 30))
                if (i.hasExtra("count")) e.putInt("count", i.getIntExtra("count", 3))
                i.getStringExtra("cancel")?.let { e.putBoolean("cancel", it == "1") }
                i.getStringExtra("auto")?.let { e.putBoolean("auto", it == "1") }
                i.getStringExtra("watch")?.let { e.putString("watch", it) }
                e.commit()
                L.i(c, "设置 | ${Cfg.describe(c)}")
            }
            "flush" -> Batch.flush(c, "手动")
            "repost" -> {
                val idx = i.getIntExtra("idx", -1)
                val item = Store.items.find { it.idx == idx }
                if (item == null) L.i(c, "重推失败 | 没有 #$idx（进程可能重启过）")
                else { Store.pending.remove(item); Reposter.post(c, item, i.getStringExtra("mode") ?: Cfg.mode(c)) }
            }
            "list" -> {
                if (Store.items.isEmpty()) L.i(c, "存货 | 空")
                Store.items.forEach {
                    L.i(c, "存货 | #${it.idx} | ${it.label} | ${it.title} | 收到=${L.t(it.gotAt)} | 有入口=${it.pi != null} | 已推${it.reposts}次")
                }
            }
            "status" -> L.i(c, "状态 | 进程=${Process.myPid()} | ${Cfg.describe(c)} | 已拦${Store.items.size} 待推${Store.pending.size}")
            "clearours" -> { c.getSystemService(NotificationManager::class.java).cancelAll(); L.i(c, "清掉我们的通知") }
            "clearlog" -> L.clear(c)
            "dnd" -> {
                val on = i.getStringExtra("on") == "1"
                val svc = RelayListener.instance
                if (svc == null) L.i(c, "勿扰 | 监听没连上，无法请求")
                else {
                    svc.requestInterruptionFilter(
                        if (on) android.service.notification.NotificationListenerService.INTERRUPTION_FILTER_PRIORITY
                        else android.service.notification.NotificationListenerService.INTERRUPTION_FILTER_ALL
                    )
                    L.i(c, "勿扰 | 请求${if (on) "打开（只允许重要打扰）" else "关闭"}")
                }
            }
        }
    }
}

/** 请系统重新连接监听服务（已连上时什么也不做）。 */
fun requestRebind(ctx: Context, why: String) {
    try {
        android.service.notification.NotificationListenerService.requestRebind(
            android.content.ComponentName(ctx, RelayListener::class.java)
        )
        L.i(ctx, "请求重连监听 | $why")
    } catch (e: Exception) {
        L.i(ctx, "请求重连监听失败 | $why | ${e.javaClass.simpleName}: ${e.message}")
    }
}

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, i: Intent) = requestRebind(ctx.applicationContext, "开机完成")
}
