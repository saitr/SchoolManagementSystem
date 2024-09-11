from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('user', UserAPIView, basename='User')
router.register('login',LoginAPIView,basename='Login')
router.register('logout',LogoutAPIView,basename='Logout')
router.register('teacher',TeacherListAPIView,basename="Teacher")
router.register('admin',AdminListAPIView,basename='Admin')
router.register('role',RoleAPIView,basename="Role")
urlpatterns = [
    path('', include(router.urls)),
]
