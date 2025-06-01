import random
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

# Create your models here.
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ("archived", "Archived")
    )
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField("Category", related_name="posts")


    class Meta:
        ordering = ['-created_at', 'title']
    def __str__ (self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)+ str(random.randint(1, 1000000))
        super().save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = [ 'name']
    def __str__ (self):
        return self.name
