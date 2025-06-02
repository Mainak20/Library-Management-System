from django.urls import path
from .views import user_signup, admin_dashboard, admin_login, admin_signup, user_login, user_dashboard, user_signup, logout_view, profile_view, chat

urlpatterns = [
    path('user/signup/', user_signup, name='user_signup'),
    path('admin/signup/', admin_signup, name='admin_signup'),
    path('user/login/', user_login, name='user_login'),
    path('admin/login/', admin_login, name='admin_login'),
    path('logout/', logout_view, name='logout'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('user-dashboard/', user_dashboard, name='user_dashboard'),
    path('profile/', profile_view, name='profile'),
    path('chat/',chat, name='chat'),

]