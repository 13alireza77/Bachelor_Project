from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, AccessLevel, RequestHistory


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class CustomAccessLevel(admin.ModelAdmin):
    model = AccessLevel
    list_display = ('user', 'max_number_of_data',)
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ('user',)


class CustomRequestHistory(admin.ModelAdmin):
    model = RequestHistory
    list_display = ('user', 'request_id', 'create_date', 'count_data', 'status',)
    list_filter = ('status',)
    search_fields = ('user', 'request_id', 'create_date', 'count_data', 'status',)
    ordering = ('user',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RequestHistory, CustomRequestHistory)
admin.site.register(AccessLevel, CustomAccessLevel)
