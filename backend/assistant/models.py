from django.db import models

class ChatLog(models.Model):
    user_message = models.TextField()
    ai_response  = models.TextField()
    timestamp    = models.DateTimeField(auto_now_add=True)
    session_id   = models.CharField(max_length=100, blank=True, default='default')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user_message[:50]}"
