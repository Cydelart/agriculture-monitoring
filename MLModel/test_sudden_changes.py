import pandas as pd
from datetime import datetime, timedelta
from sudden_change_anomaly import SensorAnalyzer  # your file with the function

# ------------------------------
# Test data: 5-min intervals
# ------------------------------


start_time = datetime.now()


timestamps = [
    start_time + timedelta(minutes=5*0),
    start_time + timedelta(minutes=5*1),
    start_time + timedelta(minutes=5*2),
    start_time + timedelta(minutes=5*3),
    start_time + timedelta(minutes=5*4),
    start_time + timedelta(minutes=5*5),
    start_time + timedelta(minutes=5*6),
    start_time + timedelta(minutes=5*7),
    start_time + timedelta(minutes=5*8),
    start_time + timedelta(minutes=5*9),
    start_time + timedelta(minutes=5*10),
    start_time + timedelta(minutes=5*11),
    start_time + timedelta(minutes=5*12),
    start_time + timedelta(minutes=5*13),
    start_time + timedelta(minutes=5*14),
    start_time + timedelta(minutes=5*15),
    start_time + timedelta(minutes=5*16),
    start_time + timedelta(minutes=5*17),
    start_time + timedelta(minutes=5*18),
    start_time + timedelta(minutes=5*19),
    start_time + timedelta(minutes=5*20),
    start_time + timedelta(minutes=5*21),
    start_time + timedelta(minutes=5*22),
    start_time + timedelta(minutes=5*23),
    start_time + timedelta(minutes=5*24),
    start_time + timedelta(minutes=5*25),
    start_time + timedelta(minutes=5*26),
    start_time + timedelta(minutes=5*27),
    start_time + timedelta(minutes=5*28),
    start_time + timedelta(minutes=5*29),
    start_time + timedelta(minutes=5*30),
    start_time + timedelta(minutes=5*31),
    start_time + timedelta(minutes=5*32),
    start_time + timedelta(minutes=5*33),
    start_time + timedelta(minutes=5*34),
    start_time + timedelta(minutes=5*35),
    start_time + timedelta(minutes=5*36),
    start_time + timedelta(minutes=5*37),
    start_time + timedelta(minutes=5*38),
    start_time + timedelta(minutes=5*39),
    start_time + timedelta(minutes=5*40),
]

# ------------------------------
# 38 moisture values (explicites)
# ------------------------------
moisture = [
    50,  # 0 
    45,  # 1 
    45,  # 2
    45,  # 3
    45,  # 4
    15,  # 5
    15,  # 6
    15,  # 7
    15,  # 8
    15,  # 9
    15,  # 10
    15,  # 11
    15,  # 12
    15,  # 13
    15,  # 14
    15,  # 15
    15,  # 16
    15,  # 17
    15,  # 18
    15,  # 19
    15,  # 20
    15,  # 21
    15,  # 22
    15,  # 23
    15,  # 24
    15,  # 25
    15,  # 26
    15,  # 27
    15,  # 28
    15,  # 29
    15,  # 30
    15,  # 31
    15,  # 32
    15,  # 33
    15,  # 34
    15,  # 35
    15,  # 36
    15,  # 37
    15,  # 38
    15,  # 39
    15,  # 40
]

# ------------------------------
# 38 temperature values (explicites)
# ------------------------------
temperature = [
    25,  # 0
    25,  # 1
    25,  # 2
    25,  # 3
    25,  # 4
    25,  # 5
    25,  # 6
    25,  # 7
    25,  # 8
    25,  # 9
    25,  # 10
    25,  # 11
    25,  # 12
    25,  # 13
    25,  # 14
    25,  # 15
    25,  # 16
    25,  # 17
    25,  # 18
    25,  # 19
    25,  # 20
    25,  # 21
    25,  # 22
    25,  # 23
    25,  # 24
    25,  # 25
    25,  # 26
    25,  # 27
    25,  # 28
    25,  # 29
    25,  # 30
    25,  # 31
    25,  # 32
    25,  # 33
    25,  # 34
    25,  # 35
    25,  # 36
    25,  # 37
    25,  # 38
    25,  # 39
    25,  # 40
]

# ------------------------------
# 38 plot IDs (explicites)
# ------------------------------
plot_id = [
    "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1",
    "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1",
    "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1",
    "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1",
    "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1", "Plot 1"
]

df_test = pd.DataFrame({
    "timestamp": timestamps,
    "moisture": moisture,
    "temperature": temperature,
    "plot": plot_id  # Nouvelle colonne ajoutée
})


# ------------------------------
# Test the function
# ------------------------------
analyzer = SensorAnalyzer()
anomalies = analyzer.sudden_change(df_test)

print("Detected anomalies:")
for idx, desc in anomalies:
    print(f"Row {idx}: {desc}")
