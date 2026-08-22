"""
REST 分页 — ``StandardPagination``
==================================

在 ``settings.REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS']`` 中注册；
前端统一使用 ``page``、``page_size`` 查询参数，响应含 ``count`` / ``total_pages`` / ``results``。
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardPagination(PageNumberPagination):
    """
    标准分页器
    支持参数：
    - page: 当前页码
    - page_size: 每页显示数量
    """
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        自定义返回结构
        """
        return Response({
            'count': self.page.paginator.count, # 总条数
            'total_pages': self.page.paginator.num_pages, # 总页数
            'current_page': self.page.number, # 当前页
            'page_size': self.get_page_size(self.request), # 每页大小
            'results': data # 结果列表
        })
