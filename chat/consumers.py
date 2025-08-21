import json
import django
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Configure Django settings if not already configured
import os
if not hasattr(django.conf.settings, 'configured') or not django.conf.settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatproject.settings')
    django.setup()

from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage, PrivateMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
            
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Save message to database
        await self.save_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                'sender_channel': self.channel_name
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        sender_channel = event['sender_channel']
        is_own_message = sender_channel == self.channel_name

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'is_own_message': is_own_message
        }))

    @database_sync_to_async
    def save_message(self, message):
        room, created = ChatRoom.objects.get_or_create(
            name=self.room_name,
            defaults={'created_by': self.user, 'description': f'Room {self.room_name}'}
        )
        ChatMessage.objects.create(
            room=room,
            user=self.user,
            message=message
        )

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
            
        self.user = self.scope["user"]
        self.receiver_id = self.scope['url_route']['kwargs']['user_id']
        
        # Create a unique room name for private chat
        user_ids = sorted([self.user.id, int(self.receiver_id)])
        self.room_group_name = f'private_{user_ids[0]}_{user_ids[1]}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Save private message to database
        await self.save_private_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'private_message',
                'message': message,
                'username': self.user.username,
                'sender_id': self.user.id,
                'sender_channel': self.channel_name
            }
        )

    # Receive message from room group
    async def private_message(self, event):
        message = event['message']
        username = event['username']
        sender_id = event['sender_id']
        sender_channel = event['sender_channel']
        is_own_message = sender_channel == self.channel_name

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'sender_id': sender_id,
            'is_own_message': is_own_message
        }))

    @database_sync_to_async
    def save_private_message(self, message):
        receiver = User.objects.get(id=self.receiver_id)
        PrivateMessage.objects.create(
            sender=self.user,
            receiver=receiver,
            message=message
        ) 