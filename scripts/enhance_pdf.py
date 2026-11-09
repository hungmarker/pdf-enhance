"""Upscale every raster image inside a PDF with Real-ESRGAN x4 and write a new PDF.

Images are replaced in place (same xref), so layout, rotation, clipping and
transparency (SMask) stay exactly as in the original.

Normally launched through run.py (which sets up the environment first).
Usage: python -I enhance_pdf.py INPUT.pdf [OUTPUT.pdf] [--max-side 8000] [--min-side 64]
"""
import argparse, io, os, sys, zlib
import warnings; warnings.filterwarnings("ignore")
import numpy as np, torch, fitz
from PIL import Image
from spandrel import ModelLoader

try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
if os.environ.get("PDF_ENHANCE_HOME"):
    CACHE = os.environ["PDF_ENHANCE_HOME"]
elif os.name == "nt":
    CACHE = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "pdf-enhance")
else:
    CACHE = os.path.expanduser("~/.cache/pdf-enhance")
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst", nargs="?")
ap.add_argument("--max-side", type=int, default=8000, help="cap longest side after upscale")
ap.add_argument("--min-side", type=int, default=64, help="skip images smaller than this")
ap.add_argument("--jpeg-quality", type=int, default=94)
a = ap.parse_args()
dst = a.dst or os.path.splitext(a.src)[0] + " - HD.pdf"

dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
model = ModelLoader().load_from_file(os.path.join(CACHE, "models", "RealESRGAN_x4plus.pth")).to(dev).eval()

def upscale(img, tile=256, pad=16):
    arr = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    H, W, _ = arr.shape
    out = np.zeros((H * 4, W * 4, 3), np.float32)
    for y in range(0, H, tile):
        for x in range(0, W, tile):
            y0, x0 = max(y - pad, 0), max(x - pad, 0)
            y1, x1 = min(y + tile + pad, H), min(x + tile + pad, W)
            t = torch.from_numpy(arr[y0:y1, x0:x1].transpose(2, 0, 1))[None].to(dev)
            with torch.no_grad():
                r = model(t)[0].clamp(0, 1).cpu().numpy().transpose(1, 2, 0)
            ty, tx = (y - y0) * 4, (x - x0) * 4
            hh, ww = min(tile, H - y) * 4, min(tile, W - x) * 4
            out[y * 4:y * 4 + hh, x * 4:x * 4 + ww] = r[ty:ty + hh, tx:tx + ww]
    im = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
    if max(im.size) > a.max_side:
        s = a.max_side / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return im

doc = fitz.open(a.src)

def set_image(xref, data, w, h, filt, cs=None):
    doc.update_stream(xref, data, compress=False)
    doc.xref_set_key(xref, "Width", str(w)); doc.xref_set_key(xref, "Height", str(h))
    doc.xref_set_key(xref, "Filter", filt); doc.xref_set_key(xref, "DecodeParms", "null")
    doc.xref_set_key(xref, "BitsPerComponent", "8"); doc.xref_set_key(xref, "Decode", "null")
    if cs: doc.xref_set_key(xref, "ColorSpace", cs)

done = set()
smask_of = {}
for page in doc:
    for info in page.get_images(full=True):
        xref, smask = info[0], info[1]
        if xref in done: continue
        done.add(xref)
        w, h = info[2], info[3]
        if min(w, h) < a.min_side:
            print(f"skip xref {xref}: too small {w}x{h}"); continue
        if doc.xref_get_key(xref, "ImageMask")[1] == "true":
            print(f"skip xref {xref}: stencil mask"); continue
        try:
            pix = fitz.Pixmap(doc, xref)
            if pix.alpha: pix = fitz.Pixmap(pix, 0)
            if pix.n not in (1, 3): pix = fitz.Pixmap(fitz.csRGB, pix)  # CMYK/indexed -> RGB
            src_img = Image.frombytes("L" if pix.n == 1 else "RGB", (pix.width, pix.height), pix.samples)
        except Exception as e:
            print(f"skip xref {xref}: {e}"); continue
        big = upscale(src_img)
        W, H = big.size
        # keep the original ICC profile when channel count matches, else fall back to Device space
        cs_key = doc.xref_get_key(xref, "ColorSpace")[1]
        orig_n = fitz.Pixmap(doc, xref).n - (1 if fitz.Pixmap(doc, xref).alpha else 0)
        if src_img.mode == "L":
            big = big.convert("L")
            new_cs = None if orig_n == 1 and "Indexed" not in cs_key else "/DeviceGray"
        else:
            new_cs = None if orig_n == 3 and "Indexed" not in cs_key else "/DeviceRGB"
        if smask:
            # opaque photo-like background stays JPEG; transparent overlays use lossless Flate
            set_image(xref, zlib.compress(big.tobytes(), 9), W, H, "/FlateDecode", new_cs)
            if smask not in done:
                done.add(smask)
                mp = fitz.Pixmap(doc, smask)
                m = Image.frombytes("L", (mp.width, mp.height), mp.samples).resize((W, H), Image.LANCZOS)
                set_image(smask, zlib.compress(m.tobytes(), 9), W, H, "/FlateDecode", "/DeviceGray")
        else:
            b = io.BytesIO(); big.save(b, "JPEG", quality=a.jpeg_quality, subsampling=0)
            set_image(xref, b.getvalue(), W, H, "/DCTDecode", new_cs)
        print(f"xref {xref}: {w}x{h} -> {W}x{H}" + (" (+mask)" if smask else ""))

doc.save(dst, garbage=3, deflate=True)
print("saved:", dst, f"{os.path.getsize(dst)/1e6:.1f} MB")
