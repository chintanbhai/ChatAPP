from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ChatRoom, ChatMessage, PrivateMessage

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('chat_home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'chat/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'chat/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'chat/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')
    
    return render(request, 'chat/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def chat_home(request):
    rooms = ChatRoom.objects.all().order_by('-created_at')
    # Exclude admin/superuser accounts from regular chat users list
    users = User.objects.exclude(id=request.user.id).exclude(is_staff=True).exclude(is_superuser=True)
    return render(request, 'chat/home.html', {
        'rooms': rooms, 
        'users': users,
        'is_admin': request.user.is_staff or request.user.is_superuser
    })

@login_required
def room(request, room_name):
    room_obj, created = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={'created_by': request.user, 'description': f'Room {room_name}'}
    )
    messages = ChatMessage.objects.filter(room=room_obj)
    return render(request, 'chat/room.html', {
        'room_name': room_name, 
        'room_obj': room_obj,
        'messages': messages
    })

@login_required
def private_chat(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    messages = PrivateMessage.objects.filter(
        sender__in=[request.user, receiver],
        receiver__in=[request.user, receiver]
    )
    return render(request, 'chat/private_chat.html', {
        'receiver': receiver,
        'messages': messages
    })

@login_required
def get_users(request):
    # Exclude admin/superuser accounts from API response
    users = User.objects.exclude(id=request.user.id).exclude(is_staff=True).exclude(is_superuser=True).values('id', 'username')
    return JsonResponse({'users': list(users)})
