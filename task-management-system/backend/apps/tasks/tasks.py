import csv
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q
from celery import shared_task
from .models import Task, TaskHistory
from apps.projects.models import Project
from apps.users.models import User
logger = logging.getLogger(__name__)
@shared_task(bind=True, max_retries=3)
def send_daily_report(self):
 """Відправити щоденний звіт по email всім користувачам"""
 try:
 users = User.objects.filter(is_active=True)

 for user in users:
 # Статистика для користувача
 tasks_assigned = Task.objects.filter(assignee=user)
 tasks_todo = tasks_assigned.filter(status='todo').count()
 tasks_in_progress = tasks_assigned.filter(status='in_progress').count()
 tasks_done = tasks_assigned.filter(status='done').count()

 # Прострочені завдання
 overdue_tasks = tasks_assigned.filter(
 deadline__lt=timezone.now(),
 status__in=['todo', 'in_progress']
 ).count()

 # Формування email
 subject = f'Daily Report - {timezone.now().date()}'
 message = f"""
 Hi {user.username},

 Your daily task summary:
 - To Do: {tasks_todo}
 - In Progress: {tasks_in_progress}
 - Done: {tasks_done}
 - Overdue: {overdue_tasks}

 Total assigned tasks: {tasks_assigned.count()}

 Have a productive day!
 """

 send_mail(
 subject,
 message,
 settings.DEFAULT_FROM_EMAIL,
 [user.email],
 fail_silently=False,
 )

 logger.info(f'Daily report sent to {user.email}')

 return f'Daily reports sent to {users.count()} users'

 except Exception as exc:
 logger.error(f'Error sending daily report: {exc}')
 raise self.retry(exc=exc, countdown=60)
@shared_task(bind=True, max_retries=3)
def process_csv_import(self, file_path, project_id, user_id):
 """
 Асинхронний імпорт завдань з CSV файлу

 CSV format:
 title,description,status,priority,assignee_email,deadline
 """
 try:
 project = Project.objects.get(id=project_id)
 created_by = User.objects.get(id=user_id)

 tasks_created = 0
 tasks_failed = 0
 errors = []

 with open(file_path, 'r', encoding='utf-8') as csvfile:
 reader = csv.DictReader(csvfile)
 total_rows = sum(1 for row in reader)
 csvfile.seek(0)
 reader = csv.DictReader(csvfile)

 for idx, row in enumerate(reader, 1):
 try:
 # Знайти assignee
 assignee = None
 if row.get('assignee_email'):
 assignee = User.objects.filter(
 email=row['assignee_email']
 ).first()

 # Парсинг deadline
 deadline = None
 if row.get('deadline'):
 from django.utils.dateparse import parse_datetime
 deadline = parse_datetime(row['deadline'])

 # Створити завдання
 task = Task.objects.create(
 title=row['title'],
 description=row.get('description', ''),
 status=row.get('status', 'todo'),
 priority=row.get('priority', 'medium'),
 project=project,
 assignee=assignee,
 created_by=created_by,
 deadline=deadline,
 )
 tasks_created += 1

 # Оновити прогрес
 self.update_state(
 state='PROGRESS',
 meta={'current': idx, 'total': total_rows}
 )

 except Exception as e:
 tasks_failed += 1
 errors.append(f"Row {idx}: {str(e)}")
 logger.error(f"Error importing row {idx}: {e}")

 result = {
 'tasks_created': tasks_created,
 'tasks_failed': tasks_failed,
 'errors': errors[:10] # Перші 10 помилок
 }

 logger.info(f'CSV import completed: {result}')
 return result

 except Exception as exc:
 logger.error(f'Error processing CSV import: {exc}')
 raise self.retry(exc=exc, countdown=60)
@shared_task
def cleanup_old_tasks():
 """Архівувати або видаляти старі завдання"""
 try:
 # Видалити done завдання старше 90 днів
 cutoff_date = timezone.now() - timedelta(days=90)

 old_tasks = Task.objects.filter(
 status='done',
 updated_at__lt=cutoff_date
 )

 count = old_tasks.count()

 # Можна додати архівацію перед видаленням
 # for task in old_tasks:
 # archive_task(task)

 old_tasks.delete()

 logger.info(f'Cleaned up {count} old tasks')
 return f'Deleted {count} old tasks'

 except Exception as e:
 logger.error(f'Error cleaning up old tasks: {e}')
 raise
@shared_task
def check_deadlines():
 """Перевірити дедлайни та відправити нагадування"""
 try:
 # Завдання з дедлайном в наступні 24 години
 tomorrow = timezone.now() + timedelta(hours=24)

 upcoming_tasks = Task.objects.filter(
 deadline__lte=tomorrow,
 deadline__gte=timezone.now(),
 status__in=['todo', 'in_progress']
 ).select_related('assignee', 'project')

 notifications_sent = 0

 for task in upcoming_tasks:
 if task.assignee and task.assignee.email:
 hours_left = (task.deadline - timezone.now()).total_seconds() / 3600

 subject = f'Deadline approaching: {task.title}'
 message = f"""
 Hi {task.assignee.username},

 Task "{task.title}" has a deadline in {hours_left:.1f} hours.

 Project: {task.project.name}
 Status: {task.get_status_display()}
 Priority: {task.get_priority_display()}
 Deadline: {task.deadline}

 Please complete it on time!
 """

 send_mail(
 subject,
 message,
 settings.DEFAULT_FROM_EMAIL,
 [task.assignee.email],
 fail_silently=True,
 )

 notifications_sent += 1

 logger.info(f'Sent {notifications_sent} deadline notifications')
 return f'Sent {notifications_sent} notifications'

 except Exception as e:
 logger.error(f'Error checking deadlines: {e}')
 raise
@shared_task
def generate_analytics():
 """Генерувати складну аналітику та статистику"""
 try:
 # Статистика по проектах
 projects_stats = []

 for project in Project.objects.all():
 tasks = Task.objects.filter(project=project)

 stats = {
 'project_id': project.id,
 'project_name': project.name,
 'total_tasks': tasks.count(),
 'completed_tasks': tasks.filter(status='done').count(),
 'in_progress_tasks': tasks.filter(status='in_progress').count(),
 'overdue_tasks': tasks.filter(
 deadline__lt=timezone.now(),
 status__in=['todo', 'in_progress']
 ).count(),
 }

 # Completion rate
 if stats['total_tasks'] > 0:
 stats['completion_rate'] = (
 stats['completed_tasks'] / stats['total_tasks'] * 100
 )
 else:
 stats['completion_rate'] = 0

 projects_stats.append(stats)

 # Зберегти статистику (можна додати окрему модель Analytics)
 # Analytics.objects.create(date=timezone.now().date(), data=projects_stats)

 logger.info(f'Generated analytics for {len(projects_stats)} projects')
 return {'projects': len(projects_stats), 'stats': projects_stats}

 except Exception as e:
 logger.error(f'Error generating analytics: {e}')
 raise
@shared_task(bind=True)
def test_celery(self):
 """Тестова задача для перевірки Celery"""
 logger.info('Test task executed successfully')
 return 'Celery is working!'
