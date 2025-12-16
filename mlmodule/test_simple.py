"""
Simple test script for Iris

Run this to see if everything works!
"""
import os
import sys
import django

# Setup Django
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agriculture_backend.settings")
django.setup()

from mlmodule.iris_service import run_batch_detection, check_single_reading

print("="*60)
print("IRIS THE ANALYST - SIMPLE TEST")
print("="*60)

# Test 1: Check a single reading
print("\nTest 1: Checking a normal reading...")
result = check_single_reading(
    plot_id=1,
    temperature=22.0,
    humidity=65.0,
    moisture=45.0,
    create_event=False  # Don't save to database
)
print(f"Result: {'ANOMALY' if result['is_anomaly'] else 'NORMAL'}")

# Test 2: Check an extreme reading (should be anomaly)
print("\nTest 2: Checking an extreme reading...")
result = check_single_reading(
    plot_id=1,
    temperature=50.0,  # Very hot!
    humidity=10.0,     # Very dry!
    moisture=5.0,      # Very dry soil!
    create_event=False
)
print(f"Result: {'ANOMALY' if result['is_anomaly'] else 'NORMAL'}")

# Test 3: Run batch detection (if you have recent data)
print("\nTest 3: Running batch detection on last 60 minutes...")
results = run_batch_detection(
    minutes=60,
    create_events=True 
)

print("\n" + "="*60)
print("TESTS COMPLETE!")
print("="*60)

print(results)
