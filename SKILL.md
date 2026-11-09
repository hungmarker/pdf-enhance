---
name: print-upscale
description: Free AI upscaling of PDFs and images (JPG/PNG/WEBP/TIFF) to print quality with Real-ESRGAN x4 — runs offline on the user's machine, no watermark; sharpens text and edges, removes compression artifacts, keeps PDF layout intact. Works on Mac and Windows. Use when the user sends a PDF/image (or folder) and asks to sharpen, enhance, upscale, make it print-ready, or says it is blurry/pixelated — including Vietnamese requests like "làm nét", "tăng chất lượng", "để in", "ảnh bị mờ/vỡ" — or types "/print-upscale <file>".
---

# Print Upscale — PDFs & images to print quality

Posters, flyers, menus and AI/Canva images are often only 1000–2500 px: fine on a phone, blurry in print. This skill upscales 4× with Real-ESRGAN (capped at 8000 px on the long side) and tags output at 300 dpi:

- **PDF** → every image inside is upscaled and replaced in place; position, rotation and transparency unchanged → `<name> - HD.pdf`
- **Image** → `<name> - HD.jpg` (JPEG q95), or `.png` if the image has transparency or `--png` is given
- **Folder** → every PDF/image inside (files already ending in ` - HD` are skipped)

Originals are never modified. **Reply in the user's language** (e.g. Vietnamese if they write in Vietnamese). `SKILL_DIR` is the folder containing this SKILL.md.

## Command

| | Mac / Linux | Windows |
|---|---|---|
| Command | `python3 "SKILL_DIR/scripts/run.py" "INPUT"` | `py -3 "SKILL_DIR\scripts\run.py" "INPUT"` (use `python` if `py` is missing) |

Several INPUTs are allowed. Options: `-o OUTPUT` (single input only), `--max-side 8000` (use `4000` for a lighter file to send in messages), `--png`, `--jpeg-quality 95`, `--setup-only`.

**Image pasted directly into the chat** (no file path): find the temporary image file the harness saved (its path usually appears in the message) and run with `-o` pointing into the user's Downloads folder, using a clear file name.

`run.py` detects the machine and **installs itself on first run** (~500 MB, once): a private Python environment + the right PyTorch build (Apple Silicon → Apple GPU; Windows/Linux with NVIDIA → CUDA; otherwise CPU) + the 64 MB model. Install folder: `~/.cache/print-upscale` (Mac) or `%LOCALAPPDATA%\print-upscale` (Windows).

No Python: tell the user to install it from https://www.python.org/downloads/ (Windows: check **"Add python.exe to PATH"**), then run again. Do not install Python for them.

## Workflow

1. **Look at the file** — Read tool (PDF: pages "1-3") to see the content.
2. **Run it.** First-time setup takes a few minutes → run in the background or with a long timeout and tell the user. Without a GPU (typical Windows office PC) a small poster takes minutes and a large one can take 10+ minutes → always run in the background and warn them.
3. **Check** — with the installed Python (Mac: `~/.cache/print-upscale/venv/bin/python`, Windows: `%LOCALAPPDATA%\print-upscale\venv\Scripts\python.exe`; it has Pillow and PyMuPDF `fitz`), crop the same small-text/logo area from the old and new versions, scale both to the same size, and view them to compare. Make sure the layout did not shift.
4. **Report**:
   - new file path, size before → after, file size
   - **printable size**: the script prints "print @300dpi up to … cm" (images) or "~… dpi" at page size (PDFs). ≥300 dpi = sharp up close; 150–300 = fine for a wall poster; <150 = small prints only.
   - the **real** improvement: if the original was already sharp, say the gain is small
   - text inside images stays an image (much sharper, but not vector); the AI does not change text, but suggest proofreading phone numbers, addresses and websites.

## Printing notes (mention when the user says they will print)
- Files are **RGB**; print shops convert to CMYK, so bright reds/greens may print slightly duller. If color matters → test print.
- No **bleed**; for edge-to-edge printing shops usually need +3 mm (⅛ in) per side or will trim slightly.
- Compare the **aspect ratio** with the paper (A4 = 1:1.414, Letter = 1:1.294, 18×24 in = 3:4); a mismatch means white margins or cropping.

## Technical notes
- PDF: opaque images → JPEG q95; images with transparency → lossless, mask resized to match. CMYK/Indexed converted to RGB. Vector/text-only PDFs → report that they are already sharp.
- Images already ≥ 8000 px are skipped (already large enough).
- Setup failed midway: delete the install folder and run `run.py --setup-only`.
