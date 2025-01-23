from rest_framework.pagination import LimitOffsetPagination


class PageToOffsetPagination(LimitOffsetPagination):
    page_size = 6

    def get_offset(self, request):
        page = request.query_params.get('page')
        if page:
            page = int(page) - 1
            return page * self.page_size
        return super().get_offset(request)
