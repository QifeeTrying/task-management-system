from rest_framework import serializers
from .models import Task, TaskHistory
class TaskSerializer(serializers.ModelSerializer):
 class Meta:
 model = Task
 fields = [
 'id', 'title', 'description', 'status', 'priority',
 'project', 'assignee', 'created_by', 'deadline',
 'created_at', 'updated_at'
 ]
 read_only_fields = ['created_by', 'created_at', 'updated_at']
class TaskImportSerializer(serializers.Serializer):
 file = serializers.FileField()
 project = serializers.IntegerField()