from django.urls import include, path
from .views import *
from .views import enviar_pregunta_api, obtener_top_preguntas_api 
from .views import networking_ofertas_list

urlpatterns = [
    path('api_authorization/', include('rest_framework.urls')),
    path('home_api', home_api, name="Home_api"),
    path('view_usuarios/', User_APIView.as_view(), name="api_usuarios"),
    path('view_ubicacion/', Ubicacion_APIView.as_view(), name="api_ubicacion"),
    path('preguntas/enviar/', enviar_pregunta_api, name='enviar_pregunta_api'),
    path('preguntas/top/<int:evento_id>/', obtener_top_preguntas_api, name='obtener_top_preguntas_api'),
    
    # Ofertas
    path('ofertas/', ofertas_list, name='api_ofertas_list'),
    path('ofertas/<int:pk>/', oferta_detail, name='api_oferta_detail'),
    
    # Networking
    path('networking/ofertas/', networking_ofertas_list, name='api_networking_ofertas'),
    path('networking/ofertas/<int:pk>/', networking_ver_oferta, name='api_networking_ver_oferta'),
     
]
