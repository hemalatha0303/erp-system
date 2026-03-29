from typing import Tuple


# Grading table as per institution standards
GRADE_SCALE = [
    # (min_percentage, letter_grade, grade_points)
    (90, "A+", 10),
    (80, "A", 9),
    (70, "B", 8),
    (60, "C", 7),
    (50, "D", 6),
    (40, "E", 5),
    (0, "F", 0),
]


def _to_float(value) -> float:
    """Convert value to float, handling None, strings, and invalid values"""
    if value is None:
        return 0.0
    if isinstance(value, str):
        cleaned = value.strip().upper()
        if cleaned in ("AB", "A", "ABSENT"):
            return 0.0
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0


def round2(value: float) -> float:
    """Round to 2 decimal places"""
    try:
        return round(float(value), 2)
    except Exception:
        return 0.0


def calculate_mid_marks(objective: float, descriptive: float, openbook: float, seminar: float) -> float:
    """
    Calculate mid exam marks from components.
    
    Formula:
    - Objective[20 marks] / 2 = 10 marks
    - Descriptive[30 marks] / 3 = 10 marks
    - Open book[20 marks] / 4 = 5 marks
    - Seminar[5 marks] / 1 = 5 marks
    Total = 30 marks
    """
    objective_scaled = _to_float(objective) / 2.0  # 20/2 = 10
    descriptive_scaled = _to_float(descriptive) / 3.0  # 30/3 = 10
    openbook_scaled = _to_float(openbook) / 4.0  # 20/4 = 5
    seminar_scaled = _to_float(seminar) / 1.0  # 5/1 = 5
    
    total = objective_scaled + descriptive_scaled + openbook_scaled + seminar_scaled
    return round2(total)


def calculate_final_internal_marks(mid1: float, mid2: float) -> float:
    """
    Calculate final internal marks from mid1 and mid2.
    
    Formula: Final Internal = (Best of Mid1/Mid2 × 0.8 + Least of Mid1/Mid2 × 0.2)
    Each mid is out of 30 marks, so final internal is out of 30 marks
    """
    m1 = _to_float(mid1)
    m2 = _to_float(mid2)
    
    best = max(m1, m2)
    least = min(m1, m2)
    
    final_internal = (best * 0.8) + (least * 0.2)
    return round2(final_internal)


def calculate_semester_marks(internal_marks: float, external_marks: float) -> float:
    """
    Calculate semester marks from internal and external components.
    
    Formula: Semester Marks = (30 marks internal + 70 marks external)
    
    Note: internal_marks should already be out of 30
    Note: external_marks should be out of 70
    """
    internal = _to_float(internal_marks)  # Out of 30
    external = _to_float(external_marks)  # Out of 70
    
    semester_total = internal + external  # Total out of 100
    return round2(semester_total)


def grade_from_percentage(percentage: float) -> Tuple[str, int]:
    """
    Get grade letter and grade points based on percentage.
    
    Grading Table:
    ≥90: A+ (10 points)
    80-89: A (9 points)
    70-79: B (8 points)
    60-69: C (7 points)
    50-59: D (6 points)
    40-49: E (5 points)
    <40: F (0 points)
    """
    score = _to_float(percentage)
    score = max(0.0, min(score, 100.0))
    
    for cutoff, letter, points in GRADE_SCALE:
        if score >= cutoff:
            return letter, points
    
    return "F", 0


# Backward compatibility alias
def calc_mid_total(openbook: float, objective: float, descriptive: float, seminar: float) -> float:
    """Backward compatibility wrapper"""
    return calculate_mid_marks(objective, descriptive, openbook, seminar)


def calc_final_internal(mid1: float, mid2: float) -> float:
    """Backward compatibility wrapper"""
    return calculate_final_internal_marks(mid1, mid2)


def grade_from_score(score: float) -> Tuple[str, int]:
    """Backward compatibility wrapper"""
    return grade_from_percentage(score)


def calc_sgpa(total_points: float, total_credits: float) -> float:
    """
    Calculate Semester Grade Point Average (SGPA).
    
    Formula: SGPA = Σ(Credits × Grade Points) / Σ Credits
    """
    if not total_credits:
        return 0.0
    sgpa = total_points / total_credits
    return round2(sgpa)


def calc_cgpa(semester_rows) -> float:
    """
    Calculate Cumulative Grade Point Average (CGPA).
    
    Formula: CGPA = Σ(Credits × SGPA) / Σ Credits
    Computed over all semesters
    """
    total_points = 0.0
    total_credits = 0.0
    
    for row in semester_rows or []:
        if row is None:
            continue
        
        credits = getattr(row, "total_credits", 0) or 0
        sgpa = getattr(row, "sgpa", 0) or 0
        
        total_points += float(sgpa) * float(credits)
        total_credits += float(credits)
    
    if not total_credits:
        return 0.0
    
    cgpa = total_points / total_credits
    return round2(cgpa)


def cgpa_to_percentage(cgpa: float) -> float:
    """
    Convert CGPA to equivalent percentage as per AICTE regulations.
    
    Formula: Equivalent Percentage = (CGPA - 0.75) × 10
    """
    cgpa_val = _to_float(cgpa)
    percentage = (cgpa_val - 0.75) * 10
    return round2(max(0.0, percentage))
