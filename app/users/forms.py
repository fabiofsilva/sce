from django.contrib.auth.forms import BaseUserCreationForm

from .models import User


class UserCriacaoForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'tenant')
