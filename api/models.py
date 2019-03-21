from django.db import models


class Image(models.Model):

    image = models.ImageField(blank=False, null=False)


class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

