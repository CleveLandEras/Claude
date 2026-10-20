// 用法：swift pl_网页截图测量.swift 页面.html 输出.jpg 宽度 [测量.js]
// 按「宽度」排版、整页截图（Retina 屏上为 2 倍像素），并执行测量脚本、把结果（JSON 字符串）打印到标准输出。
// 与 pl_网页截图.swift 的区别：读取权限给页面所在文件夹（可放在草稿目录）；固定浅色；能同时量元素位置；
// 长页面分段截（每段 1500 CSS 像素），存为 输出_0.jpg、输出_1.jpg……，由调用方拼接（WebKit 一次截太长会降为 1 倍）。
// 测量脚本的坐标请用 CSS 像素（getBoundingClientRect + scrollY）。
import WebKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1]); let out = args[2]
let width = CGFloat(Double(args[3]) ?? 1280)
let js = args.count > 4 ? (try? String(contentsOfFile: args[4], encoding: .utf8)) ?? "null" : "null"
let TILE: CGFloat = 1500
let base = (out as NSString).deletingPathExtension
func shoot(_ w: WKWebView, _ i: Int, _ hh: CGFloat) {
  let top = CGFloat(i) * TILE
  if top >= hh { print("tiles", i); exit(0) }
  let cfg = WKSnapshotConfiguration(); cfg.rect = NSRect(x: 0, y: top, width: width, height: min(TILE, hh - top))
  cfg.snapshotWidth = NSNumber(value: Double(width * 2))   // 要 2 倍像素；Retina 屏上会再乘 2，使用方按实际宽度换算
  w.takeSnapshot(with: cfg) { img, e in
    guard let img = img, let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
          let data = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.92]) else { print("fail", e as Any); exit(1) }
    try! data.write(to: URL(fileURLWithPath: "\(base)_\(i).jpg"))
    shoot(w, i + 1, hh)
  }
}
class D: NSObject, WKNavigationDelegate {
  func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
      w.evaluateJavaScript("document.documentElement.scrollHeight") { h, _ in
        let hh = CGFloat((h as? NSNumber)?.doubleValue ?? 2000)
        w.frame = NSRect(x: 0, y: 0, width: width, height: hh)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
          w.evaluateJavaScript(js) { r, e in
            if let s = r as? String { print(s) } else { print("null") }
            shoot(w, 0, hh)
          }
        }
      }
    }
  }
}
let app = NSApplication.shared
let d = D()
let w = WKWebView(frame: NSRect(x: 0, y: 0, width: width, height: 900))
w.appearance = NSAppearance(named: .aqua)   // 固定浅色，避免系统深色模式让页面走深色样式
w.navigationDelegate = d
w.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
app.run()
