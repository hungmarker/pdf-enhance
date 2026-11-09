# pdf-enhance — Skill Claude Code làm nét PDF

Làm nét poster / flyer / menu dạng PDF bằng AI (Real-ESRGAN x4). Chữ và viền sắc hơn, hết vết nhòe do nén, **bố cục giữ nguyên**. File gốc không bị sửa — bản mới lưu thành `<tên> - HD.pdf` cạnh file gốc.

> Cần **Claude Code** (tab **Code** trong app Claude desktop, hoặc bản CLI). Không chạy trong khung chat thường trên claude.ai.

## Cài đặt

### Mac
1. Mở **Terminal**, kiểm tra Python: `python3 --version`. Nếu máy hỏi cài *Command Line Tools* → bấm **Install**.
2. Cài skill:
   ```bash
   git clone https://github.com/hungmarker/pdf-enhance ~/.claude/skills/pdf-enhance
   ```

### Windows
1. Cài **Python 3.10 trở lên** từ https://www.python.org/downloads/ — ở màn hình đầu **tick ô "Add python.exe to PATH"**.
2. Cài **Git for Windows** từ https://git-scm.com/download/win (Claude Code trên Windows cũng cần cái này).
3. Mở **PowerShell**, cài skill:
   ```powershell
   git clone https://github.com/hungmarker/pdf-enhance "$env:USERPROFILE\.claude\skills\pdf-enhance"
   ```

### Lần chạy đầu
Lần đầu dùng, skill tự nhận diện máy và tự cài (khoảng **500 MB**, chỉ một lần, mất vài phút):
- Mac chip M → dùng GPU của Apple (nhanh)
- Windows có card NVIDIA → dùng GPU NVIDIA (nhanh)
- Máy khác → dùng CPU (chậm hơn: vài phút đến hơn 10 phút mỗi poster)

Muốn cài trước cho sẵn: `python3 ~/.claude/skills/pdf-enhance/scripts/run.py --setup-only` (Mac) hoặc `py -3 "$env:USERPROFILE\.claude\skills\pdf-enhance\scripts\run.py" --setup-only` (Windows).

## Cách dùng
Trong Claude Code, kéo file PDF vào khung chat và gõ:

```
/pdf-enhance
```

hoặc chỉ cần nói *"tăng chất lượng file PDF này"*. Claude sẽ chạy, so sánh bản cũ/mới và báo lại.

## Cập nhật
```bash
git -C ~/.claude/skills/pdf-enhance pull
```
(Windows: `git -C "$env:USERPROFILE\.claude\skills\pdf-enhance" pull`)

## Gỡ
Xóa thư mục `~/.claude/skills/pdf-enhance` và thư mục cài `~/.cache/pdf-enhance` (Mac) hoặc `%LOCALAPPDATA%\pdf-enhance` (Windows).

## Ghi công
Model [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) (BSD-3-Clause) của Xintao Wang và cộng sự, tải trực tiếp từ trang release chính thức khi cài. PDF xử lý bằng [PyMuPDF](https://pymupdf.readthedocs.io/).
