from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Quick health check to test database connection"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Get database info
        db_engine = connection.settings_dict['ENGINE']
        db_name = connection.settings_dict.get('NAME', 'N/A')
        db_host = connection.settings_dict.get('HOST', 'N/A')
        
        return JsonResponse({
            'status': 'healthy',
            'database': {
                'engine': db_engine,
                'name': db_name,
                'host': db_host,
                'connected': True
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
