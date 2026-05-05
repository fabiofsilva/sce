from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from core.api.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    # autenticação JWT
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # documentação OpenAPI — restrita a is_staff=True (configurado em SPECTACULAR_SETTINGS)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # apps
    path('', include('fornecedores.urls')),
]
