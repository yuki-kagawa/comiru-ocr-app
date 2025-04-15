from django.db import models
from accounts.models import Child

class LessonEvaluation(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='lesson_evaluations')
    date = models.DateField()
    teacher = models.CharField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    page = models.CharField(max_length=50)
    rating = models.FloatField()

    def __str__(self):
        return f"{self.date} - {self.subject} - {self.rating} ({self.teacher})"
