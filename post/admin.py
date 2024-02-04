from django.contrib import admin
from .models import Post, Company


class PostAdmin(admin.ModelAdmin):
    list_display = ("contract_partner", "category", "title",
                    "contract_method", "recording_date")  # タイトルと著者を表示するよう設定
    list_filter = ("contract_partner",) # authorでフィルター


# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Company)
