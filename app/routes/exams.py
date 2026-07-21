from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.teacher_model import Teacher
from app.models.teacher_assignment_model import TeacherAssignment
from app.models.enrollment_model import Enrollment

from app.models.class_model import Class
from app.models.section_model import Section
from app.models.subject_model import Subject
from app.models.exam_model import Exam
from app.models.mark_model import Mark
from app.models.student_model import Student

from app.schemas.exam_schema import (
    SubjectCreate,
    ExamCreate,
    MarkCreate
)

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/exams",
    tags=["Exams"]
)


# ----------------------------
# CREATE SUBJECT
# ----------------------------

@router.post("/subjects")
def create_subject(

    data: SubjectCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_exams"
        )
    )

):

    existing = db.query(Subject).filter(

        Subject.school_id == current_user.school_id,

        Subject.name == data.name

    ).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Subject already exists"
        )

    subject = Subject(

        school_id=current_user.school_id,

        name=data.name,

        code=data.code

    )

    db.add(subject)

    db.commit()

    db.refresh(subject)

    return subject


# ----------------------------
# CREATE EXAM
# ----------------------------

@router.post("/")
def create_exam(

    data: ExamCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_exams"
        )
    )

):

    subject = db.query(
        Subject
    ).filter(

        Subject.id == data.subject_id,

        Subject.school_id == current_user.school_id

    ).first()

    if not subject:

        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    existing = db.query(
        Exam
    ).filter(

        Exam.school_id == current_user.school_id,

        Exam.title == data.title,

        Exam.class_id == data.class_id,

        Exam.section_id == data.section_id,

        Exam.subject_id == data.subject_id

    ).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Exam already exists"
        )

    exam = Exam(

        school_id=current_user.school_id,

        title=data.title,

        class_id=data.class_id,

        section_id=data.section_id,

        subject_id=data.subject_id,

        total_marks=data.total_marks

    )

    db.add(exam)

    db.commit()

    db.refresh(exam)

    return exam
# ADD MARKS
# ----------------------------

@router.post("/marks")
def add_marks(

    data: MarkCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_exams"
        )
    )

):

    student = db.query(
        Student
    ).filter(

        Student.id == data.student_id,

        Student.school_id == current_user.school_id

    ).first()


    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )


    if data.obtained_marks < 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid marks"
        )


    if data.obtained_marks > data.total_marks:

        raise HTTPException(
            status_code=400,
            detail="Obtained marks cannot exceed total marks"
        )


    existing = db.query(Mark).filter(

        Mark.school_id == current_user.school_id,

        Mark.exam_id == data.exam_id,

        Mark.student_id == data.student_id,

        Mark.subject_id == data.subject_id

    ).first()


    if existing:

        raise HTTPException(
            status_code=400,
            detail="Marks already entered"
        )


    mark = Mark(

        school_id=current_user.school_id,

        student_id=data.student_id,

        exam_id=data.exam_id,

        subject_id=data.subject_id,

        obtained_marks=data.obtained_marks,

        total_marks=data.total_marks

    )


    db.add(mark)

    db.commit()

    db.refresh(mark)


    return mark
# ----------------------------
# GET SUBJECTS
# ----------------------------

@router.get("/subjects")
def get_subjects(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_exams"
        )
    )

):

    query = db.query(Subject)

    query = apply_tenant_filter(

        query=query,

        model=Subject,

        current_user=current_user

    )

    return query.order_by(
        Subject.name
    ).all()


# ----------------------------
# GET MARKS
# ----------------------------

@router.post("/marks")
def add_marks(

    data: MarkCreate,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_exams"
        )
    )

):

    student = db.query(
        Student
    ).filter(

        Student.id == data.student_id,

        Student.school_id == current_user.school_id

    ).first()


    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )


    if data.obtained_marks < 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid marks"
        )


    if data.obtained_marks > data.total_marks:

        raise HTTPException(
            status_code=400,
            detail="Obtained marks cannot exceed total marks"
        )


    existing = db.query(Mark).filter(

        Mark.school_id == current_user.school_id,

        Mark.exam_id == data.exam_id,

        Mark.student_id == data.student_id,

        Mark.subject_id == data.subject_id

    ).first()


    if existing:

        raise HTTPException(
            status_code=400,
            detail="Marks already entered"
        )


    mark = Mark(

        school_id=current_user.school_id,

        student_id=data.student_id,

        exam_id=data.exam_id,

        subject_id=data.subject_id,

        obtained_marks=data.obtained_marks,

        total_marks=data.total_marks

    )


    db.add(mark)

    db.commit()

    db.refresh(mark)


    return mark
# ----------------------------
# GET EXAMS
# ----------------------------

@router.get("/")
def get_exams(

    class_id: int | None = None,

    section_id: int | None = None,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    query = db.query(Exam)

    query = apply_tenant_filter(

        query=query,

        model=Exam,

        current_user=current_user

    )

    if class_id is not None:

        query = query.filter(
            Exam.class_id == class_id
        )

    if section_id is not None:

        query = query.filter(
            Exam.section_id == section_id
        )

    return query.all()
#  ----------------------------
# GET SINGLE EXAM
# ----------------------------
@router.get("/teacher")
def teacher_exams(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_exams"
        )
    )

):

    teacher = db.query(
        Teacher
    ).filter(

        Teacher.school_id ==
        current_user.school_id,

        Teacher.user_id ==
        current_user.id

    ).first()


    if not teacher:
        return []


    assignments = db.query(
        TeacherAssignment
    ).filter(

        TeacherAssignment.school_id ==
        current_user.school_id,

        TeacherAssignment.teacher_id ==
        teacher.id

    ).all()


    if not assignments:
        return []


    result = []


    for assignment in assignments:


        exams = (
            db.query(Exam)
            .join(
                Subject,
                Exam.subject_id == Subject.id
            )
            .filter(

                Exam.school_id ==
                current_user.school_id,

                Exam.class_id ==
                assignment.class_id,

                Exam.section_id ==
                assignment.section_id,

                Subject.name ==
                assignment.subject

            )
            .all()
        )


        for exam in exams:


            subject = db.query(
                Subject
            ).filter(

                Subject.id ==
                exam.subject_id

            ).first()


            class_obj = db.query(
                Class
            ).filter(

                Class.id ==
                exam.class_id

            ).first()


            section_obj = db.query(
                Section
            ).filter(

                Section.id ==
                exam.section_id

            ).first()



            result.append({

                "id": exam.id,

                "title": exam.title,

                "subject":
                    subject.name
                    if subject
                    else "",

                "class_name":
                    class_obj.name
                    if class_obj
                    else "",

                "section_name":
                    section_obj.name
                    if section_obj
                    else "",

                "total_marks":
                    exam.total_marks

            })


    return result


@router.get("/teacher/{exam_id}")
def teacher_exam_detail(

    exam_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_exams"
        )
    )

):

    exam = db.query(Exam).filter(

        Exam.id == exam_id,

        Exam.school_id == current_user.school_id

    ).first()


    if not exam:
        raise HTTPException(
            status_code=404,
            detail="Exam not found"
        )


    subject = db.query(Subject).filter(
        Subject.id == exam.subject_id
    ).first()


    class_obj = db.query(Class).filter(
        Class.id == exam.class_id
    ).first()


    section_obj = db.query(Section).filter(
        Section.id == exam.section_id
    ).first()



    return {

        "id": exam.id,

        "title": exam.title,

        "subject_id": exam.subject_id,

        "subject":
            subject.name if subject else "",

        "class_id":
            exam.class_id,

        "class_name":
            class_obj.name if class_obj else "",

        "section_id":
            exam.section_id,

        "section_name":
            section_obj.name if section_obj else "",

        "total_marks":
            exam.total_marks

    }


@router.get("/teacher/{exam_id}/students")
def teacher_exam_students(

    exam_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_exams"
        )
    )

):


    exam = db.query(Exam).filter(

        Exam.id == exam_id,

        Exam.school_id == current_user.school_id

    ).first()


    if not exam:
        raise HTTPException(
            status_code=404,
            detail="Exam not found"
        )


    enrollments = db.query(Enrollment).filter(

        Enrollment.school_id ==
        current_user.school_id,

        Enrollment.class_id ==
        exam.class_id,

        Enrollment.section_id ==
        exam.section_id,

        Enrollment.status ==
        "active"

    ).all()



    students = []


    for enrollment in enrollments:


        student = db.query(Student).filter(

            Student.id ==
            enrollment.student_id

        ).first()


        if student:

            students.append({

                "enrollment_id":
                    enrollment.id,

                "student_id":
                    student.id,

                "student_name":
                    f"{student.first_name} {student.last_name}",

                "admission_number":
                    student.admission_number

            })


    return students


@router.get("/student/me")
def student_my_exams(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_exams"
        )
    )

):


    student = db.query(Student).filter(

        Student.school_id ==
        current_user.school_id,

        Student.user_id ==
        current_user.id

    ).first()



    if not student:

        return []



    enrollments = db.query(Enrollment).filter(

        Enrollment.school_id ==
        current_user.school_id,

        Enrollment.student_id ==
        student.id,

        Enrollment.status ==
        "active"

    ).all()



    exams = []



    for enrollment in enrollments:


        class_exams = db.query(Exam).filter(

            Exam.school_id ==
            current_user.school_id,

            Exam.class_id ==
            enrollment.class_id,

            Exam.section_id ==
            enrollment.section_id

        ).all()



        for exam in class_exams:


            subject = db.query(Subject).filter(

                Subject.id ==
                exam.subject_id

            ).first()



            class_obj = db.query(Class).filter(

                Class.id ==
                exam.class_id

            ).first()



            section_obj = db.query(Section).filter(

                Section.id ==
                exam.section_id

            ).first()



            exams.append({

                "id":
                    exam.id,


                "title":
                    exam.title,


                "subject":
                    subject.name
                    if subject
                    else "",


                "class_name":
                    class_obj.name
                    if class_obj
                    else "",


                "section_name":
                    section_obj.name
                    if section_obj
                    else "",


                "total_marks":
                    exam.total_marks

            })



    return exams








@router.get("/student/results")
def student_results(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("view_exams")
    )

):

    student = db.query(Student).filter(

        Student.user_id == current_user.id,

        Student.school_id == current_user.school_id

    ).first()


    if not student:
        return []


    results = db.query(Mark).filter(

        Mark.student_id == student.id,

        Mark.school_id == current_user.school_id

    ).all()


    return [
        {
            "id": mark.id,
            "exam_id": mark.exam_id,
            "subject_id": mark.subject_id,
            "obtained_marks": mark.obtained_marks,
            "total_marks": mark.total_marks
        }
        for mark in results
    ]

@router.get("/student/results")
def student_results(

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission("view_exams")
    )

):

    student = db.query(Student).filter(

        Student.school_id == current_user.school_id,

        Student.user_id == current_user.id

    ).first()


    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )


    enrollments = db.query(Enrollment).filter(

        Enrollment.school_id == current_user.school_id,

        Enrollment.student_id == student.id

    ).all()


    enrollment_ids = [
        e.id for e in enrollments
    ]


    marks = db.query(Mark).filter(

        Mark.school_id == current_user.school_id,

        Mark.enrollment_id.in_(enrollment_ids)

    ).all()


    results = []


    for mark in marks:

        subject = db.query(Subject).filter(
            Subject.id == mark.subject_id
        ).first()


        exam = db.query(Exam).filter(
            Exam.id == mark.exam_id
        ).first()


        results.append({

            "id": mark.id,

            "subject":
                subject.name
                if subject
                else "",

            "exam":
                exam.title
                if exam
                else "",

            "obtained_marks":
                mark.obtained_marks,

            "total_marks":
                mark.total_marks

        })


    return results

@router.get("/{exam_id}")
def get_exam(

    exam_id: int,

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "view_students"
        )
    )

):

    exam = db.query(
        Exam,
        Subject.name.label("subject_name")
    ).join(

        Subject,
        Subject.id == Exam.subject_id

    )

    exam = apply_tenant_filter(

        query=exam,

        model=Exam,

        current_user=current_user

    )

    exam = exam.filter(

        Exam.id == exam_id

    ).first()

    if not exam:

        raise HTTPException(
            status_code=404,
            detail="Exam not found"
        )

    exam_data, subject_name = exam

    return {

        "id": exam_data.id,

        "title": exam_data.title,

        "class_id": exam_data.class_id,

        "section_id": exam_data.section_id,

        "subject_id": exam_data.subject_id,

        "subject": subject_name,

        "total_marks": exam_data.total_marks

    }



