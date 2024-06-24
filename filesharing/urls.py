from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signup/', views.SignupView.as_view(), name='signup'),
    path('api/verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/upload-file/', views.FileUploadView.as_view(), name='upload-file'),
    path('api/list-files/', views.ListFilesView.as_view(), name='list-files'),
    path('api/download-file/<int:pk>/', views.DownloadFileView.as_view(), name='download-file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
