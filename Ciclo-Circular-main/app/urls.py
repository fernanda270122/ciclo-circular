from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .api_views import OfertaViewSet, NecesidadViewSet


# Router para la API
router = DefaultRouter()
router.register(r'ofertas', OfertaViewSet, basename='oferta')
router.register(r'necesidades', NecesidadViewSet, basename='necesidad')
urlpatterns = [
    # --- HOME Y DIAGNÓSTICO ---
    path('', views.home, name="home"),
    path('auto_diagnostico', views.autoDiagnostico, name="auto_diagnostico"),
    path('auto_diagnostico/<int:empresa_id>/', views.autoDiagnostico, name="auto_diagnostico_empresa"),

    # --- ETAPA EXTRACCIÓN ---
    path('extraccion_materiaPrima', views.extraccionMateriaPrima, name="extraccion_materiaPrima"),
    path('agregar_entrada_extraccion', views.agregarEntradaExtraccion, name="agregar_entrada_extraccion"),
    path('agregar_salida_extraccion', views.agregarSalidaExtraccion, name="agregar_salida_extraccion"),
    path('agregar_oportunidad_extraccion', views.agregarOportunidadExtraccion, name="agregar_oportunidad_extraccion"),
    path('eliminar_entrada_extraccion/<int:id>/', views.eliminarEntradaExtraccion, name='eliminar_entrada_extraccion'),
    path('eliminar_oportunidad_extraccion/<int:id>/', views.eliminarOportunidadExtraccion, name='eliminar_oportunidad_extraccion'),
    path('eliminar_salida_extraccion/<int:id>/', views.eliminarSalidaExtraccion, name='eliminar_salida_extraccion'),
    
    # --- ETAPA DISEÑO ---
    path('diseño_Produccion', views.diseño_Produccion, name="diseño_Produccion"),
    path('agregar_entrada_diseño', views.agregarEntradaDiseño, name="agregar_entrada_diseño"),
    path('agregar_salida_diseño', views.agregarSalidaDiseño, name="agregar_salida_diseño"),
    path('agregar_oportunidad_diseño', views.agregarOportunidadDiseño, name="agregar_oportunidad_diseño"),
    path('eliminar_entrada_diseño/<int:id>/', views.eliminarEntradaDiseño, name='eliminar_entrada_diseño'),
    path('eliminar_oportunidad_diseño/<int:id>/', views.eliminarOportunidadDiseño, name='eliminar_oportunidad_diseño'),
    path('eliminar_salida_diseño/<int:id>/', views.eliminarSalidaDiseño, name='eliminar_salida_diseño'),

    # --- ETAPA LOGÍSTICA ---
    path('logistica', views.logistica, name="logistica"),
    path('agregar_entrada_logistica', views.agregarEntradaLogistica, name="agregar_entrada_logistica"),
    path('agregar_salida_logistica', views.agregarSalidaLogistica, name="agregar_salida_logistica"),
    path('agregar_oportunidad_logistica', views.agregarOportunidadLogistica, name="agregar_oportunidad_logistica"),
    path('eliminar_entrada_logistica/<int:id>/', views.eliminarEntradaLogistica, name='eliminar_entrada_logistica'),
    path('eliminar_oportunidad_logistica/<int:id>/', views.eliminarOportunidadLogistica, name='eliminar_oportunidad_logistica'),
    path('eliminar_salida_logistica/<int:id>/', views.eliminarSalidaLogistica, name='eliminar_salida_logistica'),

    # --- ETAPA COMPRA ---
    path('compra', views.compra, name="compra"),
    path('agregar_entrada_compra', views.agregarEntradaCompra, name="agregar_entrada_compra"),
    path('agregar_salida_compra', views.agregarSalidaCompra, name="agregar_salida_compra"),
    path('agregar_oportunidad_compra', views.agregarOportunidadCompra, name="agregar_oportunidad_compra"),
    path('eliminar_entrada_compra/<int:id>/', views.eliminarEntradaCompra, name='eliminar_entrada_compra'),
    path('eliminar_oportunidad_compra/<int:id>/', views.eliminarOportunidadCompra, name='eliminar_oportunidad_compra'),
    path('eliminar_salida_compra/<int:id>/', views.eliminarSalidaCompra, name='eliminar_salida_compra'),

    # --- ETAPA USO CONSUMO ---
    path('uso_consumo', views.usoConsumo, name="uso_consumo"),
    path('agregar_entrada_uso', views.agregarEntradaUso, name="agregar_entrada_uso"),
    path('agregar_salida_uso', views.agregarSalidaUso, name="agregar_salida_uso"),
    path('agregar_oportunidad_uso', views.agregarOportunidadUso, name="agregar_oportunidad_uso"),
    path('eliminar_entrada_uso_consumo/<int:id>/', views.eliminarEntradaUsoConsumo, name='eliminar_entrada_uso_consumo'),
    path('eliminar_oportunidad_uso/<int:id>/', views.eliminarOportunidadUso, name='eliminar_oportunidad_uso'),
    path('eliminar_salida_uso_consumo/<int:id>/', views.eliminarSalidaUso, name='eliminar_salida_uso_consumo'),

    # --- ETAPA FIN DE VIDA ---
    path('fin_vida', views.finVida, name="fin_vida"),
    path('agregar_entrada_fin', views.agregarEntradaFin, name="agregar_entrada_fin"),
    path('agregar_salida_fin', views.agregarSalidaFin, name="agregar_salida_fin"),
    path('agregar_oportunidad_fin', views.agregarOportunidadFin, name="agregar_oportunidad_fin"),
    path('eliminar_entrada_fin_vida/<int:id>/', views.eliminarEntradaFinVida, name='eliminar_entrada_fin_vida'),
    path('eliminar_oportunidad_fin_vida/<int:id>/', views.eliminarOportunidadFinVida, name='eliminar_oportunidad_fin_vida'),
    path('eliminar_salida_fin_vida/<int:id>/', views.eliminarSalidaFinVida, name='eliminar_salida_fin_vida'),

    # --- IDEAS ---
    path('ideas/', views.ingresar_ideas, name="ingresar_ideas"),
    path('ideas/<int:etapa_id>/', views.ingresar_ideas, name='ingresar_idea'),

    # --- PERFIL Y USUARIO ---
    path('mi_perfil', views.mi_perfil, name="mi_perfil"),
    path('mi-cv/', views.subir_cv, name='subir_cv'),
    path('perfil/oferta/', views.guardar_oferta, name='guardar_oferta'),
    path('perfil/necesidad/', views.guardar_necesidad, name='guardar_necesidad'),
    path('perfil/guardar_keywords_cv/', views.guardar_keywords_cv, name='guardar_keywords_cv'),
    path('perfil/eliminar-cv/', views.eliminar_cv, name='eliminar_cv'),
    
    # 1. Vista de Usuario
    path('bolsa/mis-ofertas/', views.crear_oferta_laboral, name='mis_ofertas'),
    path('mis-matches/', views.mis_matches, name='mis_matches'),
    # 2. Vista de Candidato
    path('bolsa/oportunidades/', views.mis_oportunidades, name='mis_oportunidades'), 
    
    path('gestion-bolsa/', views.admin_ofertas, name='gestion-bolsa'),
    path('gestion-necesidades/', views.admin_necesidades, name='gestion-necesidades'),
    path('oferta/eliminar/<int:oferta_id>/', views.eliminar_oferta, name='eliminar_oferta'),
    path('oferta/ver/<int:oferta_id>/', views.ver_oferta, name='ver_oferta'),
    # 4. CRUD
    path('oferta/editar/<int:oferta_id>/', views.editar_oferta, name='editar_oferta'),
    path('oferta/eliminar/<int:oferta_id>/', views.eliminar_oferta, name='eliminar_oferta'),

    # --- CALENDARIO Y EVENTOS ---
    path('calendario/seleccion/', views.seleccion_empresa_calendario, name='seleccion_empresa_calendario'),
    path('calendario-corporativo/', views.vista_calendario, name='ver_calendario'),
    path('api/eventos/', views.listar_eventos, name='api_listar_eventos'),
    path('api/guardar_evento/', views.guardar_evento, name='guardar_evento'), 
    path('api/eliminar_evento/', views.eliminar_evento, name='eliminar_evento'),
    
    
    
    # Rutas Eventos (Líneas separadas correctamente)
    path('evento/<int:evento_id>/asistencia/', views.gestionar_asistencia, name='gestionar_asistencia'),
    path('evento/enviar/<int:evento_id>/', views.enviar_solicitud_confirmacion, name='enviar_solicitud_confirmacion'),
    path('evento/<int:evento_id>/enviar-formal/', views.enviar_entrada_formal, name='enviar_formal'),
    
    path('eventos/mis-invitaciones/', views.mis_invitaciones, name='mis_invitaciones'),
    path('invitacion/<int:invitacion_id>/responder/<str:respuesta>/', views.responder_invitacion, name='responder_invitacion'),
    path('eventos/<int:evento_id>/recordar-pendientes/', views.enviar_recordatorio_pendientes, name='enviar_recordatorio_pendientes'),

    # --- API SELECTORES ---
    path('api/get_facultades/', views.get_facultades, name='get_facultades'),
    path('api/get_departamentos/', views.get_departamentos, name='get_departamentos'),
    path('api/get_carreras/', views.get_carreras, name='get_carreras'),

    path('dashboard/', views.home, name='home_admin'),  # El menú pide 'home_admin'
    path('frecuencias/', views.home, name='home_admin_frecuencias'), # El menú pide 'home_admin_frecuencias'
    path('graficos/', views.home, name='home_graficos'), # El menú pide 'home_graficos'
    path('logs/', views.home, name='log_telegram'), # El menú pide 'log_telegram'
    path('api-root/', views.home, name='Home_api'), # El menú pide 'Home_api' (Cuidado con mayúscula)
    
    # Ruta de usuarios (si no tienes la vista admin_usuarios, usa home temporalmente)
    path('admin-usuarios/', views.home, name='admin_usuarios'),
    path('procesamiento/', views.home, name='home_procesamiento'),
    path('notificaciones/', views.home, name='menu_notificaciones'),
    path('descargar-plantilla/', views.descargar_plantilla, name='descargar_plantilla'),
    
    #path('mi-calendario/', views.vista_calendario, name='ver_calendario'),
    path('responder-invitacion-ajax/<int:evento_id>/<str:accion>/', views.responder_invitacion_ajax, name='responder_invitacion_ajax'),
    path('mi-calendario/', views.ver_calendario_view, name='ver_calendario'),
    path('ping/', views.ping),
    
    path('preguntas/<int:evento_id>/', views.listar_preguntas, name='listar_preguntas'),
    # Esta es la ruta nueva exclusiva para el portal de administración
    
    path('cron/recordatorios/<str:token>/', views.ejecutar_recordatorios_cron, name='cron_recordatorios'),
    

    # Iniciar pago
    path('pagos/iniciar/<int:evento_id>/', views.iniciar_pago_evento, name='iniciar_pago_evento'),
    
    # Retornos visuales
    path('pagos/exito/', views.pago_exitoso, name='pago_exitoso'),
    path('pagos/fallo/', views.pago_fallido, name='pago_fallido'),
    path('pagos/pendiente/', views.pago_pendiente, name='pago_pendiente'),
    
    # Webhook
    path('api/pagos/webhook/', views.webhook_mercadopago, name='webhook_mercadopago'),
   
   
   path('recuperar-clave/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('recuperar-clave/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('recuperar-clave/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('recuperar-clave/completo/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    


    # Rutas para Networking (Empresas/Trabajos)
    path('networking/guardar/', views.guardar_empresa_trabajo, name='guardar_empresa_trabajo'),
    path('networking/eliminar/<int:id>/', views.eliminar_empresa_trabajo, name='eliminar_empresa_trabajo'),
    
    path('perfil/guardar-bancos/', views.guardar_bancos_usuario, name='guardar_bancos_usuario'),
    
    path('mi-membresia/', views.mi_membresia, name='mi_membresia'),
    
    path('pagos/membresia/iniciar/<int:plan_id>/', views.iniciar_pago_membresia, name='iniciar_pago_membresia'),
    path('api/bolsa/', include(router.urls)),
    
    #RUTA DE NECESITO OFREZCO
    
    path('ofrezco-necesito/', views.vista_networking, name='pagina_networking'),
    # path('api/ofertas/<int:oferta_id>/', ver_oferta_api),
    path('networking/guardar-oferta/', views.guardar_oferta, name='guardar_oferta'),

    path('api/', include('api.urls')),
    
    path('networking/oferta/editar/<int:oferta_id>/', views.editar_networking_oferta, name='editar_networking_oferta'),
    path('networking/oferta/eliminar/<int:oferta_id>/', views.eliminar_networking_oferta, name='eliminar_networking_oferta'),
    path('networking/necesidad/editar/<int:necesidad_id>/', views.editar_networking_necesidad, name='editar_networking_necesidad'),
    path('networking/necesidad/eliminar/<int:necesidad_id>/', views.eliminar_networking_necesidad, name='eliminar_networking_necesidad'),
    path('networking/necesidad/ver/<int:necesidad_id>/', views.ver_necesidad, name='ver_necesidad'),
    
    # DESCARGA DE EXCEL PARA PREGUNTAS EN EVENTOS 
    path('evento/<int:evento_id>/descargar-historial/', views.descargar_historial_evento, name='descargar_historial_evento'),
    
    #ELIMINAR HISTORIAL DE CHAT DEDSPUES DE 30 DIAS
    path('cron/limpiar-historial/<str:token>/', views.limpiar_historial_cron, name='limpiar_historial_cron'),
    
    #PANEL COORDINADOR PARA DESCARGA DE EXCEL
    path('panel-coordinador/', views.panel_coordinador, name='panel_coordinador'),
    
    path('evento/<int:evento_id>/limpiar-chat/', views.limpiar_chat_evento, name='limpiar_chat_evento'),
    

    #TIENDA
    path('tienda/', views.tienda, name='tienda'),
    path('tienda/comprar/<int:producto_id>/', views.iniciar_pago_producto, name='iniciar_pago_producto'),
    path('tienda/pago/exito/', views.pago_producto_exitoso, name='pago_producto_exitoso'),
    path('tienda/pago/fallo/', views.pago_producto_fallido, name='pago_producto_fallido'),


    # Encuestas
    path('encuestas/<int:encuesta_id>/responder/', views.responder_encuesta, name='responder_encuesta'),
    path('mis-encuestas/', views.mis_encuestas, name='mis_encuestas'),
    
    #BIBLIOTECA
    path('biblioteca/', views.biblioteca, name='biblioteca'),
    path('biblioteca/crear/', views.biblioteca_crear, name='biblioteca_crear'),                                             
    path('biblioteca/editar/<int:pk>/', views.biblioteca_editar, name='biblioteca_editar'),
    path('biblioteca/eliminar/<int:pk>/', views.biblioteca_eliminar, name='biblioteca_eliminar'),
    ]