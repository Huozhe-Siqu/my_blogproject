from django.contrib import admin

# Register your models here.
from .models import Post,Category,Tag

class PostAdmin(admin.ModelAdmin):
    list_display = ["title","created_time","modified_time","category","author"]
    fields = ["title","body","excerpt","category","tags"]

    def save_model(self, request, obj, form, change) -> None:
        obj.author = request.user
        return super().save_model(request, obj, form, change)

# 把新增加Postadmin也注册进来
admin.site.register(Post,PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)