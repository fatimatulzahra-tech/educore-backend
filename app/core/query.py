from app.core.tenant_context import get_school_id


def apply_tenant_filter(

    query,

    model,

    current_user

):

    role = getattr(
        current_user,
        "role",
        None
    )


    # PLATFORM ADMIN
    if role == "platform_admin":

        return query


    # PRINCIPAL
    if role == "principal":

        return query.filter(

            model.school_id ==

            current_user.school_id

        )


    # TEACHER
    if role == "teacher":

        return query.filter(

            model.school_id ==

            current_user.school_id

        )


    # STUDENT
    if role == "student":

        return query.filter(

            model.id ==

            current_user.student_id

        )


    # PARENT
    if role == "parent":

        return query.filter(

            model.parent_id ==

            current_user.id

        )


    # DEFAULT
    return query.filter(

        model.school_id ==

        current_user.school_id

    )