# Giải thích code dự án Aagent

## Tổng quan nhanh
Dự án gồm 2 file chính:

- `GUI.py`: giao diện Tkinter để nhập thông tin người dùng và cấu hình học tập.
- `Agent_core.py`: xử lý đăng nhập hệ thống trường, lấy bảng điểm bằng Selenium, lưu dữ liệu JSON, rồi dùng AI Agent để phân tích và đề xuất kế hoạch cải thiện GPA.

## Luồng chạy chính
1. Chạy `main()` trong `Agent_core.py`.
2. Mở GUI (`SimpleTrainingProgramGUI`) để nhập:
   - tài khoản/mật khẩu,
   - file PDF chương trình đào tạo,
   - số kỳ còn lại,
   - học phí tín chỉ.
3. Sau khi xác nhận, chương trình lấy thông tin đăng nhập từ GUI.
4. `GpaAnalyzer.setup_driver()` khởi tạo Edge WebDriver.
5. `login_and_scrape()` đăng nhập vào cổng trường và truy cập trang bảng điểm.
6. `_extract_grades_data()` đọc bảng điểm, chuẩn hóa dữ liệu môn học và GPA theo kỳ/tích lũy.
7. `save_data()` ghi dữ liệu ra `ket_qua.json`.
8. `setup_agent()` tạo AI agent (Agno + Ollama) với knowledge base từ JSON.
9. `analyze_gpa()` gửi yêu cầu phân tích và nhận kết quả có cấu trúc (`PhanTichKetQua`).
10. In kết quả tóm tắt ra terminal.

## Các model dữ liệu trong `Agent_core.py`
- `MonCanCaiThien`: mô tả môn cần cải thiện (mã môn, điểm, tín chỉ, mức ưu tiên...).
- `HocPhanUuTien`: mô tả học phần nên ưu tiên học.
- `ChienLuocCaiThien`: chiến lược cải thiện học tập.
- `KeHoachHocTap`: kế hoạch tổng hợp theo mục tiêu GPA.
- `PhanTichKetQua`: kết quả phân tích cuối cùng trả về cho người dùng.

## Xử lý lỗi
- Có `try/except` ở các bước chính: khởi tạo driver, đăng nhập/scrape, lưu file, phân tích AI.
- GUI kiểm tra đầu vào trước khi cho phép tiếp tục.

## File dữ liệu
- `ket_qua.json`: chứa dữ liệu bảng điểm đã scrape và được dùng làm knowledge base cho agent.
