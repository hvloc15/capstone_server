from rest_framework.exceptions import status
from rest_framework.response import Response


class ExceptionHandlerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self,request, exception):
        status_code = status.HTTP_400_BAD_REQUEST
        if hasattr(exception, 'status_code'):
            status_code = exception.status_code

        return Response({"status":status_code,"message": exception}, status.HTTP_200_OK)
