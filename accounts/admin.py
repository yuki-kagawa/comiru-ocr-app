from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Child, User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('個人情報', {'fields': ('email',)}),
        ('パーミッション', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'birthday', 'gender', 'juku')
    list_filter = ('gender', 'juku')
    search_fields = ('name', 'parent__username', 'juku')
    ordering = ('-created_at',)