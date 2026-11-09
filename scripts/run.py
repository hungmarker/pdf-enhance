"""print-upscale: free AI upscaling of PDFs and images to print quality.
Cross-platform entry point (macOS / Windows / Linux).

    Mac:      python3 scripts/run.py INPUT [INPUT ...] [-o OUTPUT] [options]
    Windows:  py -3 scripts\\run.py INPUT [INPUT ...] [-o OUTPUT] [options]

INPUT: a .pdf, an image (.jpg .png .webp .bmp .tif) or a folder of them.
Output: "<name> - HD.pdf" / "<name> - HD.jpg" (".png" if transparent) next to the input.
Options: --max-side 8000  --png  --jpeg-quality 95  --min-side 64  --setup-only

On first run it creates a private Python environment and downloads the AI model
(about 500 MB, once).
"""
import os, platform, shutil, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"

def home_dir():
    if os.environ.get("PRINT_UPSCALE_HOME"):
        return os.environ["PRINT_UPSCALE_HOME"]
    if IS_WIN:
        return os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "print-upscale")
    return os.path.join(os.path.expanduser("~"), ".cache", "print-upscale")

HOME = home_dir()
VENV = os.path.join(HOME, "venv")
VPY = os.path.join(VENV, "Scripts", "python.exe") if IS_WIN else os.path.join(VENV, "bin", "python")
MODEL = os.path.join(HOME, "models", "RealESRGAN_x4plus.pth")
MODEL_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
STAMP = os.path.join(HOME, ".installed-v1")
BASE_PKGS = ["pymupdf", "pillow", "numpy", "spandrel", "packaging", "safetensors"]

def log(msg):
    print(f"[print-upscale] {msg}", flush=True)

def pip(*args):
    subprocess.check_call([VPY, "-m", "pip", "install", "--disable-pip-version-check", "-q", *args])

def has_nvidia():
    return shutil.which("nvidia-smi") is not None and subprocess.call(
        ["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def install_torch():
    if (IS_WIN or sys.platform.startswith("linux")) and has_nvidia():
        log("NVIDIA GPU found -> installing PyTorch with CUDA (large download)")
        try:
            pip("torch", "--index-url", "https://download.pytorch.org/whl/cu126"); return
        except subprocess.CalledProcessError:
            log("CUDA build failed, falling back to CPU build")
    if IS_WIN or sys.platform.startswith("linux"):
        log("Installing PyTorch (CPU build)")
        pip("torch", "--index-url", "https://download.pytorch.org/whl/cpu")
    else:
        log("Installing PyTorch (Apple GPU / MPS)" if platform.machine() == "arm64" else "Installing PyTorch")
        pip("torch")

def setup():
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9+ is required. Install it from https://www.python.org/downloads/")
    os.makedirs(os.path.dirname(MODEL), exist_ok=True)
    model_ok = os.path.exists(MODEL) and os.path.getsize(MODEL) > 60_000_000
    if os.path.exists(STAMP) and os.path.exists(VPY) and model_ok:
        return
    log(f"First-time setup in {HOME} ({platform.system()} {platform.machine()})")
    if not os.path.exists(VPY):
        log("Creating Python environment")
        subprocess.check_call([sys.executable, "-m", "venv", VENV])
    subprocess.call([VPY, "-m", "pip", "install", "-q", "--disable-pip-version-check", "--upgrade", "pip"])
    install_torch()
    log("Installing PDF/image libraries")
    pip(*BASE_PKGS)
    if not (os.path.exists(MODEL) and os.path.getsize(MODEL) > 60_000_000):
        log("Downloading Real-ESRGAN model (64 MB)")
        tmp = MODEL + ".part"
        urllib.request.urlretrieve(MODEL_URL, tmp)
        os.replace(tmp, MODEL)
    open(STAMP, "w").write("ok\n")
    log("Setup complete")

def main():
    args = sys.argv[1:]
    setup()
    if "--setup-only" in args:
        return
    if not args or args[0] in ("-h", "--help"):
        print(__doc__); return
    env = dict(os.environ, PRINT_UPSCALE_HOME=HOME, PYTHONIOENCODING="utf-8")
    sys.exit(subprocess.call([VPY, "-I", os.path.join(HERE, "upscale.py"), *args], env=env))

if __name__ == "__main__":
    main()
