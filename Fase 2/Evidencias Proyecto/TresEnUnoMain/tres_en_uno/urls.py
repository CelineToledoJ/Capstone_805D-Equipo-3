from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('miapp.urls')), 
        
    # 1. Olvidé Contraseña (Solicitar Email)
    path('auth/olvide-contrasena/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        success_url='/auth/olvide-contrasena/enviado/'
    ), name='password_reset'),
    
    # 2. Confirmación de envío
    path('auth/olvide-contrasena/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    
    # 3. Resetear Contraseña (Establecer Nueva Clave)
    path('auth/resetear-contrasena/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/auth/resetear-contrasena/completo/'
    ), name='password_reset_confirm'),
    
    # 4. Finalización
    path('auth/resetear-contrasena/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)