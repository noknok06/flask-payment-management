from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post, Company, Approval, TrnPost
from .forms import PostForm
from datetime import datetime, date
from django.db.models import Q
from django.urls import reverse
import markdown

STATUS_NEW = 10
STATUS_ESTIMATE_REQUESTED = 20
STATUS_ESTIMATE_IN_PROGRESS = 30
STATUS_ORDER_PLACED = 40
STATUS_ACCOUNTED = 50
STATUS_PENDING = 90
STATUS_AGGREGATION = 100

status_mapping = {
    STATUS_NEW: '新規',
    STATUS_ESTIMATE_REQUESTED: '見積依頼済',
    STATUS_ESTIMATE_IN_PROGRESS: '見積確認中',
    STATUS_ORDER_PLACED: '発注済',
    STATUS_ACCOUNTED: '計上済',
    STATUS_PENDING: '保留',
    STATUS_AGGREGATION: '案件集約'
}

class PostStatusUpdate(DetailView):
    model = Post
    context_object_name = "task"

    def get_queryset(self):
        return Post.objects.all()

    def get_context_data(self, **kwargs):
        now = datetime.now()
        trn = TrnPost(
            post=kwargs['object'], 
            status_date=date(now.year, now.month, now.day), 
            status=STATUS_ACCOUNTED,
            notes=""
        )
        trn.save()
        return ""

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.get_context_data(object=self.object)
        return redirect(reverse('list'))

class ApprovalList(ListView):
    model = Approval
    fields = "__all__"
    context_object_name = "approval"
    template_name = 'post/approval_list.html'

    def get_queryset(self):
        return Approval.objects.all()

class CompanyList(ListView):
    model = Company
    fields = "__all__"
    context_object_name = "company"
    template_name = 'post/company_list.html'

    def get_queryset(self):
        return Company.objects.all()

class CompanyDetail(DetailView):
    model = Company
    context_object_name = "company"

    def get_queryset(self):
        return Company.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_instance = context['object']
        related_posts = Post.objects.filter(contract_partner=company_instance)

        for post in related_posts:
            post.status = status_mapping.get(post.status, "未対応")
            post.description = markdown.markdown(post.description)

        context["related_posts"] = related_posts
        return context

class PostListAll(ListView):
    model = Post
    fields = "__all__"
    context_object_name = "tasks"
    template_name = 'post/post_listall.html'

    def get_queryset(self):
        posts = Post.objects.all().order_by("recording_date")
        for post in posts:
            post.status = status_mapping.get(post.status, "未対応")
        return posts

class PostManage(ListView):
    model = Post
    fields = "__all__"
    context_object_name = "tasks"
    template_name = 'post/post_manage.html'

    def get_queryset(self):
        project = self.request.GET.get('project')
        order_date_from = self.request.GET.get('order_date_from')
        order_date_to = self.request.GET.get('order_date_to')
        recording_date = self.request.GET.get('recording_date')

        posts = Post.objects.all().order_by("order_date").filter(status=STATUS_ORDER_PLACED)

        if project:
            posts = posts.filter(title__icontains=project)

        if order_date_from:
            order_date_from = datetime.strptime(order_date_from, '%Y-%m-%d')
            posts = posts.filter(order_date__gte=order_date_from)

        if order_date_to:
            order_date_to = datetime.strptime(order_date_to, '%Y-%m-%d')
            posts = posts.filter(order_date__lte=order_date_to)

        if recording_date:
            recording_date = datetime.strptime(recording_date, '%Y-%m-%d')
            posts = posts.filter(recording_date=recording_date)

        for post in posts:
            post.status = status_mapping.get(post.status, "未対応")
        return posts

class PostList(ListView):
    model = Post
    fields = "__all__"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        try:
            tag = self.kwargs.get('tag')
            if tag:
                posts = Post.objects.filter(tag__tag=tag)
            else:
                posts = Post.objects.all()

            not_ordering_post = posts.filter(status__lt=STATUS_PENDING, order_date=None).order_by("recording_date")

            this_month_post = posts.filter(
                Q(recording_date__year=current_year, recording_date__month=current_month) |
                (Q(contract_method='毎月') & Q(status=STATUS_ORDER_PLACED))
            ).order_by("contract_partner", "recording_date")

            monthly_post = posts.filter(contract_method='毎月', status=STATUS_ESTIMATE_REQUESTED).order_by("recording_date")

            wait_record_post = posts.filter(status=STATUS_ORDER_PLACED).exclude(status=STATUS_PENDING).order_by("recording_date")

        except Exception as e:
            not_ordering_post = Post.objects.none()
            this_month_post = Post.objects.none()
            monthly_post = Post.objects.none()
            wait_record_post = Post.objects.none()
            print(e)

        context = super().get_context_data(**kwargs)

        for post in not_ordering_post:
            post.status = status_mapping.get(post.status, "未対応")
        for post in this_month_post:
            post.status = status_mapping.get(post.status, "未対応")
        for post in monthly_post:
            post.status = status_mapping.get(post.status, "未対応")
        for post in wait_record_post:
            post.status = status_mapping.get(post.status, "未対応")

        this_month_post_with_trn = [
            {'post': post, 'has_trn_post': TrnPost.objects.filter(post=post, status_date__year=current_year, status_date__month=current_month).exists()}
            for post in this_month_post
        ]

        wait_record_post_with_trn = [
            {'post': post, 'has_trn_post': TrnPost.objects.filter(post=post, status_date__year=current_year, status_date__month=current_month).exists()}
            for post in wait_record_post
        ]

        context.update({
            'not_ordering_post': not_ordering_post,
            'not_ordering_cnt': len(not_ordering_post),
            'monthly_cnt': len(monthly_post),
            'this_month_cnt': len(this_month_post),
            'this_month_post_with_trn': this_month_post_with_trn,
            'wait_record_cnt': len(wait_record_post),
            'wait_record_post_with_trn': wait_record_post_with_trn
        })
        return context

class PostDetail(DetailView):
    model = Post
    context_object_name = "task"

    def get_queryset(self):
        return Post.objects.all()

    def get_context_data(self, **kwargs):
        title = kwargs['object'].id
        related_posts = Post.objects.filter(parent_code=title)
        now = datetime.now()
        has_current_month_status = kwargs['object'].monthly_statuses.filter(
            status_date__year=now.year,
            status_date__month=now.month
        ).exists()
        all_price = sum(int(p.amount) for p in related_posts if p.amount)

        for post in related_posts:
            post.status = status_mapping.get(post.status, "未対応")

        context = super().get_context_data(**kwargs)
        context['task'].description = markdown.markdown(context['task'].description)
        context.update({
            'related_post': related_posts,
            'all_price': all_price,
            'has_current_month_status': has_current_month_status
        })
        return context

class PostCreate(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy("list")

    def get_template_names(self):
        return 'post/post_form.html'

class PostUpdate(UpdateView):
    form_class = PostForm
    queryset = Post.objects.all()

    def get_success_url(self):
        return reverse("detail", kwargs={"pk":self.object.pk})

    def post(self, request, *args, **kwargs):
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
        if request.session.get('global_page') == "manage":
            self.success_url = reverse_lazy("orderlist")
        elif request.session.get('global_page') == "alllist":
            self.success_url = reverse_lazy("listall")

        return super().post(request, *args, **kwargs)
