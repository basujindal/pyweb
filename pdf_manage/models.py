from django.db import models


class UploadModel(models.Model):
    upload_title = models.CharField(max_length=50, default="")
    upload_file = models.FileField()

    # resumes = models.FileField(upload_to=’resumes/’, blank=True, null=True)
