from django.db import models
from django.conf import settings
from auth_app.models import User
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os
from datetime import date
from django.contrib.auth import get_user_model

class Senior(models.Model):
    id = models.AutoField(primary_key=True)
    postcode = models.CharField(max_length=255, default=" ")
    address = models.CharField(max_length=255)
    detail_address = models.CharField(max_length=255, default=" ")
    name = models.CharField(max_length=100)
    birthdate = models.DateField(default=date(1900, 1, 1))
    gender = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    has_alzheimers = models.BooleanField(default=False, null=True, blank=True)
    has_parkinsons = models.BooleanField(default=False, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    photo = models.ImageField(upload_to='senior_photos/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "senior"


User = get_user_model()

class Care(models.Model):
    care_type = models.CharField(max_length=100)  # SHOP, VISIT
    parkinson_diagnosis = models.BooleanField(default=False)
    datetime = models.DateTimeField(default=timezone.now)
    visit_date = models.DateField(null=True, blank=True)
    visit_time = models.TimeField(null=True, blank=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    seniors = models.ManyToManyField("Senior", related_name="cares_seniors")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="cares_approved")

    CARE_STATE_CHOICES = [
        ('NOT_APPROVED', '요청 승인 대기'),
        ('COMPLETED', '요청 처리 완료'),
        ('APPROVED', '요청 승인 완료'),
        ('REJECT', '요청 거절'),
    ]

    care_state = models.CharField(
        max_length=50, default="NOT_APPROVED",  choices=CARE_STATE_CHOICES
    )
    admin_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.care_type

    class Meta:
        db_table = "care"
        
        
        

def upload_to(instance, filename):
    today = datetime.today().strftime('%Y%m%d')
    base_filename = os.path.splitext(filename)[0]
    extension = filename.split('.')[-1]
    new_filename = f"{base_filename}_{today}.{extension}"
    return os.path.join(f'volunteer_report/{instance.report.user.id}/{instance.report.care.id}/image', new_filename)



class Report(models.Model):
    care = models.ForeignKey(Care, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='미등록')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    audio_test_result = models.CharField(max_length=255, default='결과 분석 중입니다.')

    # 이상 부위 정보 필드 추가
    no_issue = models.BooleanField(default=False)
    eye = models.BooleanField(default=False)
    teeth = models.BooleanField(default=False)
    skin = models.BooleanField(default=False)
    back = models.BooleanField(default=False)
    other = models.BooleanField(default=False)
    other_text = models.CharField(max_length=255, blank=True, null=True)
    doctor_opinion = models.TextField(blank=True, null=True)
    user_request = models.TextField(blank=True, null=True)

    # # 이미지 파일 필드 추가
    # images = models.ImageField(upload_to=upload_to, blank=True, null=True)

    def __str__(self):
        return f"Report for Care ID {self.care.id}"

class ReportImage(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)

    def __str__(self):
        return f"Image for Report ID {self.report.id}"

    class Meta:
        db_table = "report_image"


# Report가 생성될 때 care_status를 'COMPLETED'로 변경하는 시그널
@receiver(post_save, sender=Report)
def update_care_status_on_report_create(sender, instance, created, **kwargs):
    if created:
        care = instance.care
        care.care_state = 'COMPLETED'
        care.save()


# Report가 삭제될 때 care_status를 'APPROVED'로 변경하는 시그널
@receiver(models.signals.post_delete, sender=Report)
def update_care_status_on_report_delete(sender, instance, **kwargs):
    care = instance.care
    care.care_state = 'APPROVED'
    care.save()

