"""
Serializers for CMS API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article
from workers.tasks import generate_article_task


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ArticleSerializer(serializers.ModelSerializer):
    """Article serializer."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    editor_name = serializers.CharField(source='editor.username', read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'summary_english', 'body', 'status',
            'author', 'author_name', 'editor', 'editor_name',
            'featured_image', 'featured_image_url',
            'meta_title', 'meta_description',
            'og_title', 'og_description', 'og_image', 'og_image_url',
            'source_url', 'source_feed',
            'created_at', 'updated_at', 'published_at',
            'generation_started_at', 'generation_completed_at',
        ]
        read_only_fields = [
            'id', 'slug', 'created_at', 'updated_at',
            'generation_started_at', 'generation_completed_at',
        ]
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_og_image_url(self, obj):
        if obj.og_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.og_image.url)
            return obj.og_image.url
        return None


class ArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for article lists."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'status',
            'author_name', 'created_at', 'updated_at', 'published_at',
            'source_url', 'featured_image_url',
        ]
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None


class ArticleGenerateSerializer(serializers.Serializer):
    """Serializer for triggering article generation."""
    article_id = serializers.IntegerField()
    
    def validate_article_id(self, value):
        try:
            article = Article.objects.get(id=value)
            if article.status != 'fetched':
                raise serializers.ValidationError(
                    "Article must be in 'fetched' status to generate."
                )
            return value
        except Article.DoesNotExist:
            raise serializers.ValidationError("Article not found.")
    
    def save(self):
        article_id = self.validated_data['article_id']
        # Trigger Celery task
        task = generate_article_task.delay(article_id)
        return {'task_id': task.id, 'article_id': article_id}

