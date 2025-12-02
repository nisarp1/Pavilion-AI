"""
API views for RSS Fetcher.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import RSSFeed
from .serializers import RSSFeedSerializer
from .tasks import fetch_single_feed_task, fetch_single_rss_feed, fetch_rss_feeds, fetch_google_trends_sports, enhance_articles_with_google_trends, _get_trending_topics_from_google_trends
import logging


class RSSFeedViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing RSS feeds.
    """
    queryset = RSSFeed.objects.all()
    serializer_class = RSSFeedSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def fetch(self, request, pk=None):
        """
        Manually trigger fetching of a single RSS feed.
        Works synchronously if Celery is not available.
        """
        feed = self.get_object()
        
        # Try to use Celery if available, otherwise run synchronously
        try:
            task = fetch_single_feed_task.delay(feed.id)
            return Response({
                'message': 'Feed fetch task started',
                'task_id': task.id,
                'feed_id': feed.id
            }, status=status.HTTP_202_ACCEPTED)
        except Exception:
            # Celery not available, run synchronously
            try:
                result = fetch_single_rss_feed(feed.url)
                feed.last_fetched_at = timezone.now()
                feed.save()
                
                return Response({
                    'message': 'Feed fetched successfully',
                    'articles_created': result.get('articles_created', 0),
                    'feed_id': feed.id
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def fetch_all(self, request):
        """
        Manually trigger fetching of all active RSS feeds.
        Works synchronously if Celery is not available.
        Force parameter forces fetch even if recently fetched.
        """
        try:
            # Force fetch when manually triggered
            result = fetch_rss_feeds(force=True)
            return Response({
                'message': 'All feeds fetched successfully',
                'articles_created': result.get('articles_created', 0),
                'errors': result.get('errors', [])
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='fetch-trends')
    def fetch_trends(self, request):
        """
        Manually trigger fetching of Sports trending topics from RSS feeds.
        Works synchronously if Celery is not available.
        """
        try:
            # Try to use Celery if available, otherwise run synchronously
            try:
                task = fetch_google_trends_sports.delay()
                return Response({
                    'message': 'Trends fetch task started',
                    'task_id': task.id
                }, status=status.HTTP_202_ACCEPTED)
            except Exception:
                # Celery not available, run synchronously
                result = fetch_google_trends_sports()
                return Response({
                    'message': 'Trends fetched successfully',
                    'articles_created': result.get('articles_created', 0)
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='enhance-trends')
    def enhance_trends(self, request):
        """
        Manually trigger enhancement of trend articles with Google Trends data.
        Works synchronously if Celery is not available.
        """
        try:
            # Try to use Celery if available, otherwise run synchronously
            try:
                task = enhance_articles_with_google_trends.delay()
                return Response({
                    'message': 'Google Trends enhancement task started',
                    'task_id': task.id
                }, status=status.HTTP_202_ACCEPTED)
            except Exception:
                # Celery not available, run synchronously
                result = enhance_articles_with_google_trends()
                return Response({
                    'message': 'Google Trends enhancement completed',
                    'articles_enhanced': result.get('articles_enhanced', 0)
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='realtime-trends')
    def realtime_trends(self, request):
        """
        Get real-time Google Trends data for display.
        Returns trending topics without creating articles.
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Get trending topics
            trending_topics = _get_trending_topics_from_google_trends()
            
            # Ensure we always return a list
            if not isinstance(trending_topics, list):
                trending_topics = list(trending_topics) if trending_topics else []
            
            # Ensure we have at least fallback topics
            if not trending_topics:
                from .tasks import _get_fallback_trends
                trending_topics = _get_fallback_trends()
            
            logger.info(f"Returning {len(trending_topics)} trending topics")
            
            # Format response
            return Response({
                'trending_topics': trending_topics,
                'count': len(trending_topics),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching real-time trends: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            # Return fallback topics even on error
            from .tasks import _get_fallback_trends
            fallback = _get_fallback_trends()
            return Response({
                'error': str(e),
                'trending_topics': fallback,
                'count': len(fallback),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)  # Still return 200 with fallback data
    
    @action(detail=False, methods=['get'], url_path='twitter-trends')
    def twitter_trends(self, request):
        """
        Get real-time Twitter trends for sports in India.
        Returns trending topics without creating articles.
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Get Twitter trending topics for sports in India
            from .tasks import _get_twitter_trends_sports_india
            trending_topics = _get_twitter_trends_sports_india()
            
            # Ensure we always return a list
            if not isinstance(trending_topics, list):
                trending_topics = list(trending_topics) if trending_topics else []
            
            # Ensure we have at least fallback topics
            if not trending_topics:
                from .tasks import _get_twitter_fallback_trends
                trending_topics = _get_twitter_fallback_trends()
            
            logger.info(f"Returning {len(trending_topics)} Twitter trending topics")
            
            # Format response
            return Response({
                'trending_topics': trending_topics,
                'count': len(trending_topics),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching Twitter trends: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            # Return fallback topics even on error
            from .tasks import _get_twitter_fallback_trends
            fallback = _get_twitter_fallback_trends()
            return Response({
                'error': str(e),
                'trending_topics': fallback,
                'count': len(fallback),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)  # Still return 200 with fallback data


