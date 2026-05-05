from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Estende o payload JWT padrão adicionando email, tenant_id, tenant_name e groups."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['tenant_id'] = user.tenant_id
        token['tenant_name'] = user.tenant.name if user.tenant else None
        token['groups'] = list(user.groups.values_list('name', flat=True))
        return token
