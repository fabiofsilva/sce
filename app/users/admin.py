from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserCriacaoForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCriacaoForm

    list_display = ['email', 'first_name', 'last_name', 'tenant', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'tenant']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    filter_horizontal = ['groups', 'user_permissions']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dados pessoais', {'fields': ('first_name', 'last_name')}),
        ('Tenant', {'fields': ('tenant',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'tenant'),
        }),
    )
    readonly_fields = ['last_login', 'date_joined']
