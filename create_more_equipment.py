#!/usr/bin/env python
"""Create additional equipment listings"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from equipment.models import Equipment, Category, EquipmentSpecification
from accounts.models import CompanyProfile
from decimal import Decimal

company = CompanyProfile.objects.first()
print(f'✅ Using: {company.company_name}\n')

equipment_data = [
    {'name': 'CAT C18 Generator 600kVA', 'cat': 'Generators', 'daily': 800, 'weight': 3500, 'mfr': 'Caterpillar', 'yr': 2022, 'specs': {'Power': '600 kVA', 'Engine': 'Cat C18', 'Fuel': 'Diesel'}},
    {'name': 'Perkins 1500 Gen 450kVA', 'cat': 'Generators', 'daily': 650, 'weight': 2800, 'mfr': 'Perkins', 'yr': 2023, 'specs': {'Power': '450 kVA', 'Fuel': 'Diesel', 'Noise': '72 dB'}},
    {'name': 'Toyota 8FD25 Forklift 2.5T', 'cat': 'Forklifts', 'daily': 180, 'weight': 2500, 'mfr': 'Toyota', 'yr': 2021, 'specs': {'Capacity': '2.5 T', 'Lift': '4.5 m', 'Engine': 'Diesel'}},
    {'name': 'Hyster H5.0FT Forklift 5T', 'cat': 'Forklifts', 'daily': 250, 'weight': 5000, 'mfr': 'Hyster', 'yr': 2022, 'specs': {'Capacity': '5.0 T', 'Lift': '6.0 m', 'Trans': 'Auto'}},
    {'name': 'Genie Z-45 Boom Lift', 'cat': 'Aerial Lifts', 'daily': 420, 'weight': 7200, 'mfr': 'Genie', 'yr': 2022, 'specs': {'Height': '15.7 m', 'Reach': '7.6 m', 'Capacity': '227 kg'}},
    {'name': 'JLG 600S Telescopic Boom', 'cat': 'Aerial Lifts', 'daily': 380, 'weight': 8500, 'mfr': 'JLG', 'yr': 2023, 'specs': {'Height': '18.3 m', 'Reach': '15.2 m', 'Drive': '4WD'}},
    {'name': 'Dynapac CA2500D Roller 5T', 'cat': 'Compactors', 'daily': 320, 'weight': 5000, 'mfr': 'Dynapac', 'yr': 2021, 'specs': {'Weight': '5 T', 'Width': '1350 mm', 'Freq': '53 Hz'}},
    {'name': 'Bomag BW213D Roller 13T', 'cat': 'Compactors', 'daily': 480, 'weight': 13000, 'mfr': 'Bomag', 'yr': 2022, 'specs': {'Weight': '13 T', 'Width': '2130 mm', 'Speed': '11 km/h'}},
    {'name': 'Volvo A30G Dump Truck 28T', 'cat': 'Dump Trucks', 'daily': 750, 'weight': 18500, 'mfr': 'Volvo', 'yr': 2021, 'specs': {'Capacity': '28 m³', 'Payload': '28 T', 'Engine': '309 hp'}},
    {'name': 'CAT 730 Articulated Truck', 'cat': 'Dump Trucks', 'daily': 820, 'weight': 21000, 'mfr': 'Caterpillar', 'yr': 2023, 'specs': {'Capacity': '30 m³', 'Payload': '30 T', 'Engine': '348 hp'}},
    {'name': 'Komatsu PC200 Excavator', 'cat': 'Excavators', 'daily': 480, 'weight': 19500, 'mfr': 'Komatsu', 'yr': 2022, 'specs': {'Bucket': '1.0 m³', 'Depth': '6.5 m', 'Engine': '123 kW'}},
    {'name': 'Hitachi ZX250 Excavator', 'cat': 'Excavators', 'daily': 520, 'weight': 24800, 'mfr': 'Hitachi', 'yr': 2023, 'specs': {'Bucket': '1.2 m³', 'Depth': '7.0 m', 'Engine': '141 kW'}},
    {'name': 'CAT D6T Bulldozer', 'cat': 'Bulldozers', 'daily': 680, 'weight': 22000, 'mfr': 'Caterpillar', 'yr': 2021, 'specs': {'Blade': '3.8 m', 'Engine': '186 kW', 'Type': 'Track'}},
    {'name': 'John Deere 850K Dozer', 'cat': 'Bulldozers', 'daily': 720, 'weight': 18900, 'mfr': 'John Deere', 'yr': 2022, 'specs': {'Blade': '3.5 m', 'Engine': '164 kW', 'Type': 'Track'}},
    {'name': 'CAT 950M Wheel Loader', 'cat': 'Loaders', 'daily': 580, 'weight': 17500, 'mfr': 'Caterpillar', 'yr': 2022, 'specs': {'Bucket': '3.1 m³', 'Engine': '203 kW', 'Type': 'Wheel'}},
]

created = 0
for eq in equipment_data:
    cat, _ = Category.objects.get_or_create(name=eq['cat'])
    specs = eq.pop('specs', {})
    
    daily = Decimal(str(eq['daily']))
    equipment = Equipment.objects.create(
        name=eq['name'],
        category=cat,
        seller_company=company,
        manufacturer=eq['mfr'],
        year=eq['yr'],
        weight=Decimal(str(eq['weight'])),
        daily_rate=daily,
        weekly_rate=daily * 6,
        monthly_rate=daily * 24,
        city='DXB',
        country='UAE',
        status='available',
        available_units=2
    )
    
    # Add specifications
    for spec_name, spec_value in specs.items():
        EquipmentSpecification.objects.create(
            equipment=equipment,
            name=spec_name,
            value=spec_value
        )
    
    created += 1
    print(f'✅ {created}. {equipment.name} - ${eq["daily"]}/day')

print(f'\n🎉 Created {created} equipment!')
print(f'📊 Total equipment in database: {Equipment.objects.count()}')
