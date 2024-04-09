from django.db import models


class Task(models.Model):

    taskName = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000)
    modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.recipeName