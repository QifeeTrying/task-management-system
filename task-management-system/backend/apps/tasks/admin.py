from django.contrib import admin
from .models import Task, TaskHistory
class TaskHistoryInline(admin.TabularInline):
 model = TaskHistory
 extra = 0
 readonly_fields = ['changed_by', 'field_name', 'old_value', 'new_value', 'changed_at']
 can_delete = False
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
 list_display = ['title', 'status', 'priority', 'project', 'assignee', 'deadline']
 list_filter = ['status', 'priority', 'created_at']
 search_fields = ['title', 'description']
 raw_id_fields = ['project', 'assignee', 'created_by']
 date_hierarchy = 'created_at'
 inlines = [TaskHistoryInline]

 fieldsets = (
 ('Basic Info', {
 'fields': ('title', 'description', 'project')
 }),
 ('Status & Priority', {
 'fields': ('status', 'priority')
 }),
 ('Assignment', {
 'fields': ('assignee', 'created_by', 'deadline')
 }),
 )
