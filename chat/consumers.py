# consumers.py
import json
import asyncio
import requests
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from channels.db import database_sync_to_async
from accounts.models import MMUser
from channels.layers import get_channel_layer

class MattermostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        print("Connected")

        if not self.user.is_authenticated:
            await self.close()
            return

        # Retrieve Mattermost Access Token
        self.mm_access_token = self.user.mattermost_access_token
        self.mm_user_id = self.user.mattermost_user_id
        print("Token and stuff : ", self.mm_access_token, "   ",self.mm_user_id)

        # Get user’s channels and subscribe to them
        self.user_channels = await self.get_user_channels()
        print("Get channels and got : ", self.user_channels)
        for channel in self.user_channels:
            await self.channel_layer.group_add(
                f"mattermost_channel_{channel['id']}",
                self.channel_name
            )

        await self.accept()
        await self.connect_to_mattermost()

    @database_sync_to_async
    def get_user_channels(self):
        """Fetch channels the user is a member of"""
        headers = {"Authorization": f"Bearer {self.mm_access_token}"}
        response = requests.get(
            f"{settings.MATTERMOST_API_URL}/users/{self.mm_user_id}/channels",
            headers=headers
        )
        print("Gotten response for channels : ", response.json())
        return response.json()

    async def listen_to_mattermost(self):
        seq_number = 2
        while True:
            try:
                message = await self.mattermost_ws.recv()
                data = json.loads(message)
                event_type = data.get('event')

                print("Got Event from Mattermost : ", event_type)
                
                if event_type in [
                    "posted", "post_edited", "post_deleted", "reaction_added", "reaction_removed",
                    "channel_viewed", "channel_updated", "channel_created", "channel_deleted",
                    "member_added", "member_removed", "typing", "user_added", "user_removed", "user_updated"
                ]:
                    await self.send(json.dumps({
                        'type': event_type,
                        'data': data['data']
                    }))

                if seq_number % 60 == 0:
                    await self.mattermost_ws.send(json.dumps({
                        "seq": seq_number,
                        "action": "ping"
                    }))
                seq_number += 1

            except websockets.exceptions.ConnectionClosed:
                await self.reconnect()
                break
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'error': f'Error processing message: {str(e)}'
                }))

    async def broadcast_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps(event["data"]))

    async def broadcast_channel_update(self, event):
        """Send channel update to WebSocket"""
        await self.send(text_data=json.dumps(event['data']))

    async def join_channel(self, channel_id):
        """Join a new channel group"""
        await self.channel_layer.group_add(
            f"mattermost_channel_{channel_id}",
            self.channel_name
        )

    async def leave_channel(self, channel_id):
        """Leave a channel group"""
        await self.channel_layer.group_discard(
            f"mattermost_channel_{channel_id}",
            self.channel_name
        )

    async def disconnect(self, close_code):
        # Leave all channel groups
        for channel in self.user_channels:
            await self.leave_channel(channel['id'])
        
        if self.mattermost_ws:
            await self.mattermost_ws.close()

    # Rest of the methods remain the same...

    async def connect_to_mattermost(self):
        # Convert Mattermost API URL to WebSocket URL
        ws_url = settings.MATTERMOST_API_URL.replace('http', 'ws') + '/websocket'
        
        try:
            self.mattermost_ws = await websockets.connect(ws_url)

            print("Connecting to mattermost")
            
            # Authentication message
            auth_message = {
                "seq": 1,
                "action": "authentication_challenge",
                "data": {
                    "token": self.user.mattermost_access_token
                }
            }
            await self.mattermost_ws.send(json.dumps(auth_message))
            
            print("sent authentication message to mattermost")

            # Start listening for Mattermost events
            asyncio.create_task(self.listen_to_mattermost())
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Failed to connect to Mattermost: {str(e)}'
            }))
            await self.close()
    
    async def reconnect(self):
        """Attempt to reconnect to Mattermost WebSocket"""
        await asyncio.sleep(5)  # Wait before reconnecting
        await self.connect_to_mattermost()

    # async def receive(self, text_data):
    #     """Handle WebSocket messages from frontend"""
    #     try:
    #         data = json.loads(text_data)
    #         action = data.get("action")
    #         print("Message from frontend : ", data)

    #         if action == "send_message":
    #             await self.handle_send_message(data)
    #         elif action == "delete_message":
    #             await self.handle_delete_message(data)
    #         elif action == "add_reaction":
    #             await self.handle_add_reaction(data)
    #         elif action == "reply_message":
    #             await self.handle_reply_message(data)

    #     except Exception as e:
    #         await self.send(text_data=json.dumps({"error": f"Error processing action: {str(e)}"}))


    # async def handle_send_message(self, data):
    #     """
    #     Send message to Mattermost via WebSocket
    #     """
    #     try:
    #         headers = {"Authorization": f"Bearer {self.user.mattermost_access_token}"}
    #         payload = {
    #             "channel_id": data['channel_id'],
    #             "message": data['message']
    #         }
    #         response = requests.post(f"{settings.MATTERMOST_API_URL}/posts", json=payload, headers=headers)
    #         print("resonse : recieved for sending a message : ")
            
    #     except Exception as e:
    #         await self.send(json.dumps({
    #             'type': 'error',
    #             'message': f'Error sending message: {str(e)}'
    #         }))

    # async def handle_add_reaction(self, data):
    #     """
    #     Add reaction to a message via WebSocket
    #     """
    #     try:
    #         reaction = {
    #             "seq": 1,
    #             "action": "add_reaction",
    #             "data": {
    #                 "post_id": data['post_id'],
    #                 "emoji_name": data['emoji_name']
    #             }
    #         }
    #         await self.mattermost_ws.send(json.dumps(reaction))
            
    #     except Exception as e:
    #         await self.send(json.dumps({
    #             'type': 'error',
    #             'message': f'Error adding reaction: {str(e)}'
    #         }))

    # async def handle_delete_message(self, data):
    #     """
    #     Delete a message via WebSocket
    #     """
    #     try:
    #         delete_request = {
    #             "seq": 1,
    #             "action": "delete_post",
    #             "data": {
    #                 "post_id": data['post_id']
    #             }
    #         }
    #         await self.mattermost_ws.send(json.dumps(delete_request))
            
    #     except Exception as e:
    #         await self.send(json.dumps({
    #             'type': 'error',
    #             'message': f'Error deleting message: {str(e)}'
    #         }))

    # async def handle_reply_message(self, data):
    #     """Handle replying to a message"""
    #     message = {
    #         "action": "post",
    #         "seq": 5,
    #         "data": {
    #             "channel_id": data['channel_id'],
    #             "message": data['message'],
    #             "root_id": data['post_id']
    #         }
    #     }
    #     await self.mattermost_ws.send(json.dumps(message))