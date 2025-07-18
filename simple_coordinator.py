"""
Simplified coordinator for testing without external AI libraries
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Local imports
from models.training_program import TrainingProgram, Course, CourseType, GraduationAnalysis
from data.sample_program import SAMPLE_TRAINING_PROGRAM

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCoordinator:
    """
    Simplified coordinator for basic testing without AI agents
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.training_program = None
        self.gpa_data = None
        
    def load_sample_training_program(self) -> TrainingProgram:
        """Load sample training program for testing"""
        try:
            self.training_program = TrainingProgram(**SAMPLE_TRAINING_PROGRAM)
            logger.info("Sample training program loaded successfully")
            return self.training_program
        except Exception as e:
            logger.error(f"Error loading sample training program: {e}")
            raise
    
    def load_gpa_data(self, gpa_file: str = "ket_qua.json") -> Dict[str, Any]:
        """Load GPA data from file"""
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
        """Analyze graduation requirements"""
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
            
            # Simple graduation estimate
            avg_credits_per_semester = 18
            semesters_needed = max(1, (remaining_credits + avg_credits_per_semester - 1) // avg_credits_per_semester)
            estimated_graduation = f"Khoảng {semesters_needed} học kỳ"
            
            analysis = GraduationAnalysis(
                chuong_trinh_dao_tao=self.training_program,
                mon_da_hoc=completed_courses,
                mon_con_lai=remaining_courses,
                tin_chi_da_hoan_thanh=total_completed_credits,
                tin_chi_con_lai=remaining_credits,
                ty_le_hoan_thanh=completion_rate,
                du_kien_tot_nghiep=estimated_graduation
            )
            
            # Save analysis
            analysis_file = self.output_dir / "simple_graduation_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis.model_dump(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Graduation analysis completed. Saved to {analysis_file}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing graduation requirements: {e}")
            raise
    
    def generate_simple_recommendation(self, analysis: GraduationAnalysis, 
                                     target_gpa: float = 3.6) -> Dict[str, Any]:
        """Generate simple recommendations without AI"""
        try:
            current_gpa = self.gpa_data.get('total_gpa', [])[-1].get('gpa_chung', 0) if self.gpa_data.get('total_gpa') else 0
            
            # Find courses that need improvement (low grades with high credits)
            improvement_candidates = []
            for grade_record in self.gpa_data.get('bang_diem', []):
                if (grade_record.get('tin_chi', 0) > 0 and 
                    grade_record.get('diem_so', 0) < 6.0 and
                    grade_record.get('diem_so', 0) > 0):
                    improvement_candidates.append({
                        "ma_mon": grade_record['ma_mon'],
                        "ten_mon": grade_record['ten_mon'],
                        "diem_so": grade_record['diem_so'],
                        "tin_chi": grade_record['tin_chi'],
                        "priority": grade_record['tin_chi'] * (6.0 - grade_record['diem_so'])
                    })
            
            # Sort by priority (impact on GPA)
            improvement_candidates.sort(key=lambda x: x['priority'], reverse=True)
            
            # Categorize remaining courses
            remaining_by_type = {}
            for course_type in CourseType:
                remaining_courses = [
                    course for course in analysis.mon_con_lai 
                    if course.loai_mon == course_type
                ]
                remaining_by_type[course_type.value] = len(remaining_courses)
            
            recommendation = {
                "current_status": {
                    "gpa": current_gpa,
                    "completed_credits": analysis.tin_chi_da_hoan_thanh,
                    "remaining_credits": analysis.tin_chi_con_lai,
                    "completion_rate": analysis.ty_le_hoan_thanh
                },
                "target_gpa": target_gpa,
                "gpa_gap": target_gpa - current_gpa,
                "improvement_recommendations": {
                    "courses_to_retake": improvement_candidates[:5],  # Top 5 priorities
                    "estimated_impact": "Cải thiện 5 môn điểm thấp nhất có thể tăng GPA lên khoảng 0.3-0.5 điểm"
                },
                "remaining_courses_summary": remaining_by_type,
                "graduation_timeline": analysis.du_kien_tot_nghiep,
                "key_recommendations": [
                    "Ưu tiên học lại các môn có điểm thấp và tín chỉ cao",
                    "Hoàn thành các môn bắt buộc theo đúng thứ tự tiên quyết",
                    "Tập trung vào các môn chuyên ngành trong những học kỳ cuối",
                    f"Cần cải thiện GPA thêm {target_gpa - current_gpa:.1f} điểm để đạt mục tiêu"
                ]
            }
            
            # Save recommendation
            rec_file = self.output_dir / "simple_recommendation.json"
            with open(rec_file, 'w', encoding='utf-8') as f:
                json.dump(recommendation, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Simple recommendation generated. Saved to {rec_file}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            raise

def test_simple_coordinator():
    """Test function for simple coordinator"""
    try:
        coordinator = SimpleCoordinator()
        
        # Load sample data
        program = coordinator.load_sample_training_program()
        print(f"✓ Training program loaded: {program.ten_chuong_trinh}")
        print(f"  Total credits required: {program.tong_tin_chi}")
        print(f"  Number of courses: {len(program.cac_mon_hoc)}")
        
        # Load GPA data
        gpa_data = coordinator.load_gpa_data("ket_qua.json")
        print(f"✓ GPA data loaded with {len(gpa_data.get('bang_diem', []))} course records")
        
        # Analyze graduation requirements
        analysis = coordinator.analyze_graduation_requirements()
        print(f"✓ Graduation analysis completed")
        print(f"  Completed credits: {analysis.tin_chi_da_hoan_thanh}")
        print(f"  Remaining credits: {analysis.tin_chi_con_lai}")
        print(f"  Completion rate: {analysis.ty_le_hoan_thanh:.1f}%")
        
        # Generate recommendation
        recommendation = coordinator.generate_simple_recommendation(analysis)
        print(f"✓ Recommendations generated")
        print(f"  Current GPA: {recommendation['current_status']['gpa']:.2f}")
        print(f"  Target GPA: {recommendation['target_gpa']:.2f}")
        print(f"  Courses to consider retaking: {len(recommendation['improvement_recommendations']['courses_to_retake'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_simple_coordinator()