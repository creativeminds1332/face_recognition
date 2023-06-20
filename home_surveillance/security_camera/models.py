from django.db import models

# Create your models here.
class face_dataset(models.Model):
    firstname=models.CharField(max_length=64)
    secondname=models.CharField(max_length=64)
    title=models.CharField(max_length=64)
    reg_date =models.DateTimeField(auto_now_add=True)
    image=models.FileField(upload_to='dataset/')
    def __str__(self):
        return self.firstname + ' ' + self.secondname

class Unknown_dataset(models.Model):
    capture_date=models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='dataset/')
    title=models.CharField(max_length=64, null=True)
class unrecognized(models.Model):
    serial_no=models.IntegerField(null=False, blank=False)
    cap_date=models.DateTimeField(auto_now_add=True)
    status=models.IntegerField(null=True, blank=True)