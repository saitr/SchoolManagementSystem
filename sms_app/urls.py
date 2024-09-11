from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentsAPIView

router = DefaultRouter()
router.register('student', StudentsAPIView, basename='students')

urlpatterns = [
    path('', include(router.urls)),
]