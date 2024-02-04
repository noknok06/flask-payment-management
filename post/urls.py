from django.urls import path
from .views import PostDetail, PostList, DetailView, PostCreate, PostUpdate, PostDelete, PostListAll

urlpatterns = [
    path("", PostList.as_view(), name="list"),
    path("listall/", PostListAll.as_view(), name="listall"),
    path("detail/<int:pk>", PostDetail.as_view(), name="detail"),
    path("create/", PostCreate.as_view(), name="create"),
    path("update/<int:pk>", PostUpdate.as_view(), name="update"),
    path("delete/<int:pk>", PostDelete.as_view(), name="delete"),
]