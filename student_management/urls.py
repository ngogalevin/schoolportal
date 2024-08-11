from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, LoginAPIView, LogoutAPIView, CheckLoginStatusAPIView, AuthView, ContactView  

router = DefaultRouter()
router.register(r'student_management', StudentViewSet)

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('check-login-status/', CheckLoginStatusAPIView.as_view(), name='check_login_status'),
    path('auth/', AuthView.as_view(), name='auth'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('', include(router.urls)),
]
