# print-upscale 🖨️

**Upscale miễn phí PDF và ảnh lên chất lượng in ấn**: một skill cho Claude Code, dùng AI Real-ESRGAN chạy ngay trên máy bạn.

- ✅ **Miễn phí, không giới hạn, không watermark**: không cần web upscale trả phí
- ✅ **Riêng tư**: file không bị tải lên đâu cả, AI chạy trên máy bạn
- ✅ **PDF và ảnh**: PDF, JPG, PNG, WEBP, TIFF, BMP, một file, nhiều file hay cả thư mục
- ✅ **Giữ nguyên bố cục PDF**: chỉ làm nét ảnh bên trong, vị trí và nền trong suốt y như cũ
- ✅ **Sẵn sàng để in**: phóng to 4x (tối đa 8000px), lưu ở 300 dpi, báo luôn khổ in được bao nhiêu cm
- ✅ **Mac và Windows**: tự nhận diện máy và tự cài

| Đầu vào | Kết quả | In đẹp 300 dpi đến khoảng |
|---|---|---|
| Ảnh 1467×2000 | 5868×8000 | 50 × 68 cm |
| Ảnh 1080×1350 (bài đăng Instagram) | 4320×5400 | 37 × 46 cm |
| Poster PDF A4 có ảnh 1440px | ảnh 5760px | A4 ở khoảng 480 dpi |

Hợp với: poster và flyer khuyến mãi, menu, voucher, banner tạo bằng Canva hay AI, ảnh tải từ mạng xã hội cần in lại.

> Cần **Claude Code** (tab **Code** trong app Claude desktop, hoặc bản CLI). Không chạy trong khung chat thường trên claude.ai.

---

## Cài đặt

### Mac
1. Mở **Terminal** và gõ `python3 --version`. Nếu máy hỏi cài *Command Line Tools* thì bấm **Install**.
2. Cài skill:
   ```bash
   git clone https://github.com/hungmarker/print-upscale ~/.claude/skills/print-upscale
   ```

### Windows
1. Cài **Python 3.10 trở lên** từ https://www.python.org/downloads/. Ở màn hình đầu, **tick ô "Add python.exe to PATH"**.
2. Cài **Git for Windows** từ https://git-scm.com/download/win (Claude Code trên Windows cũng cần cái này).
3. Mở **PowerShell** và cài skill:
   ```powershell
   git clone https://github.com/hungmarker/print-upscale "$env:USERPROFILE\.claude\skills\print-upscale"
   ```

### Lần chạy đầu
Lần đầu dùng, skill tự cài khoảng **500 MB**. Việc này chỉ làm một lần và mất vài phút. Skill tự chọn cách chạy nhanh nhất cho máy bạn:

| Máy | Chạy bằng | Tốc độ cho poster khoảng 1500px |
|---|---|---|
| Mac chip M (M1–M4…) | GPU Apple | khoảng 30–40 giây |
| Windows có card NVIDIA | GPU NVIDIA | nhanh, cỡ Mac chip M |
| Máy khác | CPU | vài phút, file lớn có thể hơn 10 phút |

Muốn cài trước cho sẵn:
- Mac: `python3 ~/.claude/skills/print-upscale/scripts/run.py --setup-only`
- Windows: `py -3 "$env:USERPROFILE\.claude\skills\print-upscale\scripts\run.py" --setup-only`

---

## Cách dùng
Trong Claude Code, kéo file PDF hoặc ảnh (hay cả thư mục) vào khung chat rồi gõ:

```
/print-upscale
```

hoặc nói tự nhiên, ví dụ *"làm nét file này để in"*. Claude sẽ:
1. Upscale và lưu bản mới thành `<tên> - HD.pdf` hoặc `<tên> - HD.jpg` cạnh file gốc. File gốc không bị sửa.
2. So sánh bản cũ với bản mới.
3. Báo khổ in được và nhắc những điểm cần lưu ý khi in.

Cần file nhẹ để gửi qua tin nhắn thì nói thêm *"bản nhẹ"* (giới hạn 4000px).

### Chạy không cần Claude (tùy chọn)
```bash
python3 ~/.claude/skills/print-upscale/scripts/run.py "poster.pdf" "menu.jpg" "Thu muc anh/"
```
Tùy chọn: `-o file-ra.jpg`, `--max-side 4000`, `--png`, `--jpeg-quality 95`.

---

## Mẹo khi đem in
- **Màu**: file ở hệ màu RGB (cho màn hình). Nhà in chuyển sang CMYK nên màu đỏ và xanh tươi có thể trầm hơn một chút. Nếu màu quan trọng thì nên in thử một tờ.
- **Lề tràn (bleed)**: muốn in tràn sát mép thì nhà in thường cần thêm 3 mm mỗi cạnh, hoặc họ sẽ xén nhẹ. Đừng để chữ quá sát mép.
- **Tỉ lệ**: A4 là 1:1.414, Letter là 1:1.294, 18×24 inch là 3:4. Ảnh khác tỉ lệ khổ giấy sẽ bị dư viền hoặc bị cắt.
- **Soát chữ**: AI làm nét chứ không đổi chữ, nhưng vẫn nên soát số điện thoại, địa chỉ và website trước khi in số lượng lớn.
- Chữ trong ảnh vẫn là ảnh: nét hơn rất nhiều, nhưng không phải chữ vector như file thiết kế gốc.

---

## Cập nhật
```bash
git -C ~/.claude/skills/print-upscale pull
```
Windows: `git -C "$env:USERPROFILE\.claude\skills\print-upscale" pull`

## Gỡ
Xóa thư mục skill (`~/.claude/skills/print-upscale`) và thư mục cài (`~/.cache/print-upscale` trên Mac, `%LOCALAPPDATA%\print-upscale` trên Windows).

## Ghi công
- Model [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) (BSD-3-Clause) của Xintao Wang và cộng sự, tải trực tiếp từ trang release chính thức khi cài.
- Xử lý PDF bằng [PyMuPDF](https://pymupdf.readthedocs.io/), nạp model bằng [spandrel](https://github.com/chaiNNer-org/spandrel).
