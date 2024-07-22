# from celery import Celery
# from celery.schedules import crontab
# from django.apps import apps

# app = Celery('config')

# @app.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     from django_celery_beat.models import PeriodicTask, CrontabSchedule
#     # 매일 자정마다 실행되는 작업 스케줄 설정
#     schedule, created = CrontabSchedule.objects.get_or_create(
#         minute='0',
#         hour='15',
#         day_of_week='*',
#         day_of_month='*',
#         month_of_year='*',
#         timezone='Asia/Seoul'
#     )

#     # 주기적으로 csv 생성
#     PeriodicTask.objects.get_or_create(
#         crontab=schedule,
#         name='my_task every midnight',
#         task='config.tasks.my_task',
#     )