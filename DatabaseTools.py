"""
Database access tool that only queries when the user explicitly requests it.
This tool provides lazy-loaded database access to prevent unnecessary queries.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseAccessTool:
    """
    A lazy-loaded database access tool that only queries when user requests.
    This tool supports querying student grades, GPA history, and course information.
    """
    
    def __init__(self, data_file: str = "ket_qua.json"):
        """
        Initialize the database access tool.
        
        Args:
            data_file: Path to the JSON file containing student data
        """
        self._data_file = data_file
        self._data = None  # Lazy-loaded data
        self._is_loaded = False
    
    def _load_data(self) -> Dict[str, Any]:
        """
        Lazily load data from the database file.
        Only called when data is actually needed.
        
        Returns:
            Dictionary containing the loaded data
        """
        if self._is_loaded and self._data is not None:
            return self._data
        
        try:
            with open(self._data_file, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
                self._is_loaded = True
                logger.info(f"Data loaded from {self._data_file}")
                return self._data
        except FileNotFoundError:
            logger.error(f"Database file not found: {self._data_file}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {self._data_file}")
            raise
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            raise
    
    def query_student_grades(self, semester: Optional[str] = None) -> Dict[str, Any]:
        """
        Query student grades from the database.
        Only loads data when explicitly called.
        
        Args:
            semester: Optional semester to filter results (e.g., "HK1", "HK2")
        
        Returns:
            Dictionary containing student grade information
        """
        logger.info(f"User requested: Query student grades (semester: {semester})")
        
        data = self._load_data()
        
        if not data:
            return {"error": "No data available"}
        
        # Extract relevant grade information
        grades_data = {
            "retrieved_at": datetime.now().isoformat(),
            "semester_filter": semester,
            "grades": []
        }
        
        if "bang_diem" in data:
            for grade_entry in data["bang_diem"]:
                if semester is None or grade_entry.get("hoc_ky") == semester:
                    grades_data["grades"].append(grade_entry)
        
        logger.info(f"Returned {len(grades_data['grades'])} grade records")
        return grades_data
    
    def query_gpa_history(self) -> List[Dict[str, Any]]:
        """
        Query GPA history from the database.
        Only loads data when explicitly called.
        
        Returns:
            List containing GPA history records
        """
        logger.info("User requested: Query GPA history")
        
        data = self._load_data()
        
        if not data or "total_gpa" not in data:
            return []
        
        gpa_history = data.get("total_gpa", [])
        logger.info(f"Returned {len(gpa_history)} GPA records")
        return gpa_history
    
    def query_course_info(self, course_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Query course information from the database.
        Only loads data when explicitly called.
        
        Args:
            course_code: Optional course code to filter results
        
        Returns:
            Dictionary containing course information
        """
        logger.info(f"User requested: Query course info (course_code: {course_code})")
        
        data = self._load_data()
        
        if not data:
            return {"error": "No data available"}
        
        course_data = {
            "retrieved_at": datetime.now().isoformat(),
            "course_code_filter": course_code,
            "courses": []
        }
        
        if "bang_diem" in data:
            seen_courses = set()
            for grade_entry in data["bang_diem"]:
                ma_mon = grade_entry.get("ma_mon", "")
                if course_code is None or ma_mon == course_code:
                    if ma_mon not in seen_courses:
                        seen_courses.add(ma_mon)
                        course_data["courses"].append({
                            "ma_mon": ma_mon,
                            "ten_mon": grade_entry.get("ten_mon", ""),
                            "tin_chi": grade_entry.get("tin_chi", 0),
                            "diem_chu": grade_entry.get("diem_chu", "")
                        })
        
        logger.info(f"Returned {len(course_data['courses'])} course records")
        return course_data
    
    def query_student_summary(self) -> Dict[str, Any]:
        """
        Query student summary information from the database.
        Only loads data when explicitly called.
        
        Returns:
            Dictionary containing student summary
        """
        logger.info("User requested: Query student summary")
        
        data = self._load_data()
        
        if not data:
            return {"error": "No data available"}
        
        # Build summary from available data
        summary = {
            "retrieved_at": datetime.now().isoformat(),
            "current_gpa": None,
            "total_credits": None,
            "total_courses": 0
        }
        
        # Get current GPA
        if "total_gpa" in data and len(data["total_gpa"]) > 0:
            latest_gpa_record = data["total_gpa"][-1]
            summary["current_gpa"] = latest_gpa_record.get("gpa_chung")
            summary["total_credits"] = latest_gpa_record.get("tin_chi")
        
        # Count total courses
        if "bang_diem" in data:
            summary["total_courses"] = len(data["bang_diem"])
        
        logger.info(f"Returned student summary")
        return summary
    
    def is_data_loaded(self) -> bool:
        """
        Check if data has been loaded from the database.
        
        Returns:
            True if data is loaded, False otherwise
        """
        return self._is_loaded
    
    def clear_cache(self) -> None:
        """Clear the cached data to force a fresh load on next query."""
        self._data = None
        self._is_loaded = False
        logger.info("Database cache cleared")


def create_database_tool() -> DatabaseAccessTool:
    """
    Factory function to create a database access tool instance.
    
    Returns:
        DatabaseAccessTool instance
    """
    return DatabaseAccessTool()
