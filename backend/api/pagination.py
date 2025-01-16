from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import NotFound


class PageToOffsetPagination(LimitOffsetPagination):
    def get_offset(self, request):
        page = request.query_params.get('page', None)
        if page is not None:
            try:
                limit = int(request.query_params.get(
                    'limit', 6))
                offset = (int(page) - 1) * limit
                return offset
            except ValueError:
                raise NotFound("Invalid page parameter")
        return super().get_offset(request)
