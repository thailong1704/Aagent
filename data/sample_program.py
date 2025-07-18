"""
Sample training program data for testing
"""
SAMPLE_TRAINING_PROGRAM = {
    "ten_chuong_trinh": "Kỹ thuật Điện tử - Viễn thông",
    "ma_chuong_trinh": "D520207",
    "he_dao_tao": "Đại học",
    "tong_tin_chi": 144,
    "cac_mon_hoc": [
        {
            "ma_mon": "MT1003",
            "ten_mon": "Giải tích 1",
            "tin_chi": 4,
            "loai_mon": "Đại cương",
            "hoc_ky_de_xuat": 1,
            "mon_tien_quyet": [],
            "mon_hoc_truoc": [],
            "mo_ta": "Môn học cơ bản về giải tích",
            "ghi_chu": None
        },
        {
            "ma_mon": "MT1005",
            "ten_mon": "Giải tích 2", 
            "tin_chi": 4,
            "loai_mon": "Đại cương",
            "hoc_ky_de_xuat": 2,
            "mon_tien_quyet": ["MT1003"],
            "mon_hoc_truoc": [],
            "mo_ta": "Tiếp theo của Giải tích 1",
            "ghi_chu": None
        },
        {
            "ma_mon": "MT1007",
            "ten_mon": "Đại số Tuyến tính",
            "tin_chi": 3,
            "loai_mon": "Đại cương", 
            "hoc_ky_de_xuat": 1,
            "mon_tien_quyet": [],
            "mon_hoc_truoc": [],
            "mo_ta": "Môn học về đại số tuyến tính",
            "ghi_chu": None
        },
        {
            "ma_mon": "PH1003",
            "ten_mon": "Vật lý 1",
            "tin_chi": 4,
            "loai_mon": "Đại cương",
            "hoc_ky_de_xuat": 1,
            "mon_tien_quyet": [],
            "mon_hoc_truoc": [],
            "mo_ta": "Vật lý đại cương phần 1",
            "ghi_chu": None
        },
        {
            "ma_mon": "EE1001", 
            "ten_mon": "Nhập môn Về kỹ Thuật",
            "tin_chi": 3,
            "loai_mon": "Cơ sở",
            "hoc_ky_de_xuat": 1,
            "mon_tien_quyet": [],
            "mon_hoc_truoc": [],
            "mo_ta": "Giới thiệu về kỹ thuật",
            "ghi_chu": None
        },
        {
            "ma_mon": "EE2009",
            "ten_mon": "Hệ thống Máy tính và Ngôn ngữ Lập trình",
            "tin_chi": 3,
            "loai_mon": "Cơ sở",
            "hoc_ky_de_xuat": 2,
            "mon_tien_quyet": ["EE1001"],
            "mon_hoc_truoc": [],
            "mo_ta": "Lập trình và hệ thống máy tính",
            "ghi_chu": None
        },
        {
            "ma_mon": "EE2033",
            "ten_mon": "Giải tích mạch",
            "tin_chi": 3,
            "loai_mon": "Cơ sở",
            "hoc_ky_de_xuat": 3,
            "mon_tien_quyet": ["MT1003", "PH1003"],
            "mon_hoc_truoc": [],
            "mo_ta": "Phân tích mạch điện",
            "ghi_chu": None
        },
        {
            "ma_mon": "EE3003",
            "ten_mon": "Thiết kế Hệ thống Nhúng",
            "tin_chi": 3,
            "loai_mon": "Chuyên ngành",
            "hoc_ky_de_xuat": 6,
            "mon_tien_quyet": ["EE2009"],
            "mon_hoc_truoc": [],
            "mo_ta": "Thiết kế hệ thống nhúng",
            "ghi_chu": None
        }
    ],
    "yeu_cau_tong_quat": {
        "gpa_tot_nghiep": 2.0,
        "dieu_kien_dac_biet": [
            "Hoàn thành đủ 144 tín chỉ",
            "GPA >= 2.0",
            "Hoàn thành luận văn tốt nghiệp"
        ]
    }
}