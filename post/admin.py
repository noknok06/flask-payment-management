from django.contrib import admin
from .models import Post, Company, Approval, Tag
from import_export import resources  
from import_export.admin import ImportExportModelAdmin 


class TagResource(resources.ModelResource):
   class Meta:
       model = Tag
       skip_unchanged = True
       use_bulk = True

class PostResource(resources.ModelResource):
   class Meta:
       model = Post
       skip_unchanged = True
       use_bulk = True

@admin.register(Post)
class PostAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ['id']
    list_display = ( 'id',"contract_partner", "category", "title",
                    "contract_method", "recording_date")  # タイトルと著者を表示するよう設定
    resource_class = PostResource

    
class TagAdmin(admin.ModelAdmin):
    list_display = ('id','tag')

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id','company_name')
    
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('id','title')

admin.site.register(Company, CompanyAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Approval, ApprovalAdmin)
