import os
import sys
import django

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agriculture_backend.settings")
django.setup()

from mlmodule.iris_service import run_batch_detection

print("=" * 60)
print("IRIS - BATCH TEST (ALL PLOTS) + CREATE EVENTS")
print("=" * 60)

results = run_batch_detection(
    plot_id=None,       
    minutes=60,          
    create_events=True,  
    no_duplicates=True,  
)

print("\nRESULTS:")
print(results)

if results.get("success"):
    print("\nSUMMARY:")
    print(f"Total analyzed:  {results['total_analyzed']}")
    print(f"Anomalies found: {results['anomalies_found']}")
    print(f"Anomaly rate:    {results['anomaly_rate']:.4f}")
    print(f"Events created:  {results['events_created']}")
    

    print("\nBY PLOT:")
    for pid, info in results["by_plot"].items():
        print(
            f"  Plot {pid}: analyzed={info['analyzed']}, anomalies={info['anomalies']}, "
            f"rate={info['anomaly_rate']:.4f}, events_created={info['events_created']}, "
            
        )
else:
    print("\nERROR:", results.get("message"))

