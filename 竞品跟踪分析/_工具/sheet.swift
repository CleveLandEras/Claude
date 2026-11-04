// 用法：swift sheet.swift 帧目录 输出.jpg 列数 缩略宽 [起序号 止序号]
// 把帧目录里的 jpg 按文件名排序拼成带时间标签的总览图
import AppKit

let a = CommandLine.arguments
let dir = a[1], out = a[2]
let cols = Int(a[3])!
let tw = CGFloat(Double(a[4])!)
var files = (try! FileManager.default.contentsOfDirectory(atPath: dir)).filter { $0.hasSuffix(".jpg") }.sorted()
if a.count >= 7 {
  let s = Int(a[5])!, e = min(Int(a[6])!, files.count - 1)
  files = Array(files[s...e])
}
guard let first = NSImage(contentsOfFile: dir + "/" + files[0]) else { exit(1) }
let ratio = first.size.height / first.size.width
let th = (tw * ratio).rounded()
let gap: CGFloat = 8, label: CGFloat = 22
let n = files.count, rows = (n + cols - 1) / cols
let W = Int(CGFloat(cols) * (tw + gap) + gap)
let H = Int(CGFloat(rows) * (th + label + gap) + gap)
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: W, pixelsHigh: H, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSColor(white: 0.15, alpha: 1).setFill()
NSRect(x: 0, y: 0, width: W, height: H).fill()
let attrs: [NSAttributedString.Key: Any] = [.font: NSFont.boldSystemFont(ofSize: 16), .foregroundColor: NSColor.yellow]
for (k, f) in files.enumerated() {
  guard let img = NSImage(contentsOfFile: dir + "/" + f) else { continue }
  let c = k % cols, r = k / cols
  let x = gap + CGFloat(c) * (tw + gap)
  let yTop = CGFloat(H) - gap - CGFloat(r) * (th + label + gap)
  let name = f.replacingOccurrences(of: ".jpg", with: "").replacingOccurrences(of: "t", with: "")
  (name + "s" as NSString).draw(at: NSPoint(x: x + 2, y: yTop - label + 2), withAttributes: attrs)
  img.draw(in: NSRect(x: x, y: yTop - label - th, width: tw, height: th))
}
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .jpeg, properties: [.compressionFactor: 0.8])!.write(to: URL(fileURLWithPath: out))
print("sheet \(n) frames -> \(out)")
