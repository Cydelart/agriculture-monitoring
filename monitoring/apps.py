from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'
    def ready(self):
        # Import ici (pas en haut du fichier)
        from MLModel.ML_Model import thi_detector
        from MLModel.ML_Model import df_year_normal

        thi_detector.train(df_year_normal)
        print("✅ THI Monthly Model trained")