// 用法：swift pl_缩略总览.swift 渲染图目录 输出.jpg 列数 起页 止页：把逐页渲染图拼成一张总览，用来整体判断是否清晰
import AppKit
let a = CommandLine.arguments
let dir = a[1], out = a[2], cols = Int(a[3])!, first = Int(a[4])!, last = Int(a[5])!
let tw: CGFloat = 640, th: CGFloat = 360, gap: CGFloat = 12
let n = last - first + 1, rows = (n + cols - 1) / cols
let W = Int(CGFloat(cols) * (tw + gap) + gap), H = Int(CGFloat(rows) * (th + gap) + gap)
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: W, pixelsHigh: H, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSColor(white: 0.55, alpha: 1).setFill(); NSRect(x: 0, y: 0, width: W, height: H).fill()
for k in 0..<n {
  let p = String(format: "%@/s%02d.jpg", dir, first + k)
  guard let img = NSImage(contentsOfFile: p) else { continue }
  let c = k % cols, r = k / cols
  let x = gap + CGFloat(c) * (tw + gap), y = CGFloat(H) - gap - th - CGFloat(r) * (th + gap)
  img.draw(in: NSRect(x: x, y: y, width: tw, height: th))
}
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .jpeg, properties: [.compressionFactor: 0.8])!.write(to: URL(fileURLWithPath: out))
