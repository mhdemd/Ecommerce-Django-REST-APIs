from rest_framework.pagination import LimitOffsetPagination


class NoCountPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return {
            "results": data,
            "previous": self.get_previous_link(),
            "next": self.get_next_link(),
        }

    def paginate_queryset(self, queryset, request, view=None):
        # Calculate pagination without counting the total number of records
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request
        return list(queryset[self.offset : self.offset + self.limit])
