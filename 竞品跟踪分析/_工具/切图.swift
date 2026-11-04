// 用法：切图 输入.jpg 输出前缀 每段高度：把长截图按高度切段，便于逐段检查版面
import AppKit
let a = CommandLine.arguments
guard let img = NSImage(contentsOfFile: a[1]), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let h = Int(a[3])!
var y = 0, k = 1
while y < cg.height {
  let r = CGRect(x: 0, y: y, width: cg.width, height: min(h, cg.height - y))
  if let c = cg.cropping(to: r) {
    let rep = NSBitmapImageRep(cgImage: c)
    try! rep.representation(using: .jpeg, properties: [.compressionFactor: 0.8])!.write(to: URL(fileURLWithPath: String(format: "%@_%02d.jpg", a[2], k)))
  }
  y += h; k += 1
}
print("tiles \(k-1)")
