from django.contrib import admin

from .models import User  # وارد کردن مدل سفارشی


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass  # یا تنظیمات دلخواه خود را اضافه کنید
