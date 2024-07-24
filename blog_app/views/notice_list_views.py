from blog_app.models import *
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
# 공지글 불러오기
def notice_all(request):
    
    # Blog에서 공지글만 불러오기
    notice_list = Blog.objects.filter(blog_type='NOTICE')
    
    context = {'notice_list': notice_list}
    return render(request, 'blog_app/notice_list.html', context)


@login_required
# 공지글 검색 기능
def search(request):
    query = Blog.objects.filter(title__contains=request.GET.get('search'))
    context = {'notice_list': query}
    return render(request, 'blog_app/notice_list.html', context)