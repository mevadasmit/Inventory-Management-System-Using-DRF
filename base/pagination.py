from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

class MyLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5

    def get_paginated_response(self, data):
        view = self.request.parser_context.get('view')
        message = getattr(view, 'pagination_message', "Data retrieved successfully.")

        return Response({
            "message": message,
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "data": data
        })
