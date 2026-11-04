// 用法：swift pl_网页截图.swift 页面.html 输出.jpg [宽度=1280] [起点y=0] [高度=0 表示到底]：按电脑宽度截图核对简报版面（预览窗太窄时用）
import WebKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1]); let out = args[2]
let width = CGFloat(Double(args[3]) ?? 1280)
class D: NSObject, WKNavigationDelegate {
  var wv: WKWebView!
  func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
      w.evaluateJavaScript("document.documentElement.scrollHeight") { h, _ in
        let hh = CGFloat((h as? NSNumber)?.doubleValue ?? 2000)
        w.frame = NSRect(x: 0, y: 0, width: width, height: hh)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
          let cfg = WKSnapshotConfiguration(); let top = CGFloat(Double(args.count > 4 ? args[4] : "0") ?? 0); let ch = CGFloat(Double(args.count > 5 ? args[5] : "0") ?? 0); cfg.rect = NSRect(x: 0, y: top, width: width, height: ch > 0 ? ch : hh - top)
          w.takeSnapshot(with: cfg) { img, e in
            guard let img = img, let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
                  let data = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.85]) else { print("fail", e as Any); exit(1) }
            try! data.write(to: URL(fileURLWithPath: out)); print("ok", Int(hh)); exit(0)
          }
        }
      }
    }
  }
}
let app = NSApplication.shared
let d = D()
let w = WKWebView(frame: NSRect(x: 0, y: 0, width: width, height: 900))
d.wv = w; w.navigationDelegate = d
w.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
app.run()
