from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Trade(models.Model):
    SIDE_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    
    ticker = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.side} {self.quantity} {self.ticker} @ {self.price}"
    
class StockPrice(models.Model):
    ticker = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    timestamp = models.DateTimeField(auto_now=True)
    moving_average_5min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    class Meta:
        unique_together = ('ticker', 'timestamp')
    def __str__(self):
        return f"{self.ticker}: {self.price} ({self.timestamp}) (MA: {self.moving_average_5min})"