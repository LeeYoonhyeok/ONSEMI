from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from blog_app.models import Blog, Comment, Like, BlogImage
from blog_app.forms import PostForm, CommentForm, ImageFormSet

# 게시글 상세 보기 기능
@login_required
def notice_detail(request, pk):
    
    # 게시글 불러오기
    post = get_object_or_404(Blog, pk=pk)
    
    # 조회수 증가
    post.views += 1  
    post.save()
    
    # 해당 게시글의 댓글 불러오기
    comments = post.comments.filter(parent__isnull=True)
    new_comment = None
    comment_count = comments.count() # 기본 댓글 수
    
    # 각 댓글에 대한 대댓글 수를 계산
    for comment in comments:
        comment_count += comment.replies.count()
    
    # POST 방식: 댓글 저장
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user_id = request.user  # 로그인한 사용자 설정
            new_comment.post = post
            parent_id = request.POST.get('parent_id')
            if parent_id:
                new_comment.parent = Comment.objects.get(id=parent_id)
            new_comment.save()
            page_number = request.POST.get('page', 1)
            return HttpResponseRedirect(f'{post.get_absolute_url()}?page={page_number}')
    
    # GET 방식: 댓글 작성 폼 로드
    else:
        comment_form = CommentForm()

    # 게시글 상세 페이지로 이동
    return render(request, 'blog_app/notice_detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'comment_count': comment_count,
        'page_number': request.GET.get('page', 1),
    })


# 좋아요 기능
@login_required
@require_POST
def notice_like(request, pk):
    
    # 게시글 불러오기
    post = get_object_or_404(Blog, pk=pk)
    
    # 이미 있는 객체는 가져오고, 없다면 생성
    like, created = Like.objects.get_or_create(post=post, user_id=request.user)
        
    # 좋아요 기능은 1번만 사용가능하게 해야함
    if not created: 
        like.delete()
    post.likes = post.post_likes.count()
    post.save()
    return JsonResponse({'likes': post.likes})


# 게시글 삭제 기능
@login_required
@require_POST
def notice_delete(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    if post.user_id != request.user:
        return redirect('blog_app:notice_detail', pk=pk)
    
    post.delete()
    return redirect('blog_app:notice_list')

def post_list(request):
    posts = Blog.objects.all()
    return render(request, 'blog_app/notice_list.html', {'posts': posts})


# 포스트 수정 기능
@login_required
def notice_edit(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        formset = ImageFormSet(request.POST, request.FILES, queryset=BlogImage.objects.none())
        
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.save()
            
            # 처리할 삭제된 이미지 ID
            deleted_images = request.POST.getlist('deleted_images')
            for image_id in deleted_images:
                try:
                    image = BlogImage.objects.get(id=image_id)
                    image.delete()
                except BlogImage.DoesNotExist:
                    continue

            # 새로운 이미지 저장
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = BlogImage(blog=post, image=image)
                    photo.save()
                    
            return redirect('blog_app:notice_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
        formset = ImageFormSet(queryset=BlogImage.objects.none())
        
    return render(request, 'blog_app/notice_edit.html', {'form': form, 'formset': formset, 'images': post.images.all()})



# 댓글 삭제 기능
@login_required
@require_POST
def notice_comment_delete(request, post_pk, comment_pk):
    
    # 게시글, 댓글 불러오기
    post = get_object_or_404(Blog, pk=post_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    # 댓글 작성자가 아니면 삭제 불가
    if comment.post != post or (comment.user_id != request.user and post.user_id != request.user):
        return redirect('blog_app:notice_detail', pk=post_pk)
    
    comment.delete()
    return redirect('blog_app:notice_detail', pk=post_pk)
