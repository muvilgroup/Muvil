from import_export import resources
from .models import Localizaciones

class LocalizacionesResource(resources.ModelResource):
    class Meta:
        model = Localizaciones
