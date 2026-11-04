// 用法：keyframes 视频 输出目录 采样间隔秒 阈值(0-255) 输出宽度
// 每隔采样间隔取一帧，与上一张保留帧比较 64x30 灰度缩略图的平均差，超过阈值才保留
// 另外：画面稳定（与前一采样差 < 阈值/3）持续后才保留，避免转场中间帧 —— 这里简单处理：保留差异帧的下一个稳定采样
import AVFoundation
import AppKit

let a = CommandLine.arguments
let url = URL(fileURLWithPath: a[1])
let outDir = a[2]
let step = Double(a[3])!
let thr = Double(a[4])!
let outW = CGFloat(Double(a[5])!)
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

let asset = AVURLAsset(url: url)
let dur = CMTimeGetSeconds(asset.duration)
let gen = AVAssetImageGenerator(asset: asset)
gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = CMTime(seconds: 0.03, preferredTimescale: 600)
gen.requestedTimeToleranceAfter = CMTime(seconds: 0.03, preferredTimescale: 600)
gen.maximumSize = CGSize(width: outW, height: outW)

let tw = 64, th = 30
func thumb(_ cg: CGImage) -> [Double] {
  var px = [UInt8](repeating: 0, count: tw * th)
  let cs = CGColorSpaceCreateDeviceGray()
  let ctx = CGContext(data: &px, width: tw, height: th, bitsPerComponent: 8, bytesPerRow: tw, space: cs, bitmapInfo: 0)!
  ctx.interpolationQuality = .medium
  ctx.draw(cg, in: CGRect(x: 0, y: 0, width: tw, height: th))
  return px.map { Double($0) }
}
func diff(_ x: [Double], _ y: [Double]) -> Double {
  var s = 0.0
  for i in 0..<x.count { s += abs(x[i] - y[i]) }
  return s / Double(x.count)
}

var kept: [Double]? = nil
var prev: [Double]? = nil
var pending = false
var t = 0.0
var n = 0
var log = "time\tdiff_to_kept\n"
while t < dur {
  let ct = CMTime(seconds: t, preferredTimescale: 600)
  if let cg = try? gen.copyCGImage(at: ct, actualTime: nil) {
    let th0 = thumb(cg)
    let dk = kept == nil ? 999 : diff(th0, kept!)
    let dp = prev == nil ? 999 : diff(th0, prev!)
    if dk > thr { pending = true }
    // 变化后等画面稳定（与上一采样差小）再保存
    if pending && (dp < thr / 2 || kept == nil) {
      let rep = NSBitmapImageRep(cgImage: cg)
      if let d = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.85]) {
        let name = String(format: "%@/t%06.1f.jpg", outDir, t)
        try? d.write(to: URL(fileURLWithPath: name))
        n += 1
        log += String(format: "%.1f\t%.1f\n", t, dk)
      }
      kept = th0
      pending = false
    }
    prev = th0
  }
  t += step
}
try? log.write(toFile: outDir + "/_keyframes.tsv", atomically: true, encoding: .utf8)
print("duration=\(dur) keyframes=\(n)")
