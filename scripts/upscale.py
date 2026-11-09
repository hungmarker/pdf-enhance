"""AI upscale (Real-ESRGAN x4) for PDFs and images, aimed at print quality.

Normally launched through run.py, which sets up the environment first.

  PDF   -> every raster image inside is upscaled and replaced in place
           (layout, rotation, clipping and transparency unchanged) -> "<name> - HD.pdf"
  Image -> JPG/PNG/WEBP/BMP/TIFF upscaled -> "<name> - HD.jpg" (or .png when the
           image has transparency or --png is given), tagged 300 dpi

Usage: upscale.py INPUT [INPUT ...] [-o OUTPUT] [--max-side 8000] [--png]
INPUT may be a file or a folder (all supported files inside are processed).
"""
import argparse, io, os, sys, zlib, warnings
warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np, torch, fitz
from PIL import Image, ImageOps
from spandrel import ModelLoader

Image.MAX_IMAGE_PIXELS = None
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
PRINT_DPI = 300

if os.environ.get("PRINT_UPSCALE_HOME"):
    HOME = os.environ["PRINT_UPSCALE_HOME"]
elif os.name == "nt":
    HOME = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "print-upscale")
else:
    HOME = os.path.expanduser("~/.cache/print-upscale")

ap = argparse.ArgumentParser()
ap.add_argument("inputs", nargs="+")
ap.add_argument("-o", "--output", help="output file (only with a single input)")
ap.add_argument("--max-side", type=int, default=8000, help="cap longest side after upscale (default 8000)")
ap.add_argument("--min-side", type=int, default=64, help="PDF: skip images smaller than this")
ap.add_argument("--jpeg-quality", type=int, default=95)
ap.add_argument("--png", action="store_true", help="images: save lossless PNG instead of JPG")
a = ap.parse_args()

dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
model = ModelLoader().load_from_file(os.path.join(HOME, "models", "RealESRGAN_x4plus.pth")).to(dev).eval()
if dev == "cuda":
    model = model.half()
print(f"device: {dev}", flush=True)


def upscale(img, tile=256, pad=16):
    """Real-ESRGAN x4 in tiles; returns RGB PIL image, capped to --max-side."""
    arr = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    H, W, _ = arr.shape
    out = np.zeros((H * 4, W * 4, 3), np.uint8)
    for y in range(0, H, tile):
        for x in range(0, W, tile):
            y0, x0 = max(y - pad, 0), max(x - pad, 0)
            y1, x1 = min(y + tile + pad, H), min(x + tile + pad, W)
            t = torch.from_numpy(arr[y0:y1, x0:x1].transpose(2, 0, 1))[None].to(dev)
            if dev == "cuda":
                t = t.half()
            with torch.no_grad():
                r = model(t)[0].float().clamp(0, 1).cpu().numpy().transpose(1, 2, 0)
            ty, tx = (y - y0) * 4, (x - x0) * 4
            hh, ww = min(tile, H - y) * 4, min(tile, W - x) * 4
            out[y * 4:y * 4 + hh, x * 4:x * 4 + ww] = (r[ty:ty + hh, tx:tx + ww] * 255 + 0.5).astype(np.uint8)
        print(f"  {min(100, int((y + tile) / H * 100))}%", end="\r", flush=True)
    im = Image.fromarray(out)
    if max(im.size) > a.max_side:
        s = a.max_side / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return im


def cm(px, dpi=PRINT_DPI):
    return px / dpi * 2.54


def default_out(path, ext):
    base, _ = os.path.splitext(path)
    return f"{base} - HD{ext}"


# ---------------------------------------------------------------- images
def do_image(src, dst=None):
    im = ImageOps.exif_transpose(Image.open(src))
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    w, h = im.size
    if max(w, h) >= a.max_side:
        print(f"{os.path.basename(src)}: {w}x{h} is already >= {a.max_side}px, skipped"); return
    big = upscale(im)
    if has_alpha:
        alpha = im.convert("RGBA").getchannel("A").resize(big.size, Image.LANCZOS)
        big.putalpha(alpha)
    as_png = a.png or has_alpha
    dst = dst or default_out(src, ".png" if as_png else ".jpg")
    if as_png:
        big.save(dst, "PNG", dpi=(PRINT_DPI, PRINT_DPI), optimize=False, compress_level=6)
    else:
        big.save(dst, "JPEG", quality=a.jpeg_quality, subsampling=0, dpi=(PRINT_DPI, PRINT_DPI))
    W, H = big.size
    print(f"{os.path.basename(src)}: {w}x{h} -> {W}x{H}")
    print(f"  print @300dpi up to {cm(W):.0f} x {cm(H):.0f} cm ({W/PRINT_DPI:.1f} x {H/PRINT_DPI:.1f} in)")
    print(f"  saved: {dst} ({os.path.getsize(dst)/1e6:.1f} MB)")


# ---------------------------------------------------------------- PDFs
def do_pdf(src, dst=None):
    dst = dst or default_out(src, ".pdf")
    doc = fitz.open(src)

    def set_image(xref, data, w, h, filt, cs=None):
        doc.update_stream(xref, data, compress=False)
        doc.xref_set_key(xref, "Width", str(w)); doc.xref_set_key(xref, "Height", str(h))
        doc.xref_set_key(xref, "Filter", filt); doc.xref_set_key(xref, "DecodeParms", "null")
        doc.xref_set_key(xref, "BitsPerComponent", "8"); doc.xref_set_key(xref, "Decode", "null")
        if cs:
            doc.xref_set_key(xref, "ColorSpace", cs)

    done, worst_dpi, n = set(), None, 0
    for page in doc:
        for info in page.get_images(full=True):
            xref, smask, w, h = info[0], info[1], info[2], info[3]
            if xref in done:
                continue
            done.add(xref)
            if min(w, h) < a.min_side:
                print(f"  skip image {xref}: too small {w}x{h}"); continue
            if doc.xref_get_key(xref, "ImageMask")[1] == "true":
                continue
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.alpha:
                    pix = fitz.Pixmap(pix, 0)
                orig_n = pix.n
                if pix.n not in (1, 3):
                    pix = fitz.Pixmap(fitz.csRGB, pix)  # CMYK / indexed -> RGB
                src_img = Image.frombytes("L" if pix.n == 1 else "RGB", (pix.width, pix.height), pix.samples)
            except Exception as e:
                print(f"  skip image {xref}: {e}"); continue
            big = upscale(src_img)
            W, H = big.size
            cs_key = doc.xref_get_key(xref, "ColorSpace")[1]
            if src_img.mode == "L":
                big = big.convert("L")
                new_cs = None if orig_n == 1 and "Indexed" not in cs_key else "/DeviceGray"
            else:
                new_cs = None if orig_n == 3 and "Indexed" not in cs_key else "/DeviceRGB"
            if smask:
                set_image(xref, zlib.compress(big.tobytes(), 9), W, H, "/FlateDecode", new_cs)
                if smask not in done:
                    done.add(smask)
                    mp = fitz.Pixmap(doc, smask)
                    m = Image.frombytes("L", (mp.width, mp.height), mp.samples).resize((W, H), Image.LANCZOS)
                    set_image(smask, zlib.compress(m.tobytes(), 9), W, H, "/FlateDecode", "/DeviceGray")
            else:
                b = io.BytesIO(); big.save(b, "JPEG", quality=a.jpeg_quality, subsampling=0)
                set_image(xref, b.getvalue(), W, H, "/DCTDecode", new_cs)
            n += 1
            # effective print resolution of this image at its placed size
            for r in page.get_image_rects(xref):
                if r.width > 1 and r.height > 1:
                    dpi = min(W / (r.width / 72), H / (r.height / 72))
                    worst_dpi = dpi if worst_dpi is None else min(worst_dpi, dpi)
            print(f"  image {xref}: {w}x{h} -> {W}x{H}" + (" (+transparency)" if smask else ""))
    if n == 0:
        print(f"{os.path.basename(src)}: no raster images to upscale (vector/text PDF is already sharp)"); return
    doc.save(dst, garbage=3, deflate=True)
    p0 = doc[0].rect
    print(f"{os.path.basename(src)}: {len(doc)} page(s), {n} image(s) upscaled")
    print(f"  page size {cm(p0.width, 72):.1f} x {cm(p0.height, 72):.1f} cm; image resolution at this size ~{worst_dpi:.0f} dpi")
    print(f"  saved: {dst} ({os.path.getsize(dst)/1e6:.1f} MB)")


# ---------------------------------------------------------------- main
files = []
for p in a.inputs:
    if os.path.isdir(p):
        for f in sorted(os.listdir(p)):
            fp = os.path.join(p, f)
            stem = os.path.splitext(f)[0]
            if os.path.isfile(fp) and not stem.endswith(" - HD") and os.path.splitext(f)[1].lower() in IMG_EXT | {".pdf"}:
                files.append(fp)
    else:
        files.append(p)
if a.output and len(files) != 1:
    sys.exit("-o/--output can only be used with a single input file")

failed = 0
for f in files:
    ext = os.path.splitext(f)[1].lower()
    try:
        if ext == ".pdf":
            do_pdf(f, a.output)
        elif ext in IMG_EXT:
            do_image(f, a.output)
        else:
            print(f"{f}: unsupported file type"); failed += 1
    except Exception as e:
        print(f"{f}: ERROR {e}"); failed += 1
sys.exit(1 if failed else 0)
