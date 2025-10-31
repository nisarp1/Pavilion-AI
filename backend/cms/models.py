"""
CMS models for article management.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from slugify import slugify


class Article(models.Model):
    """Article model for CMS."""
    
    STATUS_CHOICES = [
        ('fetched', 'Fetched'),      # Article fetched from RSS
        ('draft', 'Draft'),          # Article generated and ready for editing
        ('published', 'Published'),  # Article published
        ('archived', 'Archived'),    # Article archived
    ]
    
    title = models.CharField(max_length=255)  # Malayalam title
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # English slug
    summary = models.TextField(blank=True)  # Malayalam summary
    summary_english = models.TextField(blank=True, help_text="English summary")  # English summary
    body = models.TextField(blank=True)  # Malayalam body content
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='fetched'
    )
    
    # Author/Editor
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_articles'
    )
    editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_articles'
    )
    
    # Images
    featured_image = models.ImageField(
        upload_to='articles/featured/',
        null=True,
        blank=True
    )
    
    # SEO/OG Data
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    og_title = models.CharField(max_length=255, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(
        upload_to='articles/og/',
        null=True,
        blank=True
    )
    
    # RSS Source Data
    source_url = models.URLField(blank=True)
    source_feed = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Generation metadata
    generation_started_at = models.DateTimeField(null=True, blank=True)
    generation_completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def publish(self):
        """Mark article as published."""
        self.status = 'published'
        if not self.published_at:
            self.published_at = timezone.now()
        self.save()

