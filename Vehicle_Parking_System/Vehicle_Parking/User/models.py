from django.db import models
from Admin.models import User,Location,Mall,Customer,ParkingSlot
# Create your models here.


class Booking(models.Model):
    STATUS_CHOICES = [
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name="parking")
    start_time = models.DateTimeField()  # Start time of booking
    end_time = models.DateTimeField()    # End time of booking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='reserved')
    created_at = models.DateTimeField(auto_now_add=True)  # When the booking was created
    updated_at = models.DateTimeField(auto_now=True)      # When the booking was last updated
    paid_amount =models.IntegerField(default=0)
    qr_code = models.ImageField(
        upload_to='QR/')
    def __str__(self):
        return f"Booking by {self.user.username} for Slot {self.parking_slot.slot_number}"

    class Meta:
        unique_together = ('parking_slot', 'start_time', 'end_time')
        
        

class Recharge(models.Model):        
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount =models.IntegerField()
    recharged_at = models.DateTimeField(auto_now=True)
    