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
    user = request.user
    sort_by = request.GET.get('sort_by', '-created_at')
    volunteer_id = request.GET.get('volunteer_id', str(request.user.id))  # 현재 로그인한 봉사자의 ID로 기본값 설정

    reports = Report.objects.all().order_by(sort_by)

    # user_type이 'VOLUNTEER'인 봉사자 목록을 가져옴
    volunteers = list(User.objects.filter(user_type='VOLUNTEER').exclude(id=request.user.id).order_by('username').values('id', 'username'))
    current_user = {'id': request.user.id, 'username': request.user.username}
    volunteers.insert(0, current_user)  # 현재 로그인한 사용자를 맨 앞에 추가

    reports = reports.filter(user_id=volunteer_id)
    print('리포트 개수: ', reports.count())
    print('리포트 id: ', reports.values_list('id', flat=True))

    seniors = Senior.objects.select_related('user_id').values('id', 'name', 'user_id', 'user_id__username')

    # 작성 예정 보고서 목록의 신청자 목록 가져오기
    unwritten_report_users = User.objects.filter(care__approved_by_id=volunteer_id, care__care_state='APPROVED').distinct().values('id', 'username')

    # 작성 완료 보고서 목록의 신청자 목록 가져오기
    written_report_users = User.objects.filter(care__approved_by_id=volunteer_id, care__care_state='COMPLETED').distinct().values('id', 'username')

    # 작성된 보고서를 위한 페이지네이션

    report_paginator = Paginator(reports, 5)
    report_page_number = request.GET.get('report_page')
    report_page_obj = report_paginator.get_page(report_page_number)

    # 작성해야할 보고서를 위한 페이지네이션
    pending_cares = Care.objects.filter(care_state='APPROVED').exclude(id__in=Report.objects.values('care_id')).order_by('-datetime')
    pending_paginator = Paginator(pending_cares, 5)
    pending_page_number = request.GET.get('pending_page')
    pending_page_obj = pending_paginator.get_page(pending_page_number)

    pending_reports_count = pending_cares.count()

    return render(request, 'management_app/volunteer_report_list.html', {

        'report_page_obj': report_page_obj,
        'pending_page_obj': pending_page_obj,
        'sort_by': sort_by,
        'seniors': seniors,
        'users': User.objects.all(),
        'pending_reports_count': pending_reports_count,
        'volunteers': volunteers,
        'unwritten_report_users': list(unwritten_report_users),
        'written_report_users': list(written_report_users),
    })

@login_required
@volunteer_required
def seniors_for_volunteer(request, volunteer_id):
    seniors = Senior.objects.filter(cares_seniors__report__user_id=volunteer_id).distinct().select_related('user_id').values('id', 'name', 'user_id', 'user_id__username')
    return JsonResponse({'seniors': list(seniors)})