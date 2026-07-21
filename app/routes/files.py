from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

from sqlalchemy.orm import Session

from uuid import uuid4

import shutil
import os

from app.database.database import get_db

from app.dependencies.permission_dependencies import (
    require_permission
)

from app.core.query import apply_tenant_filter


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload")
def upload_file(

    uploaded_file: UploadFile = File(...),

    db: Session = Depends(get_db),

    current_user=Depends(
        require_permission(
            "manage_students"
        )
    )

):

    file_extension = uploaded_file.filename.split(".")[-1]

    filename = f"{uuid4()}.{file_extension}"

    # ✅ tenant-aware folder structure (important upgrade)
    tenant_folder = (
        "platform"
        if current_user.role == "platform_admin"
        else str(current_user.school_id)
    )

    tenant_dir = os.path.join(UPLOAD_DIR, tenant_folder)

    if not os.path.exists(tenant_dir):
        os.makedirs(tenant_dir)

    file_path = os.path.join(tenant_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            uploaded_file.file,
            buffer
        )

    return {

        "message": "File uploaded",

        "file_url": file_path,

        "school_id": current_user.school_id,

        "uploaded_by": current_user.id
    }