import enum


class StudentProgram(str, enum.Enum):
    MBBS = "MBBS"
    BDS = "BDS"
    NURSING = "Nursing"
    PHARMACY = "Pharmacy"
    PHYSIOTHERAPY = "Physiotherapy"
    BAMS = "BAMS"
    BHMS = "BHMS"


class DifficultyLevel(str, enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class QuizType(str, enum.Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "True/False"
    VIVA = "Viva"
    CLINICAL = "Clinical"


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "True/False"
    VIVA = "Viva"
    CLINICAL = "Clinical"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    EXCUSED = "Excused"


class AnalyticsEventType(str, enum.Enum):
    STUDY_HOURS = "study_hours"
    QUIZ_SCORE = "quiz_score"
    ATTENDANCE = "attendance"
    FLASHCARD_REVIEW = "flashcard_review"
    NOTE_CREATED = "note_created"
    PDF_UPLOAD = "pdf_upload"
    AI_TUTOR_SESSION = "ai_tutor_session"
    CLINICAL_ATTEMPT = "clinical_attempt"


class FileType(str, enum.Enum):
    PDF = "pdf"
    IMAGE = "image"
    OTHER = "other"

    
class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class StudyMode(str, enum.Enum):
    LEARN = "Learn"
    EXAM = "Exam"
    REVISION = "Revision"
    VIVA = "Viva"
    CLINICAL = "Clinical"