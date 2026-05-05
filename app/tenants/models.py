from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    name = models.CharField(verbose_name='Nome', max_length=255, unique=True)
    slug = models.SlugField(verbose_name='Slug', max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(verbose_name='Ativo', default=True)
    created_at = models.DateTimeField(verbose_name='Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
