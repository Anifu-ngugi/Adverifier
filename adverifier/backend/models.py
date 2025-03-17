from django.db import models
from django.contrib.auth.models import User

class Advertisement(models.Model):
    content = models.TextField()
    url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ad #{self.id}: {self.content[:50]}..."

class VerificationResult(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name="verifications")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credibility_score = models.FloatField()
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Verification for Ad #{self.advertisement.id} - Score: {self.credibility_score}"

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{'User' if self.is_user else 'Bot'}: {self.message[:50]}..."

