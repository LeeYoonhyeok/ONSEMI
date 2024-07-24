from blog_app.models import Blog, BlogImage
from django.shortcuts import render, redirect
from blog_app.forms import PostForm, ImageFormSet
from django.contrib.auth.decorators import login_required

@login_required
# 게시글 업로드 기능
def post_upload(request):
    post = Blog()
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        formset = ImageFormSet(request.POST, request.FILES, queryset=BlogImage.objects.none())
        
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.user_id = request.user
            post.name = request.user
            post.blog_type = 'BLOG'
            post.save()
            
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = BlogImage(blog=post, image=image)
                    photo.save()
                    
            return redirect('blog_app:post_detail', pk=post.pk)
    else:
        # [추가 구현 필요] 로그인을 하지 않으면 업로드 불가
        if request.user == 'AnonymousUser':
            pass
        
        form = PostForm(instance=post)
        formset = ImageFormSet(queryset=BlogImage.objects.none())
        return render(request, 'blog_app/upload.html', {'form': form, 'formset':formset})
    
    
@login_required
# 공지사항 게시글 업로드
# [추가 구현 필요] 공지사항은 ADMIN만 올릴 수 있게 구현
def notice_upload(request):
    post = Blog()
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        formset = ImageFormSet(request.POST, request.FILES, queryset=BlogImage.objects.none())
        
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.user_id = request.user
            post.name = request.user
            post.blog_type = 'NOTICE'
            post.save()
            
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = BlogImage(blog=post, image=image)
                    photo.save()
                    
            return redirect('blog_app:notice_detail', pk=post.pk)
    else:
        # [추가 구현 필요] 로그인을 하지 않으면 업로드 불가
        if request.user == 'AnonymousUser':
            pass
        
        form = PostForm(instance=post)
        formset = ImageFormSet(queryset=BlogImage.objects.none())
        return render(request, 'blog_app/upload.html', {'form': form, 'formset':formset})
    
 
