"""
Serializers for CMS API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article, Category
from workers.tasks import generate_article_task


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer with nested children."""
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'parent_name',
            'order', 'is_active', 'children', 'article_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def validate_parent(self, value):
        """Validate parent category."""
        if value and value.id == getattr(self.instance, 'id', None):
            raise serializers.ValidationError("A category cannot be its own parent.")
        return value
    
    def get_children(self, obj):
        """Get child categories."""
        children = obj.children.filter(is_active=True).order_by('order', 'name')
        return CategorySerializer(children, many=True).data
    
    def get_article_count(self, obj):
        """Get count of articles in this category."""
        return obj.articles.count()


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight category serializer for lists."""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'parent_name',
            'order', 'is_active', 'children_count'
        ]
    
    def get_children_count(self, obj):
        """Get count of child categories."""
        return obj.children.filter(is_active=True).count()


class ArticleSerializer(serializers.ModelSerializer):
    """Article serializer."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    editor_name = serializers.CharField(source='editor.username', read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()
    categories = CategoryListSerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.filter(is_active=True),
        source='categories',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'summary_english', 'body', 'status', 'category',
            'categories', 'category_ids',
            'author', 'author_name', 'editor', 'editor_name',
            'featured_image', 'featured_image_url',
            'meta_title', 'meta_description',
            'og_title', 'og_description', 'og_image', 'og_image_url',
            'source_url', 'source_feed', 'trend_data',
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
    categories = CategoryListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'status', 'category',
            'categories',
            'author_name', 'created_at', 'updated_at', 'published_at',
            'source_url', 'featured_image_url', 'trend_data',
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

