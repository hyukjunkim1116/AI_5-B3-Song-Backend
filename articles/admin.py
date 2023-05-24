from django.contrib import admin
from .models import Article, Comment


@admin.register(Article)
class RoomAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class RoomAdmin(admin.ModelAdmin):
    pass
