from django.contrib import admin
from .models import Article


@admin.register(Article)
class RoomAdmin(admin.ModelAdmin):
    pass
