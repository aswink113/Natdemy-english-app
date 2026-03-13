import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We will use a general 'call_room' for simplicity,
        # but in production, rooms should be per user or per call session
        self.room_group_name = "call_room"
        
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
        message_type = data.get("type", "call_message")
        
        # Broadcast the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "call_message",
                "message": data.get("message", {}),
                "sender": data.get("sender", "unknown")
            }
        )

    # Receive message from room group
    async def call_message(self, event):
        message = event["message"]
        sender = event.get("sender", "unknown")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "call_message",
            "message": message,
            "sender": sender
        }))
