"""
models.py - Database models for Jarvis AI Assistant

This file defines how chat data is stored in SQLite.
Each ChatLog entry = one conversation turn (user message + AI response).
"""
from django.db import models


class ChatLog(models.Model):
    """
    Stores every conversation between user and AI.
    
    Fields:
      - user_message : what the user typed/said
      - ai_response  : what Jarvis replied
      - timestamp    : when the exchange happened (auto-set)
      - session_id   : groups messages into a session (optional, for multi-user)
    """
    user_message = models.TextField()                          # User's input
    ai_response  = models.TextField()                          # AI's reply
    timestamp    = models.DateTimeField(auto_now_add=True)     # Auto timestamp
    session_id   = models.CharField(max_length=100, blank=True, default='default')

    class Meta:
        ordering = ['-timestamp']   # Newest first by default
        verbose_name = "Chat Log"
        verbose_name_plural = "Chat Logs"

    def __str__(self):
        # Short preview in Django admin
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user_message[:50]}"
