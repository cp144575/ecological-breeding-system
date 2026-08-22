"""牲畜模块 Django Admin：大类、区域、批次列表筛选与搜索字段配置。"""
from django.contrib import admin
from .models import LivestockCategory, LivestockArea, LivestockBatch

@admin.register(LivestockCategory)
class LivestockCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_code', 'standard_cycle')
    search_fields = ('name', 'category_code')

@admin.register(LivestockArea)
class LivestockAreaAdmin(admin.ModelAdmin):
    list_display = ('area_name', 'farmer', 'description')
    list_filter = ('farmer',)
    search_fields = ('area_name',)

@admin.register(LivestockBatch)
class LivestockBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_code', 'category', 'area', 'farmer', 'quantity', 'status')
    list_filter = ('status', 'category', 'area', 'farmer')
    search_fields = ('batch_code', 'breed')
