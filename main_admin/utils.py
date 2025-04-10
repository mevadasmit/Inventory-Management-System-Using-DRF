from rest_framework.response import Response
from rest_framework import status

def success_response(message, data=None, status_code=status.HTTP_200_OK):
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return Response(response, status=status_code)

def error_response(errors, message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"error": errors, "message": message}, status=status_code)

def delete_response(message, status_code=status.HTTP_200_OK):
    return Response({"message": message}, status=status_code)
