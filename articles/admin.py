from django.contrib import admin
from .models import Article, Comment


class GenreFilter(admin.SimpleListFilter):
    title = "Filter by Genre"

    parameter_name = "content"

    def lookups(self, request, model_admin):
        return [
            ("hiphop", "Hiphop"),
            ("pop", "Pop"),
            ("edm", "Edm"),
        ]

    def queryset(self, request, articles):
        word = self.value()
        if word == "hiphop":
            return articles.filter(content__contains=word)
        elif word == "pop":
            return articles.filter(content__contains=word)
        elif word == "edm":
            return articles.filter(content__contains=word)
        else:
            return articles


@admin.action(description="Set all contents to empty")
def reset_contents(model_admin, request, articles):
    for article in articles.all():
        article.content = ""
        article.save()


@admin.register(Article)
class RoomAdmin(admin.ModelAdmin):
    readonly_fields = ("comments_url_list",)
    fieldsets = [
        (
            "Article",
            {
                "fields": [
                    "title",
                    "content",
                    "owner",
                    "bookmark",
                ],
            },
        ),
        (
            "Comments",
            {"fields": ["comments_url_list"]},
        ),
    ]
    actions = (reset_contents,)
    list_display = (
        "title",
        "content",
        "owner",
        "total_bookmarks",
        "created_at",
        "updated_at",
        "total_comments",
    )
    list_filter = (
        GenreFilter,
        "created_at",
        "updated_at",
    )
    search_fields = (
        "^owner__nickname",  # starts_with
        "=title",  # equal
        "content",  # contain
    )


@admin.register(Comment)
class RoomAdmin(admin.ModelAdmin):
    pass
