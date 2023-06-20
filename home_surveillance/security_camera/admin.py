from django.contrib import admin
from .models import face_dataset
from .models import Unknown_dataset
from .models import unrecognized
# Register your models here.
admin.site.register(face_dataset)
admin.site.register(Unknown_dataset)
admin.site.register(unrecognized)