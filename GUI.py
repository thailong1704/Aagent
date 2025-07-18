import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from datetime import datetime

class SimpleTrainingProgramGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý Chương trình Đào tạo")
        self.root.geometry("500x500")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.pdf_file = tk.StringVar()
        self.remaining_semesters = tk.IntVar()
        self.credit_fee = tk.DoubleVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="QUẢN LÝ CHƯƠNG TRÌNH ĐÀO TẠO", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Login frame
        login_frame = ttk.LabelFrame(main_frame, text="Đăng nhập", padding="10")
        login_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Username
        ttk.Label(login_frame, text="Tài khoản:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(login_frame, textvariable=self.username, width=30).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Password
        ttk.Label(login_frame, text="Mật khẩu:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(login_frame, textvariable=self.password, show="*", width=30).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        login_frame.columnconfigure(1, weight=1)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Chọn file chương trình đào tạo (PDF)", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        file_entry_frame = ttk.Frame(file_frame)
        file_entry_frame.pack(fill=tk.X)
        
        ttk.Entry(file_entry_frame, textvariable=self.pdf_file, state='readonly').pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(file_entry_frame, text="Chọn PDF", command=self.select_pdf).pack(side=tk.RIGHT)
        
        # Information input frame
        input_frame = ttk.LabelFrame(main_frame, text="Thông tin học tập", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Remaining semesters
        ttk.Label(input_frame, text="Số kì còn lại:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(input_frame, from_=1, to=20, textvariable=self.remaining_semesters, width=10).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Credit fee
        ttk.Label(input_frame, text="Học phí/tín chỉ (x1.000 VNĐ):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.credit_fee, width=20).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Export button
        export_button = ttk.Button(main_frame, text="Xác nhận", command=self.export_json)
        export_button.pack(pady=20)
        
    def select_pdf(self):
        """Chọn file PDF chương trình đào tạo"""
        filename = filedialog.askopenfilename(
            title="Chọn file chương trình đào tạo",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            self.pdf_file.set(filename)
    
    def export_json(self):
        """Xuất dữ liệu ra file JSON"""
        # Kiểm tra dữ liệu đầu vào
        if not self.username.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập tài khoản!")
            return
            
        if not self.password.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu!")
            return
            
        if not self.pdf_file.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file PDF chương trình đào tạo!")
            return
            
        if self.remaining_semesters.get() <= 0:
            messagebox.showerror("Lỗi", "Số kì còn lại phải lớn hơn 0!")
            return
            
        if self.credit_fee.get() <= 0:
            messagebox.showerror("Lỗi", "Học phí tín chỉ phải lớn hơn 0!")
            return
        
        # Tạo dữ liệu JSON
        self.data = {
            "user_info": {
                "username": self.username.get().strip(),
                "password": self.password.get().strip(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "training_program": {
                "pdf_file_path": self.pdf_file.get(),
                "remaining_semesters": self.remaining_semesters.get(),
                "credit_fee": self.credit_fee.get()* 1000  # Chuyển đổi sang VNĐ
            },
            
            
        }       
        if self.data:
            try:
                messagebox.showinfo("thông báo", "Xuất dữ liệu thành công!")
                self.root.destroy()   
            except Exception as e:
                messagebox.showerror("Lỗi không thể xuất", f"Đã xảy ra lỗi khi xuất dữ liệu: {str(e)}")
          
    

