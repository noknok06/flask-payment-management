from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy
from .models import Post, Company, Approval
from .forms import PostForm
from datetime import datetime, timedelta
from django.db.models import Q

import markdown

# グローバル変数を定義
# global_page = ""

status_mapping = {
    0: '見積依頼済',
    1: '見積確認中',
    2: '発注済',
    3: '計上済',
    99: '新規',
    100: '保留'
}

class ApprovalList(ListView):
    model = Approval
    fields = "__all__"
    context_object_name = "approval"
    template_name = 'post/approval_list.html'
    # paginate_by = 10
    
    def get_queryset(self):
        posts = Approval.objects.all()
        return posts

class CompanyList(ListView):
    model = Company
    fields = "__all__"
    context_object_name = "company"
    template_name = 'post/company_list.html'
    # paginate_by = 10
    
    def get_queryset(self):
        posts = Company.objects.all()
        return posts


class CompanyDetail(DetailView):
    model = Company
    context_object_name = "company"

    def get_queryset(self):
        return Company.objects.all()
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        company_instance = context['object']
        company_name = company_instance.company_name
        company_instance = Company.objects.get(company_name=company_name)
        related_posts = Post.objects.filter(contract_partner=company_instance)

        for post in related_posts:
            post.status = status_mapping.get(post.status, "未対応")
            post.description = markdown.markdown(post.description)

        context = super().get_context_data(**kwargs)
        # context['object'].company_description = markdown.markdown(context['object'].company_description)
        context["related_posts"] = related_posts
        return context

class PostListAll(ListView):
    model = Post
    fields = "__all__"
    context_object_name = "tasks"
    template_name = 'post/post_listall.html'
    # paginate_by = 10
    
    def get_queryset(self):
        
        # global global_page
        # global_page = "alllist"

        posts = Post.objects.all().order_by("recording_date")
        for post in posts:
            post.status = status_mapping.get(post.status, "未対応")

        return posts


class PostManage(ListView):
    model = Post
    fields = "__all__"
    context_object_name = "tasks"
    template_name = 'post/post_manage.html'
    # paginate_by = 10

    
    def get_queryset(self):
        project = self.request.GET.get('project')
        # status = self.request.GET.get('status')
        order_date_from = self.request.GET.get('order_date_from')
        order_date_to = self.request.GET.get('order_date_to')
        recording_date = self.request.GET.get('recording_date')

        posts = Post.objects.all().order_by("order_date").filter(status=2)
            
        # global global_page
        # global_page = "manage"

        # Filter by project
        if project:
            posts = posts.filter(title__icontains=project)

        if order_date_from:
            order_date_from = datetime.strptime(order_date_from, '%Y-%m-%d')
            posts = posts.filter(order_date__gte=order_date_from)

        if order_date_to:
            order_date_to = datetime.strptime(order_date_to, '%Y-%m-%d')
            posts = posts.filter(order_date__lte=order_date_to)
            
        if recording_date:
            order_date_to = datetime.strptime(recording_date, '%Y-%m-%d')
            posts = posts.filter(recording_date=recording_date)

        for post in posts:
            post.status = status_mapping.get(post.status, "未対応")
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

        # global global_page
        # global_page = "list"

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
            tag = self.kwargs.get('tag')
            if tag == None:  
                posts = Post.objects.all()
            else:
                posts = Post.objects.filter(tag__tag=tag)
            
            not_ordering_post = posts.filter(
                status__lt=100,
                order_date = None,
            ).order_by("recording_date")
            
            today = now.date()
            delay_accounting_post = posts.filter(
                status__lt='3',
                recording_date__lt=today
                )

            current_month = today.month
            this_month_post = posts.filter(
                Q(status='2', recording_date__month=current_month) | Q(status='3', recording_date__month=current_month)
              
            ).order_by("contract_partner","recording_date")

            monthly_post = posts.filter(
                contract_method__in=['毎月'], status='2'
            ).order_by("recording_date")

            # 翌月以降の投稿を抽出
            next_month_post = posts.filter(
                recording_date__gte=next_month_first_day, status='2'
            ).order_by("recording_date")
            
            # 計上待ち
            wait_record_post = posts.exclude(
                status__icontains='3'
            ).exclude(
                status__icontains='100'
            ).order_by("recording_date")

        except Exception as e:
            not_ordering_post = Post.objects.none()
            delay_accounting_post = Post.objects.none()
            this_month_post = Post.objects.none()
            monthly_post = Post.objects.none()
            next_month_post = Post.objects.none()
            wait_record_post = Post.objects.none()
            print(e)

        context = super().get_context_data(**kwargs)

        for post in not_ordering_post:
            post.status = status_mapping.get(post.status, "未対応")
        for post in delay_accounting_post:
            post.status = status_mapping.get(post.status, "未対応")
        for post in this_month_post:
            post.status = status_mapping.get(post.status, "未対応")
        for post in monthly_post:
            post.status = status_mapping.get(post.status, "未対応")
        for post in next_month_post:
            post.status = status_mapping.get(post.status, "未対応")
        for post in wait_record_post:
            post.status = status_mapping.get(post.status, "未対応")

        context['not_ordering_post'] = not_ordering_post
        context['not_ordering_cnt'] = len(not_ordering_post)
        context['delay_accounting_post'] = delay_accounting_post
        context['delay_accounting_cnt'] = len(delay_accounting_post)
        context['this_month_post'] = this_month_post
        context['this_month_cnt'] = len(this_month_post)
        context['monthly_post'] = monthly_post
        context['monthly_cnt'] = len(monthly_post)
        context['next_month_post'] = next_month_post
        context['next_month_cnt'] = len(next_month_post)
        context['wait_record_post'] = wait_record_post
        context['wait_record_cnt'] = len(wait_record_post)
        return context


class PostDetail(DetailView):
    model = Post
    context_object_name = "task"

    # def get_queryset(self):
        
    #     global global_page
    #     global_page = "detail"

    def get_queryset(self):
        return Post.objects.all()
    
    def get_context_data(self, **kwargs):
        # global global_page
        # global_page = "detail"
        title = kwargs['object'].id
        print("id:" + str(title))
        related_posts = Post.objects.filter(parent_code=title)
        all_price = 0
        
        for post in related_posts:
            post.status = status_mapping.get(post.status, "未対応")
            
        for p in related_posts:
            try:
                all_price = all_price + int(p.amount)
            except Exception as e:
                print(e)
        print(related_posts)
        context = super().get_context_data(**kwargs)
        context['task'].description = markdown.markdown(context['task'].description)
        context['related_post'] = related_posts
        context['all_price'] = all_price
        return context

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
    
    def post(self, request, *args, **kwargs):
        # global global_page
        # if global_page == "manage":
        #     self.success_url = reverse_lazy("orderlist")  # 成功時のリダイレクト先を変更する
        # elif global_page == "alllist":
        #     self.success_url = reverse_lazy("listall") 
        # elif global_page == "detail":
        #     self.success_url = reverse_lazy("detail", kwargs={'pk': kwargs['pk']})
        # else:
        #     pass
        if request.session.get('global_page') == "manage":
            self.success_url = reverse_lazy("orderlist")
        elif request.session.get('global_page') == "alllist":
            self.success_url = reverse_lazy("listall")
        elif request.session.get('global_page') == "detail":
            self.success_url = reverse_lazy("detail", kwargs={'pk': kwargs['pk']})

        return super().post(request, *args, **kwargs)

class PostDelete(DeleteView):
    model = Post
    success_url = reverse_lazy("list")
    context_object_name = "task"

    def post(self, request, *args, **kwargs):
        # global global_page
        # if global_page == "manage":
        #     self.success_url = reverse_lazy("orderlist")  # 成功時のリダイレクト先を変更する
        # elif global_page == "alllist":
        #     self.success_url = reverse_lazy("listall") 
        # else:
        #     pass
        if request.session.get('global_page') == "manage":
            self.success_url = reverse_lazy("orderlist")
        elif request.session.get('global_page') == "alllist":
            self.success_url = reverse_lazy("listall")

        return super().post(request, *args, **kwargs)
