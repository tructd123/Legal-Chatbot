from document_processor import LegalDocumentProcessor

# 1. Khởi tạo
proc = LegalDocumentProcessor()

# 2. Đọc file MỘT LẦN DUY NHẤT và lưu vào biến
print("Đang xử lý file...")
#full_text = proc.read_pdf("data\\22-qh-15.signed.pdf")


full_text, pages = proc.read_pdf(r"data\\22-qh-15.signed.pdf", return_pages=True)
print("Tổng số trang:", len(pages))

for idx in range(1009, min(len(pages), 1016)):
    print(f"Trang {idx+1}: {len(pages[idx])} ký tự")


# 3. In tổng số ký tự
print(f"✅ Tổng số ký tự: {len(full_text)}")

# 4. Tách trang (Lưu ý: Logic này chỉ là tương đối, xem giải thích bên dưới)
# Vì hàm read_pdf trả về string nối liền, ta tạm split theo dòng trống
pages = full_text.split("\n\n") 
print(f"Số đoạn/trang tách được: {len(pages)}")

# 5. In thử nội dung
for i, page in enumerate(pages[20:25]): # Chỉ in 5 đoạn đầu để kiểm tra
    print(f"--- Đoạn {i+1} ---")
    print(page.replace('\n', ' ')) # In gọn 500 ký tự đầu
    print("...")