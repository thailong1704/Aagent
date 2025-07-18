"""
Data models for training program information
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class CourseType(str, Enum):
    """Enum for course types"""
    GENERAL = "Đại cương"
    FOUNDATION = "Cơ sở"
    MAJOR = "Chuyên ngành"
    ELECTIVE = "Tự chọn"
    THESIS = "Luận văn/Đồ án"

class Course(BaseModel):
    """Model for individual course information"""
    ma_mon: str = Field(..., description="Mã môn học")
    ten_mon: str = Field(..., description="Tên môn học")
    tin_chi: int = Field(..., description="Số tín chỉ")
    loai_mon: CourseType = Field(..., description="Loại môn học")
    hoc_ky_de_xuat: Optional[int] = Field(None, description="Học kỳ đề xuất")
    mon_tien_quyet: List[str] = Field(default_factory=list, description="Danh sách mã môn tiên quyết")
    mon_hoc_truoc: List[str] = Field(default_factory=list, description="Danh sách mã môn học trước")
    mo_ta: Optional[str] = Field(None, description="Mô tả môn học")
    ghi_chu: Optional[str] = Field(None, description="Ghi chú đặc biệt")
    
    @validator('tin_chi')
    def validate_tin_chi(cls, v):
        if v <= 0:
            raise ValueError('Số tín chỉ phải lớn hơn 0')
        return v

class TrainingProgram(BaseModel):
    """Model for complete training program"""
    ten_chuong_trinh: str = Field(..., description="Tên chương trình đào tạo")
    ma_chuong_trinh: str = Field(..., description="Mã chương trình đào tạo")
    he_dao_tao: str = Field(..., description="Hệ đào tạo (Đại học, Thạc sĩ, ...)")
    tong_tin_chi: int = Field(..., description="Tổng số tín chỉ yêu cầu tốt nghiệp")
    cac_mon_hoc: List[Course] = Field(..., description="Danh sách tất cả môn học")
    yeu_cau_tong_quat: Dict[str, Any] = Field(default_factory=dict, description="Yêu cầu tổng quát khác")
    
    @validator('tong_tin_chi')
    def validate_tong_tin_chi(cls, v):
        if v <= 0:
            raise ValueError('Tổng tín chỉ phải lớn hơn 0')
        return v
    
    def get_courses_by_type(self, course_type: CourseType) -> List[Course]:
        """Lấy danh sách môn học theo loại"""
        return [course for course in self.cac_mon_hoc if course.loai_mon == course_type]
    
    def get_course_by_code(self, ma_mon: str) -> Optional[Course]:
        """Tìm môn học theo mã môn"""
        for course in self.cac_mon_hoc:
            if course.ma_mon == ma_mon:
                return course
        return None
    
    def get_total_credits_by_type(self, course_type: CourseType) -> int:
        """Tính tổng tín chỉ theo loại môn học"""
        return sum(course.tin_chi for course in self.get_courses_by_type(course_type))

class GraduationAnalysis(BaseModel):
    """Model for graduation requirement analysis"""
    chuong_trinh_dao_tao: TrainingProgram = Field(..., description="Chương trình đào tạo")
    mon_da_hoc: List[str] = Field(..., description="Danh sách mã môn đã học")
    mon_con_lai: List[Course] = Field(..., description="Danh sách môn còn lại cần học")
    tin_chi_da_hoan_thanh: int = Field(..., description="Số tín chỉ đã hoàn thành")
    tin_chi_con_lai: int = Field(..., description="Số tín chỉ còn lại")
    ty_le_hoan_thanh: float = Field(..., description="Tỷ lệ hoàn thành (%)")
    du_kien_tot_nghiep: str = Field(..., description="Dự kiến thời gian tốt nghiệp")
    
    @validator('ty_le_hoan_thanh')
    def validate_ty_le(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Tỷ lệ hoàn thành phải nằm trong khoảng 0-100%')
        return v