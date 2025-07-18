"""
Test script for demonstrating PDF reading functionality
"""
import json
from pathlib import Path
from models.training_program import TrainingProgram
from data.sample_program import SAMPLE_TRAINING_PROGRAM
from simple_coordinator import SimpleCoordinator

def create_sample_training_program_file():
    """Create a sample training program JSON file"""
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        program_file = output_dir / "training_program.json"
        with open(program_file, 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_TRAINING_PROGRAM, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Sample training program file created: {program_file}")
        return str(program_file)
    except Exception as e:
        print(f"✗ Error creating sample file: {e}")
        return None

def test_complete_workflow():
    """Test the complete workflow"""
    print("="*50)
    print("TESTING COMPLETE PDF READER AND COORDINATOR WORKFLOW")
    print("="*50)
    
    # Create sample training program file
    program_file = create_sample_training_program_file()
    if not program_file:
        return False
    
    # Test coordinator
    coordinator = SimpleCoordinator()
    
    try:
        # Load training program
        program = coordinator.load_sample_training_program()
        print(f"\n1. Training Program Analysis:")
        print(f"   Name: {program.ten_chuong_trinh}")
        print(f"   Code: {program.ma_chuong_trinh}")
        print(f"   Total Credits: {program.tong_tin_chi}")
        
        # Analyze by course type
        for course_type in ["Đại cương", "Cơ sở", "Chuyên ngành"]:
            courses = [c for c in program.cac_mon_hoc if c.loai_mon == course_type]
            total_credits = sum(c.tin_chi for c in courses)
            print(f"   {course_type}: {len(courses)} courses, {total_credits} credits")
        
        # Load GPA data
        gpa_data = coordinator.load_gpa_data("ket_qua.json")
        current_gpa = gpa_data.get('total_gpa', [])[-1].get('gpa_chung', 0) if gpa_data.get('total_gpa') else 0
        
        print(f"\n2. Current Academic Status:")
        print(f"   Current GPA: {current_gpa:.2f}")
        print(f"   Total courses completed: {len([g for g in gpa_data.get('bang_diem', []) if g.get('tin_chi', 0) > 0])}")
        
        # Graduation analysis
        analysis = coordinator.analyze_graduation_requirements()
        print(f"\n3. Graduation Analysis:")
        print(f"   Completed Credits: {analysis.tin_chi_da_hoan_thanh}/{analysis.chuong_trinh_dao_tao.tong_tin_chi}")
        print(f"   Completion Rate: {analysis.ty_le_hoan_thanh:.1f}%")
        print(f"   Remaining Credits: {analysis.tin_chi_con_lai}")
        print(f"   Estimated Graduation: {analysis.du_kien_tot_nghiep}")
        
        # Generate recommendations
        recommendation = coordinator.generate_simple_recommendation(analysis, target_gpa=3.6)
        print(f"\n4. Recommendations:")
        print(f"   Target GPA: {recommendation['target_gpa']:.2f}")
        print(f"   GPA Gap: {recommendation['gpa_gap']:.2f}")
        print(f"   Priority Courses to Retake: {len(recommendation['improvement_recommendations']['courses_to_retake'])}")
        
        if recommendation['improvement_recommendations']['courses_to_retake']:
            print("   Top 3 priorities:")
            for i, course in enumerate(recommendation['improvement_recommendations']['courses_to_retake'][:3], 1):
                print(f"     {i}. {course['ma_mon']} - {course['ten_mon']} (Current: {course['diem_so']:.1f})")
        
        print(f"\n5. Key Recommendations:")
        for i, rec in enumerate(recommendation['key_recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n✓ Complete workflow test successful!")
        print(f"✓ Results saved to output/ directory")
        
        return True
        
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_workflow()