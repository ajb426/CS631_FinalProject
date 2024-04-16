# custom_session_middleware.py in the same app directory as your models

from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.timezone import now
from django.utils import timezone
from .models import Session

class CustomSessionMiddleware(SessionMiddleware):
    """
    Custom session middleware that extends the default Django session middleware to
    handle custom session creation, updating, and management based on user activity.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.
        """

        self.get_response = get_response

    def __call__(self, request):
        """
        Method that is called on each request before the view (and later middleware) are called.

        Ensures a session exists for each user and logs session activity, creating a new session
        if the last activity was more than a day ago or if no session exists.
        """

        session_id = request.session.session_key
        if not session_id:
            # Ensure we have a session key.
            request.session.save()
            session_id = request.session.session_key

        now = timezone.now()
        session_log, created = Session.objects.get_or_create(
            session_id=session_id,
            defaults={'session_datetime': now, 'latest_activity': now, 'user': request.user if request.user.is_authenticated else None}
        )

        if not created and (now - session_log.session_datetime).days >= 1:
            # If more than a day has passed since last activity, start a new session.
            request.session.flush()  # Clear the current session and create a new one
            session_id = request.session.session_key
            Session.objects.create(
                session_id=session_id,
                session_datetime=now,
                latest_activity=now,
                user=request.user if request.user.is_authenticated else None
            )
        else:
            session_log.latest_activity = now
            if request.user.is_authenticated:
                session_log.user = request.user
            session_log.save()

        response = self.get_response(request)
        return response