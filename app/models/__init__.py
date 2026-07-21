# FORCE SQLALCHEMY REGISTRATION OF ALL MODELS

from app.models.user_model import User
from app.models.role_model import Role
from app.models.permission_model import Permission
from app.models.role_permission_model import RolePermission
from app.models.user_role_model import UserRole

from app.models.school_model import School
from app.models.teacher_model import Teacher
from app.models.student_model import Student

from app.models.teacher_assignment_model import TeacherAssignment
from app.models.class_model import Class
from app.models.section_model import Section

from app.models.enrollment_model import Enrollment
from app.models.attendance_model import Attendance

from app.models.exam_model import Exam
from app.models.mark_model import Mark
from app.models.result_model import Result

from app.models.payment_model import Payment
from app.models.fee_plan_model import FeePlan
from app.models.student_fee_model import StudentFee

from app.models.file_model import File
from app.models.audit_log_model import AuditLog

from app.models.invitation_model import Invitation
from app.models.refresh_token_model import RefreshToken