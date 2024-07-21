from django.shortcuts import render, reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.dispatch import receiver
from django.db.models import Max

from monitoring_app.signals import my_signal
from management_app.models import Care, Senior, Report, ReportImage
from auth_app.models import User

# 시그널을 받았는지 여부를 저장할 변수
signal_received = False
   
def family_monitor(request):
    user = User.objects.get(email=request.user.email)
    if user.user_type == '':
        user.user_type = 'FAMILY'
        user.save()
        
    
    sort_by = request.GET.get("sort_by", "datetime")
    order = request.GET.get("order", "asc")
    selected_senior_id = request.GET.get('selected_senior_id', '')
    selected_care_state = request.GET.get('care_state', '')
    selected_order = request.GET.get('order', 'desc')
   
    # 현재 로그인한 사용자의 ID
    user_id = request.user.id
   
    if order == "desc":
        sort_by = "-" + sort_by
   
    # 현재 로그인한 사용자의 Care 객체만 필터링
    cares = Care.objects.filter(user_id=user_id)
   
    if selected_senior_id:
        cares = cares.filter(seniors__id=selected_senior_id)
    if selected_care_state:
        cares = cares.filter(care_state=selected_care_state)
    if selected_order == 'asc':
        cares = cares.order_by('datetime')
    else:
        cares = cares.order_by('-datetime')
    seniors = Senior.objects.filter(user_id=user_id)
   
    cares = cares.order_by(sort_by)
    users = User.objects.all()  # 모든 사용자 정보 가져오기

    selected_senior = None
    if selected_senior_id:
        selected_senior = Senior.objects.get(id=selected_senior_id)
   
    reports = Report.objects.filter(care__in=cares)
    sorted_reports = reports.order_by('-created_at')  # created_at 등 원하는 필드로 정렬
    last_report = sorted_reports.first()  # 가장 마지막 report 가져오기
    sorted_cares = cares.order_by('-datetime')
    
    latest_date = sorted_cares.aggregate(latest_date=Max('datetime__date'))['latest_date']
    sorted_cares_latest = sorted_cares.filter(datetime__date=latest_date)
    recent_not_approved_care = Care.objects.filter(seniors=selected_senior, care_state='NOT_APPROVED').order_by('-datetime').first()

    
    context = {
        "cares" : cares,
        "sorted_cares_latest": sorted_cares_latest,
        "users": users,
        "selected_user": user_id,
        'selected_senior_id': selected_senior_id,
        'selected_care_state': selected_care_state,
        'selected_order': selected_order,
        "seniors": seniors,
        "selected_senior": selected_senior,
        "reports" : sorted_reports,
        "recent_not_approved_care" : recent_not_approved_care,
        "last_report" : last_report,
    }
    
    return render(request, "monitoring_app/family_monitor.html", context)

def family_monitor_image(request,report_id):
    reports = Report.objects.filter(id=report_id)
    context = {"reports":reports}
    
    return render(request, "monitoring_app/care_image.html", context)

care = None
# 시그널을 받았을 때 처리할 함수
@receiver(my_signal)
def handle_my_signal(sender, **kwargs):
    global signal_received
    signal_received = True
    global care
    care = sender
    
# 시그널 수신 여부를 체크하는 view
@csrf_exempt
def poll_signal(request):
    global signal_received
    if request.method == 'GET':
        response = {'signal_received': signal_received}
        if signal_received:
            
            # 본인이 요청한 케어인지 확인
            if request.user == care.user_id:
                print('request', request.user)
                print('care', care.user_id)
                print(care.seniors.all())
                response = {'signal_received': signal_received,
                            'username': care.user_id.username,
                            'seniorname': care.seniors.all()[0].name,
                            'state': care.care_state,
                            'visit_date': care.visit_date,
                            'visit_time': care.visit_time}
            # 시그널을 처리한 후 다시 초기화
            signal_received = False
        return JsonResponse(response)
