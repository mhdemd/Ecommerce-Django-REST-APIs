from rest_framework.pagination import PageNumberPagination


# Remove __count from pagination queryset
class NoCountPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return {
            "results": data,
            "previous": self.get_previous_link(),
            "next": self.get_next_link(),
        }

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_page_size(request)
        self.offset = self.get_offset(request)
        self.request = request
        return list(queryset[self.offset : self.offset + self.limit])
