# AgriBot - Rule-Based AI Agent 🤖

## What is AgriBot?

**AgriBot is a simple AI agent that:**
- Analyzes sensor readings (temperature, humidity, moisture)
- Uses **14 smart rules** (10 basic + 4 advanced)
- Generates **human-readable recommendations** with templates
- Includes **trend detection** for moisture drops and temperature anomalies

**Not machine learning, just smart rules!** Easy to understand for students.

---

## How It Works

### 1. Rule Engine (14 Rules Total)

**Basic Rules (10):** Standard environmental conditions
```python
# Example Basic Rule:
if temperature > 35 and humidity < 30 and moisture < 20:
    diagnosis = "Heat stress with severe drought"
    action = "URGENT: Immediate irrigation required"
    urgency = 5  # Very urgent!
```

**Advanced Rules (4):** Trend-based analysis
```python
# Example Advanced Rule:
if moisture_trend < -10:  # Dropped >10%
    diagnosis = "Rapid soil moisture depletion"
    action = "Check irrigation system - possible leak"
    urgency = 5
```

### 2. Template Engine
Converts technical data into structured explanations:

```
Template includes:
- Timestamp and anomaly type
- Model confidence score  
- Specific sensor values/trends
- Recommended action
- Confidence level
```

### 3. Recommendation Generator
Combines rules + templates = smart advice!

---

## ⚡ Quick Start

### Basic Usage (Simple)

```python
from mlmodule.agribot import get_recommendation_for_readings

# Get advice for sensor readings
rec = get_recommendation_for_readings(
    plot_id=1,
    temperature=38.0,  # Hot!
    humidity=15.0,     # Dry!
    moisture=10.0,     # Very dry soil!
    severity='high'
)

print(rec['diagnosis'])  # "Heat stress with severe drought"
print(rec['action'])     # "URGENT: Immediate irrigation required..."
print(rec['urgency'])    # 5
```

### Option 2: For Anomaly Events

```python
from mlmodule.agribot import create_recommendation_record
from monitoring.models import AnomalyEvent

# Get an anomaly
anomaly = AnomalyEvent.objects.get(id=123)

# Generate and save recommendation
recommendation = create_recommendation_record(anomaly)

print(recommendation.recommended_action)
print(recommendation.explanation_text)
print(recommendation.confidence)
```

### Option 3: RESTful API

```bash
# Get advice for readings
POST /api/iris/advice/
{
  "plot_id": 1,
  "temperature": 38.0,
  "humidity": 15.0,
  "moisture": 10.0,
  "severity": "high"
}

# Generate recommendation for anomaly
POST /api/iris/recommend/
{
  "anomaly_id": 123,
  "save_to_db": true
}
```

---

## The 14 Rules

### Basic Rules (10)

| Rule | Condition | Diagnosis | Urgency |
|------|-----------|-----------|---------|
| 1 | T>35, H<30, M<20 | Extreme drought/heat | 5 |
| 2 | T>30, M<30 | Water stress | 4 |
| 3 | T<10, H>80, M>70 | Fungal risk | 4 |
| 4 | M>80 | Waterlogged | 3 |
| 5 | M<15 | Severe dryness | 4 |
| 6 | H>85, 20<T<30 | Disease risk | 3 |
| 7 | H<25 | Low humidity | 2 |
| 8a | T>40 | Extreme heat | 5 |
| 8b | T<5 | Frost risk | 5 |
| 9 | T>28, H<40 | Hot & dry air | 3 |
| 10 | Default | Minor variation | 1 |

### Advanced Rules (4) - Trend-Based

| Rule | Condition | Diagnosis | Urgency |
|------|-----------|-----------|---------|
| 11 | Moisture drop >10% | Irrigation failure | 5 |
| 12 | Temperature >+5°C above normal | Heat stress | 4 |
| 13 | Confidence 0.4-0.6 | Needs verification | 2 |
| 14 | 2+ extreme sensors | Multiple stress factors | 5 |

**Advanced Usage:**
```python
from mlmodule.agribot import AgriBotRules

# Use advanced rules with trend data
result = AgriBotRules.analyze_with_trends(
    temperature=26.0,
    humidity=55.0,
    moisture=28.0,
    severity='high',
    moisture_trend=-12.0,     # Dropped 12%!
    temp_trend=7.0,           # 7°C above normal
    anomaly_confidence=0.85   # High confidence
)

print(result['diagnosis'])  # "Rapid soil moisture depletion detected"
print(result['action'])     # "URGENT: Check irrigation system..."
```

---

## Example Output

**Advanced Rule Example (Irrigation Failure):**

```
On 2025-12-15 at 09:20, sensor readings detected an irrigation_failure 
anomaly (model confidence 0.85).

Sensor Readings:
  • Temperature: 26.0°C
  • Humidity: 55.0%
  • Soil Moisture: 28.0%
Moisture drop: -12.0%

Diagnosis: Rapid soil moisture depletion detected

Explanation: Soil moisture dropped 12.0% rapidly. Possible irrigation 
system failure, leak, or pump malfunction.

Agent Recommendation: URGENT: Check irrigation system immediately. 
Inspect for leaks. Verify pump operation. Begin manual watering if needed.

Confidence Level: HIGH
```

---

## Example Scenarios

### Scenario 1: Drought
```python
Input: T=38°C, H=15%, M=10%
Diagnosis: "Heat stress with severe drought"
Action: "URGENT: Immediate irrigation required. Consider shade covers."
Urgency: 5/5
```

### Scenario 2: Waterlogged
```python
Input: T=22°C, H=85%, M=90%
Diagnosis: "Soil waterlogging detected"
Action: "Stop irrigation immediately. Check drainage system."
Urgency: 3/5
```

### Scenario 3: Frost Risk
```python
Input: T=3°C, H=70%, M=50%
Diagnosis: "Frost risk"
Action: "Protect crops with covers. Consider heating if available."
Urgency: 5/5
```

---

## File Structure

```
mlmodule/
├── agribot.py              ⭐ Main file (~450 lines)
│   ├── AgriBotRules        - Rule engine (10 rules)
│   ├── ExplanationGenerator - Templates (4 formats)
│   ├── generate_recommendation() - Main function
│   ├── create_recommendation_record() - Save to DB
│   └── get_recommendation_for_readings() - Quick check
│
└── test_agribot.py         - Test script
```

---

## Understanding the Code

### 1. AgriBotRules Class
```python
class AgriBotRules:
    @staticmethod
    def analyze_conditions(temperature, humidity, moisture, severity):
        # RULE 1: Check extreme heat + drought
        if temperature > 35 and humidity < 30 and moisture < 20:
            return {
                'diagnosis': 'Heat stress...',
                'action': 'Immediate irrigation...',
                'urgency': 5
            }
        
        # RULE 2, 3, 4... (more rules)
        
        # DEFAULT: If no rule matches
        return  {
            'diagnosis': 'Minor variation',
            'urgency': 1
        }
```

Simple if-then logic! Each rule returns what's wrong and what to do.

### 2. ExplanationGenerator Class
```python
class ExplanationGenerator:
    TEMPLATES = {
        'farmer_friendly': (
            "⚠️ Alert for your plot!\n"
            "What we found: {diagnosis}\n"
            "What you should do: {action}\n"
        )
    }
    
    @staticmethod
    def generate(template_type, data):
        template = ExplanationGenerator.TEMPLATES[template_type]
        return template.format(**data)  # Fill in the blanks!
```

Uses Python string formatting to fill templates with data.

### 3. Main Function
```python
def get_recommendation_for_readings(plot_id, temperature, humidity, moisture):
    # Step 1: Apply rules
    rule_result = AgriBotRules.analyze_conditions(...)
    
    # Step 2: Prepare data
    data = {
        'diagnosis': rule_result['diagnosis'],
        'action': rule_result['action'],
        ...
    }
    
    # Step 3: Generate explanation
    explanation = ExplanationGenerator.generate('farmer_friendly', data)
    
    return {
        'diagnosis': rule_result['diagnosis'],
        'action': rule_result['action'],
        'explanation': explanation
    }
```

That's it! Rules → Data → Template → Recommendation!

---

## Integration with Iris

Iris (ML) + AgriBot (Rules) = Complete System

```
1. Iris detects anomaly → Creates AnomalyEvent
2. AgriBot analyzes anomaly → Creates AgentRecommendation
3. Farmer gets: What's wrong + What to do!
```

You can auto-generate recommendations:

```python
# After Iris detects anomaly
from mlmodule.iris_service import run_batch_detection
from mlmodule.agribot import create_recommendation_record

# Detect anomalies
results = run_batch_detection(minutes=10)

# For each anomaly, generate recommendation
from monitoring.models import AnomalyEvent

recent_anomalies = AnomalyEvent.objects.filter(
    anomaly_type__icontains='Unusual sensor combo'
).order_by('-timestamp')[:10]

for anomaly in recent_anomalies:
    rec = create_recommendation_record(anomaly)
    print(f"Created recommendation {rec.id} for anomaly {anomaly.id}")
```

---

## Testing

```bash
# Test all rules (basic + advanced)
pipenv run python mlmodule/test_agribot.py
```

The test script covers:
- ✓ 5 basic scenarios (drought, waterlogging, frost, fungal, normal)
- ✓ 4 advanced scenarios (moisture drop, sustained temp, low confidence, multiple stressors)

---

## For Your Report

**What to Say:**

> "I implemented a **rule-based AI agent** called AgriBot that generates recommendations for detected anomalies. The system uses:
>
> 1. **Rule Engine**: 10 if-then rules that analyze sensor combinations
> 2. **Template Engine**: Converts technical data into farmer-friendly messages
> 3. **Recommendation Generator**: Combines rules and templates to provide actionable advice
>
> Unlike machine learning, this is a **knowledge-based system** - simple, explainable, and easy to modify. Each rule checks specific conditions (e.g., high temperature + low moisture = drought) and returns a diagnosis and recommended action.
>
> The system integrates with Iris (ML anomaly detection) to provide complete monitoring: Iris finds unusual patterns, AgriBot explains what they mean and what to do about them."

---

## Key Concepts

1. **Rule-Based System** - Uses if-then logic, not ML
2. **Template-Based Generation** - Fills in blanks in text templates
3. **Explainable AI** - You can see exactly why it gave that advice
4. **Domain Knowledge** - Rules encode farming expertise

---

## Why This Design?

✅ **Simple** - Just if-then logic, anyone can understand  
✅ **Explainable** - Can trace exactly which rule triggered  
✅ **Modifiable** - Easy to add/change rules  
✅ **No Training** - No ML training needed  
✅ **Fast** - Instant recommendations  
✅ **Reliable** - Same input = same output

---

## Next Steps

1. Test: `pipenv run python mlmodule/test_agribot.py`
2. Try API: `POST /api/iris/advice/`
3. View in DB: `/admin/monitoring/agentrecommendation/`
4. Customize rules in `agribot.py`

**AgriBot is ready to give smart farming advice!** 🌱
