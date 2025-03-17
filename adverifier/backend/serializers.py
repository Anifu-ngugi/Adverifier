from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Advertisement, VerificationResult, ChatMessage

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'

class VerificationResultSerializer(serializers.ModelSerializer):
    advertisement_content = serializers.SerializerMethodField()
    
    class Meta:
        model = VerificationResult
        fields = '__all__'
    
    def get_advertisement_content(self, obj):
        return obj.advertisement.content if obj.advertisement else None

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
