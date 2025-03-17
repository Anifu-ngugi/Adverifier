from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, CustomAuthToken, AdvertisementViewSet,
    VerificationResultViewSet, ChatMessageViewSet, ChatBotView
)

router = DefaultRouter()
router.register(r'advertisements', AdvertisementViewSet)
router.register(r'verification-results', VerificationResultViewSet)
router.register(r'chat-messages', ChatMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('chat/', ChatBotView.as_view(), name='chat'),
]
