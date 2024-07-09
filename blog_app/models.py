from django.db import models
from auth_app.models import User

# 게시판(자유게시판, 공지사항)
class Blog(models.Model):
    blog_id = models.AutoField(primary_key=True, db_column='blog_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    name = models.CharField(db_column='name', max_length=255)
    title = models.TextField(verbose_name='제목', db_column='title')
    content = models.TextField(verbose_name='내용', db_column='content')
    image = models.ImageField(verbose_name='사진', upload_to='blog/%Y/%m/', db_column='image', blank=True, null=True)
    datetime = models.DateTimeField(db_column='datetime', auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    blog_type = models.CharField(max_length=63, db_column='blog_type', blank=False, null=False)
    
    class Meta:
        db_table = "Blog"
        

# 댓글
class Comment(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name='댓글 입력')
    datetime = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return self.content
    

# 좋아요
class Like(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='post_likes')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user_id')