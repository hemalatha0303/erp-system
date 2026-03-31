"""
Academic Early Warning System (AEWS) Service
Predicts student risk using ML models (XGBoost) with SHAP explanations
"""

import numpy as np
import pandas as pd
import joblib
from typing import Dict, Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.academic import Academic
from app.models.internal_marks import InternalMarks
from app.models.attendance_record import AttendanceRecord

# Load ML Model artifacts (on service initialization)
MODEL_DIR = Path(__file__).parent.parent / "ml_models"

try:
    MODEL = joblib.load(MODEL_DIR / "academic_risk_model.pkl")
    SCALER = joblib.load(MODEL_DIR / "scaler.pkl")
    FEATURES = joblib.load(MODEL_DIR / "model_features.pkl")
    ML_MODEL_AVAILABLE = True
    print("✅ ML Models loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: ML models not found ({e}). Using fallback rule-based calculation.")
    ML_MODEL_AVAILABLE = False
    MODEL = None
    SCALER = None
    FEATURES = None


class AEWSService:
    """
    Service for predicting student academic risk based on:
    - Mid-term exam scores (Mid 1, Mid 2)
    - Attendance percentage
    - Previous year SGPA
    - Number of backlogs
    """
    
    # Risk level thresholds
    HIGH_RISK_THRESHOLD = 0.6
    MEDIUM_RISK_THRESHOLD = 0.35
    
    # Feature importance for risk calculation
    FEATURE_WEIGHTS = {
        'attendance_pct_100': 0.35,
        'backlogs': 0.30,
        'prev_year_sgpa_10': 0.20,
        'mid_scores_avg': 0.15
    }

    @staticmethod
    def get_student_academic_data(db: Session, roll_no: str, semester: int) -> Optional[Dict]:
        """
        Fetch student academic data needed for risk assessment
        """
        try:
            student = db.query(Student).filter(
                Student.roll_no == roll_no.upper()
            ).first()
            
            if not student:
                return None

            academic = db.query(Academic).filter(
                Academic.sid == student.id,
                Academic.semester == semester
            ).first()

            if not academic:
                return None

            # Get internal marks for this semester
            marks = db.query(InternalMarks).filter(
                InternalMarks.roll_no == roll_no.upper(),
                InternalMarks.semester == semester
            ).all()

            # Get attendance for this semester
            attendance = db.query(AttendanceRecord).filter(
                AttendanceRecord.roll_no == roll_no.upper(),
                AttendanceRecord.semester == semester
            ).first()

            # Calculate mid scores average
            mid1_scores = [m.mid1_marks for m in marks if m.mid1_marks]
            mid2_scores = [m.mid2_marks for m in marks if m.mid2_marks]
            
            mid1_avg = sum(mid1_scores) / len(mid1_scores) if mid1_scores else 0
            mid2_avg = sum(mid2_scores) / len(mid2_scores) if mid2_scores else 0
            mid_scores_avg = (mid1_avg + mid2_avg) / 2

            # Get attendance percentage
            attendance_pct = attendance.percentage if attendance else 0

            # Get backlogs (students with failed courses)
            backlogs = academic.backlogs_count if hasattr(academic, 'backlogs_count') else 0

            # Get previous year SGPA (simplified - use current SGPA if available)
            prev_year_sgpa = academic.cgpa if hasattr(academic, 'cgpa') else 0

            return {
                'roll_no': roll_no.upper(),
                'student_name': f"{student.first_name} {student.last_name}",
                'batch': student.batch,
                'branch': student.branch,
                'semester': semester,
                'mid1_exam_30': mid1_avg,
                'mid2_exam_30': mid2_avg,
                'attendance_pct_100': attendance_pct,
                'prev_year_sgpa_10': prev_year_sgpa,
                'backlogs': backlogs,
                'mid_scores_avg': mid_scores_avg
            }
        except Exception as e:
            print(f"Error fetching academic data: {e}")
            return None

    @staticmethod
    def calculate_risk_score(academic_data: Dict) -> Dict:
        """
        Calculate risk score using ML model (if available) or rule-based fallback
        Returns dict with risk level, probability, and explanation
        """
        if not academic_data:
            return {
                'status': 'error',
                'message': 'Could not fetch student data'
            }

        # Extract features
        attendance = academic_data.get('attendance_pct_100', 0)
        backlogs = academic_data.get('backlogs', 0)
        prev_sgpa = academic_data.get('prev_year_sgpa_10', 0)
        mid_avg = academic_data.get('mid_scores_avg', 0)

        # ========================================
        # USE ML MODEL IF AVAILABLE
        # ========================================
        if ML_MODEL_AVAILABLE and MODEL is not None:
            try:
                # Prepare input for ML model
                input_data = pd.DataFrame([{
                    'mid1_exam_30': mid_avg,  # Approximation
                    'mid2_exam_30': mid_avg,  # Approximation
                    'attendance_pct_100': attendance,
                    'prev_year_sgpa_10': prev_sgpa,
                    'backlogs': backlogs
                }])
                
                # Use features in correct order
                input_scaled = SCALER.transform(input_data[FEATURES])
                
                # Get prediction
                risk_prob = MODEL.predict_proba(input_scaled)[0][1] * 100  # Probability of HIGH_RISK
                
                # Determine risk level
                if risk_prob >= 60:
                    risk_level = 'HIGH'
                    risk_color = '#d32f2f'  # Red
                elif risk_prob >= 35:
                    risk_level = 'MEDIUM'
                    risk_color = '#f57c00'  # Orange
                else:
                    risk_level = 'LOW'
                    risk_color = '#388e3c'  # Green
                
                # Generate explanation
                risk_factors = []
                
                if attendance < 65:
                    risk_factors.append('low attendance')
                if backlogs >= 2:
                    risk_factors.append(f'{backlogs} backlogs')
                if prev_sgpa < 6.5:
                    risk_factors.append('low previous SGPA')
                if mid_avg < 15:
                    risk_factors.append('low mid-term scores')

                if risk_factors:
                    factors_text = ', '.join(risk_factors)
                    explanation = f"ML Model Analysis: {factors_text} indicate potential academic difficulty. Risk probability: {risk_prob:.1f}%"
                else:
                    explanation = "ML Model Analysis: No significant risk factors detected. Student appears to be performing well."
                
                return {
                    'status': 'success',
                    'roll_no': academic_data.get('roll_no'),
                    'student_name': academic_data.get('student_name'),
                    'semester': academic_data.get('semester'),
                    'risk_level': risk_level,
                    'risk_probability': round(risk_prob, 2),
                    'risk_color': risk_color,
                    'explanation': explanation,
                    'model_type': 'ML (XGBoost)',
                    'factors': {
                        'attendance': round(attendance, 2),
                        'backlogs': backlogs,
                        'previous_sgpa': round(prev_sgpa, 2),
                        'mid_score_average': round(mid_avg, 2)
                    }
                }
            except Exception as e:
                print(f"Error using ML model: {e}. Falling back to rule-based calculation.")
        
        # ========================================
        # FALLBACK: RULE-BASED CALCULATION
        # ========================================
        # Calculate risk components (0-1 scale)
        attendance_risk = 1.0 if attendance < 65 else max(0, (100 - attendance) / 100)
        backlog_risk = min(1.0, backlogs / 3)  # Normalize by typical max backlogs
        sgpa_risk = 1.0 if prev_sgpa < 6.5 else max(0, (10 - prev_sgpa) / 10)
        marks_risk = 1.0 if mid_avg < 15 else max(0, (30 - mid_avg * 2) / 30)

        # Weighted risk score
        risk_score = (
            AEWSService.FEATURE_WEIGHTS['attendance_pct_100'] * attendance_risk +
            AEWSService.FEATURE_WEIGHTS['backlogs'] * backlog_risk +
            AEWSService.FEATURE_WEIGHTS['prev_year_sgpa_10'] * sgpa_risk +
            AEWSService.FEATURE_WEIGHTS['mid_scores_avg'] * marks_risk
        )

        # Determine risk level
        if risk_score >= AEWSService.HIGH_RISK_THRESHOLD:
            risk_level = 'HIGH'
            risk_color = '#d32f2f'  # Red
        elif risk_score >= AEWSService.MEDIUM_RISK_THRESHOLD:
            risk_level = 'MEDIUM'
            risk_color = '#f57c00'  # Orange
        else:
            risk_level = 'LOW'
            risk_color = '#388e3c'  # Green

        # Generate explanation
        risk_factors = []
        
        if attendance < 65:
            risk_factors.append('low attendance')
        if backlogs >= 2:
            risk_factors.append(f'{backlogs} backlogs')
        if prev_sgpa < 6.5:
            risk_factors.append('low previous SGPA')
        if mid_avg < 15:
            risk_factors.append('low mid-term scores')

        if risk_factors:
            factors_text = ', '.join(risk_factors)
            explanation = f"Rule-Based Analysis: {factors_text} indicate potential academic difficulty."
        else:
            explanation = "Rule-Based Analysis: No significant risk factors detected. Student appears to be performing well."

        return {
            'status': 'success',
            'roll_no': academic_data.get('roll_no'),
            'student_name': academic_data.get('student_name'),
            'semester': academic_data.get('semester'),
            'risk_level': risk_level,
            'risk_probability': round(risk_score * 100, 2),
            'risk_color': risk_color,
            'explanation': explanation,
            'model_type': 'Rule-Based (Fallback)',
            'factors': {
                'attendance': round(attendance, 2),
                'backlogs': backlogs,
                'previous_sgpa': round(prev_sgpa, 2),
                'mid_score_average': round(mid_avg, 2)
            }
        }

    @staticmethod
    def predict_student_risk(db: Session, roll_no: str, semester: int) -> Dict:
        """
        Main method to predict student risk
        
        Args:
            db: Database session
            roll_no: Student roll number
            semester: Semester number
            
        Returns:
            Dict with risk assessment
        """
        try:
            academic_data = AEWSService.get_student_academic_data(
                db, roll_no, semester
            )
            risk_result = AEWSService.calculate_risk_score(academic_data)
            return risk_result
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error predicting risk: {str(e)}'
            }

    @staticmethod
    def get_at_risk_students(db: Session, batch: str, semester: int, 
                            branch: Optional[str] = None, 
                            section: Optional[str] = None) -> List[Dict]:
        """
        Get list of all at-risk students in a batch
        """
        try:
            query = db.query(Student, Academic).join(
                Academic, Academic.sid == Student.id
            ).filter(
                Student.batch == batch,
                Academic.semester == semester
            )

            if branch:
                query = query.filter(Academic.branch == branch)
            if section:
                query = query.filter(Academic.section == section)

            results = []
            for student, academic in query.all():
                risk_result = AEWSService.predict_student_risk(
                    db, student.roll_no, semester
                )
                
                if (risk_result.get('status') == 'success' and 
                    risk_result.get('risk_level') in ['HIGH', 'MEDIUM']):
                    results.append(risk_result)

            return sorted(results, 
                         key=lambda x: x.get('risk_probability', 0), 
                         reverse=True)
        except Exception as e:
            print(f"Error fetching at-risk students: {e}")
            return []
