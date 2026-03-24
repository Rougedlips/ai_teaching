from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, Boolean, func
from sqlalchemy.dialects.postgresql import JSONB  # 引入 PostgreSQL 特有的 JSONB 类型
from database import Base

# 1. 用户表
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    real_name = Column(String(50), nullable=True)
    student_no = Column(String(50), unique=True, nullable=True)
    grade = Column(String(20), nullable=True)
    class_name = Column(String(50), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    bio = Column(String, nullable=True)     # 个人简介
    skills = Column(String, nullable=True)  # 擅长技术

# 2. 课程表
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False)
    course_code = Column(String(50), unique=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id")) 

# ================= 新增部分 =================

# 3. 作业表
# models.py

class Assignment(Base):
    __tablename__ = "assignments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    deadline = Column(String)

    # 🌟 核心修改：确保这里 nullable=True
    evaluation_config = Column(String, nullable=True)
    course_id = Column(Integer, nullable=True)
    ai_criteria = Column(String, nullable=True)


class AssignmentPublishConfig(Base):
    __tablename__ = "assignment_publish_configs"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False, unique=True, index=True)
    class_id = Column(Integer, ForeignKey("teaching_classes.id"), nullable=False, index=True)
    target_type = Column(String(20), nullable=False, default="individual")


class ReportTask(Base):
    __tablename__ = "report_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    deadline = Column(String, nullable=True)
    class_id = Column(Integer, ForeignKey("teaching_classes.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class ReportTaskPublishConfig(Base):
    __tablename__ = "report_task_publish_configs"

    id = Column(Integer, primary_key=True, index=True)
    report_task_id = Column(Integer, ForeignKey("report_tasks.id"), nullable=False, unique=True, index=True)
    class_id = Column(Integer, ForeignKey("teaching_classes.id"), nullable=False, index=True)
    target_type = Column(String(20), nullable=False, default="individual")


class ReportSubmission(Base):
    __tablename__ = "report_submissions"

    id = Column(Integer, primary_key=True, index=True)
    report_task_id = Column(Integer, ForeignKey("report_tasks.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    score = Column(Integer, nullable=True)
    ai_feedback = Column(String, nullable=True)
    teacher_comment = Column(String, nullable=True)
    ai_criteria = Column(String, nullable=True)
    status = Column(String, default="submitted", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

# 4. 代码提交表（记录学生提交历史及AI评测结果）
class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer)
    student_id = Column(Integer)
    code_content = Column(String)
    score = Column(Integer, nullable=True)
    ai_feedback = Column(String, nullable=True)
    ai_criteria = Column(String, nullable=True) # 老师批改时输入的要点
    status = Column(String, default="pending")  # 状态：pending(待批改), finished(已批改)
    teacher_comment = Column(String, nullable=True) # 存老师的最终评语


class AIReviewHistory(Base):
    __tablename__ = "ai_review_histories"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, index=True, nullable=False)
    assignment_id = Column(Integer, nullable=True)
    ai_model = Column(String(50), nullable=True)
    review_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class SubmissionTeamMeta(Base):
    __tablename__ = "submission_team_meta"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False, unique=True, index=True)
    team_id = Column(Integer, ForeignKey("class_teams.id"), nullable=True, index=True)
    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)


class ReportSubmissionTeamMeta(Base):
    __tablename__ = "report_submission_team_meta"

    id = Column(Integer, primary_key=True, index=True)
    report_submission_id = Column(Integer, ForeignKey("report_submissions.id"), nullable=False, unique=True, index=True)
    team_id = Column(Integer, ForeignKey("class_teams.id"), nullable=True, index=True)
    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)


# --- 🌟 直接新增：Team 表 ---
class Team(Base):

    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    leader_id = Column(Integer)
    members = Column(String) # 存储成员ID，如 "1,2,5"

# ================= 学期/班级/组队管理（持久化） =================
class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)


class TeachingClass(Base):
    __tablename__ = "teaching_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class ClassStudent(Base):
    __tablename__ = "class_students"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("teaching_classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class ClassTeam(Base):
    __tablename__ = "class_teams"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("teaching_classes.id"), nullable=False)
    name = Column(String(100), nullable=False)


class ClassTeamMember(Base):
    __tablename__ = "class_team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("class_teams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)


