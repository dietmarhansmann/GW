import AppKit

func color(_ hex: UInt32) -> NSColor {
    NSColor(
        calibratedRed: CGFloat((hex >> 16) & 0xff) / 255,
        green: CGFloat((hex >> 8) & 0xff) / 255,
        blue: CGFloat(hex & 0xff) / 255,
        alpha: 1
    )
}

func drawIcon(size: Int, output: String) throws {
    let side = CGFloat(size)
    let image = NSImage(size: NSSize(width: side, height: side))
    let bitmap = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: size,
        pixelsHigh: size,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    )!
    image.addRepresentation(bitmap)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
    let scale = side / 512
    let context = NSGraphicsContext.current!.cgContext
    context.saveGState()
    context.scaleBy(x: scale, y: scale)
    context.setAllowsAntialiasing(true)
    context.setShouldAntialias(true)

    let background = NSBezierPath(roundedRect: NSRect(x: 0, y: 0, width: 512, height: 512), xRadius: 112, yRadius: 112)
    NSGradient(colors: [color(0x087451), color(0x064E3B)])!.draw(in: background, angle: -45)

    // A complete top-down court gives the icon a clear tennis-court backdrop.
    let court = NSBezierPath(roundedRect: NSRect(x: 62, y: 62, width: 388, height: 388), xRadius: 32, yRadius: 32)
    color(0x13865A).setFill()
    court.fill()
    color(0xE4FFE9).setStroke()
    court.lineWidth = 5
    court.stroke()

    let courtLines = NSBezierPath()
    courtLines.move(to: NSPoint(x: 104, y: 86))
    courtLines.line(to: NSPoint(x: 104, y: 426))
    courtLines.move(to: NSPoint(x: 408, y: 86))
    courtLines.line(to: NSPoint(x: 408, y: 426))
    courtLines.move(to: NSPoint(x: 104, y: 170))
    courtLines.line(to: NSPoint(x: 408, y: 170))
    courtLines.move(to: NSPoint(x: 104, y: 342))
    courtLines.line(to: NSPoint(x: 408, y: 342))
    courtLines.move(to: NSPoint(x: 256, y: 170))
    courtLines.line(to: NSPoint(x: 256, y: 342))
    courtLines.move(to: NSPoint(x: 78, y: 256))
    courtLines.line(to: NSPoint(x: 434, y: 256))
    color(0xE4FFE9).withAlphaComponent(0.9).setStroke()
    courtLines.lineWidth = 4
    courtLines.stroke()

    // Tennis ball in the foreground.
    let ball = NSBezierPath(ovalIn: NSRect(x: 162, y: 166, width: 188, height: 188))
    color(0xD5F47A).setFill()
    ball.fill()
    color(0xF5FFD9).setStroke()
    ball.lineWidth = 5
    ball.stroke()

    let seam = NSBezierPath()
    seam.move(to: NSPoint(x: 196, y: 311))
    seam.curve(to: NSPoint(x: 316, y: 311), controlPoint1: NSPoint(x: 224, y: 253), controlPoint2: NSPoint(x: 288, y: 253))
    seam.move(to: NSPoint(x: 196, y: 201))
    seam.curve(to: NSPoint(x: 316, y: 201), controlPoint1: NSPoint(x: 224, y: 259), controlPoint2: NSPoint(x: 288, y: 259))
    color(0xF5FFD9).setStroke()
    seam.lineWidth = 7
    seam.lineCapStyle = .round
    seam.stroke()

    // Compact monogram above the ball, legible at home-screen size.
    let monogram = NSAttributedString(
        string: "GW",
        attributes: [
            .font: NSFont.systemFont(ofSize: 42, weight: .black),
            .foregroundColor: color(0xF2FFF7),
            .kern: 2
        ]
    )
    let textSize = monogram.size()
    monogram.draw(at: NSPoint(x: (512 - textSize.width) / 2, y: 405 - textSize.height / 2))

    context.restoreGState()
    NSGraphicsContext.restoreGraphicsState()

    guard let png = bitmap.representation(using: .png, properties: [:]) else {
        throw NSError(domain: "AppIcon", code: 1, userInfo: [NSLocalizedDescriptionKey: "Unable to encode PNG"])
    }
    try png.write(to: URL(fileURLWithPath: output))
}

for (size, path) in [(192, "icons/icon-192.png"), (512, "icons/icon-512.png"), (512, "icons/icon-maskable-512.png")] {
    try drawIcon(size: size, output: path)
}
