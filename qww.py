from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from agno.agent import Agent
import json
from agno.models.ollama import Ollama
from agno.agent import Agent, AgentKnowledge
from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List, Optional
from agno.document import Document
from agno.knowledge.json import JSONKnowledgeBase

class MonCanCaiThien(BaseModel):
    ma_mon: str = Field(..., description="Mã số của môn học cần cải thiện.")
    ten_mon: str = Field(..., description="Tên môn học cần cải thiện.")
    diem_so: float = Field(..., description="Điểm số hiện tại của môn học theo dạng thang điểm GPA.")
    tin_chi: int = Field(..., description="Số tín chỉ của môn học.")
    ly_do: str = Field(..., description="Lý do tại sao môn này cần cải thiện (ví dụ: điểm thấp, ảnh hưởng GPA, đã rớt, ...).")


class HocPhanUuTien(BaseModel):
    ma_mon: str = Field(..., description="Mã số của học phần nên được ưu tiên học.")
    ten_mon: str = Field(..., description="Tên của học phần nên được ưu tiên học.")
    tin_chi: int = Field(..., description="Số tín chỉ của học phần.")
    uu_tien_vi: str = Field(..., description="Lý do nên ưu tiên học học phần này (ví dụ: tín chỉ cao, điểm dễ cải thiện, bắt buộc tốt nghiệp, ...).")

class KeHoachHocTap(BaseModel):
    thoi_gian: str = Field(..., description="Khoảng thời gian dự kiến để thực hiện kế hoạch học tập (ví dụ: '6 tháng', '2 học kỳ').")
    chien_luoc: str = Field(..., description="Chiến lược cụ thể để cải thiện GPA (ví dụ: học nhóm, học lại, học với tutor, tăng thời gian tự học, ...).")

class PhanTichKetQua(BaseModel):
    nhan_xet: str = Field(..., description="Nhận xét tổng quan về kết quả học tập hiện tại của sinh viên.")
    mon_can_cai_thien: List[MonCanCaiThien] = Field(..., description="Danh sách các môn học có điểm thấp hoặc chưa đạt cần được cải thiện.")
    hoc_phan_uu_tien: List[HocPhanUuTien] = Field(..., description="Danh sách các học phần nên ưu tiên học để nâng cao GPA.")
    ke_hoach: KeHoachHocTap = Field(..., description="Kế hoạch học tập cụ thể để cải thiện GPA trong thời gian tới.")






taikhoan = input(" nhap tai khoan: ")
matkhau = input("nhap mat khau: ")

driver = webdriver.Edge()
driver.get("https://sso.hcmut.edu.vn/cas/login?service=https%3A%2F%2Fmybk.hcmut.edu.vn%2Fapp%2Flogin%2Fcas")

username = driver.find_element(By.NAME, "username")
username.send_keys(taikhoan)

password = driver.find_element(By.NAME, "password")
password.send_keys(matkhau)

login = driver.find_element(By.NAME, 'submit')
login.click()

driver.get("https://mybk.hcmut.edu.vn/app/sinh-vien/ket-qua-hoc-tap/bang-diem-hoc-ky")
time.sleep(5)

table = driver.find_element(By.ID, "lsKetQuaHocTap")

rows = table.find_elements(By.XPATH, ".//tbody/tr")


bang_diem = []
total_gpa =[]

for row in rows:
    
    cols = row.find_elements(By.TAG_NAME, "td")
    if len(cols) >= 8: 
        mon_hoc = {
            "ma_mon": cols[0].text.strip(),
            "ten_mon": cols[1].text.strip(),
            "tin_chi": cols[2].text.strip(),
            "diem_tp": cols[3].text.strip(),
            "diem_so": cols[4].text.strip(),
            "diem_chu": cols[5].text.strip(),
            "diem_dat": cols[6].text.strip(),
            "cap_nhat": cols[7].text.strip()
        } 
        bang_diem.append(mon_hoc)
footer_rows = table.find_elements(By.XPATH, ".//tr[td[@colspan='2']]")
for footer_row in footer_rows:
 
    footer_tds = footer_row.find_elements(By.XPATH, ".//td[@colspan='2']")
    if len(footer_tds) >= 3:
        gpa = {
            "tin_chi": footer_tds[0].text.strip(),     
            "gpa_hk": footer_tds[1].text.strip(),  
            "gpa_chung": footer_tds[2].text.strip()
        }
        total_gpa.append(gpa)

ket_qua = {

     "bang_diem": bang_diem,
    "total_gpa": total_gpa
}

with open("ket_qua.json", "w", encoding="utf-8") as f:
     json.dump(ket_qua, f, ensure_ascii=False, indent=2)



knowledge_base = JSONKnowledgeBase(path="ket_qua.json")

with open("ket_qua.json", "r", encoding="utf-8") as f:
    data = json.load(f)

driver.quit()

agent = Agent(
    model=Ollama(id="qwen3:8b"),
    description=dedent("""Bạn là một cố vấn học tập giúp sinh viên phân tích kết quả học tập và đưa ra kế hoạch cải thiện GPA.
                          Hãy phân tích từ file ket_qua.json từ đó đưa ra cac môn cần cải thiện, ưu tiên học phần và kế hoạch học tập cụ thể."""),
    instructions=[dedent(f"""
    Bạn được cung cấp dữ liệu bảng điểm thực tế của sinh viên từ file JSON.
    
    QUAN TRỌNG: 
    - CHỈ sử dụng dữ liệu có trong file ket_qua.json
    - KHÔNG tự tạo ra mã môn hoặc tên môn không có trong dữ liệu
    - Phân tích dựa trên điểm số thực tế từ trường "diem_so"
    - GPA hiện tại: {data['total_gpa'][-1]['gpa_chung'] if data['total_gpa'] else 'N/A'}
    
    Nhiệm vụ:
    1. Phân tích các môn có điểm thấp (< 6.0 hoặc điểm chữ D, F)
    2. Ưu tiên các môn có tín chỉ cao và điểm thấp
    3. Đưa ra kế hoạch cụ thể để đạt GPA cao
    4. Chỉ đề xuất học lại các môn thực sự cần thiết
    
    Lưu ý: Nếu một môn đã học lại và cải thiện điểm (có nhiều lần xuất hiện), chỉ tính điểm cao nhất.
    """)],
    response_model=PhanTichKetQua,
    knowledge=knowledge_base,
   
    search_knowledge=True,  
    markdown=True,
    add_references=True
    
)

agent.print_response(
    "hãy giúp tôi cách cải thiện lên GPA 3.6 " 
   
)
