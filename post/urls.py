from django.urls import path
from .views import PostDetail, PostList, PostManage, PostCreate, PostUpdate, PostDelete, PostListAll ,CompanyList ,CompanyDetail, ApprovalList, PostStatusUpdate
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", PostList.as_view(), name="list"),
    path("tag/<str:tag>", PostList.as_view(), name="list"),
    path("listall/", PostListAll.as_view(), name="listall"),
    path("orderlist/", PostManage.as_view(), name="orderlist"),
    path("approval/", ApprovalList.as_view(), name="approval"),
    path("company/", CompanyList.as_view(), name="company"),
    path("company/<int:pk>", CompanyDetail.as_view(), name="company_detail"),
    path("detail/<int:pk>", PostDetail.as_view(), name="detail"),
    path("create/", PostCreate.as_view(), name="create"),
    path("update/<int:pk>", PostUpdate.as_view(), name="update"),
    path("delete/<int:pk>", PostDelete.as_view(), name="delete"),
    path("monthly/<int:pk>", PostStatusUpdate.as_view(), name="monthly_statuses_update"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)