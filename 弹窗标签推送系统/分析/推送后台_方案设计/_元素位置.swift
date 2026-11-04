// 用法：swift _元素位置.swift 页面.html 宽度 "CSS选择器"：按电脑宽度加载页面，打印每个匹配元素的 id、top、height、left、width（截图定位用）
import WebKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1])
let width = CGFloat(Double(args[2]) ?? 1280)
let sel = args[3]
class D: NSObject, WKNavigationDelegate {
  func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
      w.evaluateJavaScript("document.documentElement.scrollHeight") { h, _ in
        let hh = CGFloat((h as? NSNumber)?.doubleValue ?? 2000)
        w.frame = NSRect(x: 0, y: 0, width: width, height: hh)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
          let js = "Array.from(document.querySelectorAll(" + "`" + sel + "`" + ")).map(e=>{const r=e.getBoundingClientRect();const s=e.closest('section');return [(s&&s.id)||'', e.id||e.className, Math.round(r.top+window.scrollY), Math.round(r.height), Math.round(r.left), Math.round(r.width)].join('\\t')}).join('\\n')"
          w.evaluateJavaScript(js) { r, e in print(r as? String ?? "err \(String(describing: e))"); exit(0) }
        }
      }
    }
  }
}
let app = NSApplication.shared
let d = D()
let w = WKWebView(frame: NSRect(x: 0, y: 0, width: width, height: 900))
w.navigationDelegate = d
w.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
app.run()
