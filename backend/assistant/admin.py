from django.contrib import admin
from .models import ChatLog

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display   = ('timestamp', 'session_id', 'user_message', 'ai_response')
    list_filter    = ('session_id',)
    search_fields  = ('user_message', 'ai_response')
    readonly_fields = ('timestamp',)
