import os
from celery import Celery
from celery.schedules import crontab
# Встановити Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
# Завантажити конфігурацію з Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')
# Автоматично знаходити tasks.py в apps
app.autodiscover_tasks()
# Конфігурація Celery Beat (періодичні задачі)
app.conf.beat_schedule = {
 'send-daily-report': {
 'task': 'apps.tasks.tasks.send_daily_report',
 'schedule': crontab(hour=9, minute=0), # Щодня о 9:00
 },
 'cleanup-old-tasks': {
 'task': 'apps.tasks.tasks.cleanup_old_tasks',
 'schedule': crontab(hour=2, minute=0), # Щодня о 2:00
 },
 'check-deadlines': {
 'task': 'apps.tasks.tasks.check_deadlines',
 'schedule': crontab(minute='*/30'), # Кожні 30 хвилин
 },
 'generate-analytics': {
 'task': 'apps.tasks.tasks.generate_analytics',
 'schedule': crontab(hour=0, minute=0), # Щодня о 00:00
 },
}
@app.task(bind=True, ignore_result=True)
def debug_task(self):
 """Debug task для тестування Celery"""
 print(f'Request: {self.request!r}')