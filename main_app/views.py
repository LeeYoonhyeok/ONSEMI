from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from auth_app.models import User

#Create your views here.
def index(request):
    return render(request, 'page/index.html')

def introduce(request):
    return render(request, 'page/introduce.html')

def family(request):
    return render(request, 'page/family.html')

def volunteer(request):
    return render(request,'page/volunteer.html')


def terms(request):
    return render(request,'page/terms.html')

@login_required
def user_page(request):
    if not request.user.is_authenticated:
        messages.error(request, '로그인이 필요한 서비스입니다.')
        return render(request, 'page/index.html')
    user_type = request.user.user_type
    
    if user_type == 'FAMILY':
        return redirect('/management/senior/list')
    elif user_type == 'VOLUNTEER':
        return redirect('/management/care/list')
    elif user_type == 'ADMIN':
        return redirect('/admin')
    return render(request, 'default_dashboard') 

