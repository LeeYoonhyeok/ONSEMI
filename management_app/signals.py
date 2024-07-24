from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from management_app.models import Report

# Report가 생성될 때 care_status를 'COMPLETED'로 변경하는 시그널
@receiver(post_save, sender=Report)
def update_care_status_on_report_create(sender, instance, created, **kwargs):
    if created:
        care = instance.care
        care.care_state = 'COMPLETED'
        care.save()

# Report가 삭제될 때 care_status를 'APPROVED'로 변경하는 시그널
@receiver(post_delete, sender=Report)
def update_care_status_on_report_delete(sender, instance, **kwargs):
    care = instance.care
    care.care_state = 'APPROVED'
    care.save()