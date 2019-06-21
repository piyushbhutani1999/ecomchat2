from django.contrib import admin

# Register your models here.
from .models import Dialog, Message

admin.site.register(Dialog)
admin.site.register(Message)