from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import IntegrityError
from auth_app.models import User
from management_app.models import Care, Senior
from auth_app.utils import family_required  # 해당 페이지는 보호자로 로그인했을 때만 접근이 가능하게 수정!!
from datetime import datetime
from django.contrib.auth import get_user_model
from datetime import date


# Create your views here.

# 1 -> easy
# user(보호자)가 노인을 등록하는 기능 (예상 : html파일 1+개?)
#       -> 위에거 수정하는 페이지(html1개+)


# 2 -> normal
# user(보호자)가 Care를 등록하는 기능(예상 :html파일 1+개?) -> 어려움
#       -> 위에거 수정하는 페이지(html1개+)

# 3 ->개어렵
# user(봉사자)가 user(보호자)가 올린 Care를 확인하는 = 조회하는 기능(예상 :html 1+개?)
# 여러 방면으로 조회할 수 있어야함 ( 노인 카테고리로 조회, 오름차순, 내림차순, or 유저별로, 지역별로, 날짜별로 오름차순)
# NOT_APPROVED, CONFIRMED, APPROVED
# 4 ->hard
# user(보호자)가 자신이 올린 Care를 확인하는 기능(예상: html 1개 이상)
# 여러 방면으로 조회할 수 있어야함
# 위에거랑 같은데 유저별은 없겠죠?
# NOT_APPROVED, CONFIRMED, APPROVED

from django.http import JsonResponse
@login_required
@family_required
def add_care(request):
    if request.method == "GET":
        user = request.user
        user_senior_list = user.senior_set.all()
        selected_senior_id = request.GET.get("selected_senior_id")
        selected_senior = Senior.objects.get(id=selected_senior_id) if selected_senior_id else None
        context = {"seniors": user_senior_list, "selected_senior": selected_senior}
        return render(request, "management_app/add_care.html", context)

    if request.method == "POST":
        care_type = request.POST.get("care_type")
        title = request.POST.get("title")
        content = request.POST.get("content")
        senior_id = request.POST.get("senior")
        parkinson_diagnosis = request.POST.get("parkinson_diagnosis")
        
        parkinson_diagnosis = parkinson_diagnosis == "on"
                
        user = request.user
        senior = Senior.objects.get(pk=senior_id)
        
        existing_care = Care.objects.filter(
            seniors=senior,
            care_state='NOT_APPROVED'
        ).first()

        if existing_care:
            message = f"{senior.name}님은 승인 되지 않은 요청 건이 존재합니다. \n마이 페이지에서 확인 및 수정하시기 바랍니다. \n※승인 되기 전까지 케어 요청을 무한히 보내는 것을 방지"
            return JsonResponse({'error': message})

        care = Care(
            care_type=care_type,
            title=title,
            content=content,
            user_id=user,
            parkinson_diagnosis=parkinson_diagnosis,
        )
        care.save()
        care.seniors.add(senior)

        return JsonResponse({'success': True, 'redirect_url': f'/monitoring/family_monitor/?selected_senior_id={senior_id}'})
    return JsonResponse({'error': '유효하지 않은 요청입니다.'}, status=400)
        

@login_required
@family_required
def show_one_care(request, care_id):
    care = Care.objects.get(pk=int(care_id))
    if request.method == 'POST':
        care_state = request.POST.get('care_state')
        admin_message = request.POST.get('admin_message')

        if care_state in ['APPROVED', 'REJECT']:
            care.care_state = care_state
        care.admin_message = admin_message
        care.save()
        return redirect('show_one_care', care_id=care_id)

    context = {"care": care}
    return render(request, "management_app/show_one_care.html", context)


@login_required
@family_required
def update_care(request, care_id):
    care = get_object_or_404(Care, pk=care_id)

    if request.method == "GET":
        senior = care.seniors.first()
        context = {"care": care, "senior": senior}
        return render(request, "management_app/update_one_care.html", context)

    elif request.method == "POST":
        care_type = request.POST.get("care_type")
        title = request.POST.get("title")
        content = request.POST.get("content")
        senior_id = request.POST.get("senior")
        parkinson_diagnosis = request.POST.get("parkinson_diagnosis")

        if care_type:
            care.care_type = care_type
        if title:
            care.title = title
        if content:
            care.content = content
        if senior_id:
            selected_senior = Senior.objects.get(pk=int(senior_id))
            care.seniors.clear()  # Clear existing seniors
            care.seniors.add(selected_senior)  # Add the selected senior
            
        if parkinson_diagnosis == "on":
            care.parkinson_diagnosis = True
        else:
            care.parkinson_diagnosis = False

        senior_id = senior_id or care.seniors.first().id
        care.save()
        return redirect(f"/monitoring/family_monitor/?selected_senior_id={senior_id}")

@login_required
@family_required
def delete_care(request, care_id):
    care = get_object_or_404(Care, id=care_id)
    senior_id = request.POST.get("senior")
    senior_id = senior_id or care.seniors.first().id
    care.delete()    
    return redirect(f"/monitoring/family_monitor/?selected_senior_id={senior_id}")


@login_required
@family_required
def add_senior(request):
    if request.method == "GET":
        context = {"ages": [i for i in range(1, 120)]}
        return render(request, "management_app/add_senior.html", context)

    if request.method == "POST":
        name = request.POST.get("name")
        postcode = request.POST.get("postcode")
        address = request.POST.get("address")
        detail_address = request.POST.get("detail_address")        
        gender = request.POST.get("gender")
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        day = int(request.POST.get('day'))
        birthdate = date(year, month, day)
        phone_number = request.POST.get("phone_number")
        has_alzheimers = request.POST.get("has_alzheimers")
        has_parkinsons = request.POST.get("has_parkinsons")
        photo = request.FILES.get("photo")        

        user = request.user
        senior = Senior(
            name=name,
            postcode = postcode,
            address=address,
            detail_address = detail_address,
            birthdate=birthdate,
            gender=gender,
            phone_number=phone_number,
            has_alzheimers =has_alzheimers,
            has_parkinsons = has_parkinsons,
            user_id=user,
            photo = photo,
        )

        senior.save()

        return redirect("/management/senior/list/")


@login_required
@family_required
def update_senior(request, id):
    senior = get_object_or_404(Senior, id=id)
    
    if request.method == 'POST':
        senior.name = request.POST.get('name', senior.name)
        year = int(request.POST.get('year', senior.birthdate.year))
        month = int(request.POST.get('month', senior.birthdate.month))
        day = int(request.POST.get('day', senior.birthdate.day))
        senior.birthdate = datetime(year, month, day)
        senior.gender = request.POST.get('gender', senior.gender)
        senior.phone_number = request.POST.get('phone', senior.phone_number)
        senior.has_alzheimers = request.POST.get('has_alzheimers') 
        senior.has_parkinsons = request.POST.get('has_parkinsons')
        senior.address = request.POST.get("address")
        senior.detail_address = request.POST.get("detail_address")
        senior.gender = request.POST.get("gender")
        senior.postcode = request.POST.get("postcode")

        if 'photo' in request.FILES:
            senior.photo = request.FILES['photo']
        
        senior.save()
        return redirect('/management/senior/list/')
    
    context = {
        'senior': senior,
    }
    return render(request, 'management_app/update_senior.html', context)


@login_required
@family_required
def delete_senior(request, id):
    # 노인 객체 가져오기
    senior = get_object_or_404(Senior, id=id)

    if request.method == 'POST':
        #    pass

        # 노인 삭제
        senior.delete()

        # 삭제 후 리디렉션할 URL 설정 (선택 사항)
        return redirect('/management/senior/list/')  # 사용자의 노인 리스트 화면으로 리디렉션
    # return render(request, 'management_app/senior_confirm_delete.html', {'senior': senior})