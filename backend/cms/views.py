"""
API views for CMS.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Article, Category, Media, WebStory
from .serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticleGenerateSerializer,
    CategorySerializer,
    CategoryListSerializer,
    MediaSerializer,
    WebStorySerializer,
    WebStoryListSerializer,
)


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing articles.
    """
    queryset = Article.objects.all()
    
    def get_permissions(self):
        """
        Allow public read access (list, retrieve) but require authentication for write operations.
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        queryset = Article.objects.all()
        status_filter = self.request.query_params.get('status', None)
        category_filter = self.request.query_params.get('category', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if category_filter:
            # Try to filter by categories (many-to-many) using slug first
            # This handles category slugs like 'cricket', 'football', etc.
            try:
                category_obj = Category.objects.filter(slug=category_filter, is_active=True).first()
                if category_obj:
                    queryset = queryset.filter(categories=category_obj)
                else:
                    # Fallback: filter by source category (for backward compatibility)
                    # This handles source categories like 'reliable_sources', 'trends', etc.
                    queryset = queryset.filter(category=category_filter)
            except Exception as e:
                # If category lookup fails, fallback to source category
                queryset = queryset.filter(category=category_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """
        Trigger article generation for a fetched article.
        Works synchronously if Celery is not available.
        """
        article = self.get_object()
        
        if article.status != 'fetched':
            return Response(
                {'error': "Article must be in 'fetched' status to generate."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to use Celery if available, otherwise run synchronously
        try:
            from workers.tasks import generate_article_task
            # Try to run as Celery task
            task = generate_article_task.delay(article.id)
            return Response({
                'message': 'Article generation started',
                'task_id': task.id,
                'article_id': article.id
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as celery_error:
            # Celery not available, run synchronously
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Celery not available, running synchronously: {str(celery_error)}")
            
            try:
                from workers.tasks import _generate_article_task_impl
                # Call the implementation function directly (synchronously)
                result = _generate_article_task_impl(article.id)
                
                # Refresh article from database
                article.refresh_from_db()
                
                if result and result.get('success'):
                    return Response({
                        'message': 'Article generated successfully',
                        'article_id': article.id,
                        'status': article.status
                    }, status=status.HTTP_200_OK)
                else:
                    error_msg = result.get('error', 'Generation failed') if result else 'Generation failed'
                    logger.error(f"Article generation failed: {error_msg}")
                    return Response({
                        'error': error_msg
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ImportError as import_error:
                logger.error(f"Failed to import generation function: {str(import_error)}")
                return Response({
                    'error': f'Failed to import generation module: {str(import_error)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"Error generating article: {str(e)}", exc_info=True)
                return Response({
                    'error': f'Generation error: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish an article.
        """
        article = self.get_object()
        article.publish()
        article.editor = request.user
        article.save()
        
        serializer = self.get_serializer(article)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive an article.
        """
        article = self.get_object()
        article.status = 'archived'
        article.save()
        
        serializer = self.get_serializer(article)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update multiple articles.
        Expected payload: {
            "article_ids": [1, 2, 3],
            "updates": {
                "category_ids": [1, 2],  # Add categories (will be merged with existing)
                "status": "published",    # Update status
                "category": "trends"      # Update source category
            }
        }
        """
        article_ids = request.data.get('article_ids', [])
        updates = request.data.get('updates', {})
        
        if not article_ids:
            return Response(
                {'error': 'article_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not updates:
            return Response(
                {'error': 'updates is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            articles = Article.objects.filter(id__in=article_ids)
            updated_count = 0
            
            for article in articles:
                # Update status if provided
                if 'status' in updates:
                    article.status = updates['status']
                    if updates['status'] == 'published' and not article.published_at:
                        from django.utils import timezone
                        article.published_at = timezone.now()
                
                # Update source category if provided
                if 'category' in updates:
                    article.category = updates['category']
                
                # Handle category_ids - add to existing categories
                if 'category_ids' in updates:
                    category_ids = updates['category_ids']
                    if category_ids:  # Only update if not empty
                        # Get category objects
                        categories = Category.objects.filter(id__in=category_ids, is_active=True)
                        # Add to existing categories (use set to avoid duplicates)
                        existing_ids = set(article.categories.values_list('id', flat=True))
                        new_ids = set(category_ids)
                        # Merge: add new categories, keep existing
                        all_ids = list(existing_ids | new_ids)
                        article.categories.set(all_ids)
                
                article.save()
                updated_count += 1
            
            return Response({
                'message': f'Successfully updated {updated_count} article(s)',
                'updated_count': updated_count
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories and subcategories.
    """
    queryset = Category.objects.all()
    
    def get_permissions(self):
        """
        Allow public read access (list, retrieve, tree) but require authentication for write operations.
        """
        if self.action in ['list', 'retrieve', 'tree', 'children']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_queryset(self):
        queryset = Category.objects.all()
        parent_only = self.request.query_params.get('parent_only', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if parent_only == 'true':
            # Return only parent categories (no parent)
            queryset = queryset.filter(parent__isnull=True)
        
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('order', 'name')
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Get all children of a category."""
        category = self.get_object()
        children = category.children.filter(is_active=True).order_by('order', 'name')
        serializer = CategoryListSerializer(children, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree with all parents and children."""
        parents = Category.objects.filter(parent__isnull=True, is_active=True).order_by('order', 'name')
        serializer = CategorySerializer(parents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """Batch update category order and parent relationships."""
        updates = request.data.get('updates', [])
        
        if not isinstance(updates, list):
            return Response(
                {'error': 'updates must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            for update in updates:
                category_id = update.get('id')
                if not category_id:
                    continue
                
                category = Category.objects.get(id=category_id)
                
                if 'order' in update:
                    category.order = update['order']
                
                if 'parent' in update:
                    parent_id = update['parent']
                    if parent_id:
                        category.parent = Category.objects.get(id=parent_id)
                    else:
                        category.parent = None
                
                category.save()
            
            return Response({'message': 'Categories updated successfully'})
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MediaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing media library.
    """
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        queryset = Media.objects.all()
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(alt_text__icontains=search) |
                Q(description__icontains=search) |
                Q(file__icontains=search)
            )
        
        # Filter by MIME type (images only for now)
        mime_type = self.request.query_params.get('mime_type', None)
        if mime_type:
            queryset = queryset.filter(mime_type__startswith=mime_type)
        else:
            # Default to images only
            queryset = queryset.filter(mime_type__startswith='image/')
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class WebStoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing web stories.
    """
    queryset = WebStory.objects.all().prefetch_related('slides')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            include_slides = self.request.query_params.get('include_slides', '').lower() == 'true'
            if include_slides:
                return WebStorySerializer
            return WebStoryListSerializer
        return WebStorySerializer

    def get_queryset(self):
        queryset = WebStory.objects.all().prefetch_related('slides')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        published_after = self.request.query_params.get('published_after')
        if published_after:
            queryset = queryset.filter(published_at__gte=published_after)

        queryset = queryset.order_by('-published_at', '-created_at')

        page_size = self.request.query_params.get('page_size')
        if page_size:
            try:
                page_size = int(page_size)
                if page_size > 0:
                    queryset = queryset[:page_size]
            except ValueError:
                pass

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(editor=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        story = self.get_object()
        story.publish()
        story.editor = request.user
        story.save()
        serializer = self.get_serializer(story)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def latest(self, request):
        """
        Return recently published stories (default last 24 hours).
        """
        try:
            hours = int(request.query_params.get('hours', 24))
        except (TypeError, ValueError):
            hours = 24

        hours = max(1, min(hours, 168))  # between 1 hour and 7 days

        try:
            limit = int(request.query_params.get('limit', 6))
        except (TypeError, ValueError):
            limit = 6

        limit = max(1, min(limit, 50))
        include_slides = request.query_params.get('include_slides', '').lower() == 'true'

        cutoff = timezone.now() - timedelta(hours=hours)
        queryset = (
            WebStory.objects.filter(
                status='published',
                published_at__isnull=False,
                published_at__gte=cutoff,
            )
            .order_by('-published_at', '-created_at')
            .prefetch_related('slides')
        )[:limit]

        serializer_class = WebStorySerializer if include_slides else WebStoryListSerializer
        serializer = serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

