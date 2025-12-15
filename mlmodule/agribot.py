"""
AgriBot - Simple Rule-Based AI Agent

This AI agent analyzes anomalies and generates recommendations.
Uses simple if-then rules and template-based text generation.

Easy to understand, impressive results!
"""
from monitoring.models import AnomalyEvent, AgentRecommendation


# ============================================================================
# RULE ENGINE - The Brain of the AI
# ============================================================================

class AgriBotRules:
    """
    Rule-based decision engine.
    
    Each rule checks conditions and returns an action if matched.
    Rules are checked in order from most specific to most general.
    """
    
    @staticmethod
    def analyze_conditions(temperature, humidity, moisture, severity):
        """
        Analyze sensor conditions and return the matching rule.
        
        Args:
            temperature: Temperature value
            humidity: Humidity value
            moisture: Soil moisture value
            severity: Anomaly severity ('low', 'medium', 'high')
        
        Returns:
            Dictionary with:
                - diagnosis: What's wrong
                - cause: Why it happened
                - action: What to do
                - urgency: How urgent (1-5)
                - category: Type of problem
        """
        
        # RULE 1: Extreme heat + dry conditions
        if temperature > 35 and humidity < 30 and moisture < 20:
            return {
                'diagnosis': 'Heat stress with severe drought',
                'cause': 'High temperature combined with very low humidity and dry soil',
                'action': 'URGENT: Immediate irrigation required. Consider shade covers.',
                'urgency': 5,
                'category': 'drought_stress'
            }
        
        # RULE 2: Hot and dry (moderate)
        if temperature > 30 and moisture < 30:
            return {
                'diagnosis': 'Heat and water stress',
                'cause': 'Temperature above optimal range with insufficient soil moisture',
                'action': 'Increase irrigation frequency. Water early morning or evening.',
                'urgency': 4,
                'category': 'water_stress'
            }
        
        # RULE 3: Cold and wet conditions
        if temperature < 10 and humidity > 80 and moisture > 70:
            return {
                'diagnosis': 'Cold and waterlogged conditions',
                'cause': 'Low temperature with excessive moisture promotes fungal growth',
                'action': 'Improve drainage. Consider fungicide application. Reduce watering.',
                'urgency': 4,
                'category': 'fungal_risk'
            }
        
        # RULE 4: Waterlogged soil
        if moisture > 80:
            return {
                'diagnosis': 'Soil waterlogging detected',
                'cause': 'Excessive soil moisture can suffocate roots',
                'action': 'Stop irrigation immediately. Check drainage system. Aerate soil if possible.',
                'urgency': 3,
                'category': 'overwatering'
            }
        
        # RULE 5: Very dry soil
        if moisture < 15:
            return {
                'diagnosis': 'Severe soil dryness',
                'cause': 'Soil moisture critically low',
                'action': 'Begin gradual irrigation. Avoid flooding - water slowly.',
                'urgency': 4,
                'category': 'drought'
            }
        
        # RULE 6: High humidity with moderate temp
        if humidity > 85 and 20 < temperature < 30:
            return {
                'diagnosis': 'High humidity risk',
                'cause': 'Elevated humidity creates favorable conditions for diseases',
                'action': 'Improve air circulation. Monitor for fungal diseases. Reduce watering.',
                'urgency': 3,
                'category': 'disease_risk'
            }
        
        # RULE 7: Low humidity
        if humidity < 25:
            return {
                'diagnosis': 'Very low humidity',
                'cause': 'Dry air can stress plants and increase water needs',
                'action': 'Increase irrigation slightly. Consider mulching to retain moisture.',
                'urgency': 2,
                'category': 'dry_air'
            }
        
        # RULE 8: Temperature extremes
        if temperature > 40:
            return {
                'diagnosis': 'Extreme heat alert',
                'cause': 'Temperature exceeds safe range for most crops',
                'action': 'Emergency cooling needed. Install shade nets. Increase water misting.',
                'urgency': 5,
                'category': 'extreme_heat'
            }
        
        if temperature < 5:
            return {
                'diagnosis': 'Frost risk',
                'cause': 'Temperature approaching freezing point',
                'action': 'Protect crops with covers. Consider heating if available.',
                'urgency': 5,
                'category': 'frost_risk'
            }
        
        # RULE 9: Moderate moisture but temp/humidity imbalance
        if temperature > 28 and humidity < 40:
            return {
                'diagnosis': 'Hot and dry air',
                'cause': 'Temperature high with low atmospheric moisture',
                'action': 'Monitor plants for wilting. Increase irrigation if needed.',
                'urgency': 3,
                'category': 'heat_dry'
            }
        
        # RULE 10: Based on severity alone (fallback)
        if severity == 'high':
            return {
                'diagnosis': 'Significant environmental anomaly',
                'cause': 'Sensor readings show unusual pattern',
                'action': 'Inspect plot carefully. Check sensors. Monitor closely.',
                'urgency': 3,
                'category': 'anomaly_general'
            }
        
        # DEFAULT RULE
        return {
            'diagnosis': 'Minor environmental variation',
            'cause': 'Conditions slightly outside normal range',
            'action': 'Continue monitoring. No immediate action required.',
            'urgency': 1,
            'category': 'minor_variation'
        }
    
    @staticmethod
    def analyze_with_trends(temperature, humidity, moisture, severity, 
                           moisture_trend=None, temp_trend=None, anomaly_confidence=None):
        """
        Enhanced analysis with trend detection and confidence levels.
        
        This adds more sophisticated rules based on:
        - Moisture drop rate
        - Sustained temperature anomalies  
        - Confidence levels
        
        Args:
            temperature, humidity, moisture: Current sensor values
            severity: Anomaly severity
            moisture_trend: % change in moisture (e.g., -12 = dropped 12%)
            temp_trend: Temperature deviation from normal (e.g., +7 = 7°C above normal)
            anomaly_confidence: ML model confidence (0.0-1.0)
        
        Returns:
            Dictionary with diagnosis, cause, action, urgency, category
        """
        
        # ADVANCED RULE 1: Rapid moisture drop (possible leak/failure)
        if moisture_trend is not None and moisture_trend < -10:
            return {
                'diagnosis': 'Rapid soil moisture depletion detected',
                'cause': f'Soil moisture dropped {abs(moisture_trend):.1f}% rapidly. Possible irrigation system failure, leak, or pump malfunction.',
                'action': 'URGENT: Check irrigation system immediately. Inspect for leaks. Verify pump operation. Begin manual watering if needed.',
                'urgency': 5,
                'category': 'irrigation_failure',
                'details': f'Moisture drop: {moisture_trend:.1f}%'
            }
        
        # ADVANCED RULE 2: Sustained high temperature (heat stress)
        if temp_trend is not None and temp_trend > 5:
            return {
                'diagnosis': 'Sustained temperature anomaly - heat stress risk',
                'cause': f'Temperature {temp_trend:.1f}°C above normal range for extended period. Prolonged heat exposure.',
                'action': 'Implement heat stress mitigation: Increase shade coverage, boost irrigation frequency, consider misting systems.',
                'urgency': 4,
                'category': 'heat_stress',
                'details': f'Temp above normal: +{temp_trend:.1f}°C'
            }
        
        # ADVANCED RULE 3: Low confidence anomaly (verification needed)
        if anomaly_confidence is not None and 0.4 <= anomaly_confidence <= 0.6:
            return {
                'diagnosis': 'Low-confidence anomaly detected',
                'cause': f'Sensor pattern shows potential issue, but model confidence is borderline ({anomaly_confidence:.2f}).',
                'action': 'Monitor closely. Verify with manual inspection. Check sensor calibration. Observe for pattern development.',
                'urgency': 2,
                'category': 'low_confidence_anomaly',
                'details': f'Confidence: {anomaly_confidence:.2f} (LOW)'
            }
        
        # ADVANCED RULE 4: Multiple stress factors (compound anomalies)
        #Check if multiple sensors show extreme values
        extreme_temp = temperature > 35 or temperature < 10
        extreme_humidity = humidity > 85 or humidity < 25
        extreme_moisture = moisture > 80 or moisture < 20
        
        extreme_count = sum([extreme_temp, extreme_humidity, extreme_moisture])
        
        if extreme_count >= 2:
            factors = []
            if extreme_temp:
                factors.append(f"temperature ({temperature}°C)")
            if extreme_humidity:
                factors.append(f"humidity ({humidity}%)")
            if extreme_moisture:
                factors.append(f"moisture ({moisture}%)")
            
            return {
                'diagnosis': 'Multiple simultaneous stress factors detected',
                'cause': f'Compound environmental stress: {", ".join(factors)}. Multiple parameters critically affected.',
                'action': 'URGENT: Comprehensive plot inspection required. Address all stress factors. Consider emergency interventions.',
                'urgency': 5,
                'category': 'multiple_anomalies',
                'details': f'{extreme_count} stress factors: {", ".join(factors)}'
            }
        
        # Fall back to basic rules if no trend-based rules matched
        return AgriBotRules.analyze_conditions(temperature, humidity, moisture, severity)


# ============================================================================
# EXPLANATION GENERATOR - Makes It Human-Readable
# ============================================================================

class ExplanationGenerator:
    """
    Generates human-friendly explanations using templates.
    
    Uses deterministic template structure as specified:
    - Timestamp and anomaly type
    - Model confidence score
    - Specific sensor values/trends
    - Recommended action
    - Overall confidence level
    """
    
    # Templates for different message types
    TEMPLATES = {
        'detailed': (
            "On {timestamp}, sensor readings detected a {category} anomaly (model confidence {confidence:.2f}).\n\n"
            "Sensor Readings:\n"
            "  • Temperature: {temperature}°C\n"
            "  • Humidity: {humidity}%\n"
            "  • Soil Moisture: {moisture}%\n"
            "{trend_info}\n"
            "Diagnosis: {diagnosis}\n\n"
            "Explanation: {cause}\n\n"
            "Agent Recommendation: {action}\n\n"
            "Confidence Level: {confidence_level}"
        ),
        
        'summary': (
            "AgriBot Analysis Report\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Plot: {plot_name}\n"
            "Time: {timestamp}\n"
            "Anomaly Type: {category}\n"
            "Model Confidence: {confidence:.2f}\n\n"
            "📊 Sensor Readings:\n"
            "   Temperature: {temperature}°C\n"
            "   Humidity: {humidity}%\n"
            "   Soil Moisture: {moisture}%\n\n"
            "🔍 Diagnosis: {diagnosis}\n\n"
            "💡 Explanation: {cause}\n\n"
            "✅ Recommended Action: {action}\n\n"
            "⚠️ Confidence: {confidence_level} ({confidence:.0%})"
        ),
        
        'short': (
            "Anomaly detected at {timestamp}: {diagnosis}. {action} (Confidence: {confidence:.0%})"
        ),
        
        'technical': (
            "On {timestamp}, AgriBot detected {category} conditions on Plot {plot_id} "
            "(model confidence {confidence:.2f}). "
            "Environmental readings: T={temperature}°C, H={humidity}%, M={moisture}%. "
            "{diagnosis}. Root cause: {cause}. "
            "Recommended intervention: {action}. Confidence: {confidence_level}."
        ),
        
        'farmer_friendly': (
            "⚠️ Alert for Plot {plot_id}\n"
            "Time: {timestamp}\n\n"
            "What we found: {diagnosis}\n"
            "Sensor readings: {temperature}°C, {humidity}% humidity, {moisture}% soil moisture\n\n"
            "Why this happened: {cause}\n\n"
            "What you should do: {action}\n\n"
            "How sure are we: {confidence_level} (confidence: {confidence:.0%})\n"
            "How urgent: {urgency_label}"
        )
    }
    
    @staticmethod
    def generate(template_type, data):
        """
        Generate explanation from template and data.
        
        Args:
            template_type: Which template to use
            data: Dictionary with values to fill in
        
        Returns:
            Formatted string with proper structure
        """
        if template_type not in ExplanationGenerator.TEMPLATES:
            template_type = 'detailed'
        
        # Add derived fields for better templates
        enriched_data = data.copy()
        
        # Add confidence level label
        conf = enriched_data.get('confidence', 0.5)
        if conf >= 0.85:
            enriched_data['confidence_level'] = 'HIGH'
        elif conf >= 0.6:
            enriched_data['confidence_level'] = 'MEDIUM'
        else:
            enriched_data['confidence_level'] = 'LOW'
        
        # Add urgency label
        urgency = enriched_data.get('urgency', 1)
        if urgency >= 4:
            enriched_data['urgency_label'] = '🔴 Very Urgent'
        elif urgency >= 2:
            enriched_data['urgency_label'] = '🟡 Moderately Urgent'
        else:
            enriched_data['urgency_label'] = '🟢 Not Urgent'
        
        # Add trend info if available
        if 'trend_info' not in enriched_data:
            enriched_data['trend_info'] = ""
        
        template = ExplanationGenerator.TEMPLATES[template_type]
        
        try:
            return template.format(**enriched_data)
        except KeyError as e:
            # Fallback if data is missing
            return (
                f"On {enriched_data.get('timestamp', 'unknown time')}, "
                f"AgriBot detected: {enriched_data.get('diagnosis', 'analysis in progress')}. "
                f"Recommendation: {enriched_data.get('action', 'monitor situation')}. "
                f"(Confidence: {conf:.0%})"
            )


# ============================================================================
# RECOMMENDATION ENGINE - Puts It All Together
# ============================================================================

def generate_recommendation(anomaly_event, template_type='summary'):
    """
    Main function: Analyze anomaly and generate recommendation.
    
    This is what you call to get AI recommendations!
    
    Args:
        anomaly_event: AnomalyEvent instance
        template_type: How to format the output ('summary', 'short', 'technical', 'farmer_friendly')
    
    Returns:
        Dictionary with:
            - recommended_action: What to do
            - explanation_text: Why and how
            - confidence: How confident (0-1)
            - diagnosis: The problem identified
            - urgency: How urgent (1-5)
    """
    # Extract sensor values from anomaly event
    # The anomaly_type contains the sensor readings
    readings = _parse_sensor_values(anomaly_event.anomaly_type)
    
    # Apply rules to analyze the situation
    rule_result = AgriBotRules.analyze_conditions(
        temperature=readings['temperature'],
        humidity=readings['humidity'],
        moisture=readings['moisture'],
        severity=anomaly_event.severity
    )
    
    # Calculate confidence based on urgency and severity
    confidence = _calculate_confidence(rule_result['urgency'], anomaly_event.severity)
    
    # Prepare data for explanation
    explanation_data = {
        'plot_id': anomaly_event.plot_id,
        'plot_name': f"Plot {anomaly_event.plot_id}",
        'timestamp': anomaly_event.timestamp.strftime('%Y-%m-%d %H:%M'),
        'severity': anomaly_event.severity.upper(),
        'temperature': readings['temperature'],
        'humidity': readings['humidity'],
        'moisture': readings['moisture'],
        'diagnosis': rule_result['diagnosis'],
        'cause': rule_result['cause'],
        'action': rule_result['action'],
        'urgency': rule_result['urgency'],
        'category': rule_result['category']
    }
    
    # Generate human-readable explanation
    explanation = ExplanationGenerator.generate(template_type, explanation_data)
    
    return {
        'recommended_action': rule_result['action'],
        'explanation_text': explanation,
        'confidence': confidence,
        'diagnosis': rule_result['diagnosis'],
        'urgency': rule_result['urgency'],
        'category': rule_result['category']
    }


def create_recommendation_record(anomaly_event, template_type='farmer_friendly'):
    """
    Generate recommendation and save to database.
    
    Args:
        anomaly_event: AnomalyEvent instance
        template_type: Format for explanation
    
    Returns:
        Created AgentRecommendation instance
    """
    # Generate the recommendation
    recommendation = generate_recommendation(anomaly_event, template_type)
    
    # Check if recommendation already exists
    existing = AgentRecommendation.objects.filter(
        anomaly_event=anomaly_event
    ).first()
    
    if existing:
        # Update existing
        existing.recommended_action = recommendation['recommended_action']
        existing.explanation_text = recommendation['explanation_text']
        existing.confidence = recommendation['confidence']
        existing.save()
        print(f"Updated recommendation for anomaly {anomaly_event.id}")
        return existing
    else:
        # Create new
        rec = AgentRecommendation.objects.create(
            anomaly_event=anomaly_event,
            recommended_action=recommendation['recommended_action'],
            explanation_text=recommendation['explanation_text'],
            confidence=recommendation['confidence']
        )
        print(f"Created recommendation for anomaly {anomaly_event.id}")
        return rec


def get_recommendation_for_readings(plot_id, temperature, humidity, moisture, severity='medium'):
    """
    Get recommendation for specific sensor readings (without anomaly event).
    
    Useful for testing or real-time advice.
    
    Args:
        plot_id: Plot ID
        temperature, humidity, moisture: Sensor values
        severity: Severity level
    
    Returns:
        Recommendation dictionary
    """
    # Apply rules
    rule_result = AgriBotRules.analyze_conditions(
        temperature=temperature,
        humidity=humidity,
        moisture=moisture,
        severity=severity
    )
    
    # Prepare explanation data
    explanation_data = {
        'plot_id': plot_id,
        'plot_name': f"Plot {plot_id}",
        'timestamp': 'now',
        'severity': severity.upper(),
        'temperature': temperature,
        'humidity': humidity,
        'moisture': moisture,
        'diagnosis': rule_result['diagnosis'],
        'cause': rule_result['cause'],
        'action': rule_result['action'],
        'urgency': rule_result['urgency'],
        'category': rule_result['category']
    }
    
    # Generate explanation
    explanation = ExplanationGenerator.generate('farmer_friendly', explanation_data)
    
    return {
        'diagnosis': rule_result['diagnosis'],
        'action': rule_result['action'],
        'explanation': explanation,
        'urgency': rule_result['urgency'],
        'confidence': _calculate_confidence(rule_result['urgency'], severity)
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _parse_sensor_values(anomaly_type_text):
    """
    Extract sensor values from anomaly description.
    
    Example: "Unusual sensor combo: T=35.0°C, H=20.0%, M=15.0%"
    """
    import re
    
    # Default values
    values = {
        'temperature': 25.0,
        'humidity': 50.0,
        'moisture': 40.0
    }
    
    # Try to extract values using regex
    temp_match = re.search(r'T=([0-9.]+)', anomaly_type_text)
    humid_match = re.search(r'H=([0-9.]+)', anomaly_type_text)
    moist_match = re.search(r'M=([0-9.]+)', anomaly_type_text)
    
    if temp_match:
        values['temperature'] = float(temp_match.group(1))
    if humid_match:
        values['humidity'] = float(humid_match.group(1))
    if moist_match:
        values['moisture'] = float(moist_match.group(1))
    
    return values


def _calculate_confidence(urgency, severity):
    """
    Calculate confidence score based on urgency and severity.
    
    Returns float between 0 and 1.
    """
    severity_scores = {
        'low': 0.6,
        'medium': 0.8,
        'high': 0.95
    }
    
    base_confidence = severity_scores.get(severity, 0.7)
    
    # Adjust based on urgency
    urgency_adjustment = (urgency - 3) * 0.05  # -0.1 to +0.1
    
    confidence = base_confidence + urgency_adjustment
    
    # Clamp between 0.5 and 0.99
    return max(0.5, min(0.99, confidence))
