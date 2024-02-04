from django.db import models
from django.utils import timezone

# Create your models here.
class Post(models.Model):
    
    CHOICE = (
        (0, '見積依頼済'),
        (1, '見積確認中'),
        (2, '発注済'),
        (3, '計上済'),
    )
    CHOICE_CONTRACT = (
        ('１回', '１回'),
        ('毎月', '毎月'),
        ('まとめて', 'まとめて'),
    )
    
    contract_partner = models.CharField("契約先", max_length=30)
    category = models.CharField("案件分類", max_length=30, blank=True)
    title = models.CharField("案件名", max_length=30)
    
    description = models.TextField("契約内容", blank=True)

    contract_period_st = models.DateField("契約開始日", blank=True)
    contract_period_fi = models.DateField("契約終了日", blank=True)
    contract_method = models.CharField("支払方法", max_length=20, choices=CHOICE_CONTRACT, blank=True)
    order_date = models.DateField("発注日", blank=True)
    recording_date = models.DateField("計上予定日", blank=True)

    approval_flg = models.BooleanField("稟議有無")
    approval_data = models.CharField("稟議", max_length=300, blank=True)

    status = models.IntegerField("ステータス", max_length=20, choices=CHOICE)

    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    def __str__(self):
        return self.title
