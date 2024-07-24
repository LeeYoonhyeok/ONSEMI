from django.urls import path
from .views import auth_views, profile_update_views, profile_views, find_user_id_views

urlpatterns = [
    path("login/", auth_views.login_user),
    path("register/", auth_views.register_user, name="ds"),
    path("logout/", auth_views.logout_user),
    path("profile/", profile_views.show_user_profile),
    path("profile/update/", profile_update_views.update_profile),
    path("profile/update/password/", profile_update_views.update_password),
    path('find_user_id/', find_user_id_views.find_user_id, name='find_user_id'),
    path('reset_password/', auth_views.reset_password, name='reset_password'),
]
