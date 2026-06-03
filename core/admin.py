from django.contrib import admin
from .models import PlatformApplication

@admin.register(PlatformApplication)
class PlatformApplicationAdmin(admin.ModelAdmin):
    list_display = ('name_cn', 'applicant', 'status', 'created_at')
    list_filter = ('status', 'level', 'category')
    search_fields = ('name_cn', 'applicant__username')
    readonly_fields = ('applicant', 'created_at', 'updated_at')