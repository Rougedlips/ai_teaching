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
    major_direction = Column(String(100), nullable=True)
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


class ClassLearningSurvey(Base):
    __tablename__ = "class_learning_surveys"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("teaching_classes.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    analysis_score = Column(Integer, nullable=True)
    open_mind_score = Column(Integer, nullable=True)
    thinking_confidence_score = Column(Integer, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


# ================= 综合项目组队申请体系 =================

class ProjectTopic(Base):
    __tablename__ = "project_topics"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    materials = Column(Text, nullable=True)
    attachment_path = Column(String, nullable=True)
    direction = Column(String(100), nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(20), nullable=False, default="teacher")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class ProjectApplicationSetting(Base):
    __tablename__ = "project_application_settings"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False, unique=True, index=True)
    is_enabled = Column(Boolean, default=False, nullable=False)
    open_start = Column(String(20), nullable=True)
    open_end = Column(String(20), nullable=True)
    min_team_size = Column(Integer, default=2, nullable=False)
    max_team_size = Column(Integer, default=6, nullable=False)


class ProjectClassTopicConfig(Base):
    __tablename__ = "project_class_topic_configs"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("teaching_classes.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("project_topics.id"), nullable=False, index=True)


class ProjectTeam(Base):
    __tablename__ = "project_teams"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("teaching_classes.id"), nullable=False, index=True)
    team_no = Column(String(50), nullable=False)
    team_name = Column(String(100), nullable=False)
    direction = Column(String(100), nullable=False)
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("project_topics.id"), nullable=True, index=True)
    advisor_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    apply_note = Column(Text, nullable=True)
    apply_attachment_path = Column(String, nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    review_comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class ProjectTeamMember(Base):
    __tablename__ = "project_team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("project_teams.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)





