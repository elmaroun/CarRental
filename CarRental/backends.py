from django.contrib.auth.backends import BaseBackend
from .models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class MongoDBAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Normalize email/username
            username = username.lower().strip() if username else None
            
            # Try both email and username fields
            if '@' in username:
                user = User.objects.get(email__iexact=username)
            else:
                user = User.objects.get(username__iexact=username)
            
            logger.debug(f"Found user: {user.email}")
            
            if user.check_password(password):
                logger.debug("Password matches")
                user.last_login = timezone.now()
                user.save()
                return user
            else:
                logger.debug("Password does NOT match")
                print('password')
                return None
                
        except User.DoesNotExist:
            logger.debug(f"User not found: {username}")
            print('here')
            return None
        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            print('here2')
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None