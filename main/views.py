from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import FileUpload
from .serializers import UserSerializer, FileUploadSerializer
from .permissions import IsOpsUser

User = get_user_model()

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if not user.is_ops:
            token = RefreshToken.for_user(user)
            encrypted_url = f"{settings.BASE_URL}/api/verify-email/?token={str(token.access_token)}"
            send_mail(
                'Verify your email',
                f'Please verify your email using this link: {encrypted_url}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

class VerifyEmailView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.query_params.get('token')
        user = get_object_or_404(User, email_verified=False, email_verification_token=token)
        user.email_verified = True
        user.save()
        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({'is_ops': self.user.is_ops})
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed('Invalid credentials')

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_ops': user.is_ops,
        })

class FileUploadView(generics.CreateAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [IsOpsUser]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class ListFilesView(generics.ListAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FileUpload.objects.filter(uploaded_by=self.request.user)

class DownloadFileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        file_upload = get_object_or_404(FileUpload, pk=pk)
        if request.user in file_upload.allowed_users.all():
            encrypted_url = f"{settings.BASE_URL}/media/{file_upload.file.name}"
            return Response({"download-link": encrypted_url, "message": "success"}, status=status.HTTP_200_OK)
        return Response({"message": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
