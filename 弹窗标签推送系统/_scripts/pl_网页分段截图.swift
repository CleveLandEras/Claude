// 用法：swift pl_网页分段截图.swift 页面.html 输出前缀 [宽度=1440] [每段高度参考=1500]
// 按「宽度」排版，整页截图（到 .page 底部为止），页高超过「每段高度参考」×1.15 时平均切成几段（切口选在文字行之间），存为 输出前缀_1.jpg、输出前缀_2.jpg ……；
// 只有一段时存为 输出前缀.jpg。段数、各段起止（CSS 像素）打印到标准输出（JSON）。
// 与 pl_网页截图测量.swift 的区别：段高可调、切口选在文字行之间；读取权限给整个磁盘（页面可放在草稿目录，相对路径的图片照常显示）。
// 固定浅色。由 pl_原型截图_读者视角.py 调用，也可单独用。
import WebKit
import AppKit
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1])
let outPrefix = args[2]
let width = CGFloat(Double(args.count > 3 ? args[3] : "1440") ?? 1440)
let maxSeg = Double(args.count > 4 ? args[4] : "1500") ?? 1500

let cutJS = """
(function(maxSeg){
  var H = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
  var pg = document.querySelector('.page');
  if (pg) H = Math.min(H, Math.ceil(pg.getBoundingClientRect().bottom + window.scrollY));
  var iv = [];
  var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  var r = document.createRange();
  while (w.nextNode()) {
    var n = w.currentNode;
    if (!n.nodeValue.trim()) continue;
    var p = n.parentElement; if (!p) continue;
    var tag = p.tagName; if (tag === 'STYLE' || tag === 'SCRIPT') continue;
    r.selectNodeContents(n);
    var rs = r.getClientRects();
    for (var i = 0; i < rs.length; i++) {
      var a = rs[i].top + window.scrollY, b = rs[i].bottom + window.scrollY;
      if (b - a > 1) iv.push([a, b]);
    }
  }
  iv.sort(function(x, y){ return x[0] - y[0]; });
  function crossing(y) {
    var c = 0;
    for (var i = 0; i < iv.length; i++) {
      if (iv[i][0] >= y) break;
      if (iv[i][1] > y) c++;
    }
    return c;
  }
  // 段数：每段不超过 maxSeg×1.15；平均分，再在目标位置附近找不切断文字的切口
  var cnt = Math.max(1, Math.ceil(H / (maxSeg * 1.15)));
  var seg = H / cnt, cuts = [0];
  for (var k = 1; k < cnt; k++) {
    var target = k * seg, best = target, bestC = 1e9, win = seg * 0.3;
    for (var d = 0; d <= win && bestC > 0; d += 2) {
      var cand = [target - d, target + d];
      for (var j = 0; j < 2; j++) {
        var y = cand[j];
        if (y <= cuts[cuts.length - 1] + 200) continue;
        var c = crossing(y);
        if (c < bestC) { bestC = c; best = y; }
      }
    }
    cuts.push(Math.round(best));
  }
  cuts.push(H);
  return JSON.stringify(cuts);
})(\(maxSeg))
"""

func shoot(_ w: WKWebView, _ cuts: [Double], _ i: Int) {
  if i >= cuts.count - 1 { print(cuts); exit(0) }
  let top = CGFloat(cuts[i]), h = CGFloat(cuts[i + 1] - cuts[i])
  let cfg = WKSnapshotConfiguration()
  cfg.rect = NSRect(x: 0, y: top, width: width, height: h)
  cfg.snapshotWidth = NSNumber(value: Double(width))
  w.takeSnapshot(with: cfg) { img, e in
    guard let img = img, let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
          let data = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.88]) else { print("fail", e as Any); exit(1) }
    let path = cuts.count == 2 ? "\(outPrefix).jpg" : "\(outPrefix)_\(i + 1).jpg"
    try! data.write(to: URL(fileURLWithPath: path))
    shoot(w, cuts, i + 1)
  }
}
class D: NSObject, WKNavigationDelegate {
  func fail(_ e: Error) { print("load fail", e); exit(2) }
  func webView(_ w: WKWebView, didFail n: WKNavigation!, withError e: Error) { fail(e) }
  func webView(_ w: WKWebView, didFailProvisionalNavigation n: WKNavigation!, withError e: Error) { fail(e) }
  func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
      w.evaluateJavaScript("Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)") { h, _ in
        let hh = CGFloat((h as? NSNumber)?.doubleValue ?? 2000)
        w.frame = NSRect(x: 0, y: 0, width: width, height: hh)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
          w.evaluateJavaScript(cutJS) { r, e in
            var cuts: [Double] = [0, Double(hh)]
            if let s = r as? String, let d = s.data(using: .utf8), let a = try? JSONSerialization.jsonObject(with: d) as? [Double] { cuts = a }
            shoot(w, cuts, 0)
          }
        }
      }
    }
  }
}
let app = NSApplication.shared
let d = D()
let w = WKWebView(frame: NSRect(x: 0, y: 0, width: width, height: 900))
w.appearance = NSAppearance(named: .aqua)
w.navigationDelegate = d
w.loadFileURL(url, allowingReadAccessTo: URL(fileURLWithPath: "/"))
app.run()
