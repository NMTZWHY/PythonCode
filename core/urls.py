from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt
from .views import (
    PlatformApplicationViewSet,
    UserLogin,
    UserRegister,
    AvatarUpload,
    UserUpdate,
    MyApplyList,
    PendingApplyList,
    AuditPass,
    AuditReject,
    AuditRecordList, RichImageUpload, ApplyDetail
)

router = DefaultRouter()
router.register(r'applications', PlatformApplicationViewSet, basename="platform_application")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    # 用户相关
    path('login/', csrf_exempt(UserLogin.as_view()), name='login'),
    path('register/', csrf_exempt(UserRegister.as_view()), name='register'),
    path('upload/avatar/', csrf_exempt(AvatarUpload.as_view()), name='avatar_upload'),
    path('user/update/', csrf_exempt(UserUpdate.as_view()), name='user_update'),
    # 审批业务接口（统一加csrf_exempt，和前面格式一致）
    path('my/apply/', csrf_exempt(MyApplyList.as_view()), name='my_apply'),
    path('pending/apply/', csrf_exempt(PendingApplyList.as_view()), name='pending_apply'),
    path('audit/pass/', csrf_exempt(AuditPass.as_view()), name='audit_pass'),
    path('audit/reject/', csrf_exempt(AuditReject.as_view()), name='audit_reject'),
    path('audit/record/', csrf_exempt(AuditRecordList.as_view()), name='audit_record'),
    path('upload/image/', csrf_exempt(RichImageUpload.as_view()), name='rich_img_upload'),
    path('apply/detail/', csrf_exempt(ApplyDetail.as_view()), name='apply_detail'),
]