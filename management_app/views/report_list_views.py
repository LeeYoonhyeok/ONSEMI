from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from auth_app.utils import volunteer_required
from django.core.paginator import Paginator
from management_app.models import Report, Care, Senior
from auth_app.models import User
from django.http import JsonResponse

@login_required
@volunteer_required
def report_list(request):
    volunteer_id = str(request.user.id)
    
    # GET 방식 : 작성 예정 보고서와 작성 완료 보고서 출력
    if request.method == 'GET':
        pending_cares = Care.objects.filter(care_state='APPROVED',
                                            approved_by=volunteer_id).order_by('-datetime')
        
        reports = Report.objects.filter(care__approved_by_id=volunteer_id).order_by('-updated_at')
    
    # POST 방식 : 보고서 목록 필터링 하여 출력
    else:

        # 작성 예정 보고서 필터링
        type_pending = request.POST.get('type_pending')     # 케어 타입
        order_pending = request.POST.get('order_pending')   # 정렬 방법
        pending_report_user = request.POST.get('pending_report_user') # 케어 요청자

        # 케어 타입만 전체 조회한 경우
        if type_pending == 'total' and pending_report_user != 'total':
            pending_cares = Care.objects.filter(care_state='APPROVED', approved_by=volunteer_id, 
                                                user_id=pending_report_user)
        
        # 케어 요청자만 전체 조회한 경우    
        elif type_pending != 'total' and pending_report_user == 'total':
            pending_cares = Care.objects.filter(care_state='APPROVED', approved_by=volunteer_id,
                                                care_type=type_pending)
        
        # 케어 요청자, 케어 타입 모두 전체 조회한 경우
        elif type_pending == 'total' and pending_report_user == 'total':
            pending_cares = Care.objects.filter(care_state='APPROVED',approved_by=volunteer_id)
        
        try:  
            pending_cares = pending_cares.order_by(order_pending)  # 필터링한 값 정렬
        except:
            pending_cares = Care.objects.filter(care_state='APPROVED',
                                                approved_by=volunteer_id).order_by('-datetime')  # APPROVED에서 적용하기를 눌렀다면 아무작업도 안함

        # 작성 완료 보고서 필터링
        type_submitted = request.POST.get('type_submitted')     # 케어 타입
        order_submitted = request.POST.get('order_submitted')   # 정렬 방법
        submitted_report_user = request.POST.get('submitted_report_user') # 케어 요청자

        # 케어 타입만 전체 조회한 경우
        if type_submitted == 'total' and submitted_report_user != 'total':
            reports = Report.objects.filter(care__approved_by_id=volunteer_id, 
                                                user__id=submitted_report_user)
        
        # 케어 요청자만 전체 조회한 경우    
        elif type_submitted != 'total' and submitted_report_user == 'total':
            reports = Report.objects.filter(care__approved_by_id=volunteer_id,
                                                care__care_type=type_submitted)
        
        # 케어 요청자, 케어 타입 모두 전체 조회한 경우
        elif type_submitted == 'total' and submitted_report_user == 'total':
            reports = Report.objects.filter(care__approved_by_id=volunteer_id)
        
        try:  
            reports = reports.order_by(order_submitted)  # 필터링한 값 정렬
        except:
            reports = Report.objects.filter(care__approved_by_id=volunteer_id).order_by('-updated_at')  # APPROVED에서 적용하기를 눌렀다면 아무작업도 안함

    # 작성 예정 보고서의 정렬 항목인 신청자 초기 value 설정
    pending_report_users = User.objects.filter(care__approved_by_id=volunteer_id, care__care_state='APPROVED').distinct().values('id', 'username')

    # 작성 완료 보고서의 정렬 항목인 신청자 초기 value 설정
    submitted_report_users = User.objects.filter(care__approved_by_id=volunteer_id, care__care_state='COMPLETED').distinct().values('id', 'username')


    # 작성 예정 보고서를 위한 페이지네이션

    pending_paginator = Paginator(pending_cares, 5)
    pending_page_number = request.GET.get('pending_page')
    pending_page_obj = pending_paginator.get_page(pending_page_number)

    pending_reports_count = pending_cares.count()


    # 작성 완료 보고서를 위한 페이지네이션

    report_paginator = Paginator(reports, 5)
    report_page_number = request.GET.get('report_page')
    report_page_obj = report_paginator.get_page(report_page_number)

    context = {
        'report_page_obj': report_page_obj,
        'pending_page_obj': pending_page_obj,
        'pending_reports_count': pending_reports_count,
        'pending_report_users': list(pending_report_users),
        'submitted_report_users': list(submitted_report_users),
    }


    return render(request, 'management_app/volunteer_report_list.html', context)

@login_required
@volunteer_required
def seniors_for_volunteer(request, volunteer_id):
    seniors = Senior.objects.filter(cares_seniors__report__user_id=volunteer_id).distinct().select_related('user_id').values('id', 'name', 'user_id', 'user_id__username')
    return JsonResponse({'seniors': list(seniors)})