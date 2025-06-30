from agno.agent import Agent
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(id="qwen3:8b"),
    markdown=True
)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story.")
# Create a knowledge base for the Agent
knowledge_base = AgentKnowledge(values)

# Add information to the knowledge base
knowledge_base.load_text("đây là bảng điểm ")


# Add the knowledge base to the Agent and
# give it a tool to search the knowledge base as needed
agent = Agent(knowledge=knowledge_base, search_knowledge=True)

# Print the response in the terminal
agent.print_response("hãy đưa ra lời khuyên cho việc cái thiện để gpa lên 3.0")


bangdiem = driver.find_element(By.CLASS_NAME, "col-md-12")  
td_elements = bangdiem.find_element(By.ID, "lsKetQuaHocTap") 
for td in td_elements:
    print(td.text)   
values = [td.text for td in td_elements]




if len(footer_tds) >= 3:
        gpa = {
            "tc_text" : footer_tds[0].text.strip(),     # "Số tín chỉ đạt/đăng ký học kỳ: 11/15 - Số TCTL chung: 17"
    "dtbhk_text" : footer_tds[1].text.strip(),  # "ĐTBHK: 2.1"
    "dtbtl_text" : footer_tds[2].text.strip()
        }