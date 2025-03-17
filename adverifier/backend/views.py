from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.shortcuts import get_object_or_404
from .models import Advertisement, VerificationResult, ChatMessage
from .serializers import (
    UserSerializer, AdvertisementSerializer, VerificationResultSerializer,
    ChatMessageSerializer
)
from .rag_llm_system import AdVerificationSystem

# Initialize the verification system
ad_verification_system = AdVerificationSystem()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.all().order_by('-created_at')
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAuthenticated]

class VerificationResultViewSet(viewsets.ModelViewSet):
    queryset = VerificationResult.objects.all().order_by('-created_at')
    serializer_class = VerificationResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter results to only show those belonging to the current user"""
        return self.queryset.filter(user=self.request.user)

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by('created_at')
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter messages to only show those belonging to the current user"""
        return self.queryset.filter(user=self.request.user)

class ChatBotView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_message = request.data.get('message', '')
        
        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the user message
        user_chat = ChatMessage.objects.create(
            user=request.user,
            message=user_message,
            is_user=True
        )
        
        # Check if message contains ad verification request
        if any(keyword in user_message.lower() for keyword in ['verify', 'check', 'ad', 'advertisement', 'credibility']):
            # Extract ad content
            ad_content = user_message
            if "verify this ad:" in user_message.lower():
                ad_content = user_message.split("verify this ad:", 1)[1].strip()
            
            # Save the advertisement
            ad = Advertisement.objects.create(content=ad_content)
            
            # Verify the advertisement
            verification = ad_verification_system.verify_advertisement(ad_content)
            
            # Save the verification result
            result = VerificationResult.objects.create(
                advertisement=ad,
                user=request.user,
                credibility_score=verification['credibility_score'],
                explanation=verification['explanation']
            )
            
            # Generate and save bot response
            bot_response = f"Ad Verification Result:\n" \
                          f"Credibility Score: {verification['credibility_score']:.2f}/1.00\n\n" \
                          f"Analysis:\n{verification['explanation']}\n\n"
            
            if 'issues' in verification and verification['issues']:
                bot_response += "Issues Identified:\n" + "\n".join([f"- {issue}" for issue in verification['issues']]) + "\n\n"
            
            if 'recommendations' in verification and verification['recommendations']:
                bot_response += "Recommendations:\n" + "\n".join([f"- {rec}" for rec in verification['recommendations']])
        else:
            # Handle general chat
            bot_response = "I'm your ad verification assistant. To verify an advertisement, please send me the ad content with 'Verify this ad:' followed by the advertisement text."
        
        # Save the bot response
        bot_chat = ChatMessage.objects.create(
            user=request.user,
            message=bot_response,
            is_user=False
        )
        
        return Response({
            'user_message': user_chat.message,
            'bot_response': bot_chat.message,
            'timestamp': bot_chat.created_at
        })
