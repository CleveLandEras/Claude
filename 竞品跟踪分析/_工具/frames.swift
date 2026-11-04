// 用法：swift frames.swift 视频 输出目录 间隔秒 最大宽度
// 按固定间隔抽帧，文件名 t0000.0.jpg（秒）
import AVFoundation
import AppKit

let a = CommandLine.arguments
let url = URL(fileURLWithPath: a[1])
let outDir = a[2]
let step = Double(a[3])!
let maxW = CGFloat(Double(a[4])!)
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

let asset = AVURLAsset(url: url)
let dur = CMTimeGetSeconds(asset.duration)
let gen = AVAssetImageGenerator(asset: asset)
gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = CMTime(seconds: 0.05, preferredTimescale: 600)
gen.requestedTimeToleranceAfter = CMTime(seconds: 0.05, preferredTimescale: 600)
gen.maximumSize = CGSize(width: maxW, height: maxW)

var t = 0.0
var n = 0
while t < dur {
  let ct = CMTime(seconds: t, preferredTimescale: 600)
  if let cg = try? gen.copyCGImage(at: ct, actualTime: nil) {
    let rep = NSBitmapImageRep(cgImage: cg)
    if let d = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.82]) {
      let name = String(format: "%@/t%06.1f.jpg", outDir, t)
      try? d.write(to: URL(fileURLWithPath: name))
      n += 1
    }
  }
  t += step
}
print("duration=\(dur) frames=\(n)")
