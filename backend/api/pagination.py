from rest_framework.pagination import LimitOffsetPagination


class PageToOffsetPagination(LimitOffsetPagination):
    page_size = 6
    page_size_query_param = 'page'
