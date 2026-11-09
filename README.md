# print-upscale 🖨️

**Free AI upscaling of PDFs and images to print quality.** A Claude Code skill powered by Real-ESRGAN that runs entirely on your own computer.

- ✅ **Free, unlimited, no watermark**: no paid upscaling website needed
- ✅ **Private**: your files never leave your computer
- ✅ **PDFs and images**: PDF, JPG, PNG, WEBP, TIFF and BMP, as a single file, several files or a whole folder
- ✅ **PDF layout untouched**: only the images inside are sharpened; positions, rotation and transparency stay exactly the same
- ✅ **Print-ready**: 4× upscale (capped at 8000 px), tagged 300 dpi, and it tells you how large you can print
- ✅ **Mac and Windows**: detects your machine and installs itself

| Input | Output | Prints sharp at 300 dpi up to |
|---|---|---|
| 1467×2000 image | 5868×8000 | 50 × 68 cm (19.6 × 26.7 in) |
| 1080×1350 Instagram post | 4320×5400 | 37 × 46 cm (14.4 × 18 in) |
| A4 PDF poster with a 1440 px image | 5760 px image | A4 at ~480 dpi |

Great for promo posters and flyers, menus, gift vouchers, banners made in Canva or with AI, and social media images you need to print.

> Requires **Claude Code** (the **Code** tab in the Claude desktop app, or the CLI). It does not run in the regular claude.ai chat.

---

## Install

### Mac
1. Open **Terminal** and run `python3 --version`. If macOS offers to install the *Command Line Tools*, click **Install**.
2. Install the skill:
   ```bash
   git clone https://github.com/hungmarker/print-upscale ~/.claude/skills/print-upscale
   ```

### Windows
1. Install **Python 3.10 or newer** from https://www.python.org/downloads/. On the first screen, **check "Add python.exe to PATH"**.
2. Install **Git for Windows** from https://git-scm.com/download/win (Claude Code on Windows needs it too).
3. Open **PowerShell** and install the skill:
   ```powershell
   git clone https://github.com/hungmarker/print-upscale "$env:USERPROFILE\.claude\skills\print-upscale"
   ```

### First run
On first use the skill installs what it needs, about **500 MB**. This happens once and takes a few minutes. It picks the fastest option for your machine:

| Machine | Runs on | Speed for a ~1500 px poster |
|---|---|---|
| Apple Silicon Mac (M1–M4…) | Apple GPU | ~30–40 seconds |
| Windows with an NVIDIA card | NVIDIA GPU | fast, similar to Apple Silicon |
| Anything else | CPU | a few minutes; large files can take 10+ minutes |

To install ahead of time:
- Mac: `python3 ~/.claude/skills/print-upscale/scripts/run.py --setup-only`
- Windows: `py -3 "$env:USERPROFILE\.claude\skills\print-upscale\scripts\run.py" --setup-only`

---

## Usage
In Claude Code, drag a PDF, an image or a folder into the chat and type:

```
/print-upscale
```

or just ask in plain words, e.g. *"sharpen this file for printing"*. Claude will:
1. Upscale it and save `<name> - HD.pdf` or `<name> - HD.jpg` next to the original. The original is never modified.
2. Compare the old and new versions side by side.
3. Tell you the printable size and what to watch out for when printing.

Need a lighter file for messaging apps? Ask for a *"smaller version"* (capped at 4000 px).

### Run without Claude (optional)
```bash
python3 ~/.claude/skills/print-upscale/scripts/run.py "poster.pdf" "menu.jpg" "Image folder/"
```
Options: `-o output.jpg`, `--max-side 4000`, `--png`, `--jpeg-quality 95`.

---

## Printing tips
- **Color**: files are RGB (screen colors). Print shops convert to CMYK, so bright reds and greens may print slightly duller. If color matters, order a test print.
- **Bleed**: for edge-to-edge printing, shops usually need an extra 3 mm (⅛ in) on each side or will trim a little. Keep text away from the edges.
- **Aspect ratio**: A4 is 1:1.414, US Letter is 1:1.294, 18×24 in is 3:4. An image with a different ratio will get white margins or be cropped.
- **Proofread**: the AI sharpens text but never rewrites it. Still, double-check phone numbers, addresses and websites before a large print run.
- Text inside images stays an image: much sharper, but not vector text like the original design file.

---

## Update
```bash
git -C ~/.claude/skills/print-upscale pull
```
Windows: `git -C "$env:USERPROFILE\.claude\skills\print-upscale" pull`

## Uninstall
Delete the skill folder (`~/.claude/skills/print-upscale`) and the install folder (`~/.cache/print-upscale` on Mac, `%LOCALAPPDATA%\print-upscale` on Windows).

## Credits
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) model (BSD-3-Clause) by Xintao Wang et al., downloaded from its official release page during setup.
- PDF handling by [PyMuPDF](https://pymupdf.readthedocs.io/); model loading by [spandrel](https://github.com/chaiNNer-org/spandrel).
