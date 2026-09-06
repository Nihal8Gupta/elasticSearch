from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    errors = response.data
    message = "Request failed."

    if isinstance(errors, dict):
        detail = errors.get("detail")
        if detail:
            message = str(detail)

    response.data = {
        "success": False,
        "message": message,
        "errors": errors,
    }
    return response
