---
name: pdf-enhance
description: Tăng chất lượng hình ảnh trong file PDF (poster, flyer, notice, menu tiệm…) bằng AI Real-ESRGAN x4 — làm nét chữ/viền, xóa vết nén JPEG, giữ nguyên bố cục gốc. Chạy được trên Mac và Windows. Dùng khi người dùng gửi PDF và nói "tăng chất lượng", "làm nét", "upscale", "PDF bị mờ/vỡ", "/pdf-enhance <file>".
---

# PDF Enhance — làm nét ảnh trong PDF

Poster/flyer xuất từ Canva hoặc AI thường là PDF chỉ chứa ảnh raster độ phân giải thấp. Skill này upscale **từng ảnh** trong PDF 4x bằng Real-ESRGAN rồi **thay ngay tại chỗ**, nên vị trí, xoay, clip và nền trong suốt giữ y như bản gốc. File gốc không bị sửa. Trả lời người dùng bằng ngôn ngữ họ dùng (thường là tiếng Việt).

`SKILL_DIR` dưới đây là thư mục chứa file SKILL.md này.

## Lệnh chạy theo hệ điều hành

| | Mac / Linux | Windows |
|---|---|---|
| Python để khởi chạy | `python3` | `py -3` (nếu không có thì `python`) |
| Lệnh | `python3 "SKILL_DIR/scripts/run.py" "INPUT.pdf"` | `py -3 "SKILL_DIR\scripts\run.py" "INPUT.pdf"` |

`run.py` tự nhận diện máy và **tự cài lần đầu** (~500 MB, chỉ một lần): tạo môi trường Python riêng, cài PyTorch phù hợp (Mac chip M → GPU Apple; Windows có NVIDIA → bản CUDA; còn lại → bản CPU), tải model 64 MB. Dữ liệu cài nằm ở `~/.cache/pdf-enhance` (Mac) hoặc `%LOCALAPPDATA%\pdf-enhance` (Windows).

Nếu không có Python: báo người dùng cài từ https://www.python.org/downloads/ (Windows: tick **"Add python.exe to PATH"**), rồi chạy lại. Không tự cài Python hộ.

## Quy trình

1. **Xem nhanh PDF** — đọc file bằng Read tool (pages "1-3") để biết nội dung, số trang.
2. **Chạy** (mặc định ra `<tên gốc> - HD.pdf` cạnh file gốc). Lần đầu cài đặt lâu (vài phút) → chạy nền (`run_in_background`) hoặc timeout dài; báo người dùng đang cài lần đầu.
   Tùy chọn: `--max-side 8000` (giới hạn cạnh dài sau upscale; dùng `4000` cho file nhẹ để gửi tin nhắn), `--min-side 64`, `--jpeg-quality 94`, `--setup-only` (chỉ cài).
   Máy Windows không có NVIDIA chạy bằng CPU: poster nhỏ vài phút, poster lớn có thể >10 phút — luôn chạy nền và báo trước.
3. **Kiểm tra** — dùng Python trong môi trường đã cài (Mac: `~/.cache/pdf-enhance/venv/bin/python`, Windows: `%LOCALAPPDATA%\pdf-enhance\venv\Scripts\python.exe`) với PyMuPDF (`import fitz`) để render bản mới (toàn trang, ~60–100 dpi) và crop ~180–300 dpi một vùng chữ nhỏ ở cả bản cũ lẫn mới; xem ảnh để so sánh. Đảm bảo bố cục không lệch.
4. **Báo lại**: đường dẫn file mới, kích thước ảnh trước → sau (script in ra), dung lượng file, mức cải thiện thật sự (nếu bản gốc vốn đã nét thì nói rõ là cải thiện ít), lưu ý chữ trong ảnh vẫn là ảnh (nét hơn nhưng không phải vector).

## Ghi chú
- Ảnh nền đục → JPEG q94; ảnh có nền trong suốt → nén lossless, mask được resize theo.
- CMYK/Indexed được chuyển sang RGB; stencil mask và ảnh quá nhỏ bị bỏ qua. PDF chỉ có chữ vector (không ảnh) thì không cần làm gì — báo người dùng là file đã nét sẵn.
- Lỗi cài đặt giữa chừng: xóa thư mục cài (đường dẫn ở trên) rồi chạy lại `run.py --setup-only`.
