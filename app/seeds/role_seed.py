from sqlalchemy.orm import Session

from app.models.role_model import Role


def seed_roles(db: Session):

    roles = [

        "platform_admin",

        "principal",

        "teacher",

        "student",

        "parent",

        "accountant"
    ]

    for role_name in roles:

        normalized_role = (
            role_name
            .strip()
            .lower()
        )

        existing_role = db.query(
            Role
        ).filter(
            Role.name == normalized_role
        ).first()

        if not existing_role:

            role = Role(
                name=normalized_role
            )

            db.add(role)

    db.commit()

    print(
        "Roles seeded successfully"
    )