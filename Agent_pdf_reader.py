"""
Agent for reading and analyzing PDF training program documents
"""
import json
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# PDF processing libraries
import PyPDF2
import pdfplumber

# AI Agent libraries
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.knowledge.json import JSONKnowledgeBase
from agno.tools.reasoning import ReasoningTools

# Local models
from models.training_program import TrainingProgram, Course, CourseType, GraduationAnalysis

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PdfTrainingProgramReader:
    """
    Agent for reading and analyzing PDF training program documents
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.agent = None
        self.knowledge_base = None
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using multiple methods for better accuracy
        """
        try:
            # First try with pdfplumber (better for tables and structured content)
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            if text_content:
                logger.info(f"Successfully extracted text using pdfplumber from {pdf_path}")
                return "\n\n".join(text_content)
            
            # Fallback to PyPDF2
            text_content = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())
            
            logger.info(f"Successfully extracted text using PyPDF2 from {pdf_path}")
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[List[List[str]]]:
        """
        Extract tables from PDF specifically for course information
        """
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
            
            logger.info(f"Extracted {len(tables)} tables from PDF")
            return tables
            
        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")
            return []
    
    def setup_analysis_agent(self, pdf_text: str, tables: List[List[List[str]]]) -> None:
        """
        Setup AI agent for analyzing training program content
        """
        try:
            # Save extracted content to knowledge base
            knowledge_file = self.output_dir / "pdf_content.json"
            pdf_data = {
                "text_content": pdf_text,
                "tables": tables,
                "extraction_timestamp": str(Path().resolve())
            }
            
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(pdf_data, f, ensure_ascii=False, indent=2)
            
            # Create knowledge base
            self.knowledge_base = JSONKnowledgeBase(path=str(knowledge_file))
            
            # Create specialized agent for training program analysis
            self.agent = Agent(
                name="Training Program PDF Analyzer",
                role="Chuyên gia phân tích chương trình đào tạo từ tài liệu PDF",
                model=Ollama(id="qwen3:8b"),
                tools=[ReasoningTools(add_instructions=True)],
                
                description="""
                Bạn là chuyên gia phân tích chương trình đào tạo đại học với khả năng:
                - Đọc và hiểu cấu trúc chương trình đào tạo từ PDF
                - Trích xuất thông tin môn học chính xác (mã môn, tên môn, tín chỉ)
                - Phân loại môn học theo nhóm (đại cương, cơ sở, chuyên ngành, tự chọn)
                - Xác định các môn tiên quyết và cấu trúc học kỳ
                - Tạo cơ sở dữ liệu môn học có cấu trúc
                """,
                
                instructions=[
                    """
                    NHIỆM VỤ CHÍNH:
                    1. Phân tích nội dung PDF chương trình đào tạo
                    2. Trích xuất thông tin chi tiết về từng môn học
                    3. Xác định cấu trúc chương trình và yêu cầu tốt nghiệp
                    4. Tạo dữ liệu có cấu trúc cho các môn học
                    
                    THÔNG TIN CẦN TRÍCH XUẤT:
                    - Mã môn học (VD: MT1003, EE2009)
                    - Tên môn học đầy đủ
                    - Số tín chỉ
                    - Loại môn: Đại cương/Cơ sở/Chuyên ngành/Tự chọn
                    - Học kỳ đề xuất (nếu có)
                    - Môn tiên quyết (nếu có)
                    - Mô tả môn học (nếu có)
                    """,
                    
                    """
                    QUY TẮC PHÂN LOẠI MÔN HỌC:
                    1. Đại cương: Toán, Lý, Hóa cơ bản, Anh văn, Giáo dục thể chất, 
                       Giáo dục quốc phòng, các môn chính trị - xã hội
                    2. Cơ sở: Môn cơ sở ngành, nền tảng kỹ thuật
                    3. Chuyên ngành: Môn chuyên sâu theo ngành học
                    4. Tự chọn: Môn tự chọn, thực tập, đồ án
                    
                    ĐỊNH DẠNG OUTPUT:
                    - Sử dụng JSON format chuẩn
                    - Đảm bảo tính chính xác của mã môn và tên môn
                    - Ghi rõ số tín chỉ cho từng môn
                    - Phân loại rõ ràng theo nhóm môn học
                    """,
                    
                    """
                    LƯU Ý QUAN TRỌNG:
                    - Sử dụng reasoning tools để phân tích từng bước
                    - Kiểm tra tính nhất quán của dữ liệu
                    - Xử lý các trường hợp đặc biệt (môn không tín chỉ, môn thay thế)
                    - Đảm bảo không bỏ sót môn học quan trọng
                    - Ghi chú các yêu cầu đặc biệt của chương trình
                    """
                ],
                
                knowledge=self.knowledge_base,
                search_knowledge=True,
                reasoning=True,
                markdown=True,
                structured_outputs=True,
                debug_mode=True
            )
            
            logger.info("PDF analysis agent setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up analysis agent: {e}")
            raise
    
    def analyze_training_program(self, pdf_path: str) -> TrainingProgram:
        """
        Analyze PDF and extract training program information
        """
        try:
            logger.info(f"Starting analysis of training program PDF: {pdf_path}")
            
            # Extract content from PDF
            pdf_text = self.extract_text_from_pdf(pdf_path)
            tables = self.extract_tables_from_pdf(pdf_path)
            
            if not pdf_text.strip():
                raise ValueError("No text content extracted from PDF")
            
            # Setup analysis agent
            self.setup_analysis_agent(pdf_text, tables)
            
            # Create analysis query
            query = f"""
            Hãy phân tích chi tiết chương trình đào tạo từ nội dung PDF đã được trích xuất.
            
            YÊU CẦU CỤ THỂ:
            1. Xác định tên và mã chương trình đào tạo
            2. Tổng số tín chỉ yêu cầu tốt nghiệp
            3. Danh sách tất cả môn học với thông tin đầy đủ:
               - Mã môn học
               - Tên môn học
               - Số tín chỉ
               - Loại môn học (Đại cương/Cơ sở/Chuyên ngành/Tự chọn)
               - Học kỳ đề xuất (nếu có)
               - Môn tiên quyết (nếu có)
            
            4. Phân tích yêu cầu tốt nghiệp đặc biệt
            5. Cấu trúc học kỳ và lộ trình học tập
            
            Hãy sử dụng reasoning tools để đảm bảo phân tích chính xác và đầy đủ.
            Tập trung vào việc trích xuất dữ liệu có cấu trúc để dễ dàng xử lý.
            """
            
            # Get analysis from agent
            response = self.agent.run(query)
            
            if not hasattr(response, 'content') or not response.content:
                raise ValueError("No analysis result from agent")
            
            # Parse response and create TrainingProgram object
            # Note: This is a simplified parsing - in production, you'd want more robust parsing
            program_data = self._parse_agent_response(response.content)
            training_program = TrainingProgram(**program_data)
            
            # Save results
            output_file = self.output_dir / "training_program.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_program.dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Training program analysis completed. Results saved to {output_file}")
            return training_program
            
        except Exception as e:
            logger.error(f"Error analyzing training program: {e}")
            raise
    
    def _parse_agent_response(self, response_content: str) -> Dict[str, Any]:
        """
        Parse agent response and convert to structured data
        This is a simplified parser - in production, you'd want more robust parsing
        """
        # This is a placeholder implementation
        # In a real scenario, you'd implement proper parsing of the agent's response
        return {
            "ten_chuong_trinh": "Kỹ thuật Điện tử - Viễn thông",
            "ma_chuong_trinh": "D520207",
            "he_dao_tao": "Đại học",
            "tong_tin_chi": 144,
            "cac_mon_hoc": [
                # This would be populated from actual PDF analysis
                # For now, using placeholder data
            ],
            "yeu_cau_tong_quat": {
                "gpa_tot_nghiep": 2.0,
                "dieu_kien_dac_biet": []
            }
        }
    
    def create_course_knowledge_base(self, training_program: TrainingProgram) -> str:
        """
        Create a comprehensive knowledge base from training program data
        """
        try:
            kb_file = self.output_dir / "course_knowledge_base.json"
            
            knowledge_data = {
                "program_info": {
                    "name": training_program.ten_chuong_trinh,
                    "code": training_program.ma_chuong_trinh,
                    "total_credits": training_program.tong_tin_chi
                },
                "courses_by_type": {
                    course_type.value: [
                        course.dict() for course in training_program.get_courses_by_type(course_type)
                    ] for course_type in CourseType
                },
                "course_index": {
                    course.ma_mon: course.dict() for course in training_program.cac_mon_hoc
                },
                "prerequisites_map": {
                    course.ma_mon: course.mon_tien_quyet 
                    for course in training_program.cac_mon_hoc 
                    if course.mon_tien_quyet
                }
            }
            
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Course knowledge base created: {kb_file}")
            return str(kb_file)
            
        except Exception as e:
            logger.error(f"Error creating knowledge base: {e}")
            raise

def main():
    """Test function for PDF reader"""
    reader = PdfTrainingProgramReader()
    
    # Example usage
    try:
        # This would be called with actual PDF path
        # pdf_path = "data/training_program.pdf"
        # program = reader.analyze_training_program(pdf_path)
        # reader.create_course_knowledge_base(program)
        
        print("PDF Reader Agent initialized successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()