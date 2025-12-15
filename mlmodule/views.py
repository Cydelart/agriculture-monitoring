"""
API views for ML Module (Iris + AgriBot)
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .iris_service import run_batch_detection, check_single_reading
from .agribot import (
    generate_recommendation,
    create_recommendation_record,
    get_recommendation_for_readings
)
from monitoring.models import AnomalyEvent


# ============================================================================
# IRIS ENDPOINTS (Anomaly Detection)
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_detect(request):
    """
    Run batch anomaly detection.
    
    POST /api/iris/detect/
    Body: {
        "plot_id": 1,      // optional
        "minutes": 10,     // optional, default 5
        "create_events": true  // optional, default true
    }
    """
    plot_id = request.data.get('plot_id')
    minutes = request.data.get('minutes', 5)
    create_events = request.data.get('create_events', True)
    
    try:
        results = run_batch_detection(
            plot_id=plot_id,
            minutes=minutes,
            create_events=create_events
        )
        return Response(results)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_reading(request):
    """
    Check a single sensor reading.
    
    POST /api/iris/check/
    Body: {
        "plot_id": 1,
        "temperature": 35.5,
        "humidity": 20.0,
        "moisture": 15.0,
        "create_event": true  // optional, default true
    }
    """
    # Check required fields
    required = ['plot_id', 'temperature', 'humidity', 'moisture']
    for field in required:
        if field not in request.data:
            return Response(
                {'error': f'Missing field: {field}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        result = check_single_reading(
            plot_id=int(request.data['plot_id']),
            temperature=float(request.data['temperature']),
            humidity=float(request.data['humidity']),
            moisture=float(request.data['moisture']),
            create_event=request.data.get('create_event', True)
        )
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# AGRIBOT ENDPOINTS (AI Recommendations)
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_advice(request):
    """
    Get AI recommendation for sensor readings.
    
    POST /api/agribot/advice/
    Body: {
        "plot_id": 1,
        "temperature": 38.0,
        "humidity": 15.0,
        "moisture": 10.0,
        "severity": "high"  // optional
    }
    """
    required = ['plot_id', 'temperature', 'humidity', 'moisture']
    for field in required:
        if field not in request.data:
            return Response(
                {'error': f'Missing field: {field}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        recommendation = get_recommendation_for_readings(
            plot_id=int(request.data['plot_id']),
            temperature=float(request.data['temperature']),
            humidity=float(request.data['humidity']),
            moisture=float(request.data['moisture']),
            severity=request.data.get('severity', 'medium')
        )
        return Response(recommendation)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_recommendation_for_anomaly(request):
    """
    Generate recommendation for an existing anomaly event.
    
    POST /api/agribot/recommend/
    Body: {
        "anomaly_id": 123,
        "save_to_db": true  // optional, default true
    }
    """
    anomaly_id = request.data.get('anomaly_id')
    
    if not anomaly_id:
        return Response(
            {'error': 'Missing anomaly_id'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get the anomaly event
        anomaly = AnomalyEvent.objects.get(id=anomaly_id)
        
        # Should we save to database?
        save_to_db = request.data.get('save_to_db', True)
        
        if save_to_db:
            # Create/update recommendation record
            rec = create_recommendation_record(anomaly)
            return Response({
                'recommendation_id': rec.id,
                'recommended_action': rec.recommended_action,
                'explanation': rec.explanation_text,
                'confidence': rec.confidence
            })
        else:
            # Just generate, don't save
            rec = generate_recommendation(anomaly)
            return Response({
                'recommended_action': rec['recommended_action'],
                'explanation': rec['explanation_text'],
                'confidence': rec['confidence'],
                'diagnosis': rec['diagnosis'],
                'urgency': rec['urgency']
            })
            
    except AnomalyEvent.DoesNotExist:
        return Response(
            {'error': f'Anomaly {anomaly_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
