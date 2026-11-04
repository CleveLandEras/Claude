import PDFKit
import AppKit
let a = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: a[1]))!
let out = a[2]
for i in 0..<doc.pageCount {
  let page = doc.page(at: i)!
  let b = page.bounds(for: .mediaBox)
  let s: CGFloat = 1.6
  let img = NSImage(size: NSSize(width: b.width*s, height: b.height*s))
  img.lockFocus()
  NSColor.white.set(); NSRect(x:0,y:0,width:b.width*s,height:b.height*s).fill()
  let ctx = NSGraphicsContext.current!.cgContext
  ctx.scaleBy(x: s, y: s)
  page.draw(with: .mediaBox, to: ctx)
  img.unlockFocus()
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "\(out)/p\(i+1).png"))
  print("p\(i+1)", page.string?.contains("待 Dk 定") ?? false, page.string?.contains("轮流时，玩家同时符合") ?? false)
}
