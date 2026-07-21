DEFAULT_PERMISSIONS = [

    "manage_students",
    "view_students",

    "manage_teachers",
    "view_teachers",

    "view_attendance",
    "mark_attendance",

    "manage_finance",
    "view_finance",

    "manage_exams",
    "view_exams",

    "manage_announcements"
]


DEFAULT_ROLES = {

    "principal": [

        "manage_students",
        "view_students",

        "manage_teachers",
        "view_teachers",

        
        "view_attendance",

        "manage_finance",
        "view_finance",

        "manage_exams",
        "view_exams",

        "manage_announcements"
    ],

    "teacher": [

        "view_students",

        "mark_attendance",
        "view_attendance",

        "view_exams"
    ],

    "accountant": [

        "manage_finance",
        "view_finance"
    ],

    "student": [

        "view_exams",
        "view_attendance",
        "view_finance"
    ],

    "parent": [

        "view_attendance",
        "view_exams"
    ]
}


from app.models.permission_model import Permission
from app.models.role_model import Role
from app.models.role_permission_model import RolePermission


def seed_rbac(db, school_id):

    permission_map = {}

    # CREATE GLOBAL PERMISSIONS
    for permission_name in DEFAULT_PERMISSIONS:

        existing_permission = db.query(
            Permission
        ).filter(
            Permission.name == permission_name
        ).first()

        if existing_permission:

            permission = existing_permission

        else:

            permission = Permission(
                name=permission_name
            )

            db.add(permission)
            db.commit()
            db.refresh(permission)

        permission_map[
            permission_name
        ] = permission

    # CREATE TENANT ROLES
    for role_name, permissions in DEFAULT_ROLES.items():

        existing_role = db.query(
            Role
        ).filter(

            Role.school_id == school_id,

            Role.name == role_name

        ).first()

        if existing_role:

            role = existing_role

        else:

            role = Role(

                school_id=school_id,

                name=role_name
            )

            db.add(role)

            db.commit()

            db.refresh(role)

        # ATTACH PERMISSIONS
        for permission_name in permissions:

            existing_mapping = db.query(
                RolePermission
            ).filter(

                RolePermission.role_id == role.id,

                RolePermission.permission_id ==
                permission_map[
                    permission_name
                ].id

            ).first()

            if not existing_mapping:

                role_permission = RolePermission(

                    role_id=role.id,

                    permission_id=
                    permission_map[
                        permission_name
                    ].id
                )

                db.add(role_permission)

    db.commit()

    print(
        f"RBAC seeded for school {school_id}"
    )