import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from .models import Task
from .serializers import TaskSerializer, TaskImportSerializer
from .tasks import process_csv_import
class TaskViewSet(viewsets.ModelViewSet):
 queryset = Task.objects.all()
 serializer_class = TaskSerializer

 def perform_create(self, serializer):
 serializer.save(created_by=self.request.user)

 @action(detail=False, methods=['post'])
 def import_csv(self, request):
 """
 Асинхронний імпорт завдань з CSV

 POST /api/tasks/import_csv/
 Body: multipart/form-data
 - file: CSV file
 - project: Project ID
 """
 serializer = TaskImportSerializer(data=request.data)
 serializer.is_valid(raise_exception=True)

 file = serializer.validated_data['file']
 project_id = serializer.validated_data['project']

 # Зберегти файл тимчасово
 file_path = default_storage.save(f'tmp/{file.name}', file)
 full_path = default_storage.path(file_path)

 # Запустити Celery task
 task = process_csv_import.delay(
 full_path,
 project_id,
 request.user.id
 )

 return Response({
 'task_id': task.id,
 'status': 'processing',
 'message': 'CSV import started'
 }, status=status.HTTP_202_ACCEPTED)

 @action(detail=False, methods=['get'])
 def import_status(self, request):
 """Перевірити статус імпорту"""
 task_id = request.query_params.get('task_id')

 if not task_id:
 return Response(
 {'error': 'task_id is required'},
 status=status.HTTP_400_BAD_REQUEST
 )

 from celery.result import AsyncResult
 task_result = AsyncResult(task_id)

 response = {
 'task_id': task_id,
 'status': task_result.status,
 }

 if task_result.status == 'PROGRESS':
 response['progress'] = task_result.info
 elif task_result.status == 'SUCCESS':
 response['result'] = task_result.result
 elif task_result.status == 'FAILURE':
 response['error'] = str(task_result.info)

 return Response(response)