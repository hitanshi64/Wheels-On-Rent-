from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from rentals.models import Vehicle
import os

class Command(BaseCommand):
    help = 'Seeds initial vehicle data for WheelsOnRent'

    def handle(self, *args, **kwargs):
        vehicles_data = [
            {
                'name': 'Thar 4x4',
                'brand': 'Mahindra',
                'vehicle_type': 'car',
                'model_year': 2023,
                'registration_number': 'MH-12-TR-9999',
                'price_per_day': 3200.00,
                'fuel_type': 'diesel',
                'transmission': 'automatic',
                'seating_capacity': 4,
                'image_filename': 'thar.jpg',
                'description': 'Experience the ultimate off-road adventure with the Mahindra Thar. Perfect for weekend getaways and exploring rough terrains in style and comfort.'
            },
            {
                'name': 'Swift VXI',
                'brand': 'Maruti Suzuki',
                'vehicle_type': 'car',
                'model_year': 2022,
                'registration_number': 'DL-3C-SV-4400',
                'price_per_day': 1400.00,
                'fuel_type': 'petrol',
                'transmission': 'manual',
                'seating_capacity': 5,
                'image_filename': 'swift.jpg',
                'description': 'The Maruti Swift is the go-to hatchback for city commuting. Extremely fuel-efficient, easy to park, and offers a smooth driving experience.'
            },
            {
                'name': 'Classic 350',
                'brand': 'Royal Enfield',
                'vehicle_type': 'bike',
                'model_year': 2022,
                'registration_number': 'KA-03-RE-3500',
                'price_per_day': 900.00,
                'fuel_type': 'petrol',
                'transmission': 'manual',
                'seating_capacity': 2,
                'image_filename': 'bullet.jpg',
                'description': 'Cruise through Indian roads with the iconic thumping sound of the Royal Enfield Classic 350. Ideal for road trips and solo leisure riding.'
            },
            {
                'name': 'Activa 6G',
                'brand': 'Honda',
                'vehicle_type': 'scooter',
                'model_year': 2023,
                'registration_number': 'GJ-01-AC-6600',
                'price_per_day': 450.00,
                'fuel_type': 'petrol',
                'transmission': 'automatic',
                'seating_capacity': 2,
                'image_filename': 'activa.jpg',
                'description': 'India\'s most loved scooter. The Honda Activa 6G is lightweight, reliable, and perfect for quick city errands and local sightseeing.'
            },
            {
                'name': 'S1 Pro Gen 2',
                'brand': 'Ola Electric',
                'vehicle_type': 'scooter',
                'model_year': 2023,
                'registration_number': 'UP-16-OL-1010',
                'price_per_day': 550.00,
                'fuel_type': 'electric',
                'transmission': 'automatic',
                'seating_capacity': 2,
                'image_filename': 'ola.jpg',
                'description': 'Ride into the future with the high-performance Ola S1 Pro electric scooter. Silent, smooth, and packed with futuristic features.'
            },
            {
                'name': 'Escape 3',
                'brand': 'Giant',
                'vehicle_type': 'cycle',
                'model_year': 2023,
                'registration_number': 'CY-ESC-333',
                'price_per_day': 180.00,
                'fuel_type': 'none',
                'transmission': 'none',
                'seating_capacity': 1,
                'image_filename': 'cycle.jpg',
                'description': 'Stay fit and eco-friendly with the Giant Escape hybrid bicycle. Perfect for morning fitness rides or exploring scenic tracks.'
            }
        ]

        created_count = 0
        for data in vehicles_data:
            image_filename = data.pop('image_filename', None)
            vehicle, created = Vehicle.objects.get_or_create(
                registration_number=data['registration_number'],
                defaults=data
            )
            if created:
                created_count += 1
                if image_filename:
                    source_path = os.path.join(settings.BASE_DIR, 'static', 'images', image_filename)
                    if os.path.exists(source_path):
                        with open(source_path, 'rb') as f:
                            vehicle.image.save(image_filename, File(f), save=True)

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} vehicles into the database.'))
