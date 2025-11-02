from django.db import models
from django.conf import settings
class Task(models.Model):
 """Task model"""

 STATUS_CHOICES = [
 ('todo', 'To Do'),
 ('in_progress', 'In Progress'),
 ('review', 'Review'),
 ('done', 'Done'),
 ]

 PRIORITY_CHOICES = [
 ('low', 'Low'),
 ('medium', 'Medium'),
 ('high', 'High'),
 ('urgent', 'Urgent'),
 ]

 title = models.CharField(max_length=200)
 description = models.TextField(blank=True)
 status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
 priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

 project = models.ForeignKey(
 'projects.Project',
 on_delete=models.CASCADE,
 related_name='tasks'
 )
 assignee = models.ForeignKey(
 settings.AUTH_USER_MODEL,
 on_delete=models.SET_NULL,
 null=True,
 blank=True,
 related_name='assigned_tasks'
 )
 created_by = models.ForeignKey(
 settings.AUTH_USER_MODEL,
 on_delete=models.CASCADE,
 related_name='created_tasks'
 )

 deadline = models.DateTimeField(null=True, blank=True)
 created_at = models.DateTimeField(auto_now_add=True)
 updated_at = models.DateTimeField(auto_now=True)

 def __str__(self):
     return self.title

 class Meta:
     db_table = 'tasks'
     ordering = ['-created_at']

 indexes = [
 models.Index(fields=['status', 'priority']),
 models.Index(fields=['project', 'status']),
 ]
class TaskHistory(models.Model):
 """Task history model for tracking changes"""
 task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
 changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
 field_name = models.CharField(max_length=100)
 old_value = models.TextField(blank=True)
 new_value = models.TextField(blank=True)
 changed_at = models.DateTimeField(auto_now_add=True)

 class Meta:
     db_table = 'task_history'
     ordering = ['-changed_at']
