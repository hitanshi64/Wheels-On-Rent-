from django.contrib import admin
from .models import Vehicle, Booking, Profile, ContactMessage, Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'contact_number', 'latitude', 'longitude', 'is_active')
    list_filter = ('is_active', 'city')
    search_fields = ('name', 'city', 'address')
    list_editable = ('is_active',)
    fieldsets = (
        ('Branch Info', {'fields': ('name', 'city', 'address', 'contact_number', 'is_active')}),
        ('Map Location', {
            'fields': ('latitude', 'longitude', 'google_maps_link'),
            'description': 'Tip: right-click the branch location on Google Maps and choose the coordinates to copy latitude/longitude.'
        }),
    )

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'vehicle_type', 'price_per_day', 'is_available', 'registration_number')
    list_filter = ('vehicle_type', 'is_available', 'fuel_type')
    search_fields = ('brand', 'name', 'registration_number')
    list_editable = ('price_per_day', 'is_available')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vehicle', 'renter_name', 'renter_phone', 'start_date', 'end_date', 'total_price', 'status', 'payment_status', 'payment_method', 'terms_accepted', 'refund_status', 'refund_amount')
    list_filter = ('status', 'payment_status', 'start_date', 'end_date', 'renter_gender', 'refund_status')
    search_fields = ('user__username', 'vehicle__name', 'transaction_id', 'razorpay_payment_id', 'renter_name', 'renter_phone', 'license_number')
    list_editable = ('status', 'payment_status', 'refund_status')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('created_at',)
