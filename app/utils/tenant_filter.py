def apply_tenant_filter(

    query,

    model,

    current_user
):

    if current_user.role == "platform_admin":

        return query

    if hasattr(model, "school_id"):

        return query.filter(
            model.school_id ==
            current_user.school_id
        )

    return query