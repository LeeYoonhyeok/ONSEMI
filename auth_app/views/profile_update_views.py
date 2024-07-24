from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages


@login_required
def show_profile(request):

    user = request.user

    context = {"user": user}

    return render(request, "auth_app/profile.html", context)


# 프로필 업데이트

# input tag에 read only만 보여준다
# update 할 때는 입력란
# check_password


@login_required
def update_profile(request):
    if request.method == "GET":
        return render(request, "auth_app/update_profile.html")

    if request.method == "POST":
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        # 변경 완료 후 현재 password로 사용자 재확인
        password = request.POST.get("password")

        user = request.user
        if user.check_password(password):
            if username:
                user.username = username
            if phone_number:
                user.phone_number = phone_number
            if email:
                user.email = email
            user.save()
            messages.success(request, "프로필 수정 완료!")
            return redirect("/user/profile/")
        else:
            messages.error(request, "비밀번호를 다시 입력해주세요.")

    context = {
        "user": user,
        "phone_number": user.phone_number,
        "email": user.email,
    }

    return render(request, "auth_app/profile.html")


# 유저 비밀번호 변경
@login_required
def update_password(request):
    if request.method == "GET":
        return render(request, "auth_app/update_password.html")

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        new_password_confirm = request.POST.get("new_password_confirm")

        user = request.user
        if user.check_password(current_password):
            if new_password == new_password_confirm:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(
                    request, user
                )  # Important for keeping the user logged in
                messages.success(request, "비밀번호 변경 완료!")
                return redirect("/user/profile/")
            else:
                messages.error(request, "새로운 비밀번호가 일치하지 않습니다.")
        else:
            messages.error(request, "비밀번호를 다시 입력해주세요.")

    return render(request, "auth_app/update_password.html")


# transaction 활동을 단위로 묶는다.
# 돈을
