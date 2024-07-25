from django.shortcuts import render, redirect, get_object_or_404
from management_app.models import Care
from auth_app.models import User
from django.contrib.auth.decorators import login_required
from auth_app.utils import volunteer_required
from monitoring_app.signals import my_signal
from django.core.paginator import Paginator


# 케어 목록(요청 승인 대기, 요청 승인 완료) 불러오기
@login_required
@volunteer_required
def care_list(request):
    not_approved_users = User.objects.filter(user_type='FAMILY',
                                             care__care_state="NOT_APPROVED").distinct().values('id','username')         # 보호자 목록 불러오기    
    
    approved_users = User.objects.filter(care__approved_by=request.user.id,
                                         care__care_state="APPROVED").distinct().values('id','username')       # 해당 봉사자가 승인한 케어 목록 불러오기

    # GET 방식: 케어목록 전체 출력
    if request.method == 'GET':
        not_approved_cares = Care.objects.filter(care_state='NOT_APPROVED').order_by('datetime')  # 요청 승인 대기 케어 불러오기
        
        approved_cares = Care.objects.filter(care_state='APPROVED',
                                              approved_by=request.user).order_by('datetime')  # 요청 승인 완료 케어 불러오기
        
    # POST 방식: 케어목록 필터링하여 출력
    else:
        
        # NOT_APPROVED 상태 케어 필터링 값 불러오기
        type_pending = request.POST.get('type_pending')     # 케어 타입
        order_pending = request.POST.get('order_pending')   # 정렬 방법
        user_pending = request.POST.get('user_pending')     # 케어 요청자
        
        # 케어 타입만 전체 조회한 경우
        if type_pending == 'total' and user_pending != 'total':
            not_approved_cares = Care.objects.filter(care_state='NOT_APPROVED',
                                                     user_id=user_pending)
        
        # 케어 요청자만 전체 조회한 경우    
        elif type_pending != 'total' and user_pending == 'total':
            not_approved_cares = Care.objects.filter(care_state='NOT_APPROVED', 
                                                     care_type=type_pending)
        
        # 케어 요청자, 케어 타입 모두 전체 조회한 경우
        elif type_pending == 'total' and user_pending == 'total':
            not_approved_cares = Care.objects.filter(care_state='NOT_APPROVED')
        
        try:  
            not_approved_cares = not_approved_cares.order_by(order_pending)  # 필터링한 값 정렬
        except:
            not_approved_cares = Care.objects.filter(care_state='NOT_APPROVED').order_by('datetime')  # APPROVED에서 적용하기를 눌렀다면 아무작업도 안함
        
        
        # APPROVED 상태 케어 필터링 값 불러오기
        type_pending_approved = request.POST.get('type_pending_approved')
        order_approved = request.POST.get('order_approved')
        user_approved = request.POST.get('user_approved')
        
        if type_pending_approved == 'total' and user_approved != 'total':
            approved_cares = Care.objects.filter(care_state='APPROVED',
                                                 user_id=user_approved,
                                                 approved_by=request.user)
            
        elif type_pending_approved != 'total' and user_approved == 'total':
            approved_cares = Care.objects.filter(care_state='APPROVED',
                                                 care_type=type_pending_approved,
                                                 approved_by=request.user)
            
        elif type_pending_approved == 'total' and user_approved == 'total':
            approved_cares = Care.objects.filter(care_state='APPROVED', 
                                                 approved_by=request.user)
        
        try:
            approved_cares = approved_cares.order_by(order_approved)
            
        except:
            approved_cares = Care.objects.filter(care_state='APPROVED', 
                                                 approved_by=request.user)
        
    # 페이지네이션 설정
    paginator1 = Paginator(not_approved_cares, 5)   # 상태가 NOT_APPROVED인 케어를 페이지당 5개의 객체를 보여줌
    paginator2 = Paginator(approved_cares, 5)       # 상태가 APPROVED인 케어를 페이지당 5개의 객체를 보여줌
    page_number1 = request.GET.get('page1')
    page_number2 = request.GET.get('page2')
    page_obj1 = paginator1.get_page(page_number1)
    page_obj2 = paginator2.get_page(page_number2)
    
    context = {
            "page_obj1": page_obj1,         # NOT_APPROVED 페이지네이션
            "page_obj2": page_obj2,         # APPROVED 페이지네이션
            'not_approved_users': not_approved_users,
            'approved_users': approved_users,
            'not_approved_cares': not_approved_cares,
            'approved_cares': approved_cares,
        }
        
    return render(request, "management_app/volunteer_care_list.html", context)
    

@login_required
@volunteer_required
def status_update(request, care_id):
    care = get_object_or_404(Care, id=care_id)
    senior = care.seniors.first()
    
    if request.method == 'POST':
        care.care_state = request.POST.get('state')
        care.visit_date = request.POST.get('visit_date')
        care.visit_time = request.POST.get('visit_time')
        care.approved_by = request.user
        care.save()
        my_signal.send(sender=care)
        return redirect('/management/care/list/')
    
    context = {
        'care': care,
        'senior': senior,
    }
    
    return render(request, "management_app/volunteer_care_status_update.html", context)