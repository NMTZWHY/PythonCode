from django.urls import path, include
from rest_framework.routers import DefaultRouter
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
    AuditRecordList, RichImageUpload, ApplyDetail, PlatformPublicList
)

router = DefaultRouter()
router.register(r'applications', PlatformApplicationViewSet, basename="platform_application")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    # 用户相关
    path('login/', UserLogin.as_view(), name='login'),
    path('register/', UserRegister.as_view(), name='register'),
    path('upload/avatar/', AvatarUpload.as_view(), name='avatar_upload'),
    path('user/update/', UserUpdate.as_view(), name='user_update'),
    # 审批业务接口（统一加csrf_exempt，和前面格式一致）
    path('my/apply/', MyApplyList.as_view(), name='my_apply'),
    path('pending/apply/', PendingApplyList.as_view(), name='pending_apply'),
    path('audit/pass/', AuditPass.as_view(), name='audit_pass'),
    path('audit/reject/', AuditReject.as_view(), name='audit_reject'),
    path('audit/record/', AuditRecordList.as_view(), name='audit_record'),
    path('upload/image/', RichImageUpload.as_view(), name='rich_img_upload'),
    path('apply/detail/', ApplyDetail.as_view(), name='apply_detail'),
    path('researchlist/', PlatformPublicList.as_view(), name='research_list'),
]