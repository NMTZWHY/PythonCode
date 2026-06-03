from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PlatformApplication(models.Model):
    """科研平台入驻申请表单模型"""
    # 状态选项
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
    )

    # ===================== 第一阶段：基本概况（补齐缺失字段）=====================
    name_cn = models.CharField('平台中文名称', max_length=200, default='')
    name_en = models.CharField('平台英文名称', max_length=200, default='')
    category = models.CharField('平台类别', max_length=50, default='')  # 1-重点实验室,2-工程研究中心,3-技术创新中心
    level = models.CharField('平台级别', max_length=50, default='')  # 1-国家级,2-省级,3-市级
    department = models.CharField('主管部门', max_length=200, default='')
    depend_unit = models.CharField('依托单位', max_length=200, default='')
    together_unit = models.CharField('共建单位', max_length=200, blank=True, null=True, default='')
    cooperate_unit = models.CharField('合作单位', max_length=200, blank=True, null=True, default='')
    approve_time = models.DateField('批准设立时间', null=True)
    approve_no = models.CharField('批准文号', max_length=100, default='')
    valid_period = models.CharField('建设期', max_length=100, default='')  # 日期范围字符串
    accept_status = models.CharField('验收状态', max_length=10, default='0')  # 0-未验收 1-已验收
    position = models.TextField('平台定位', default='')
    target = models.TextField('总体目标', default='')
    direction = models.TextField('主要研究方向', default='')

    # ===================== 第二阶段：组织结构（补齐缺失字段）=====================
    leader = models.CharField('平台负责人', max_length=100, default='')
    admin_leader = models.CharField('行政负责人', max_length=100, blank=True, null=True, default='')
    tech_leader = models.CharField('技术负责人', max_length=100, blank=True, null=True, default='')
    contact_name = models.CharField('平台联系人', max_length=100, blank=True, null=True, default='')
    contact_phone = models.CharField('联系电话', max_length=20, blank=True, null=True, default='')
    organization_structure = models.TextField('管理机构设置', blank=True, null=True, default='')
    inner_rule = models.TextField('内部管理制度', default='')
    academic_committee_structure = models.TextField('学术/技术委员会组成', blank=True, null=True, default='')
    academic_committee_duty = models.TextField('学术/技术委员会职责', blank=True, null=True, default='')

    # ===================== 第三阶段：科研队伍（补齐所有字段）=====================
    fixed_person_total = models.IntegerField('固定人员总数', default=0)
    core_person_num = models.IntegerField('核心骨干人数', default=0)
    title_structure = models.TextField('人员职称结构', default='')  # JSON
    education_structure = models.TextField('人员学历结构', default='')  # JSON
    age_structure = models.TextField('人员年龄结构', blank=True, null=True, default='')  # JSON
    academic_leader = models.TextField('学术带头人信息', default='')  # JSON
    high_level_talent = models.TextField('高层次人才情况', blank=True, null=True, default='')
    flowing_personnel = models.TextField('流动人员情况', blank=True, null=True, default='')
    talent_training = models.TextField('人才培养机制', blank=True, null=True, default='')

    # ===================== 第四阶段：科研条件（补齐所有字段）=====================
    room_area = models.CharField('科研用房面积', max_length=100, default='')
    lab_num = models.IntegerField('实验室数量', default=0)
    equipment_total = models.IntegerField('仪器设备总台套数', default=0)
    equipment_value = models.CharField('仪器设备总原值', max_length=100, default='')
    pilot_base_situation = models.TextField('中试基地情况', blank=True, null=True, default='')
    main_large_equipment = models.TextField('主要大型仪器设备', blank=True, null=True, default='')
    resource_database_situation = models.TextField('资源库/数据库情况', blank=True, null=True, default='')

    # ===================== 第五阶段：科研成果（补齐所有字段）=====================
    national_project_num = models.IntegerField('年度国家级项目数', default=0)
    provincial_project_num = models.IntegerField('年度省部级项目数', default=0)
    sci_ei_paper_num = models.IntegerField('年度发表SCI/EI论文数', default=0)
    monograph_num = models.IntegerField('年度出版专著数', default=0)
    invention_patent_num = models.IntegerField('年度授权发明专利数', default=0)
    utility_model_patent_num = models.IntegerField('年度授权实用新型专利数', default=0)
    science_award_num = models.IntegerField('年度获得科技奖励数', default=0)
    award_level_and_name = models.TextField('奖励级别及名称', blank=True, null=True, default='')
    achievement_transformation_num = models.IntegerField('成果转化项目数', default=0)
    technical_service_income = models.CharField('技术服务收入', max_length=100, blank=True, null=True, default='')

    # ===================== 第六阶段：开放共享（补齐所有字段）=====================
    open_rule = models.TextField('对外开放机制', default='')
    service_target = models.CharField('主要服务对象', max_length=200, default='')
    service_company_num = models.IntegerField('年度服务企业数', default=0)
    shared_service_process = models.TextField('共享服务流程', blank=True, null=True, default='')
    reservation_method = models.TextField('预约方式', blank=True, null=True, default='')
    charging_standard = models.TextField('收费标准', blank=True, null=True, default='')
    annual_service_income = models.CharField('年度服务收入总额', max_length=100, blank=True, null=True, default='')
    industry_university_research_project_num = models.IntegerField('产学研合作项目数', default=0)
    popular_science_training_activity_num = models.IntegerField('科普与培训活动次数', default=0)

    # ===================== 第七阶段：运行管理（补齐所有字段）=====================
    year_fund_total = models.CharField('年度经费总额', max_length=100, default='')
    asset_manage = models.TextField('资产管理情况', default='')
    safe_rule = models.TextField('安全管理制度', default='')
    long_term_plan = models.TextField('中长期发展规划', default='')
    funding_source_structure = models.TextField('经费来源结构', blank=True, null=True, default='')
    annual_work_plan = models.TextField('年度工作计划', blank=True, null=True, default='')
    main_problems = models.TextField('存在主要问题', blank=True, null=True, default='')
    improvement_measures = models.TextField('改进措施', blank=True, null=True, default='')
    annual_work_summary = models.TextField('年度工作总结', blank=True, null=True, default='')
    performance_evaluation_result = models.TextField('运行绩效考核结果', blank=True, null=True, default='')

    # ===================== 系统字段 =====================
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='申请人')
    status = models.CharField('申请状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('提交时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '平台入驻申请'
        verbose_name_plural = '平台入驻申请'
        ordering = ['-created_at']

    def __str__(self):
        return self.name_cn


# ===================== 用户扩展信息（保持你原有的不动）=====================
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='关联用户'
    )

    real_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='真实姓名', default='')
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name='昵称', default='')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='联系电话', default='')
    company = models.CharField(max_length=200, blank=True, null=True, verbose_name='单位名称', default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f"{self.user.username}的资料"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()