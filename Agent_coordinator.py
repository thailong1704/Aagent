"""
Coordinator Agent for integrating PDF training program analysis with GPA analysis
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from textwrap import dedent

# AI Agent libraries
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.knowledge.json import JSONKnowledgeBase
from agno.tools.reasoning import ReasoningTools

# Local imports
from models.training_program import TrainingProgram, Course, CourseType, GraduationAnalysis
from Agent_pdf_reader import PdfTrainingProgramReader

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GpaCoordinatorAgent:
    """
    Coordinator agent that integrates training program analysis with GPA data
    to provide comprehensive academic planning and recommendations
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.agent = None
        self.knowledge_base = None
        self.training_program = None
        self.gpa_data = None
        
    def load_training_program(self, pdf_path: Optional[str] = None, 
                            program_data: Optional[TrainingProgram] = None) -> TrainingProgram:
        """
        Load training program either from PDF or existing data
        """
        try:
            if program_data:
                self.training_program = program_data
                logger.info("Training program loaded from provided data")
            elif pdf_path:
                reader = PdfTrainingProgramReader(output_dir=str(self.output_dir))
                self.training_program = reader.analyze_training_program(pdf_path)
                logger.info(f"Training program loaded from PDF: {pdf_path}")
            else:
                # Try to load from existing file
                program_file = self.output_dir / "training_program.json"
                if program_file.exists():
                    with open(program_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.training_program = TrainingProgram(**data)
                    logger.info("Training program loaded from existing file")
                else:
                    raise ValueError("No training program data provided or found")
            
            return self.training_program
            
        except Exception as e:
            logger.error(f"Error loading training program: {e}")
            raise
    
    def load_gpa_data(self, gpa_file: str = "ket_qua.json") -> Dict[str, Any]:
        """
        Load GPA and grade data from existing file
        """
        try:
            if not Path(gpa_file).exists():
                raise FileNotFoundError(f"GPA data file not found: {gpa_file}")
            
            with open(gpa_file, 'r', encoding='utf-8') as f:
                self.gpa_data = json.load(f)
            
            logger.info(f"GPA data loaded from {gpa_file}")
            return self.gpa_data
            
        except Exception as e:
            logger.error(f"Error loading GPA data: {e}")
            raise
    
    def analyze_graduation_requirements(self) -> GraduationAnalysis:
        """
        Analyze graduation requirements based on training program and completed courses
        """
        try:
            if not self.training_program or not self.gpa_data:
                raise ValueError("Training program and GPA data must be loaded first")
            
            # Extract completed courses from GPA data
            completed_courses = []
            total_completed_credits = 0
            
            for grade_record in self.gpa_data.get('bang_diem', []):
                if grade_record.get('tin_chi', 0) > 0 and grade_record.get('diem_so', 0) > 0:
                    completed_courses.append(grade_record['ma_mon'])
                    total_completed_credits += grade_record['tin_chi']
            
            # Find remaining courses
            remaining_courses = []
            for course in self.training_program.cac_mon_hoc:
                if course.ma_mon not in completed_courses:
                    remaining_courses.append(course)
            
            remaining_credits = sum(course.tin_chi for course in remaining_courses)
            completion_rate = (total_completed_credits / self.training_program.tong_tin_chi) * 100
            
            # Estimate graduation timeline
            current_gpa = self.gpa_data.get('total_gpa', [])[-1].get('gpa_chung', 0) if self.gpa_data.get('total_gpa') else 0
            estimated_graduation = self._estimate_graduation_time(remaining_credits, current_gpa)
            
            analysis = GraduationAnalysis(
                chuong_trinh_dao_tao=self.training_program,
                mon_da_hoc=completed_courses,
                mon_con_lai=remaining_courses,
                tin_chi_da_hoan_thanh=total_completed_credits,
                tin_chi_con_lai=remaining_credits,
                ty_le_hoan_thanh=completion_rate,
                du_kien_tot_nghiep=estimated_graduation
            )
            
            # Save analysis results
            analysis_file = self.output_dir / "graduation_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis.dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Graduation analysis completed. Results saved to {analysis_file}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing graduation requirements: {e}")
            raise
    
    def _estimate_graduation_time(self, remaining_credits: int, current_gpa: float) -> str:
        """
        Estimate graduation timeline based on remaining credits and current performance
        """
        # Simple estimation logic - can be enhanced
        avg_credits_per_semester = 18  # Typical course load
        
        if remaining_credits <= 0:
            return "Đã đủ điều kiện tốt nghiệp"
        
        semesters_needed = (remaining_credits + avg_credits_per_semester - 1) // avg_credits_per_semester
        
        if current_gpa < 2.0:
            semesters_needed += 1  # Additional time for improvement
            return f"Khoảng {semesters_needed} học kỳ (cần cải thiện GPA)"
        elif current_gpa < 2.5:
            return f"Khoảng {semesters_needed} học kỳ"
        else:
            return f"Khoảng {max(1, semesters_needed)} học kỳ"
    
    def setup_coordinator_agent(self, analysis: GraduationAnalysis):
        """
        Setup AI agent for comprehensive academic planning
        """
        try:
            # Create comprehensive knowledge base
            kb_data = {
                "training_program": self.training_program.dict(),
                "gpa_data": self.gpa_data,
                "graduation_analysis": analysis.dict(),
                "course_mapping": self._create_course_mapping()
            }
            
            kb_file = self.output_dir / "comprehensive_knowledge_base.json"
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(kb_data, f, ensure_ascii=False, indent=2)
            
            self.knowledge_base = JSONKnowledgeBase(path=str(kb_file))
            
            # Create coordinator agent
            self.agent = Agent(
                name="Academic Planning Coordinator",
                role="Chuyên gia tư vấn kế hoạch học tập và tốt nghiệp",
                model=Ollama(id="qwen3:8b"),
                tools=[ReasoningTools(add_instructions=True)],
                
                description=dedent("""
                Bạn là chuyên gia tư vấn học tập với khả năng tích hợp phân tích:
                - Chương trình đào tạo chi tiết từ PDF
                - Kết quả học tập hiện tại (GPA, điểm số)
                - Yêu cầu tốt nghiệp và tiến độ hoàn thành
                - Lộ trình học tập tối ưu
                - Khuyến nghị cải thiện điểm số và GPA
                """),
                
                instructions=[
                    dedent(f"""
                    DỮ LIỆU TÍCH HỢP:
                    - Chương trình đào tạo: {self.training_program.ten_chuong_trinh}
                    - Tổng tín chỉ yêu cầu: {self.training_program.tong_tin_chi}
                    - Tín chỉ đã hoàn thành: {analysis.tin_chi_da_hoan_thanh}
                    - Tín chỉ còn lại: {analysis.tin_chi_con_lai}
                    - Tỷ lệ hoàn thành: {analysis.ty_le_hoan_thanh:.1f}%
                    - GPA hiện tại: {self.gpa_data.get('total_gpa', [])[-1].get('gpa_chung', 0) if self.gpa_data.get('total_gpa') else 0:.2f}
                    """),
                    
                    dedent("""
                    QUY TRÌNH PHÂN TÍCH TÍCH HỢP:
                    1. Đánh giá tiến độ theo chương trình đào tạo
                    2. Phân tích các môn cần ưu tiên (bắt buộc vs tự chọn)
                    3. Xem xét các môn tiên quyết và chuỗi môn học
                    4. Đề xuất lộ trình học tập theo học kỳ
                    5. Tính toán tác động của việc cải thiện điểm số
                    6. Đưa ra kế hoạch tổng thể để đạt mục tiêu
                    """),
                    
                    dedent("""
                    KHUYẾN NGHỊ THÔNG MINH:
                    1. Ưu tiên môn học theo tác động:
                       - Môn bắt buộc chưa đạt
                       - Môn có tín chỉ cao và điểm thấp
                       - Môn tiên quyết cho các môn khác
                    
                    2. Lộ trình tối ưu:
                       - Cân bằng tải học tập mỗi học kỳ
                       - Tận dụng cơ hội cải thiện GPA
                       - Đảm bảo đủ điều kiện tốt nghiệp
                    
                    3. Tính toán chi phí - lợi ích:
                       - Thời gian và chi phí học lại
                       - Tác động đến GPA tổng
                       - Khả năng thực hiện thực tế
                    """)
                ],
                
                knowledge=self.knowledge_base,
                search_knowledge=True,
                reasoning=True,
                markdown=True,
                structured_outputs=True,
                debug_mode=True
            )
            
            logger.info("Coordinator agent setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up coordinator agent: {e}")
            raise
    
    def _create_course_mapping(self) -> Dict[str, Any]:
        """
        Create mapping between completed courses and program requirements
        """
        mapping = {
            "completed": {},
            "remaining_by_type": {},
            "prerequisites_analysis": {}
        }
        
        # Map completed courses
        for grade_record in self.gpa_data.get('bang_diem', []):
            ma_mon = grade_record.get('ma_mon')
            if ma_mon and grade_record.get('tin_chi', 0) > 0:
                program_course = self.training_program.get_course_by_code(ma_mon)
                mapping["completed"][ma_mon] = {
                    "grade_info": grade_record,
                    "program_info": program_course.dict() if program_course else None
                }
        
        # Analyze remaining courses by type
        for course_type in CourseType:
            remaining = [
                course for course in self.training_program.get_courses_by_type(course_type)
                if course.ma_mon not in mapping["completed"]
            ]
            mapping["remaining_by_type"][course_type.value] = [c.dict() for c in remaining]
        
        return mapping
    
    def generate_comprehensive_plan(self, target_gpa: float = 3.6, 
                                  remaining_semesters: int = 4) -> Dict[str, Any]:
        """
        Generate comprehensive academic plan integrating all available data
        """
        try:
            if not self.agent:
                raise ValueError("Coordinator agent not setup. Call setup_coordinator_agent first.")
            
            query = dedent(f"""
            Hãy tạo kế hoạch học tập tổng hợp dựa trên tất cả dữ liệu có sẵn.
            
            MỤC TIÊU:
            - GPA mục tiêu: {target_gpa}
            - Số học kỳ còn lại: {remaining_semesters}
            - Tốt nghiệp đúng hạn theo chương trình
            
            YÊU CẦU PHÂN TÍCH:
            1. ĐÁNH GIÁ HIỆN TRẠNG:
               - Tiến độ theo chương trình đào tạo
               - Phân tích các môn đã học vs chưa học
               - Đánh giá GPA và điểm số hiện tại
            
            2. XÁC ĐỊNH ƯU TIÊN:
               - Môn bắt buộc chưa hoàn thành
               - Môn cần cải thiện điểm (điểm thấp, tín chỉ cao)
               - Môn tiên quyết cho chuỗi môn học
               - Môn tự chọn phù hợp
            
            3. LỘ TRÌNH CHI TIẾT:
               - Phân bổ môn học theo từng học kỳ
               - Cân bằng tải học tập (15-18 tín chỉ/kỳ)
               - Thời điểm tối ưu để học lại môn cần cải thiện
            
            4. DỰ BÁO KẾT QUẢ:
               - Khả năng đạt GPA mục tiêu
               - Thời gian dự kiến tốt nghiệp
               - Rủi ro và phương án dự phòng
            
            5. KHUYẾN NGHỊ HÀNH ĐỘNG:
               - Các bước thực hiện cụ thể
               - Tài nguyên hỗ trợ cần thiết
               - Timeline thực hiện
            
            Sử dụng reasoning tools để đảm bảo phân tích logic và toàn diện.
            """)
            
            # Get comprehensive analysis
            response = self.agent.run(query)
            
            if not hasattr(response, 'content') or not response.content:
                raise ValueError("No response from coordinator agent")
            
            # Structure the response
            plan = {
                "analysis_timestamp": str(Path().resolve()),
                "target_gpa": target_gpa,
                "remaining_semesters": remaining_semesters,
                "agent_analysis": response.content,
                "raw_data": {
                    "training_program_summary": {
                        "name": self.training_program.ten_chuong_trinh,
                        "total_credits": self.training_program.tong_tin_chi,
                        "remaining_credits": sum(
                            course.tin_chi for course in self.training_program.cac_mon_hoc
                            if course.ma_mon not in [
                                grade['ma_mon'] for grade in self.gpa_data.get('bang_diem', [])
                                if grade.get('tin_chi', 0) > 0
                            ]
                        )
                    },
                    "current_status": {
                        "gpa": self.gpa_data.get('total_gpa', [])[-1].get('gpa_chung', 0) if self.gpa_data.get('total_gpa') else 0,
                        "completed_credits": sum(
                            grade['tin_chi'] for grade in self.gpa_data.get('bang_diem', [])
                            if grade.get('tin_chi', 0) > 0 and grade.get('diem_so', 0) > 0
                        )
                    }
                }
            }
            
            # Save comprehensive plan
            plan_file = self.output_dir / "comprehensive_academic_plan.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Comprehensive academic plan generated. Saved to {plan_file}")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating comprehensive plan: {e}")
            raise

def main():
    """Test function for coordinator agent"""
    coordinator = GpaCoordinatorAgent()
    
    try:
        # Example usage
        print("Coordinator Agent initialized successfully")
        
        # In actual usage:
        # coordinator.load_gpa_data("ket_qua.json")
        # coordinator.load_training_program(pdf_path="data/training_program.pdf")
        # analysis = coordinator.analyze_graduation_requirements()
        # coordinator.setup_coordinator_agent(analysis)
        # plan = coordinator.generate_comprehensive_plan(target_gpa=3.6)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()