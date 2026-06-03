from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt  # 新增导入
from .views import (
    PlatformApplicationViewSet,
    UserLogin,
    UserRegister,
    AvatarUpload # 新增导入
)

router = DefaultRouter()
router.register(r'applications', PlatformApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    # ✅ 路由层面直接加csrf_exempt，100%生效
    path('login/', csrf_exempt(UserLogin.as_view()), name='login'),
    path('register/', csrf_exempt(UserRegister.as_view()), name='register'),
    path('upload/avatar/', AvatarUpload.as_view(), name='avatar_upload'), # 新增头像上传路由
]