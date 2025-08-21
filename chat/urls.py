from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.chat_home, name='chat_home'),
    path('room/<str:room_name>/', views.room, name='room'),
    path('private/<int:user_id>/', views.private_chat, name='private_chat'),
    path('api/users/', views.get_users, name='get_users'),
] 