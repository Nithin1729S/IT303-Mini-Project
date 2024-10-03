from django.utils.deprecation import MiddlewareMixin
from .models import PathAccess

class PathAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        # Try to get the existing PathAccess object or create a new one
        obj, created = PathAccess.objects.get_or_create(path=path)
        obj.access_count += 1
        # Logic to determine if it's a bounce (this would depend on your application flow)
        if request.session.get('last_accessed_path') != path:
            obj.bounces += 1  # Increment bounces if the last accessed path was different
        obj.save()
        request.session['last_accessed_path'] = path
