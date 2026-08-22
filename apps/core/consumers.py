"""
WebSocket 消费者 — 数据刷新广播
================================

路由：``ws/refresh/``（见 ``apps.core.routing``）。

客户端连接后加入 Channels 组 ``data_refresh_group``；服务端调用 ``send_refresh_signal`` 时
向组内推送 JSON 文本（字段 ``type`` / ``data_type`` / ``message``），前端 ``useDataRefresh`` 收到后再拉 REST 列表。

事件处理器方法名 ``refresh_message`` 须与 ``group_send`` 里的 ``type`` 字段一致。
"""
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from typing import Any


class DataRefreshConsumer(AsyncWebsocketConsumer):
    """
    异步 WebSocket 连接：仅负责组播订阅与下行推送；不做用户鉴权扩展（由 AuthMiddlewareStack 可选封装）。
    """

    async def connect(self):
        """
        客户端连接时调用
        """
        self.group_name = "data_refresh_group"
        
        # 将当前连接加入广播组
        if self.channel_layer:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        
        await self.accept()

    async def disconnect(self, close_code: Any):
        """
        客户端断开连接时调用
        """
        # 从广播组中移除
        if self.channel_layer:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        接收客户端消息（可选，目前主要由后端主动推送）
        """
        pass

    async def refresh_message(self, event):
        """
        接收来自 group 的消息并转发给客户端（payload 已在 send_refresh_signal 中序列化）
        """
        text_data = event.get("text_data")
        if text_data is None:
            # 兼容旧事件格式
            text_data = json.dumps(
                {
                    "type": "refresh",
                    "data_type": event.get("data_type", "all"),
                    "message": event["message"],
                },
                separators=(",", ":"),
            )
        await self.send(text_data=text_data)
