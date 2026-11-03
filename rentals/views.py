from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_GET
from .models import Vehicle, Booking, Branch
from . import razorpay_utils
from .forms import CustomUserCreationForm, BookingDetailsForm, ContactForm
from datetime import datetime, date
import math

def home(request):
    query = request.GET.get('q', '')
    v_type = request.GET.get('type', '')
    
    vehicles = Vehicle.objects.filter(is_available=True)
    
    if query:
        vehicles = vehicles.filter(name__icontains=query) | vehicles.filter(brand__icontains=query)
    if v_type:
        vehicles = vehicles.filter(vehicle_type=v_type)
        
    context = {
        'vehicles': vehicles,
        'query': query,
        'v_type': v_type,
        'types_list': Vehicle.VEHICLE_TYPES
    }
    return render(request, 'rentals/home.html', context)

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    details_form = BookingDetailsForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to book a vehicle.")
            return redirect('login')

        details_form = BookingDetailsForm(request.POST, request.FILES)
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if not details_form.is_valid():
            messages.error(request, "Please fill in all your details correctly before booking.")
            return render(request, 'rentals/detail.html', {'vehicle': vehicle, 'details_form': details_form})

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            today = date.today()
            
            if start_date < today:
                messages.error(request, "Start date cannot be in the past.")
            elif end_date < start_date:
                messages.error(request, "End date must be after the start date.")
            else:
                # Calculate total cost
                days = (end_date - start_date).days
                if days == 0:
                    days = 1  # Minimum 1 day charge
                total_price = days * vehicle.price_per_day
                
                # Create booking, including the renter's personal/licence details
                booking = details_form.save(commit=False)
                booking.user = request.user
                booking.vehicle = vehicle
                booking.start_date = start_date
                booking.end_date = end_date
                booking.total_price = total_price
                booking.status = 'pending'
                booking.payment_status = 'pending'
                booking.save()
                return redirect('checkout', booking_id=booking.id)
                
        except (ValueError, TypeError):
            messages.error(request, "Invalid dates selected. Please try again.")

    return render(request, 'rentals/detail.html', {'vehicle': vehicle, 'details_form': details_form})

@login_required(login_url='login')
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # If the booking is already paid, redirect to my_bookings
    if booking.payment_status == 'paid':
        return redirect('my_bookings')
        
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        terms_accepted = request.POST.get('terms_accepted')

        # Terms & Conditions must be accepted before any booking can be paid for
        if not terms_accepted:
            messages.error(request, "You must accept the Terms & Conditions before proceeding to pay.")
            return redirect('checkout', booking_id=booking.id)

        # Verify choice
        if payment_method not in [choice[0] for choice in Booking.PAYMENT_METHODS]:
            messages.error(request, "Invalid payment method selected.")
            return redirect('checkout', booking_id=booking.id)

        booking.payment_method = payment_method
        booking.terms_accepted = True

        # --- Real online payment through Razorpay (when API keys are configured) ---
        if payment_method != 'pay_at_store' and settings.RAZORPAY_ENABLED:
            try:
                order = razorpay_utils.create_order(booking.total_price, receipt=f"WOR-{booking.id}")
            except razorpay_utils.RazorpayError as exc:
                messages.error(request, f"Could not start the payment: {exc}")
                return redirect('checkout', booking_id=booking.id)
            booking.razorpay_order_id = order['id']
            booking.save()
            return render(request, 'rentals/checkout.html', {
                'booking': booking,
                'razorpay_enabled': True,
                'razorpay': {
                    'key_id': settings.RAZORPAY_KEY_ID,
                    'order_id': order['id'],
                    'amount': razorpay_utils.to_paise(booking.total_price),
                    'name': booking.renter_name,
                    'email': booking.renter_email,
                    'phone': booking.renter_phone,
                    'verify_url': reverse('razorpay_verify', args=[booking.id]),
                },
            })

        # --- Fallback: simulated payment (no Razorpay keys configured) ---
        if payment_method == 'pay_at_store':
            booking.payment_status = 'pending'
            booking.transaction_id = 'N/A (Pay on Pickup)'
            messages.info(request, "Your booking is reserved! Please complete the payment at the store during pickup.")
        else:
            import uuid
            booking.payment_status = 'paid'
            booking.transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            messages.success(request, f"Payment of ₹{booking.total_price:.0f} was successful! Transaction ID: {booking.transaction_id}")

        booking.save()
        return redirect('my_bookings')

    return render(request, 'rentals/checkout.html', {'booking': booking, 'razorpay_enabled': settings.RAZORPAY_ENABLED})

@login_required(login_url='login')
def razorpay_verify(request, booking_id):
    """Called by the browser after Razorpay Checkout succeeds. Verifies the signature, then marks the booking paid."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method != 'POST':
        return redirect('checkout', booking_id=booking.id)

    payment_id = request.POST.get('razorpay_payment_id', '')
    order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')

    if not booking.razorpay_order_id or order_id != booking.razorpay_order_id:
        messages.error(request, "Payment verification failed (order mismatch). If money was deducted, please contact us.")
        return redirect('checkout', booking_id=booking.id)

    if not razorpay_utils.verify_payment_signature(order_id, payment_id, signature):
        booking.payment_status = 'failed'
        booking.save()
        messages.error(request, "Payment verification failed. If money was deducted, please contact us.")
        return redirect('checkout', booking_id=booking.id)

    booking.payment_status = 'paid'
    booking.razorpay_payment_id = payment_id
    booking.transaction_id = payment_id
    booking.save()
    messages.success(request, f"Payment of ₹{booking.total_price:.0f} was successful! Payment ID: {payment_id}")
    return redirect('my_bookings')


@login_required(login_url='login')
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'rentals/my_bookings.html', {'bookings': bookings})


@login_required(login_url='login')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method != 'POST':
        return redirect('my_bookings')

    if not booking.can_be_cancelled():
        messages.error(
            request,
            "This booking can no longer be cancelled. Cancellations are only allowed up to 3 hours before the pickup date."
        )
        return redirect('my_bookings')

    from django.utils import timezone
    from datetime import timedelta

    booking.status = 'cancelled'
    booking.cancelled_at = timezone.now()

    if booking.payment_status == 'paid':
        # 25% cancellation penalty -> 75% refunded within 1 week
        booking.refund_amount = (booking.total_price * 75) / 100
        booking.refund_status = 'pending'
        booking.refund_due_date = (timezone.now() + timedelta(days=7)).date()

        # If the customer paid through Razorpay, send the 75% back to their original payment method
        if booking.razorpay_payment_id and settings.RAZORPAY_ENABLED:
            try:
                refund = razorpay_utils.refund_payment(
                    booking.razorpay_payment_id, booking.refund_amount,
                    notes={'booking': f'WOR-{booking.id}', 'reason': 'Customer cancellation (25% penalty)'},
                )
                booking.razorpay_refund_id = refund.get('id')
            except razorpay_utils.RazorpayError as exc:
                messages.warning(
                    request,
                    f"We could not trigger the automatic refund ({exc}). Our team will process it manually within 1 week."
                )
        booking.save()
        messages.success(
            request,
            f"Your booking has been cancelled. A refund of ₹{booking.refund_amount:.0f} "
            f"(75% of the paid amount, after a 25% cancellation penalty) will be processed "
            f"to you within 1 week, by {booking.refund_due_date.strftime('%d %b %Y')}."
        )
    else:
        booking.refund_status = 'not_applicable'
        booking.save()
        messages.success(request, "Your booking has been cancelled.")

    return redirect('my_bookings')

def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to WheelsOnRent.")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'rentals/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'rentals/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('home')


def about_us(request):
    return render(request, 'rentals/about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you shortly.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors below and try again.")
    else:
        form = ContactForm()

    return render(request, 'rentals/contact.html', {'form': form})


def _haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two lat/lon points, in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@require_GET
def branch_cities_api(request):
    """Distinct cities with at least one active branch — used for the manual city fallback dropdown."""
    cities = list(
        Branch.objects.filter(is_active=True)
        .order_by('city')
        .values_list('city', flat=True)
        .distinct()
    )
    return JsonResponse({'cities': cities})


@require_GET
def nearest_branch_api(request):
    """
    Returns the nearest active branch as JSON.
    Accepts either ?lat=..&lon=.. (from browser Geolocation) or ?city=.. (manual fallback).
    """
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    city = request.GET.get('city')

    branches = Branch.objects.filter(is_active=True)
    if not branches.exists():
        return JsonResponse({'found': False, 'message': 'No branches are available right now.'})

    nearest = None
    distance_km = None

    if lat and lon:
        try:
            user_lat, user_lon = float(lat), float(lon)
            best = None
            best_dist = None
            for b in branches:
                d = _haversine_km(user_lat, user_lon, b.latitude, b.longitude)
                if best_dist is None or d < best_dist:
                    best, best_dist = b, d
            nearest, distance_km = best, round(best_dist, 1)
        except (ValueError, TypeError):
            pass

    if nearest is None and city:
        city_branches = branches.filter(city__iexact=city.strip())
        if city_branches.exists():
            # Multiple branches in the same city: just pick the first (no GPS to rank by distance)
            nearest = city_branches.first()
        else:
            # No branch in that city — fall back to any active branch (nearest by list order)
            nearest = branches.first()

    if nearest is None:
        nearest = branches.first()

    return JsonResponse({
        'found': True,
        'id': nearest.id,
        'name': nearest.name,
        'city': nearest.city,
        'address': nearest.address,
        'contact_number': nearest.contact_number,
        'distance_km': distance_km,
        'directions_url': nearest.directions_url(),
        'map_embed_url': nearest.map_embed_url(),
        'view_on_map_url': nearest.view_on_map_url(),
    })
