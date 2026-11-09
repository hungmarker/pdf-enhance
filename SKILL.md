---
name: print-upscale
description: Upscale miễn phí PDF và ảnh (JPG/PNG/WEBP/TIFF) lên chất lượng in ấn bằng AI Real-ESRGAN x4, chạy offline trên máy, không watermark — làm nét chữ/viền, xóa vết nén, giữ nguyên bố cục. Chạy được trên Mac và Windows. Dùng khi người dùng gửi PDF/ảnh (hoặc thư mục) và nói "làm nét", "tăng chất lượng", "upscale", "để in", "ảnh/PDF bị mờ, vỡ", "/print-upscale <file>".
---

# Print Upscale — PDF & ảnh lên chất lượng in

Poster, flyer, menu, ảnh tạo bằng AI/Canva thường chỉ 1000–2500px — đủ xem trên điện thoại nhưng in ra bị nhòe. Skill này phóng to 4x bằng Real-ESRGAN (tối đa 8000px cạnh dài), lưu ở 300 dpi:

- **PDF** → upscale từng ảnh bên trong và thay tại chỗ: vị trí, xoay, nền trong suốt giữ nguyên → `<tên> - HD.pdf`
- **Ảnh** → `<tên> - HD.jpg` (JPEG q95), hoặc `.png` nếu ảnh có nền trong suốt / dùng `--png`
- **Thư mục** → xử lý mọi PDF/ảnh bên trong (bỏ qua file đã có đuôi ` - HD`)

File gốc không bị sửa. Trả lời người dùng bằng ngôn ngữ họ dùng (thường là tiếng Việt). `SKILL_DIR` là thư mục chứa file SKILL.md này.

## Lệnh chạy

| | Mac / Linux | Windows |
|---|---|---|
| Lệnh | `python3 "SKILL_DIR/scripts/run.py" "INPUT"` | `py -3 "SKILL_DIR\scripts\run.py" "INPUT"` (không có `py` thì dùng `python`) |

Có thể truyền nhiều INPUT. Tùy chọn: `-o OUTPUT` (chỉ khi 1 file), `--max-side 8000` (dùng `4000` cho file nhẹ để gửi tin nhắn), `--png`, `--jpeg-quality 95`, `--setup-only`.

**Ảnh dán thẳng vào chat** (không có đường dẫn): tìm file ảnh tạm mà harness lưu (đường dẫn thường hiện trong tin nhắn), chạy với `-o` trỏ tới thư mục Downloads của người dùng, đặt tên dễ hiểu.

`run.py` tự nhận diện máy và **tự cài lần đầu** (~500 MB, chỉ một lần): môi trường Python riêng + PyTorch phù hợp (Mac chip M → GPU Apple; Windows/Linux có NVIDIA → CUDA; còn lại → CPU) + model 64 MB. Thư mục cài: `~/.cache/print-upscale` (Mac) hoặc `%LOCALAPPDATA%\print-upscale` (Windows).

Không có Python: báo người dùng cài từ https://www.python.org/downloads/ (Windows: tick **"Add python.exe to PATH"**), rồi chạy lại. Không tự cài Python hộ.

## Quy trình

1. **Xem nhanh file** — Read tool (PDF: pages "1-3") để biết nội dung.
2. **Chạy**. Lần đầu cài mất vài phút → chạy nền hoặc timeout dài và báo người dùng. Máy không có GPU (Windows thường): poster nhỏ vài phút, poster lớn có thể >10 phút → luôn chạy nền và báo trước.
3. **Kiểm tra** — dùng Python trong môi trường đã cài (Mac: `~/.cache/print-upscale/venv/bin/python`, Windows: `%LOCALAPPDATA%\print-upscale\venv\Scripts\python.exe`; có Pillow + PyMuPDF `fitz`) crop cùng một vùng chữ nhỏ/logo ở bản cũ và bản mới, phóng lên cùng kích thước, xem ảnh để so sánh. Đảm bảo bố cục không lệch.
4. **Báo lại**:
   - đường dẫn file mới, kích thước trước → sau, dung lượng
   - **khổ in được**: script in sẵn "print @300dpi up to … cm" (ảnh) hoặc "~… dpi" ở khổ trang (PDF). ≥300 dpi = in đẹp nhìn gần; 150–300 = ổn cho poster treo tường; <150 = chỉ in nhỏ.
   - mức cải thiện **thật**: nếu bản gốc đã nét thì nói rõ là cải thiện ít
   - chữ trong ảnh vẫn là ảnh (nét hơn nhưng không phải vector); AI không đổi chữ nhưng nên soát lại số điện thoại / địa chỉ / website.

## Lưu ý khi in (nhắc khi người dùng nói sẽ in)
- File ở hệ màu **RGB**; nhà in chuyển sang CMYK → đỏ/xanh tươi có thể trầm hơn chút. Màu quan trọng → in thử 1 tờ.
- Không có **lề tràn (bleed)**; in tràn mép thì nhà in thường cần thêm 3 mm mỗi cạnh hoặc sẽ xén nhẹ.
- So **tỉ lệ** ảnh với khổ giấy (A4 = 1:1.414, Letter = 1:1.294, 18×24 in = 3:4); lệch tỉ lệ sẽ bị dư viền hoặc cắt.

## Ghi chú kỹ thuật
- PDF: ảnh nền đục → JPEG q95; ảnh có nền trong suốt → nén lossless, mask resize theo. CMYK/Indexed chuyển RGB. PDF chỉ có chữ vector → báo là đã nét sẵn.
- Ảnh đã ≥ 8000px được bỏ qua (đã đủ lớn).
- Lỗi cài đặt giữa chừng: xóa thư mục cài rồi chạy `run.py --setup-only`.
