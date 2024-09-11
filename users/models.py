from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Role(models.Model):
    class Meta:
        db_table = "Role"
    name = models.CharField(max_length=100,blank=False,null=False)
    is_active = models.BooleanField(default=True,null=True,blank=True)
    def __str__(self):
        return self.name if self.name else None

class User(AbstractUser):
    class Meta:
        db_table = 'User'
    first_name = models.CharField(max_length=100,blank=False,null=False)
    last_name = models.CharField(max_length=100,blank=False,null=False)
    password = models.CharField(max_length=100,blank=True,null=True)
    email = models.EmailField(blank=False,null=False,unique=True)
    role = models.ForeignKey(Role,on_delete=models.SET_NULL,blank=True,null=True)
    def __str__(self):
        return self.first_name if self.first_name else self.email

    