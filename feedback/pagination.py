# Mayowa Obisesan
# OVERRIDE THE CURSOR PAGINATION CLASS TO SET IT'S ATTRIBUTES
# July 19, 2022.
from rest_framework import pagination


class NinePagination(pagination.CursorPagination):
    ordering = "created_at"
    cursor_query_param = 'cursor'
    cursor_query_description = 'Nine Pagination cursor value.'
    invalid_cursor_message = 'Invalid cursor'
