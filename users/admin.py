from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group

from .forms import TANFUserCreationForm, TANFUserChangeForm
from .models import TANFUser


class TANFUserAdmin(UserAdmin):
    add_form = TANFUserCreationForm
    form = TANFUserChangeForm
    model = TANFUser
    list_display = ('email', 'stt_code', 'is_staff', 'is_active', 'last_login',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'stt_code',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'stt_code', 'is_staff', 'is_active')}),
    )
    search_fields = ('email', 'stt_code',)
    ordering = ('email',)


class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = ('content_type', 'user', 'action_time', 'object_id', 'object_repr', 'action_flag', 'change_message')
    list_display = ('content_type', 'user', 'action_time', 'object_id', 'object_repr', 'action_flag', 'change_message')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(TANFUser, TANFUserAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.unregister(Group)
