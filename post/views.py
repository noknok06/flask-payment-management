from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy
from .models import Post
from .forms import PostForm
from datetime import datetime, timedelta

status_mapping = {
    0: '見積依頼済',
    1: '見積確認中',
    2: '発注済',
    3: '計上済'
}

class PostListAll(ListView):
    model = Post
    fields = "__all__"
    context_object_name = "tasks"
    template_name = 'post/post_listall.html'
    paginate_by = 10

    def get_queryset(self):
        posts = Post.objects.all().order_by("recording_date")
        for post in posts:
            post.status = status_mapping.get(int(post.status), "未定義")
        return posts


class PostList(ListView):
    model = Post
    fields = "__all__"
    # ページネーションの表示件数
    paginate_by = 10
    # context_object_name = "tasks"

    # def get_queryset(self):

    #     return this_month_post

    def get_context_data(self, **kwargs):
        # 現在の年月を取得
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # 翌月1日の日付を生成
        if current_month == 12:  # 現在が12月の場合は次の年の1月1日
            next_month_first_day = datetime(current_year + 1, 1, 1)
        else:
            next_month_first_day = datetime(current_year, current_month + 1, 1)


        try:
            posts = Post.objects.all()
            
            not_ordering_post = posts.filter(
                order_date = None,
            ).order_by("recording_date")

            this_month_post = posts.filter(
                status__lt=3,
                recording_date__year=current_year,
                recording_date__month=current_month
            ).order_by("recording_date")

            monthly_post = posts.filter(
                contract_method = '毎月'
            ).order_by("recording_date")

            # 翌月以降の投稿を抽出
            next_month_post = posts.filter(
                recording_date__gte=next_month_first_day
            ).order_by("recording_date")

        except Exception as e:
            not_ordering_post = Post.objects.none
            this_month_post = Post.objects.none
            monthly_post = Post.objects.none
            next_month_post = Post.objects.none
            print(e)

        context = super().get_context_data(**kwargs)

        for post in not_ordering_post:
            post.status = status_mapping.get(int(post.status), "未定義")
        for post in this_month_post:
            post.status = status_mapping.get(int(post.status), "未定義")
        for post in monthly_post:
            post.status = status_mapping.get(int(post.status), "未定義")
        for post in next_month_post:
            post.status = status_mapping.get(int(post.status), "未定義")

        context['not_ordering_post'] = not_ordering_post
        context['not_ordering_cnt'] = len(not_ordering_post)
        context['this_month_post'] = this_month_post
        context['this_month_cnt'] = len(this_month_post)
        context['monthly_post'] = monthly_post
        context['next_month_post'] = next_month_post
        return context

class PostDetail(DetailView):
    model = Post
    context_object_name = "task"


class PostCreate(CreateView):
    model = Post
    form_class = PostForm  # フォームを指定する
    # fields = "__all__"
    success_url = reverse_lazy("list")

    def get_template_names(self):
        return 'post/post_form.html'


class PostUpdate(UpdateView):
    # model = Post
    form_class = PostForm  # フォームを指定する
    queryset = Post.objects.all()
    success_url = reverse_lazy("list")


class PostDelete(DeleteView):
    model = Post
    context_object_name = "task"
    success_url = reverse_lazy("list")
