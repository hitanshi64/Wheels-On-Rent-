from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('vehicle/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('checkout/<int:booking_id>/razorpay-verify/', views.razorpay_verify, name='razorpay_verify'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('about/', views.about_us, name='about'),
    path('contact/', views.contact, name='contact'),
    path('api/nearest-branch/', views.nearest_branch_api, name='nearest_branch_api'),
    path('api/branch-cities/', views.branch_cities_api, name='branch_cities_api'),
]
