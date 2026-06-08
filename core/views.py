from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import PlatformApplication, AuditRecord
from .serializers import PlatformApplicationSerializer
from django.conf import settings
import os
import uuid


# ------------------------------ 登录（已删除csrf_exempt） ------------------------------
class UserLogin(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # 关键：登录接口不需要认证

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return Response({
                "msg": "登录成功",
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "real_name": user.profile.real_name,
                    "nickname": user.profile.nickname,
                    "phone": user.profile.phone,
                    "company": user.profile.company,
                    "avatar": user.profile.avatar.name if user.profile.avatar else "",
                    "role": user.profile.role,
                }
            })
        return Response({"msg": "用户名或密码错误"}, status=401)


# ------------------------------ 注册（已删除csrf_exempt） ------------------------------
class UserRegister(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")

        real_name = request.data.get("real_name", "")
        nickname = request.data.get("nickname", "")
        phone = request.data.get("phone", "")
        company = request.data.get("company", "")

        if not username or not password:
            return Response({"msg": "用户名和密码不能为空"}, status=400)
        if len(password) < 6:
            return Response({"msg": "密码长度不能少于6位"}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({"msg": "用户名已存在"}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        user.profile.real_name = real_name
        user.profile.nickname = nickname
        user.profile.phone = phone
        user.profile.company = company
        user.profile.save()

        return Response({"msg": "注册成功"})


# ------------------------------ 头像上传（已删除csrf_exempt） ------------------------------
class AvatarUpload(APIView):
    permission_classes = [IsAuthenticated]  # 必须登录才能上传头像

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"msg": "没有上传文件"}, status=400)

        allowed_types = ['image/jpeg', 'image/png']
        if file.content_type not in allowed_types:
            return Response({"msg": "只能上传 JPG/PNG 格式的图片"}, status=400)
        if file.size > 1 * 1024 * 1024:
            return Response({"msg": "图片大小不能超过 1MB"}, status=400)

        old_filename = None
        if "old_avatar" in request.data:
            path = request.data.get("old_avatar")
            old_filename = path.split("/")[-1]

        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(settings.MEDIA_ROOT, 'avatars', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        if old_filename:
            try:
                full_old_path = os.path.join(settings.MEDIA_ROOT, 'avatars', old_filename)
                if os.path.exists(full_old_path):
                    os.remove(full_old_path)
            except:
                pass

        file_url = f"{settings.MEDIA_URL}avatars/{filename}"
        return Response({"msg": "上传成功", "data": {"url": file_url}})


# ------------------------------ 用户信息修改（已删除csrf_exempt） ------------------------------
class UserUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user  # 直接取当前登录用户，更安全

        real_name = request.data.get("real_name", "")
        nickname = request.data.get("nickname", "")
        phone = request.data.get("phone", "")
        company = request.data.get("company", "")
        avatar = request.data.get("avatar", "")

        user.profile.real_name = real_name
        user.profile.nickname = nickname
        user.profile.phone = phone
        user.profile.company = company
        if avatar:
            user.profile.avatar = avatar
        user.profile.save()

        return Response({
            "msg": "用户信息修改成功",
            "user": {
                "username": user.username,
                "real_name": user.profile.real_name,
                "nickname": user.profile.nickname,
                "phone": user.profile.phone,
                "company": user.profile.company,
                "avatar": user.profile.avatar.name if user.profile.avatar else ""
            }
        })


# ------------------------------ 科研平台申请（无需修改） ------------------------------
class PlatformApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = PlatformApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role in (1, 2):
            return PlatformApplication.objects.all()
        return PlatformApplication.objects.filter(applicant=user)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            print("====校验错误详情====", ser.errors)
            return Response(ser.errors, status=400)
        ser.save(applicant=request.user)
        return Response(ser.data, status=201)


# ------------------------------ 我的申报列表 ------------------------------
class MyApplyList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 查询当前用户所有申请单
        apps = PlatformApplication.objects.filter(applicant=request.user).prefetch_related("audit_records")
        data = []
        for item in apps:
            # 获取最新一条审批记录
            latest_audit = item.audit_records.last()
            audit_time = ""
            reject_reason = ""
            audit_result = item.status

            if latest_audit:
                audit_time = latest_audit.audit_time.strftime("%Y-%m-%d %H:%M")
                reject_reason = latest_audit.reject_reason if latest_audit.reject_reason else ""

            data.append({
                "id": item.id,
                "name_cn": item.name_cn,
                "depend_unit": item.depend_unit,
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": item.status,  # 审批状态：pending/approved/rejected
                "audit_time": audit_time,  # 审批时间
                "reject_reason": reject_reason,  # 驳回原因
                "audit_result": audit_result
            })
        return Response(data)


# ------------------------------ 待审批列表（仅管理员） ------------------------------
class PendingApplyList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.profile.role not in (1, 2):
            return Response({"msg": "无权限"}, status=403)

        # 只查待审核数据，管理员可见
        apps = PlatformApplication.objects.filter(status="pending")
        data = []
        for item in apps:
            data.append({
                "id": item.id,
                "username": item.applicant.username,
                "name_cn": item.name_cn,
                "depend_unit": item.depend_unit,
                "contact_phone": item.contact_phone,
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": item.status
            })
        return Response(data)


# ------------------------------ 审批通过 ------------------------------
class AuditPass(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.profile.role not in (1, 2):
            return Response({"msg": "无权限"}, status=403)

        apply_id = request.data.get("id")
        app = PlatformApplication.objects.get(id=apply_id)
        app.status = "approved"
        app.save()

        AuditRecord.objects.create(
            apply=app,
            audit_user=request.user,
            result="approved"
        )
        return Response({"msg": "审批通过"})


# ------------------------------ 审批驳回 ------------------------------
class AuditReject(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.profile.role not in (1, 2):
            return Response({"msg": "无权限"}, status=403)

        apply_id = request.data.get("id")
        reason = request.data.get("reject_reason", "")
        app = PlatformApplication.objects.get(id=apply_id)
        app.status = "rejected"
        app.reject_reason = reason
        app.save()

        AuditRecord.objects.create(
            apply=app,
            audit_user=request.user,
            result="rejected",
            reject_reason=reason
        )
        return Response({"msg": "已驳回"})


# ------------------------------ 审批历史 ------------------------------
class AuditRecordList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.profile.role not in (1, 2):
            return Response({"msg": "无权限"}, status=403)

        records = AuditRecord.objects.all()
        data = []
        for r in records:
            data.append({
                "id": r.id,
                "username": r.apply.applicant.username,
                "name_cn": r.apply.name_cn,
                "depend_unit": r.apply.depend_unit,
                "result": r.result,
                "reject_reason": r.reject_reason,
                "audit_time": r.audit_time.strftime("%Y-%m-%d %H:%M"),
            })
        return Response(data)
# ------------------------------ 富文本图片上传 ------------------------------
class RichImageUpload(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"code": 400, "msg": "未选择图片"}, status=400)

        # 格式、大小校验
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if file.content_type not in allowed_types:
            return Response({"code": 400, "msg": "仅支持 JPG/PNG/GIF 图片"}, status=400)
        if file.size > 2 * 1024 * 1024:
            return Response({"code": 400, "msg": "图片大小不能超过 2MB"}, status=400)

        # 生成文件名 & 保存
        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        save_dir = os.path.join(settings.MEDIA_ROOT, 'rich_images')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        with open(save_path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)

        img_url = f"{settings.MEDIA_URL}rich_images/{filename}"
        return Response({
            "code": 200,
            "msg": "上传成功",
            "data": {
                "url": img_url
            }
        })


class ApplyDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        apply_id = request.query_params.get("id")
        if not apply_id:
            return Response({"msg": "参数缺失"}, status=400)

        try:
            app = PlatformApplication.objects.get(id=apply_id)
        except PlatformApplication.DoesNotExist:
            return Response({"msg": "数据不存在"}, status=404)

        # 权限校验：普通用户只能看自己的，管理员可看全部
        user = request.user
        if user.profile.role == 0 and app.applicant != user:
            return Response({"msg": "无权限查看"}, status=403)

        # 格式化时间、空值统一处理，完全匹配前端模板
        data = {
            # 基础信息
            "id": app.id,
            "name_cn": app.name_cn or "未填写",
            "name_en": app.name_en or "未填写",
            "category": app.category or "",
            "level": app.level or "",
            "department": app.department or "未填写",
            "depend_unit": app.depend_unit or "未填写",
            "together_unit": app.together_unit or "未填写",
            "cooperate_unit": app.cooperate_unit or "未填写",
            "approve_time": app.approve_time.strftime("%Y-%m-%d") if app.approve_time else "未填写",
            "approve_no": app.approve_no or "未填写",
            "valid_period": app.valid_period or "未填写",
            "accept_status": app.accept_status or "0",
            "position": app.position or "未填写",
            "target": app.target or "未填写",
            "direction": app.direction or "未填写",

            # 组织结构
            "leader": app.leader or "未填写",
            "admin_leader": app.admin_leader or "未填写",
            "tech_leader": app.tech_leader or "未填写",
            "contact_name": app.contact_name or "未填写",
            "contact_phone": app.contact_phone or "未填写",
            "organization_structure": app.organization_structure or "未填写",
            "inner_rule": app.inner_rule or "未填写",
            "academic_committee_structure": app.academic_committee_structure or "未填写",
            "academic_committee_duty": app.academic_committee_duty or "未填写",

            # 科研队伍
            "fixed_person_total": app.fixed_person_total or 0,
            "core_person_num": app.core_person_num or 0,
            "title_structure": app.title_structure or "未填写",
            "education_structure": app.education_structure or "未填写",
            "age_structure": app.age_structure or "未填写",
            "academic_leader": app.academic_leader or "未填写",
            "high_level_talent": app.high_level_talent or "未填写",
            "flowing_personnel": app.flowing_personnel or "未填写",
            "talent_training": app.talent_training or "未填写",

            # 科研条件
            "room_area": app.room_area or "未填写",
            "lab_num": app.lab_num or 0,
            "equipment_total": app.equipment_total or 0,
            "equipment_value": app.equipment_value or "未填写",
            "pilot_base_situation": app.pilot_base_situation or "未填写",
            "main_large_equipment": app.main_large_equipment or "未填写",
            "resource_database_situation": app.resource_database_situation or "未填写",

            # 科研成果
            "national_project_num": app.national_project_num or 0,
            "provincial_project_num": app.provincial_project_num or 0,
            "sci_ei_paper_num": app.sci_ei_paper_num or 0,
            "monograph_num": app.monograph_num or 0,
            "invention_patent_num": app.invention_patent_num or 0,
            "utility_model_patent_num": app.utility_model_patent_num or 0,
            "science_award_num": app.science_award_num or 0,
            "award_level_and_name": app.award_level_and_name or "未填写",
            "achievement_transformation_num": app.achievement_transformation_num or 0,
            "technical_service_income": app.technical_service_income or "未填写",

            # 开放共享
            "open_rule": app.open_rule or "未填写",
            "service_target": app.service_target or "未填写",
            "service_company_num": app.service_company_num or 0,
            "shared_service_process": app.shared_service_process or "未填写",
            "reservation_method": app.reservation_method or "未填写",
            "charging_standard": app.charging_standard or "未填写",
            "annual_service_income": app.annual_service_income or "未填写",
            "industry_university_research_project_num": app.industry_university_research_project_num or 0,
            "popular_science_training_activity_num": app.popular_science_training_activity_num or 0,

            # 运行管理
            "year_fund_total": app.year_fund_total or "未填写",
            "asset_manage": app.asset_manage or "未填写",
            "safe_rule": app.safe_rule or "未填写",
            "long_term_plan": app.long_term_plan or "未填写",
            "funding_source_structure": app.funding_source_structure or "未填写",
            "annual_work_plan": app.annual_work_plan or "未填写",
            "main_problems": app.main_problems or "未填写",
            "improvement_measures": app.improvement_measures or "未填写",
            "annual_work_summary": app.annual_work_summary or "未填写",
            "performance_evaluation_result": app.performance_evaluation_result or "未填写",

            # 状态与时间
            "status": app.status,
            "reject_reason": app.reject_reason or "未填写",
            "created_at": app.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 追加审批记录
        latest_audit = app.audit_records.last()
        if latest_audit:
            data["audit_time"] = latest_audit.audit_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["audit_time"] = ""

        return Response(data)