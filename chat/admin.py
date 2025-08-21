from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ChatRoom, ChatMessage, PrivateMessage

# Register your models here.

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'message_preview', 'timestamp']
    list_filter = ['room', 'timestamp', 'user']
    search_fields = ['message', 'user__username', 'room__name']
    readonly_fields = ['timestamp']
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"

@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'message_preview', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read', 'sender', 'receiver']
    search_fields = ['message', 'sender__username', 'receiver__username']
    readonly_fields = ['timestamp']
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"

# Custom User Admin to show chat-related info
class ChatUserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('date_joined', 'last_login', 'is_staff', 'is_superuser')
    
    def get_inline_instances(self, request, obj=None):
        inlines = super().get_inline_instances(request, obj)
        return inlines

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, ChatUserAdmin)
