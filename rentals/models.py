from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Extra details for a registered user (phone number)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.username} Profile"


class ContactMessage(models.Model):
    """Messages submitted through the Contact Us page."""
    SUBJECT_CHOICES = [
        ('review', 'Review'),
        ('query', 'Query'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='query')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.name}"


class Branch(models.Model):
    """A physical rental branch/shop location in a city."""
    name = models.CharField(max_length=100, help_text="e.g. WheelsOnRent - Satellite")
    city = models.CharField(max_length=100)
    address = models.TextField(help_text="Full street address")
    contact_number = models.CharField(max_length=15)
    google_maps_link = models.URLField(
        max_length=500, blank=True, null=True,
        help_text="Optional: paste a Google Maps share link. If left blank, one is built from latitude/longitude."
    )
    latitude = models.FloatField(help_text="e.g. 23.0225")
    longitude = models.FloatField(help_text="e.g. 72.5714")
    is_active = models.BooleanField(default=True, help_text="Inactive branches are hidden from customers.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Branches"
        ordering = ['city', 'name']

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({self.city}) - {status}"

    def directions_url(self):
        """URL that opens Google Maps navigation to this branch (no API key required)."""
        return f"https://www.google.com/maps/dir/?api=1&destination={self.latitude},{self.longitude}"

    def map_embed_url(self):
        """URL for an embeddable Google Maps iframe (no API key required)."""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}&output=embed"

    def view_on_map_url(self):
        return self.google_maps_link or f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('bike', 'Motorcycle/Bike'),
        ('scooter', 'Scooter/Activa'),
        ('cycle', 'Bicycle/Cycle'),
    ]

    FUEL_TYPES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('none', 'None (Manual/Pedal)'),
    ]

    TRANSMISSION_TYPES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('none', 'None'),
    ]

    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    brand = models.CharField(max_length=50)
    model_year = models.IntegerField(default=2024)
    registration_number = models.CharField(max_length=20, unique=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)  # in INR (₹)
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True, help_text="Upload a photo of the vehicle")
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES, default='petrol')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_TYPES, default='manual')
    seating_capacity = models.IntegerField(default=2)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.registration_number})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('upi', 'UPI (GPay/PhonePe/Paytm)'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('pay_at_store', 'Pay at Store (Cash/UPI on Pickup)'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    REFUND_STATUS_CHOICES = [
        ('not_applicable', 'Not Applicable'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment Fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='pay_at_store')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    terms_accepted = models.BooleanField(default=False, help_text="Customer accepted Terms & Conditions before payment")
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_refund_id = models.CharField(max_length=100, blank=True, null=True)

    # Renter (customer) details collected before booking is confirmed
    renter_name = models.CharField(max_length=100, default='')
    renter_phone = models.CharField(max_length=15, default='')
    renter_email = models.EmailField(default='')
    renter_address = models.TextField(default='')
    renter_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    license_number = models.CharField(max_length=50, default='')
    license_document = models.FileField(upload_to='license_documents/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # Cancellation & refund tracking
    cancelled_at = models.DateTimeField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='not_applicable')
    refund_due_date = models.DateField(null=True, blank=True, help_text="Refund must be processed by this date (within 1 week of cancellation)")

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} - {self.vehicle.name}"

    def can_be_cancelled(self):
        """Cancellation allowed only up to 3 hours before the pickup date, and only if not already cancelled/completed."""
        from django.utils import timezone
        from datetime import datetime, time, timedelta
        if self.status in ('cancelled', 'completed'):
            return False
        pickup_datetime = timezone.make_aware(datetime.combine(self.start_date, time.min))
        cutoff = pickup_datetime - timedelta(hours=3)
        return timezone.now() <= cutoff
