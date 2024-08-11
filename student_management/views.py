from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Student
from .serializers import StudentSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.urls import reverse_lazy


logger = logging.getLogger(__name__)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def retrieve(self, request, pk=None):
        try:
            student = self.get_object()
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(student)
        return Response(serializer.data)

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        registration_number = request.data.get('registration_number')
        password = request.data.get('password')
        next_url = request.data.get('next', '/')  # Default to home page if not provided

        logger.info(f"Login attempt for {registration_number}, next_url: {next_url}")

        if not registration_number or not password:
            return Response({"error": "Registration number and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=registration_number, password=password)
        if user:
            login(request, user)
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            token, _ = Token.objects.get_or_create(user=user)

            logger.info(f"User {registration_number} authenticated successfully. Redirecting to {next_url}")

            return Response({
                'token': token.key,
                'redirect_url': next_url  # Include the next_url in the response
            })
        else:
            logger.warning(f"Failed login attempt for {registration_number}")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)




class CheckLoginStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            'user_id': user.id,
            'registration_number': user.registration_number,
            'email': user.email,
            'last_login': user.last_login,
            'is_logged_in': True
        }, status=200)


class AuthView(View):
    def get(self, request, *args, **kwargs):
        next_url = request.GET.get('next', '/')
        if request.user.is_authenticated:
            return redirect(next_url)
        return render(request, 'login.html', {'next': next_url})

    def post(self, request, *args, **kwargs):
        return LoginAPIView.as_view()(request._request, *args, **kwargs)

   
class ContactView(LoginRequiredMixin, View):
    login_url = reverse_lazy('auth')
    redirect_field_name = 'next'

    def get(self, request):
        return render(request, 'contact.html')