from django.shortcuts import render, redirect
from auth_app.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.messages import get_messages

# Create your views here.


@csrf_exempt
def login_user(request):
    if request.method == "GET":
        # 다시 로그인하러 돌아올 때 메시지가 뜨는 것을 없애는 역할
        storage = get_messages(request)
        latest_message = None
        for message in storage:
            latest_message = message
        return render(request, "auth_app/login.html", {'latest_message': latest_message})

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if len(username) == 0 or len(password) == 0:
            messages.add_message(request, messages.INFO, "write correctly")
            return redirect("/login")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            # print(user.user_type)
            if user.user_type == 'FAMILY':  # 사용자의 유형이 'FAMILY'인 경우
                return redirect("/management/senior/list")
            
            elif user.user_type == 'VOLUNTEER':  # 사용자의 유형이 'VOLUNTEER'인 경우
                return redirect("/management/care/list")
            
            elif user.user_type == 'ADMIN':  # 사용자의 유형이 'ADMIN'인 경우
                return redirect("/admin")
            elif user.user_type == '':
                user.user_type = 'FAMILY'
                user.save()
                return redirect("/monitoring/family_monitor")
            
            return redirect("/")  # 다른 사용자 유형은 홈 페이지로 리디렉션

        else:
            messages.error(request, '아이디와 비밀번호가 틀렸습니다.')  # 에러 메시지 추가


        return redirect("/user/login")


@login_required
def logout_user(request):
    logout(request)
    request.session.flush()
    return redirect("/")


@csrf_exempt
def register_user(request):
    if request.method == "GET":
        return render(request, "auth_app/register_user.html")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST.get("confirm_password")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        user_type = request.POST.get("user_type")

        user_exists = User.objects.filter(username=username).exists()

        if user_exists:
            messages.add_message(request, messages.INFO, "username exist")
            return redirect("/user/register/")

        if len(username) <= 0:
            messages.add_message(
                request, messages.INFO, "username's length is too short"
            )
            return redirect("/user/register/")

        if password != confirm_password:
            messages.add_message(request, messages.INFO, "confirm password")
            return redirect("/user/register/")

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    phone_number=phone_number,
                    email=email,
                    user_type=user_type,
                )
                if user.user_type == 'ADMIN':
                    user.is_superuser = 1
                    user.save()
        except Exception:
            return redirect("/")

        return redirect("/user/login")

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not email or not new_password or not confirm_password:
            messages.error(request, '모든 필드를 입력해주세요.')
            return JsonResponse({'success': False, 'message': '모든 필드를 입력해주세요.'})

        if new_password != confirm_password:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return JsonResponse({'success': False, 'message': '비밀번호가 일치하지 않습니다.'})

        try:
            user = User.objects.get(email=email)
            if check_password(new_password, user.password):
                messages.error(request, '기존 비밀번호와 일치합니다.')
                return JsonResponse({'success': False, 'message': '기존 비밀번호와 일치합니다.'})
            
            user.password = make_password(new_password)
            user.save()
            request.session['reset_password_success'] = True
            messages.error(request, '비밀번호가 성공적으로 변경되었습니다.')
            return JsonResponse({'success': True})
        
        except User.DoesNotExist:
            messages.error(request, '사용자를 찾을 수 없습니다.')
            return JsonResponse({'success': False, 'message': '사용자를 찾을 수 없습니다.'})

    return render(request, 'auth_app/reset_password.html')