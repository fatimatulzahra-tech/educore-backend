from contextvars import ContextVar

current_school_id = ContextVar("current_school_id", default=None)


def set_school_id(school_id: int):
    current_school_id.set(school_id)


def get_school_id():
    return current_school_id.get()