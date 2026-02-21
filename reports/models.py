from django.db import models


class MedicalReport(models.Model):
    title = models.CharField(max_length=255, default='Medical Report')
    file_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
