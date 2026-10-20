// 用法：swift pl_图片裁剪.swift 输入.png 输出.png x y 宽 高（像素，原图坐标，左上为原点）
import AppKit
let a = CommandLine.arguments
let img = NSImage(contentsOfFile: a[1])!
var r = NSRect(x: 0, y: 0, width: 0, height: 0)
let cg = img.cgImage(forProposedRect: &r, context: nil, hints: nil)!
let rect = CGRect(x: Double(a[3])!, y: Double(a[4])!, width: Double(a[5])!, height: Double(a[6])!)
let c = cg.cropping(to: rect)!
let rep = NSBitmapImageRep(cgImage: c)
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[2]))
print(c.width, c.height)
