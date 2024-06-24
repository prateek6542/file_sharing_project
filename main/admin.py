from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FileUpload

admin.site.register(User, UserAdmin)
admin.site.register(FileUpload)
