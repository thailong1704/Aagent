# Agent Training Program Analysis System

## Overview
This system integrates PDF training program analysis with GPA analysis to provide comprehensive academic planning and graduation recommendations.

## Features

### Core Components
1. **Agent_core.py** - Main GPA analysis agent (existing functionality)
2. **Agent_pdf_reader.py** - PDF training program reader and analyzer  
3. **Agent_coordinator.py** - Coordinator for integrating all analysis
4. **GUI.py** - User interface for data input (enhanced with PDF support)

### New Capabilities
- ✅ PDF training program document parsing
- ✅ Course information extraction (code, name, credits, prerequisites)
- ✅ Course categorization (General, Foundation, Major, Elective)
- ✅ Graduation requirement analysis
- ✅ Integrated GPA and curriculum planning
- ✅ Smart course retake recommendations
- ✅ Graduation timeline estimation

## Installation

### Dependencies
```bash
pip install PyPDF2 pdfplumber python-docx pydantic
```

### Optional AI Dependencies
For full AI agent functionality (requires Ollama and agno):
```bash
# Install Ollama first, then:
pip install agno
```

## Usage

### Basic Usage (Enhanced Mode)
```python
from Agent_core import GpaAnalyzer

# Initialize with enhanced mode
analyzer = GpaAnalyzer()

# Setup with PDF training program
analyzer.setup_enhanced_analysis("path/to/training_program.pdf")

# Run analysis
analyzer.setup_driver()
data = analyzer.login_and_scrape(username, password)
analyzer.save_data(data)
analyzer.setup_agent(data)

# Get comprehensive analysis
result = analyzer.analyze_with_training_program(target_gpa=3.6, remaining_semesters=4)
```

### Testing and Development
```python
# Test the system with sample data
python test_workflow.py

# Test simple coordinator without AI dependencies
python simple_coordinator.py
```

## File Structure

```
├── Agent_core.py              # Main GPA analyzer (enhanced)
├── Agent_pdf_reader.py        # PDF training program reader
├── Agent_coordinator.py       # Analysis coordinator
├── simple_coordinator.py      # Simplified version for testing
├── GUI.py                     # User interface
├── models/
│   ├── __init__.py
│   └── training_program.py    # Data models
├── data/
│   └── sample_program.py      # Sample training program data
├── output/                    # Analysis results
│   ├── training_program.json
│   ├── graduation_analysis.json
│   └── recommendations.json
└── test_workflow.py          # Complete workflow test
```

## Data Models

### TrainingProgram
- Program information (name, code, total credits)
- Course list with details
- Graduation requirements

### Course
- Course code and name
- Credits and prerequisites
- Course type categorization
- Semester recommendations

### GraduationAnalysis
- Completion status
- Remaining requirements
- Timeline estimation

## Example Output

### Graduation Analysis
```json
{
  "completed_credits": 101,
  "remaining_credits": 43,
  "completion_rate": 70.1,
  "estimated_graduation": "Khoảng 3 học kỳ"
}
```

### Recommendations
```json
{
  "courses_to_retake": [
    {
      "ma_mon": "EE2009",
      "ten_mon": "Hệ thống Máy tính và Ngôn ngữ Lập trình",
      "diem_so": 4.3,
      "priority": "High"
    }
  ],
  "key_recommendations": [
    "Ưu tiên học lại các môn có điểm thấp và tín chỉ cao",
    "Hoàn thành các môn bắt buộc theo đúng thứ tự tiên quyết"
  ]
}
```

## Testing

The system includes comprehensive testing:

```bash
# Test complete workflow
python test_workflow.py

# Expected output:
# ✓ Training program loaded: Kỹ thuật Điện tử - Viễn thông  
# ✓ GPA data loaded with 46 course records
# ✓ Graduation analysis completed
# ✓ Recommendations generated
```

## Integration Notes

### Backward Compatibility
- All existing functionality in Agent_core.py is preserved
- Enhanced mode is optional and falls back gracefully
- Original GPA analysis works without training program data

### AI Integration
- Uses Ollama with qwen3:8b model when available
- Falls back to rule-based analysis when AI unavailable
- Reasoning tools for step-by-step analysis

## Development

### Adding New Course Types
Update `CourseType` enum in `models/training_program.py`:
```python
class CourseType(str, Enum):
    GENERAL = "Đại cương"
    FOUNDATION = "Cơ sở"  
    MAJOR = "Chuyên ngành"
    ELECTIVE = "Tự chọn"
    THESIS = "Luận văn/Đồ án"
    # Add new types here
```

### Extending PDF Parsing
Modify `extract_text_from_pdf()` and `extract_tables_from_pdf()` in `Agent_pdf_reader.py` for different PDF formats.

### Custom Recommendations
Extend `generate_simple_recommendation()` in `simple_coordinator.py` for institution-specific logic.