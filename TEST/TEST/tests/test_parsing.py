from app.services.parsing_service import extract_candidate_info


def test_extract_candidate_info_basic():
    text = (
        "Name: Nguyen Van A\n"
        "Phone: 0901 234 567\n"
        "Date of Birth: 20/07/1995\n"
        "WORK EXPERIENCE\n"
        "Operator - ABC Manufacturing 2021-2023\n"
    )
    resume = extract_candidate_info(text)
    assert resume.name == "Nguyen Van A"
    assert resume.phone.endswith("0901234567")
    assert resume.birth_date == "1995-07-20"
    assert len(resume.experience) >= 1


def test_extract_candidate_info_vn_labels():
    text = (
        "Họ và tên: Tran Thi B\n"
        "SĐT: +84 912 345 678\n"
        "Ngày sinh: 1995-07-20\n"
        "Kinh nghiệm làm việc\n"
        "Nhân viên bán hàng - Cong ty XYZ 2019–2022\n"
    )
    resume = extract_candidate_info(text)
    assert resume.name == "Tran Thi B"
    assert resume.phone.endswith("0912345678")
    assert resume.birth_date == "1995-07-20"
    assert len(resume.experience) >= 1 