"""
API views for CMS.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Article, Category
from .serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticleGenerateSerializer,
    CategorySerializer,
    CategoryListSerializer,
)


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing articles.
    """
    queryset = Article.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
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


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories and subcategories.
    """
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
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

