from django.urls import include, path

urlpatterns = [
    path('api/produtos/', include('produtos.api.urls')),
]
