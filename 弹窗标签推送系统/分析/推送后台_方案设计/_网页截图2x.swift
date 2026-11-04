// 用法：swift _网页截图2x.swift 页面.html 输出.png 宽度 起点y 高度 倍率：同 pl_网页截图.swift，但按倍率输出（2 = 视网膜清晰度），供方案设计里的界面截图用
import WebKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1]); let out = args[2]
let width = CGFloat(Double(args[3]) ?? 1280)
let top = CGFloat(Double(args[4]) ?? 0); let ch = CGFloat(Double(args[5]) ?? 800); let sc = CGFloat(Double(args[6]) ?? 2)
class D: NSObject, WKNavigationDelegate {
  func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
      w.evaluateJavaScript("document.documentElement.scrollHeight") { h, _ in
        let hh = CGFloat((h as? NSNumber)?.doubleValue ?? 2000)
        w.frame = NSRect(x: 0, y: 0, width: width, height: hh)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
          let cfg = WKSnapshotConfiguration(); cfg.rect = NSRect(x: 0, y: top, width: width, height: ch); cfg.snapshotWidth = NSNumber(value: Double(width * sc))
          w.takeSnapshot(with: cfg) { img, e in
            guard let img = img, let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
                  let data = rep.representation(using: .png, properties: [:]) else { print("fail", e as Any); exit(1) }
            try! data.write(to: URL(fileURLWithPath: out)); print("ok", rep.pixelsWide, rep.pixelsHigh); exit(0)
          }
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
