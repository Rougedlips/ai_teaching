from pydantic import BaseModel
from typing import Optional, List


class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    real_name: Optional[str] = None
    student_no: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    teacher_id: Optional[int] = None
    is_admin: bool = False


class UserLogin(BaseModel):
    username: str
    password: str


class CourseCreate(BaseModel):
    course_name: str
    course_code: str
    teacher_id: int


class AssignmentCreate(BaseModel):
    title: str
    description: str
    deadline: str
    course_id: Optional[int] = None
    ai_criteria: Optional[str] = None
    target_type: Optional[str] = "individual"



class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[str] = None
    ai_criteria: Optional[str] = None


class SubmissionCreate(BaseModel):
    assignment_id: int
    student_id: int
    code_content: str


class ReportCreate(BaseModel):
    submission_id: int
    ai_feedback: str
    teacher_comment: str
    score: int
    ai_criteria: str
    ai_model: str


class ReportTaskCreate(BaseModel):
    title: str
    description: str
    deadline: str
    class_id: int
    target_type: Optional[str] = "individual"



class ReportTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[str] = None


class ReportSubmissionReviewCreate(BaseModel):
    ai_feedback: str
    teacher_comment: str
    score: int
    ai_criteria: Optional[str] = None
    ai_model: Optional[str] = None


class ReportSubmissionReturnCreate(BaseModel):
    reason: Optional[str] = None


class ProfileUpdate(BaseModel):

    user_id: int
    bio: str
    skills: str


class SemesterPublish(BaseModel):
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_enabled: bool = True


class SemesterCreate(BaseModel):
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_enabled: bool = True
    is_current: bool = False


class SemesterUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_enabled: Optional[bool] = None
    is_current: Optional[bool] = None


class SemesterSetCurrent(BaseModel):
    semester_id: int


class TeachingClassCreate(BaseModel):
    name: str
    teacher_id: int
    semester_id: Optional[int] = None


class TeachingClassUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[int] = None
    semester_id: Optional[int] = None



class ClassStudentAssign(BaseModel):
    student_ids: List[int]


class ClassTeamCreate(BaseModel):
    name: str


class TeamMembersUpdate(BaseModel):
    student_ids: List[int]


class TeamTransfer(BaseModel):
    student_id: int
    target_team_id: int


class TeacherCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    is_admin: bool = False


class TeacherUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    real_name: Optional[str] = None
    is_admin: Optional[bool] = None


class StudentCreate(BaseModel):
    username: str
    password: str
    student_no: Optional[str] = None
    real_name: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    teacher_id: Optional[int] = None


class StudentUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    student_no: Optional[str] = None
    real_name: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    teacher_id: Optional[int] = None


class PasswordReset(BaseModel):
    new_password: str
