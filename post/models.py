from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator

# Create your models here.
class Approval(models.Model):
    title = models.CharField("稟議名", max_length=50)
    approval_file = models.FileField(
        upload_to='uploads/approval/%Y/%m/%d/',
        verbose_name='稟議書',
        validators=[FileExtensionValidator(['pdf', ])],
        blank=True, null=True
    )
    def __str__(self):
        return self.title

class Company(models.Model):

    company_name = models.CharField("会社名", max_length=50)
    company_description = models.TextField("会社説明", blank=True)
    is_valid = models.BooleanField("有効/無効")
    special_notices = models.TextField("特記事項", blank=True)
    basic_contract = models.CharField("基本契約書(WEB)", max_length=3000, blank=True, null=True,)
    basic_contract_file = models.FileField(
        upload_to='uploads/basic_contract/%Y/%m/%d/',
        verbose_name='基本契約書',
        validators=[FileExtensionValidator(['pdf', ])],
        blank=True, null=True
    )

    def __str__(self):
        return self.company_name

class Tag(models.Model):
    
    tag = models.CharField("タグ", max_length=40, blank=True, null=True,)
    
    def __str__(self):
        return self.tag
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tag"],
                name="tag_unique"
            ),
        ]


class Post(models.Model):
    
    CHOICE = (
        (99, '新規'),
        (0, '見積依頼済'),
        (1, '見積確認中'),
        (2, '発注済'),
        (3, '計上済'),
        (100, '保留'),
    )
    CHOICE_CONTRACT = (
        ('１回', '１回'),
        ('毎月', '毎月'),
        ('まとめて', 'まとめて'),
    )
    
    contract_partner = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True, db_column="契約先")
    category = models.CharField("案件分類", max_length=30, blank=True)
    title = models.CharField("案件名", max_length=100)
    
    description = models.TextField("契約内容", blank=True)

    contract_period_st = models.DateField("契約開始日", blank=True, null=True,)
    contract_period_fi = models.DateField("契約終了日", blank=True, null=True,)
    contract_method = models.CharField("支払方法", max_length=20, choices=CHOICE_CONTRACT, blank=True)
    order_date = models.DateField("発注日", blank=True, null=True,)
    recording_date = models.DateField("計上予定日", blank=True, null=True,)
    amount = models.IntegerField("見積金額", blank=True, null=True,)
    reserve_fund = models.IntegerField("予備費", blank=True, null=True,)

    approval_flg = models.BooleanField("稟議有無")
    approval_data = models.CharField("稟議", max_length=300, blank=True, null=True,)
    
    asset_registration_flg = models.BooleanField("資産登録", null=False)

    accrual_accounts = models.CharField("計上科目", max_length=40, blank=True, null=True,)

    status = models.IntegerField("ステータス", choices=CHOICE, blank=True,)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, blank=True, null=True, db_column="タグ")

    quotation_file = models.FileField(
        upload_to='uploads/quotation/%Y/%m/%d/',
        verbose_name='見積書',
        validators=[FileExtensionValidator(['pdf', ])],
        blank=True, null=True
    )
    order_file = models.FileField(
        upload_to='uploads/order/%Y/%m/%d/',
        verbose_name='注文書',
        validators=[FileExtensionValidator(['pdf', ])],
        blank=True, null=True
    )
    # 新しいフィールド
    parent_code = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    def __str__(self):
        return self.title
