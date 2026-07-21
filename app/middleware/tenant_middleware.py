from starlette.middleware.base import BaseHTTPMiddleware
from app.core.tenant_context import set_school_id
from app.utils.jwt import decode_token


class TenantMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        try:
            auth = request.headers.get("authorization")

            if auth and "Bearer" in auth:

                token = auth.split(" ")[1]
                payload = decode_token(token)

                school_id = payload.get("school_id")

                if school_id:
                    set_school_id(school_id)

        except Exception:
            pass

        response = await call_next(request)
        return response