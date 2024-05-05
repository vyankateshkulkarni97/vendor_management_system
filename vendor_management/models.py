from django.db.models.signals import post_save
from django.db import models
from django.db.models import Count, F, Q
from django.db.models import Avg, ExpressionWrapper, F, DurationField


class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=20, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)  
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def calculate_on_time_delivery_rate(self):
        completed_pos = self.purchase_orders.filter(status='completed', delivery_date__lte=models.functions.Now())
        total_completed_pos = completed_pos.count()
        if total_completed_pos > 0:
            return (completed_pos.filter(acknowledgment_date__isnull=False).count() / total_completed_pos) * 100
        return 0

    def calculate_quality_rating_avg(self):
        completed_pos_with_rating = self.purchase_orders.filter(status='completed', quality_rating__isnull=False)
        total_completed_pos_with_rating = completed_pos_with_rating.count()
        if total_completed_pos_with_rating > 0:
            return completed_pos_with_rating.aggregate(avg_quality_rating=models.Avg('quality_rating'))['avg_quality_rating']
        return 0
    
    def calculate_average_response_time(self):
        response_times = self.purchase_orders.filter(acknowledgment_date__isnull=False).annotate(
            response_time=ExpressionWrapper(F('acknowledgment_date') - F('issue_date'), output_field=DurationField())
        ).aggregate(avg_response_time=Avg('response_time'))['avg_response_time']
        return response_times.total_seconds() if response_times else 0
    
    def calculate_fulfilment_rate(self):
        total_pos = self.purchase_orders.count()
        if total_pos > 0:
            successful_pos = self.purchase_orders.filter(status='completed', quality_rating__isnull=False)
            return (successful_pos.count() / total_pos) * 100
        return 0


class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders')
    po_number = models.CharField(max_length=50, unique=True)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()  
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='historical_performance')
    date = models.DateField()
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)
