from django.db import models
from users.models import User
# Create your models here.


class Students(models.Model):
    class Meta:
        db_table = "Students"
    
    student_first_name = models.CharField(max_length=100,blank=True,null=True)
    student_last_name = models.CharField(max_length=100,blank=True,null=True)
    student_class = models.CharField(max_length=100,blank=True,null=True)
    student_email = models.EmailField(unique=True,blank=False,null=False)
    student_address = models.CharField(max_length=250,blank=True,null=True)
    teacher = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)