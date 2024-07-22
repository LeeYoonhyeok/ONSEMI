from django.urls import path
from . import views

app_name = 'qa'
urlpatterns = [
    path('chatting/', views.chatting, name='chatting'),
    path('reset/', views.reset, name='reset'),
]
