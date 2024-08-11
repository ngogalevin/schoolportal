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
    authentication_classes = []  # Disable authentication for this view
    permission_classes = []      # Disable permissions for this view
    
    def post(self, request, *args, **kwargs):
        registration_number = request.data.get('registration_number')
        password = request.data.get('password')

        if not registration_number or not password:
            return Response({"error": "Registration number and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=registration_number, password=password)
        if user:
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            token, _ = Token.objects.get_or_create(user=user)

            # Get the URL for the contact page
            contact_page_url = reverse('contact')  # Assuming 'contact' is the name of your contact page URL pattern

            # Send the token and redirect URL in the response
            response = Response({
                "token": token.key,
                "redirect_url": contact_page_url
            }, status=status.HTTP_200_OK)

            # Set the token in a secure HTTP-only cookie
            response.set_cookie(
                'authToken',
                token.key,
                httponly=True,
                secure=True,
                samesite='Strict'
            )

            return response
        else:
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
    authentication_classes = [TokenAuthentication]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            return redirect('contact')
        return render(request, 'login.html')


class ContactView(View):
    def get(self, request):
        return render(request, 'contact.html')




