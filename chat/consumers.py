import json
from channels.generic.websocket import AsyncWebsocketConsumer
import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    timestamp = datetime.datetime.now().strftime('%H:%M')
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_channel': self.channel_name,
                'timestamp': self.timestamp,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        timestamp = event['timestamp']
        sender_channel = event['sender_channel']
        is_own_message = sender_channel == self.channel_name

        await self.send(text_data=json.dumps({
            'message': message,
            'is_own_message': is_own_message,
            'timestamp': timestamp,
        }))