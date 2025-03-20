from django.contrib import admin
from .models import Task




@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'completed', 'created_at')  # Added 'user' to list_display
    list_filter = ('completed', 'created_at', 'user')  # Added 'user' to list_filter
    search_fields = ('title', 'description', 'user__username')  # Added 'user__username' to search_fields
    fieldsets = (
        ('General Information', {
            'fields': ('user', 'title', 'description')  # Added 'user' to General Information
        }),
        ('Status', {
            'fields': ('completed',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # Collapse this section by default
        }),
    )

    readonly_fields = ('created_at',)  # 'created_at' remains read-only
