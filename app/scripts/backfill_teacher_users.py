from app.database.database import SessionLocal
from app.models.teacher_model import Teacher
from app.models.user_model import User
from app.models.user_role_model import UserRole
from app.models.role_model import Role
from app.utils.hash import hash_password
import secrets


def run():

    db = SessionLocal()

    teachers = db.query(Teacher).all()

    teacher_role = db.query(Role).filter(
        Role.name == "teacher"
    ).first()

    for teacher in teachers:

        # SKIP IF ALREADY LINKED
        if teacher.user_id:
            continue

        # FIND OR CREATE USER
        user = db.query(User).filter(
            User.email == teacher.email
        ).first()

        temp_password = None

        if not user:

            temp_password = secrets.token_urlsafe(8)

            user = User(
                email=teacher.email,
                hashed_password=hash_password(temp_password),
                school_id=teacher.school_id,
                role="teacher",
                is_verified=True
            )

            db.add(user)
            db.flush()

            print(f"Created user: {teacher.email} | temp pass: {temp_password}")

        # LINK TEACHER
        teacher.user_id = user.id

        # ASSIGN ROLE (SAFE CHECK)
        if teacher_role:

            existing = db.query(UserRole).filter(
                UserRole.user_id == user.id,
                UserRole.role_id == teacher_role.id
            ).first()

            if not existing:
                db.add(UserRole(
                    user_id=user.id,
                    role_id=teacher_role.id
                ))

    db.commit()
    db.close()

    print("Teacher migration completed successfully")


if __name__ == "__main__":
    run()