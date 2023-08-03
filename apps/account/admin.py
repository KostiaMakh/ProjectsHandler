from django.contrib import admin

from account.models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    pass
