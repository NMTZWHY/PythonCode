from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # 新增导入
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PlatformApplication
from .serializers import PlatformApplicationSerializer
from django.conf import settings
import os
import uuid


# 登录接口
@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(APIView):
    permission_classes = [AllowAny]

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
                    "avatar": user.profile.avatar.name if user.profile.avatar else ""
                }
            })
        return Response({"msg": "用户名或密码错误"}, status=401)


# 注册接口
@method_decorator(csrf_exempt, name='dispatch')
class UserRegister(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 原生字段
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")

        # 扩展字段
        real_name = request.data.get("real_name", "")
        nickname = request.data.get("nickname", "")
        phone = request.data.get("phone", "")
        company = request.data.get("company", "")
        avatar = request.data.get("avatar", "")

        # 验证
        if not username or not password:
            return Response({"msg": "用户名和密码不能为空"}, status=401)
        if len(password) < 6:
            return Response({"msg": "密码长度不能少于6位"}, status=401)
        if User.objects.filter(username=username).exists():
            return Response({"msg": "用户名已存在"}, status=401)

        # 创建用户
        user = User.objects.create_user(username=username, password=password, email=email)
        # 保存扩展信息
        user.profile.real_name = real_name
        user.profile.nickname = nickname
        user.profile.phone = phone
        user.profile.company = company
        if avatar:
            user.profile.avatar = avatar
        user.profile.save()

        return Response({"msg": "注册成功"})


# 新增：头像上传接口
@method_decorator(csrf_exempt, name='dispatch')
class AvatarUpload(APIView):
    permission_classes = [AllowAny]  # 允许未登录用户上传头像

    def post(self, request):
        # 获取上传的文件
        file = request.FILES.get('file')

        if not file:
            return Response({"msg": "没有上传文件"}, status=400)

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png']
        if file.content_type not in allowed_types:
            return Response({"msg": "只能上传 JPG/PNG 格式的图片"}, status=400)

        # 验证文件大小（2MB）
        if file.size > 2 * 1024 * 1024:
            return Response({"msg": "图片大小不能超过 2MB"}, status=400)

        # 生成唯一文件名（避免重名）
        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        # 保存路径：media/avatars/文件名
        save_path = os.path.join(settings.MEDIA_ROOT, 'avatars', filename)

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 保存文件
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 返回文件URL
        file_url = f"{settings.MEDIA_URL}avatars/{filename}"
        return Response({"msg": "上传成功", "data": {"url": file_url}})

class PlatformApplicationViewSet(viewsets.ModelViewSet):
    """科研平台入驻申请API"""
    queryset = PlatformApplication.objects.all()
    serializer_class = PlatformApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)