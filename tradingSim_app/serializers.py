from rest_framework import serializers
from .models import Trade

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['id', 'ticker', 'price', 'quantity', 'side', 'timestamp']
        
    def validate_ticker(self, value):
        # Simple validation - ensure ticker is uppercase and alphanumeric
        if not value.isalpha():
            raise serializers.ValidationError("Ticker must contain only letters")
        return value.upper()
        
    def validate(self, data):
        # You can add cross-field validations here if needed
        return data