// 用法：grab 视频 秒 输出.jpg [x y w h]（裁剪坐标按原视频像素 2340x1080，可省略）
// 从视频指定时间取原分辨率帧，可选裁剪，用来看清小字与价格
import AVFoundation
import AppKit

let a = CommandLine.arguments
let asset = AVURLAsset(url: URL(fileURLWithPath: a[1]))
let t = Double(a[2])!
let out = a[3]
let gen = AVAssetImageGenerator(asset: asset)
gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = CMTime(seconds: 0.02, preferredTimescale: 600)
gen.requestedTimeToleranceAfter = CMTime(seconds: 0.02, preferredTimescale: 600)
guard var cg = try? gen.copyCGImage(at: CMTime(seconds: t, preferredTimescale: 600), actualTime: nil) else { print("fail"); exit(1) }
if a.count >= 8 {
  let r = CGRect(x: Double(a[4])!, y: Double(a[5])!, width: Double(a[6])!, height: Double(a[7])!)
  if let c = cg.cropping(to: r) { cg = c }
}
let rep = NSBitmapImageRep(cgImage: cg)
try! rep.representation(using: .jpeg, properties: [.compressionFactor: 0.9])!.write(to: URL(fileURLWithPath: out))
print("ok \(cg.width)x\(cg.height) -> \(out)")
