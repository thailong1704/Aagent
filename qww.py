from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from agno.agent import Agent
import json
from agno.models.ollama import Ollama
from agno.agent import Agent, AgentKnowledge
from pydantic import BaseModel



class AgentKnowledge(BaseModel):
    bang_diem: list[dict]
    total_gpa: list[dict]
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
    if len(cols) >= 8:  # Bạn có thể điều chỉnh nếu bảng có nhiều hơn 7 cột
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
print(json.dumps(ket_qua, indent=2, ensure_ascii=False))

knowledge_base = AgentKnowledge(bang_diem=bang_diem, total_gpa=total_gpa)
agent = Agent(
    model=Ollama(id="qwen3:8b"),
    knowledge=knowledge_base,
    search_knowledge=True,
    markdown=True
)

# ✅ Yêu cầu AI đưa ra lời khuyên
agent.print_response("Dựa trên bảng điểm và GPA tổng hợp của tôi trong kiến thức đã cung cấp, hãy phân tích và đưa ra lời khuyên giúp tôi nâng GPA lên 3.0.")













