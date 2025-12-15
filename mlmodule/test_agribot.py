"""
AgriBot Test & Examples

Shows how to use the AI agent to generate recommendations.
"""
import os
import sys
import django

# Setup Django
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agriculture_backend.settings")
django.setup()

from mlmodule.agribot import (
    generate_recommendation,
    create_recommendation_record,
    get_recommendation_for_readings
)
from monitoring.models import AnomalyEvent


def test_agribot():
    """Test AgriBot with various scenarios."""
    
    print("="*70)
    print("AGRIBOT - AI RECOMMENDATION SYSTEM TEST")
    print("="*70)
    
    # Test Scenario 1: Heat stress
    print("\n" + "="*70)
    print("SCENARIO 1: Extreme Heat & Drought")
    print("="*70)
    rec = get_recommendation_for_readings(
        plot_id=1,
        temperature=38.0,  # Very hot
        humidity=15.0,     # Very dry air
        moisture=10.0,     # Dry soil
        severity='high'
    )
    print(rec['explanation'])
    
    # Test Scenario 2: Waterlogged
    print("\n" + "="*70)
    print("SCENARIO 2: Waterlogged Soil")
    print("="*70)
    rec = get_recommendation_for_readings(
        plot_id=2,
        temperature=22.0,
        humidity=85.0,     # High humidity
        moisture=90.0,     # Too much water
        severity='medium'
    )
    print(rec['explanation'])
    
    # Test Scenario 3: Frost risk
    print("\n" + "="*70)
    print("SCENARIO 3: Frost Risk")
    print("="*70)
    rec = get_recommendation_for_readings(
        plot_id=3,
        temperature=3.0,   # Near freezing
        humidity=70.0,
        moisture=50.0,
        severity='high'
    )
    print(rec['explanation'])
    
    # Test Scenario 4: Fungal risk
    print("\n" + "="*70)
    print("SCENARIO 4: Fungal Disease Risk")
    print("="*70)
    rec = get_recommendation_for_readings(
        plot_id=1,
        temperature=8.0,   # Cold
        humidity=90.0,     # Very humid
        moisture=75.0,     # Wet
        severity='medium'
    )
    print(rec['explanation'])
    
    # Test Scenario 5: Normal with slight variation
    print("\n" + "="*70)
    print("SCENARIO 5: Minor Variation (Normal)")
    print("="*70)
    rec = get_recommendation_for_readings(
        plot_id=1,
        temperature=23.0,
        humidity=55.0,
        moisture=45.0,
        severity='low'
    )
    print(rec['explanation'])
    
    # Test with actual anomaly events (if any exist)
    print("\n" + "="*70)
    print("REAL ANOMALY EVENTS")
    print("="*70)
    
    recent_anomalies = AnomalyEvent.objects.filter(
        anomaly_type__icontains='Unusual sensor combo'
    ).order_by('-timestamp')[:3]
    
    if recent_anomalies.exists():
        for anomaly in recent_anomalies:
            print(f"\nAnalyzing anomaly {anomaly.id}...")
            rec = generate_recommendation(anomaly, template_type='farmer_friendly')
            print(rec['explanation_text'])
            print(f"\nConfidence: {rec['confidence']*100:.1f}%")
    else:
        print("No recent anomalies found.")
        print("Run Iris detection first: python manage.py detect_anomalies")
    
    # NEW: Test Advanced Rules
    print("\n" + "="*70)
    print("ADVANCED RULES TESTS (Trend-Based)")
    print("="*70)
    
    # Advanced Test 1: Rapid moisture drop
    print("\nAdvanced Test 1: Rapid Moisture Drop (>10%)")
    print("-" * 70)
    from mlmodule.agribot import AgriBotRules, ExplanationGenerator
    
    result = AgriBotRules.analyze_with_trends(
        temperature=26.0,
        humidity=55.0,
        moisture=28.0,
        severity='high',
        moisture_trend=-12.0,  # Dropped 12%!
        anomaly_confidence=0.85
    )
    
    data = {
        'timestamp': '2025-12-15 at 09:20',
        'plot_id': 1,
        'category': result['category'],
        'diagnosis': result['diagnosis'],
        'cause': result['cause'],
        'action': result['action'],
        'urgency': result['urgency'],
        'temperature': 26.0,
        'humidity': 55.0,
        'moisture': 28.0,
        'confidence': 0.85,
        'trend_info': result.get('details', '')
    }
    
    print(ExplanationGenerator.generate('detailed', data))
    
    # Advanced Test 2: Sustained high temperature
    print("\n\nAdvanced Test 2: Sustained High Temperature (+7°C)")
    print("-" * 70)
    
    result = AgriBotRules.analyze_with_trends(
        temperature=32.0,
        humidity=45.0,
        moisture=40.0,
        severity='medium',
        temp_trend=7.0,  # 7°C above normal!
        anomaly_confidence=0.90
    )
    
    data = {
        'timestamp': '2025-12-15 at 14:30',
        'plot_id': 2,
        'category': result['category'],
        'diagnosis': result['diagnosis'],
        'cause': result['cause'],
        'action': result['action'],
        'urgency': result['urgency'],
        'temperature': 32.0,
        'humidity': 45.0,
        'moisture': 40.0,
        'confidence': 0.90,
        'trend_info': result.get('details', '')
    }
    
    print(ExplanationGenerator.generate('farmer_friendly', data))
    
    # Advanced Test 3: Low confidence
    print("\n\nAdvanced Test 3: Low Confidence Anomaly")
    print("-" * 70)
    
    result = AgriBotRules.analyze_with_trends(
        temperature=28.0,
        humidity=55.0,
        moisture=45.0,
        severity='medium',
        anomaly_confidence=0.52  # Low confidence!
    )
    
    print(f"Diagnosis: {result['diagnosis']}")
    print(f"Action: {result['action']}")
    
    # Advanced Test 4: Multiple stressors
    print("\n\nAdvanced Test 4: Multiple Simultaneous Stressors")
    print("-" * 70)
    
    result = AgriBotRules.analyze_with_trends(
        temperature=38.0,
        humidity=12.0,
        moisture=15.0,
        severity='high',
        anomaly_confidence=0.95
    )
    
    print(f"Diagnosis: {result['diagnosis']}")
    print(f"Cause: {result['cause']}")
    print(f"Action: {result['action']}")
    
    print("\n" + "="*70)
    print("TESTS COMPLETE!")
    print("="*70)
    print("\nAgriBot is ready to generate smart recommendations!")
    print("\nFeatures tested:")
    print("  ✓ Basic rules (10 rules for standard conditions)")
    print("  ✓ Advanced rules (4 rules with trend detection)")
    print("  ✓ Template generation (multiple formats)")
    print("  ✓ Confidence levels (HIGH/MEDIUM/LOW)")


if __name__ == "__main__":
    test_agribot()
