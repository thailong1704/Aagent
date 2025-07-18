from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from typing import List, Optional, Dict, Any
from textwrap import dedent
from pydantic import BaseModel, Field, validator
from GUI import *
import logging

# Agno imports
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.knowledge.json import JSONKnowledgeBase
from agno.tools.reasoning import ReasoningTools

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonCanCaiThien(BaseModel):
    """Model cho môn học cần cải thiện"""
    ma_mon: str = Field(..., description="Mã số của môn học cần cải thiện")
    ten_mon: str = Field(..., description="Tên đầy đủ của môn học cần cải thiện")
    diem_so: float = Field(..., description="Điểm số hiện tại theo thang điểm GPA (0-10)")
    tin_chi: int = Field(..., description="Số tín chỉ của môn học")
    diem_chu: str = Field(..., description="Điểm chữ hiện tại (A+, A, B+, B, C+, C, D+, D, F)")
    ly_do: str = Field(..., description="Lý do cụ thể tại sao môn này cần cải thiện")
    muc_do_uu_tien: str = Field(..., description="Mức độ ưu tiên: 'Cao', 'Trung bình', 'Thấp'")
    
    @validator('diem_so')
    def validate_diem_so(cls, v):
        if not 0 <= v <= 10:
            raise ValueError('Điểm số phải nằm trong khoảng 0-10')
        return v
    
    @validator('tin_chi')
    def validate_tin_chi(cls, v):
        if v <= 0:
            raise ValueError('Số tín chỉ phải lớn hơn 0')
        return v

class HocPhanUuTien(BaseModel):
    """Model cho học phần được ưu tiên"""
    ma_mon: str = Field(..., description="Mã số của học phần")
    ten_mon: str = Field(..., description="Tên đầy đủ của học phần")
    tin_chi: int = Field(..., description="Số tín chỉ của học phần")
    diem_hien_tai: Optional[float] = Field(None, description="Điểm hiện tại nếu đã học")
    uu_tien_vi: str = Field(..., description="Lý do ưu tiên học phần này")
    kha_nang_cai_thien: str = Field(..., description="Đánh giá khả năng cải thiện: 'Dễ', 'Trung bình', 'Khó'")
    thoi_gian_de_xuat: str = Field(..., description="Thời gian đề xuất học: 'Học kỳ tới', 'Học kỳ hè', 'Trong năm'")

class ChienLuocCaiThien(BaseModel):
    """Model cho chiến lược cải thiện"""
    ten_chien_luoc: str = Field(..., description="Tên chiến lược")
    mo_ta: str = Field(..., description="Mô tả chi tiết chiến lược")
    thoi_gian_thuc_hien: str = Field(..., description="Thời gian thực hiện ước tính")
    do_kho: str = Field(..., description="Mức độ khó: 'Dễ', 'Trung bình', 'Khó'")
    tai_nguyen_can_thiet: List[str] = Field(..., description="Danh sách tài nguyên cần thiết")

class KeHoachHocTap(BaseModel):
    """Model cho kế hoạch học tập"""
    muc_tieu_gpa: float = Field(..., description="Mục tiêu GPA muốn đạt được")
    thoi_gian_du_kien: str = Field(..., description="Thời gian dự kiến để đạt mục tiêu")
    chien_luoc_chinh: List[ChienLuocCaiThien] = Field(..., description="Các chiến lược chính")
    cac_buoc_thuc_hien: List[str] = Field(..., description="Các bước thực hiện cụ thể theo thứ tự")
    rui_ro_tiem_an: List[str] = Field(..., description="Các rủi ro tiềm ẩn và cách phòng tránh")

class PhanTichKetQua(BaseModel):
    """Model chính cho kết quả phân tích"""
    gpa_hien_tai: float = Field(..., description="GPA hiện tại của sinh viên")
    tong_tin_chi_da_hoc: int = Field(..., description="Tổng số tín chỉ đã học")
    nhan_xet_tong_quan: str = Field(..., description="Nhận xét chi tiết về tình hình học tập")
    diem_manh: List[str] = Field(..., description="Các điểm mạnh trong học tập")
    diem_yeu: List[str] = Field(..., description="Các điểm yếu cần cải thiện")
    mon_can_cai_thien: List[MonCanCaiThien] = Field(..., description="Danh sách môn học cần cải thiện")
    hoc_phan_uu_tien: List[HocPhanUuTien] = Field(..., description="Danh sách học phần ưu tiên")
    ke_hoach_chi_tiet: KeHoachHocTap = Field(..., description="Kế hoạch học tập chi tiết")
    du_bao_ket_qua: str = Field(..., description="Dự báo khả năng đạt được mục tiêu")

class GpaAnalyzer:
    """Class chính để phân tích GPA"""
    
    def __init__(self, output_file: str = "ket_qua.json"):
        self.output_file = output_file
        self.driver = None
        self.knowledge_base = None
        self.agent = None
        
    def setup_driver(self):
        """Thiết lập webdriver với error handling"""
        try:
            options = webdriver.EdgeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Edge(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Webdriver đã được thiết lập thành công")
            
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập webdriver: {e}")
            raise
    
    def login_and_scrape(self, username: str, password: str) -> Dict[str, Any]:
        """Đăng nhập và scrape dữ liệu với error handling"""
        try:
            self.driver.get("https://sso.hcmut.edu.vn/cas/login?service=https%3A%2F%2Fmybk.hcmut.edu.vn%2Fapp%2Flogin%2Fcas")
            
            # Đăng nhập
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(username)
            
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            
            login_button = self.driver.find_element(By.NAME, 'submit')
            login_button.click()
            
            # Chuyển đến trang bảng điểm
            self.driver.get("https://mybk.hcmut.edu.vn/app/sinh-vien/ket-qua-hoc-tap/bang-diem-hoc-ky")
            time.sleep(10)  # Đợi một chút để trang load
            
            # Đợi trang load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "lsKetQuaHocTap"))
            )
            
            return self._extract_grades_data()
            
        except TimeoutException:
            logger.error("Timeout khi tải trang")
            raise
        except NoSuchElementException as e:
            logger.error(f"Không tìm thấy element: {e}")
            raise
        except Exception as e:
            logger.error(f"Lỗi trong quá trình đăng nhập và scrape: {e}")
            raise
    
    def _extract_grades_data(self) -> Dict[str, Any]:
        
        """Trích xuất dữ liệu bảng điểm"""
        try:
            table = self.driver.find_element(By.ID, "lsKetQuaHocTap")
            rows = table.find_elements(By.XPATH, ".//tbody/tr")
            
            bang_diem = []
            total_gpa = []
            
            # Xử lý từng dòng điểm
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 8:
                    try:
                        mon_hoc = {
                            "ma_mon": cols[0].text.strip(),
                            "ten_mon": cols[1].text.strip(),
                            "tin_chi": int(cols[2].text.strip()) if cols[2].text.strip().isdigit() else 0,
                            "diem_tp": cols[3].text.strip(),
                            "diem_so": self._parse_float(cols[4].text.strip()),
                            "diem_chu": cols[5].text.strip(),
                            "diem_dat": cols[6].text.strip(),
                            "cap_nhat": cols[7].text.strip()
                        }
                        
                        filtered_bang_diem = {}
                        for mon in bang_diem:
                            ma_mon = mon["ma_mon"]
                            diem_so = mon["diem_so"]

                            if (
                                ma_mon not in filtered_bang_diem or 
                                (diem_so is not None and diem_so > filtered_bang_diem[ma_mon]["diem_so"])
    ):
        
                                if diem_so in [None, 0.0]:
                                    mon["tin_chi"] = 0
                                filtered_bang_diem[ma_mon] = mon

                        bang_diem = list(filtered_bang_diem.values())
        
                        bang_diem.append(mon_hoc)
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Lỗi khi xử lý dòng dữ liệu: {e}")
                        continue
                    
            
            # Xử lý thông tin GPA
            footer_rows = table.find_elements(By.XPATH, ".//tr[td[@colspan='2']]")
            for footer_row in footer_rows:
                footer_tds = footer_row.find_elements(By.XPATH, ".//td[@colspan='2']")
                
            
                if len(footer_tds) >= 3:

                    try:
                        tin_chi = footer_tds[0].text.strip()
                        gpa_hk_el = footer_tds[1].find_element(By.TAG_NAME, "b")
                        gpa_hk = self._parse_float(gpa_hk_el.text.strip())
                        gpa_chung_el = footer_tds[2].find_element(By.TAG_NAME, "b")
                        gpa_chung = self._parse_float(gpa_chung_el.text.strip())

                        gpa = {
                            "tin_chi": tin_chi,
                            "gpa_hk": gpa_hk,
                            "gpa_chung": gpa_chung
                        }
                        total_gpa.append(gpa)
                    except ValueError as e:
                        logger.warning(f"Lỗi khi xử lý GPA: {e}")
                        continue
            
            return {
                "bang_diem": bang_diem,
                "total_gpa": total_gpa,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất dữ liệu: {e}")
            raise
    
    def _parse_float(self, value: str) -> float:
        """Parse float value an toàn"""
        try:
            return float(value.replace(',', '.'))
        except (ValueError, AttributeError):
            return 0.0
    
    def save_data(self, data: Dict[str, Any]):
        """Lưu dữ liệu vào file JSON"""
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Dữ liệu đã được lưu vào {self.output_file}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu dữ liệu: {e}")
            raise
    
    def setup_agent(self, data: Dict[str, Any]):
        """Thiết lập agent với cấu hình nâng cao"""
        try:
            # Tạo knowledge base
            self.knowledge_base = JSONKnowledgeBase(path=self.output_file)
            
            # Lấy thông tin GPA hiện tại
            current_gpa = data['total_gpa'][-1]['gpa_chung'] if data['total_gpa'] else 0.0
            total_credits = data['total_gpa'][-1]['tin_chi'] if data['total_gpa'] else 0.0
            
            # Tạo agent với cấu hình nâng cao
            self.agent = Agent(
                name="GPA Analysis Expert",
                role="Chuyên gia phân tích và tư vấn cải thiện GPA",
                model=Ollama(id="qwen3:8b"),
                tools=[ReasoningTools(add_instructions=True)],
                
                description=dedent("""
                Bạn là chuyên gia phân tích học tập và tư vấn cải thiện GPA hàng đầu.
                Bạn có khả năng:
                - Phân tích chính xác kết quả học tập từ dữ liệu thực tế
                - Đưa ra các đề xuất cải thiện GPA khoa học và thực tiễn
                - Tạo kế hoạch học tập chi tiết và khả thi
                - Đánh giá rủi ro và đưa ra lời khuyên phòng ngừa
                """),
                
                instructions=[
                    dedent(f"""
                    ĐỮ LIỆU CẦN PHÂN TÍCH:
                    - GPA hiện tại: {current_gpa:.2f}
                    - Tổng tín chỉ đã học: {total_credits}
                    - Tổng số môn học: {len(data['bang_diem'])}
                    
                    QUY TRÌNH PHÂN TÍCH BẮNG BUỘC:
                    1. SỬ DỤNG REASONING TOOLS để suy luận từng bước
                    2. CHỈ sử dụng dữ liệu có trong file ket_qua.json
                    3. KHÔNG tự tạo ra mã môn hoặc tên môn không tồn tại
                    4. Phân tích dựa trên điểm số thực tế từ trường "diem_so"
                    5. Ưu tiên các môn có điểm < 4.0 (Grade F) và < 6.0 (Grade D)
                    6. Những môn có tín chỉ là 0 sẽ BỎ QUA trong phân tích
                    7. Phải chỉ ra được tên môn học cần cải thiện
                    """),
                    
                    dedent("""
                    NGUYÊN TẮC PHÂN TÍCH:
                    1. Tính toán chính xác:
                       - Xác định các môn có điểm thấp nhất (< 5.0, < 6.0)
                       - Ưu tiên môn có tín chỉ cao và điểm thấp
                       - Tính toán khả năng cải thiện GPA thực tế
                    
                    2. Đề xuất thực tiễn:
                       - Chỉ đề xuất học lại những môn thật sự cần thiết
                       - Ưu tiên các môn dễ cải thiện điểm số
                       - Xem xét tỷ lệ chi phí/lợi ích của việc học lại
                    
                    3. Kế hoạch khả thi:
                       - Đưa ra timeline cụ thể
                       - Ước tính thời gian cần thiết cho mỗi môn
                       - Cân nhắc khả năng thực hiện của sinh viên
                    """),
                    
                    dedent("""
                    CÁCH TÍNH TOÁN GPA MỚI:
                    - Công thức: GPA = (Tổng (điểm_số(theo thang điểm 4) × tín_chỉ)) / Tổng_tín_chỉ
                    - Khi học lại: thay thế điểm cũ bằng điểm mới
                    - Ước tính điểm có thể đạt được dựa trên thực tế
                    
                    LƯU Ý QUAN TRỌNG:
                    - Nếu một môn xuất hiện nhiều lần, chỉ tính điểm cao nhất
                    - Không đề xuất học lại môn đã có điểm >= 7.0 trừ khi có lý do đặc biệt
                    - Xem xét khả năng tài chính và thời gian của sinh viên
                           
                    """)
                ],
                
                response_model=PhanTichKetQua,
                knowledge=self.knowledge_base,
                search_knowledge=True,
                reasoning=True,
                markdown=True,
                add_references=True,
                show_tool_calls=True,
                
                # Cấu hình memory và storage
                add_history_to_messages=True,
                num_history_responses=3,
                
                # Cấu hình output
                structured_outputs=True,
                debug_mode=True
            )
            
            logger.info("Agent đã được thiết lập thành công")
            
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập agent: {e}")
            raise
    
    def analyze_gpa(self, target_gpa: float = 3.6) -> PhanTichKetQua:
        """Phân tích GPA và đưa ra kế hoạch cải thiện"""
        try:
            query = dedent(f"""
            Hãy phân tích chi tiết kết quả học tập của tôi và đưa ra kế hoạch cải thiện để đạt GPA {target_gpa}.
            
            YÊU CẦU CỤ THỂ:
            1. Phân tích tình hình học tập hiện tại một cách khách quan
            2. Xác định chính xác các môn cần cải thiện (điểm < 6.0)
            3. Ưu tiên các môn có tác động lớn nhất đến GPA
            4. Đưa ra kế hoạch cải thiện thực tế và khả thi
            5. Tính toán cụ thể khả năng đạt được mục tiêu GPA {target_gpa}
            6. Đánh giá rủi ro và thời gian cần thiết
            
            Hãy sử dụng reasoning tools để suy luận từng bước và đưa ra phân tích chính xác nhất.
            """)
            
            response = self.agent.run(query)
            
            if hasattr(response, 'content') and response.content:
                return response.content
            else:
                logger.error("Không nhận được phản hồi từ agent")
                raise ValueError("Agent không trả về kết quả phân tích")
                
        except Exception as e:
            logger.error(f"Lỗi khi phân tích GPA: {e}")
            raise
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        if self.driver:
            self.driver.quit()
            logger.info("Webdriver đã được đóng")

def main():
    """Hàm chính"""
    root = tk.Tk()
    app = SimpleTrainingProgramGUI(root)
   
    root.mainloop()
    
    analyzer = GpaAnalyzer()
    
    try:
        # Lấy username, password từ GUI
        if not hasattr(app, "data") or not app.data:
            raise ValueError("Không có dữ liệu từ GUI.")

        user_info = app.data.get("user_info", {})
        username = user_info.get("username", "").strip()
        password = user_info.get("password", "").strip()

        if not username or not password:
            raise ValueError("Thiếu tài khoản hoặc mật khẩu từ GUI.")
        # Nhập mục tiêu GPA
        try:
            target_gpa = float(input("Nhập mục tiêu GPA (mặc định 3.6): ").strip() or "3.6")
            if not 0 <= target_gpa <= 4.0:
                raise ValueError("GPA phải nằm trong khoảng 0-4.0")
        except ValueError as e:
            print(f"Lỗi: {e}")
            target_gpa = 3.6
        
        # Thiết lập và chạy scraper
        print("Đang thiết lập webdriver...")
        analyzer.setup_driver()
        
        print("Đang đăng nhập và thu thập dữ liệu...")
        data = analyzer.login_and_scrape(username, password)
        
        print("Đang lưu dữ liệu...")
        analyzer.save_data(data)
        
        print("Đang thiết lập AI agent...")
        analyzer.setup_agent(data)
        
        print("Đang phân tích GPA và tạo kế hoạch cải thiện...")
        result = analyzer.analyze_gpa(target_gpa)
        
        print("\n" + "="*50)
        print("KẾT QUẢ PHÂN TÍCH GPA")
        print("="*50)
        
        if isinstance(result, PhanTichKetQua):
            print(f"GPA hiện tại: {result.gpa_hien_tai:.2f}")
            print(f"Tổng tín chỉ đã học: {result.tong_tin_chi_da_hoc}")
            print(f"Mục tiêu GPA: {target_gpa:.2f}")
            print(f"\nNhận xét: {result.nhan_xet_tong_quan}")
            print(f"\nDự báo: {result.du_bao_ket_qua}")
        else:
            print("Phân tích đã hoàn thành. Vui lòng kiểm tra kết quả.")
        
    except KeyboardInterrupt:
        print("\nChương trình đã bị dừng bởi người dùng")
    except Exception as e:
        logger.error(f"Lỗi trong quá trình thực hiện: {e}")
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        analyzer.cleanup()

if __name__ == "__main__":
    main()