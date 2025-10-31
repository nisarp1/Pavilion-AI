"""
Django admin configuration for CMS.
"""
from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status', 'author', 'editor',
        'created_at', 'updated_at', 'published_at'
    ]
    list_filter = ['status', 'created_at', 'published_at']
    search_fields = ['title', 'slug', 'summary', 'body']
    readonly_fields = [
        'created_at', 'updated_at', 'generation_started_at',
        'generation_completed_at'
    ]
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'summary', 'summary_english', 'body', 'status')
        }),
        ('Media', {
            'fields': ('featured_image', 'og_image')
        }),
        ('SEO/OG', {
            'fields': (
                'meta_title', 'meta_description',
                'og_title', 'og_description'
            )
        }),
        ('Source', {
            'fields': ('source_url', 'source_feed')
        }),
        ('Authorship', {
            'fields': ('author', 'editor')
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'published_at',
                'generation_started_at', 'generation_completed_at'
            )
        }),
    )

