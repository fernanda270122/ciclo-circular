from django.urls import path
from . import views

# Importamos las vistas (al estar todas en .views, no necesitamos import explícito selectivo largo)
# Pero mantenemos tu estructura para no romper nada.
from .views import (
    homeAdmin, home_empresa, tablasExtraccion, entradasExtraccion, SalidasExtraccion, OportunidadExtraccion, 
    EntradaDiseño, salidaDiseño, oportunidadDiseño, EntradaLogistica, salidaLogistica, oportunidadLogistica, 
    entradaCompra, salidaCompra, oportunidadesCompra, entradaUsoConsumo, salidaUsoConsumo, oportunidadUsoConsumo, 
    entradaFin, salidaFin, oportunidadFin, tablasDiseño, tablasLogistica, tablasCompra, tablasUso, tablasFin, 
    promedioArea, promedioHome, homeFrecuenciaDiseño, homeFrecuenciaLogistica, homeFrecuenciaCompra, 
    homeFrecuenciaUso, homeFrecuenciaFin, frecuenciaDiseño, frecuenciaLogistica, frecuenciaCompra, frecuenciaUso, 
    frecuenciaFin, homeGraficos, etapaGraficos, areasExtraccion, graficosExtraccion, areasDiseño, graficosDiseño, 
    areasLogistica, graficosLogistica, areasCompra, graficosCompra, areasUso, graficosUso, areasFin, graficosFin, 
    ReporteExcel, ReporteExcelSalida, ReporteExcelOportunidades, ReporteExcelEntradaDiseño, ReporteExcelSalidaDiseño, 
    ReporteExcelOportunidadDiseño, ReporteExcelEntradaLogistica, ReporteExcelSalidaLogistica, 
    ReporteExcelOportunidadLogistica, ReporteExcelEntradaCompra, ReporteExcelSalidaCompra, 
    ReporteExcelOportunidadCompra, ReporteExcelEntradaUso, ReporteExcelSalidaUso, ReporteExcelOportunidadUso, 
    ReporteExcelEntradaFin, ReporteExcelSalidaFin, ReporteExcelOportunidadFin, log_telegan, ia_semantica, 
    descargar_resumen, procesamiento_area, procesamiento_ideas, home_procesamiento, procesamiento_aempresa, 
    admin_usuarios, editar_usuario, eliminar_usuario, resetear_clave, crear_usuario, notificaciones, 
    enviar_recordatorio_view, enviar_mensaje_todos, form_mensaje_todos, menu_notificaciones, notificaciones_comuna, 
    form_mensaje_comuna, enviar_mensaje_comuna, ver_cv, descargar_cv, procesamiento_palabra_clave, 
    asignar_coordinador, quitar_coordinador, panel_coordinador, registro, frecuencias, graficos, coordina_usuarios, 
    crear_usuario_coordinacion, ver_cv_coordinacion, editar_usuario_coordinacion, eliminar_usuario_coordinacion, 
    resetear_clave_coordinacion, procesamiento_cvs, procesamiento_ofrezco_necesito, cargar_excel_usuarios,
    # Funciones de eventos (Ahora sí están en views.py)
    gestionar_asistencia, reporte_confirmados, descargar_pdf_confirmados, enviar_recordatorio_pendientes, 
    instituciones_coordinadores, eliminar_log_correo, eliminar_todos_logs
)

urlpatterns = [
    path('home_admin', homeAdmin, name='home_admin'),
    path('home_empresa/<id>/', home_empresa, name='home_empresa'),
    path('home_graficos', homeGraficos, name="home_graficos"),
    
    # Procesamiento
    path('procesamiento_area', procesamiento_area, name='procesamiento_area'),
    path('procesamiento_ideas', procesamiento_ideas, name='procesamiento_ideas'),
    path('procesamiento/', home_procesamiento, name='home_procesamiento'),
    path('procesamiento_aempresa', procesamiento_aempresa, name='procesamiento_aempresa'),
    path('procesamiento_palabra_clave', procesamiento_palabra_clave, name='procesamiento_palabra_clave'),
    path('procesamiento_cvs', procesamiento_cvs, name='procesamiento_cvs'),
    path('procesamiento_ofrezco_necesito', procesamiento_ofrezco_necesito, name='procesamiento_ofrezco_necesito'),
    
    # Admin usuarios
    path('usuarios/', admin_usuarios, name='admin_usuarios'),
    path("usuarios/editar/<int:user_id>/", editar_usuario, name="editar_usuario"),
    path('usuarios/eliminar/<int:id>/', eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/resetear/<int:user_id>/', resetear_clave, name='resetear_clave'),
    path("usuarios/crear/", crear_usuario, name="crear_usuario"),
    
    # CV usuarios
    path('usuarios/cv/<int:user_id>/', ver_cv, name='ver_cv'),
    path('usuarios/cv/descargar/<int:cv_id>/', descargar_cv, name='descargar_cv'),
    path("administrador/cargar_excel/", cargar_excel_usuarios, name="cargar_excel_usuarios"),
    path("instituciones/coordinadores/", instituciones_coordinadores, name="instituciones_coordinadores"),
    path("mensajeria/eliminar/<int:log_id>/", eliminar_log_correo, name="eliminar_log_correo"),
    path("mensajeria/eliminar-todo/", eliminar_todos_logs, name="eliminar_todos_logs"),
    path('usuarios/<int:user_id>/agregar-cv/', views.agregar_cv, name='agregar_cv'),
    # Notificaciones
    path("notificaciones/", notificaciones, name="notificaciones"),
    path("notificaciones/opciones/", menu_notificaciones, name="menu_notificaciones"),
    path("notificaciones/enviar/<int:id_empresa>/", enviar_recordatorio_view, name="enviar_recordatorio"),
    path("notificaciones/enviar_todos/<int:id_empresa>/", enviar_mensaje_todos, name="enviar_mensaje_todos"),
    path("notificaciones/mensaje-todos/<int:id_empresa>/", form_mensaje_todos, name="form_mensaje_todos"),
    path("notificaciones/comuna/", notificaciones_comuna, name="notificaciones_comuna"),
    path("notificaciones/comuna/<str:comuna>/form/", form_mensaje_comuna, name="form_mensaje_comuna"),
    path("notificaciones/comuna/<str:comuna>/enviar/", enviar_mensaje_comuna, name="enviar_mensaje_comuna"),

    # Graficos
    path('area_graficos/<id>/', etapaGraficos, name='area_graficos'),

    # Tablas
    path('tablas_extraccion/<id>/', tablasExtraccion, name='tablas_extraccion'),
    path('tablas_diseño/<id>/', tablasDiseño, name='tablas_diseño'),
    path('tablas_logistica/<id>/', tablasLogistica, name='tablas_logistica'),
    path('tablas_compra/<id>/', tablasCompra, name='tablas_compra'),
    path('tablas_uso/<id>/', tablasUso, name='tablas_uso'),
    path('tablas_fin/<id>/', tablasFin, name='tablas_fin'),
    path('promedio_home/<id>/', promedioHome, name='promedio_home'),
    path('promedio_area/<id>/', promedioArea, name='promedio_area'),

    # Extraccion
    path('entradas_extraccion', entradasExtraccion, name='entradas_extraccion'),
    path('salidas_extraccion', SalidasExtraccion, name='salidas_extraccion'),
    path('oportuniades_extraccion', OportunidadExtraccion, name='oportuniades_extraccion'),
    path('areas_extraccion/<id>', areasExtraccion, name='areas_extraccion'),
    path('graficos_extraccion/<id>', graficosExtraccion, name='graficos_extraccion'),
    
    # Diseño
    path('entradas_diseño', EntradaDiseño, name='entradas_diseño'),
    path('salida_diseño', salidaDiseño, name='salida_diseño'),
    path('oportunidad_diseño', oportunidadDiseño, name='oportunidad_diseño'),
    path('home_frecuencia_diseño/<id>/', homeFrecuenciaDiseño, name='home_frecuencia_diseño'),
    path('frecuencia_diseño/<id>/', frecuenciaDiseño, name='frecuencia_diseño'),
    path('areas_diseño/<id>/', areasDiseño, name='areas_diseño'),
    path('graficos_diseño/<id>/', graficosDiseño, name='graficos_diseño'),
    
    # Logistica
    path('entradas_logistica', EntradaLogistica, name='entradas_logistica'),
    path('salida_logistica', salidaLogistica, name='salida_logistica'),
    path('oportunidad_logistica', oportunidadLogistica, name='oportunidad_logistica'),
    path('home_frecuencia_logistica/<id>/', homeFrecuenciaLogistica, name='home_frecuencia_logistica'),
    path('frecuencia_logistica/<id>/', frecuenciaLogistica, name='frecuencia_logistica'),
    path('areas_logistica/<id>/', areasLogistica, name='areas_logistica'),
    path('graficos_logistica/<id>/', graficosLogistica, name='graficos_logistica'),
   
    # Compra
    path('entradas_compra', entradaCompra, name='entradas_compra'),
    path('salida_compra', salidaCompra, name='salida_compra'),
    path('oportunidad_compra', oportunidadesCompra, name='oportunidad_compra'),
    path('home_frecuencia_compra/<id>/', homeFrecuenciaCompra, name='home_frecuencia_compra'),
    path('frecuencia_compra/<id>/', frecuenciaCompra, name='frecuencia_compra'),
    path('areas_compra/<id>/', areasCompra, name='areas_compra'),
    path('graficos_compra/<id>/', graficosCompra, name='graficos_compra'),

    # Uso consumo
    path('entradas_uso', entradaUsoConsumo, name='entradas_uso'),
    path('salidas_uso', salidaUsoConsumo, name='salidas_uso'),
    path('oportunidad_uso', oportunidadUsoConsumo, name='oportunidad_uso'),
    path('home_frecuencia_uso/<id>/', homeFrecuenciaUso, name='home_frecuencia_uso'),
    path('frecuencia_uso/<id>/', frecuenciaUso, name='frecuencia_uso'),
    path('areas_uso/<id>/', areasUso, name='areas_uso'),
    path('graficos_uso/<id>/', graficosUso, name='graficos_uso'),
    
    # Fin de vida
    path('entrada_fin', entradaFin, name='entrada_fin'),
    path('salidas_fin', salidaFin, name='salidas_fin'),
    path('oportunidad_fin', oportunidadFin, name='oportunidad_fin'),
    path('home_frecuencia_fin/<id>/', homeFrecuenciaFin, name='home_frecuencia_fin'),
    path('frecuencia_fin/<id>/', frecuenciaFin, name='frecuencia_fin'),
    path('areas_fin/<id>/', areasFin, name='areas_fin'),
    path('graficos_fin/<id>/', graficosFin, name='graficos_fin'),

    # Reportes Excel
    path('reporte_entradas', ReporteExcel.as_view(), name="reporte_entradas"),
    path('reporte_salidas', ReporteExcelSalida.as_view(), name="reporte_salidas"),
    path('reporte_oportunidades', ReporteExcelOportunidades.as_view(), name="reporte_oportunidades"),
    path('reporte_entradas_diseño', ReporteExcelEntradaDiseño.as_view(), name="reporte_entradas_diseño"),
    path('reporte_salidas_diseño', ReporteExcelSalidaDiseño.as_view(), name="reporte_salidas_diseño"),
    path('reporte_oportunidades_diseño', ReporteExcelOportunidadDiseño.as_view(), name="reporte_oportunidades_diseño"),
    path('reporte_entradas_logistica', ReporteExcelEntradaLogistica.as_view(), name="reporte_entradas_logistica"),
    path('reporte_salidas_logistica', ReporteExcelSalidaLogistica.as_view(), name="reporte_salidas_logistica"),
    path('reporte_oportunidades_logistica', ReporteExcelOportunidadLogistica.as_view(), name="reporte_oportunidades_logistica"),
    path('reporte_entradas_compra', ReporteExcelEntradaCompra.as_view(), name="reporte_entradas_compra"),
    path('reporte_salidas_compra', ReporteExcelSalidaCompra.as_view(), name="reporte_salidas_compra"),
    path('reporte_oportunidades_Compra', ReporteExcelOportunidadCompra.as_view(), name="reporte_oportunidades_Compra"),
    path('reporte_entradas_uso', ReporteExcelEntradaUso.as_view(), name="reporte_entradas_uso"),
    path('reporte_salidas_uso', ReporteExcelSalidaUso.as_view(), name="reporte_salidas_uso"),
    path('reporte_oportunidades_uso', ReporteExcelOportunidadUso.as_view(), name="reporte_oportunidades_uso"),
    path('reporte_entradas_fin', ReporteExcelEntradaFin.as_view(), name="reporte_entradas_fin"),
    path('reporte_salidas_fin', ReporteExcelSalidaFin.as_view(), name="reporte_salidas_fin"),
    path('reporte_oportunidades_fin', ReporteExcelOportunidadFin.as_view(), name="reporte_oportunidades_fin"),

    # Utilidades
    path('log_telegram', log_telegan, name="log_telegram"),
    path('ia_semantica', ia_semantica, name='ia_semantica'),
    path('descargar_resumen', descargar_resumen, name='descargar_resumen'),
    path('procesamiento_area/<int:id_empresa>/', procesamiento_area, name="procesamiento_area_empresa"),
    path('procesamiento_ideas/<int:id_empresa>/', procesamiento_ideas, name='procesamiento_ideas_empresa'),

    # Coordinadores
    path('usuarios/asignar-coordinador/<int:universidad_id>/', asignar_coordinador, name='asignar_coordinador'),    
    path('usuarios/quitar-coordinador/<int:user_id>/', quitar_coordinador, name='quitar_coordinador'),
    path('coordinador/', panel_coordinador, name='panel_coordinador'),
    path('registro/', registro, name='registro'),
    path('frecuencias/', frecuencias, name='frecuencias'),
    path('graficos/', graficos, name='graficos'),
    path('coordina_usuarios/', coordina_usuarios, name='coordina_usuarios'),
    path("coordinador/usuarios/crear/", crear_usuario_coordinacion, name="crear_usuario_coordinacion"),
    path("coordinador/ver_cv/<int:user_id>/", ver_cv_coordinacion, name="ver_cv_coordinacion"),
    path("coordinador/usuarios/editar/<int:user_id>/", editar_usuario_coordinacion, name="editar_usuario_coordinacion"),
    path("coordinador/usuarios/eliminar/<int:user_id>/", eliminar_usuario_coordinacion, name="eliminar_usuario_coordinacion"),
    path("coordinador/usuarios/resetear/<int:user_id>/", resetear_clave_coordinacion, name="resetear_clave_coordinacion"),

    # ========================================================
    # GESTIÓN DE EVENTOS 
    # ========================================================
    
    path('evento/<int:evento_id>/asistencia/', gestionar_asistencia, name='gestion_asistencia'), 
    path('evento/<int:evento_id>/confirmados/', reporte_confirmados, name='reporte_confirmados'),
    path('evento/<int:evento_id>/confirmados/pdf/', descargar_pdf_confirmados, name='descargar_pdf_confirmados'),
    path('evento/<int:evento_id>/recordatorio/', enviar_recordatorio_pendientes, name='enviar_recordatorio_pendientes'),
    path('gestion-calendario/', views.calendario_admin_view, name='calendario_admin'),

path('usuarios/detalle/<int:user_id>/', views.detalle_usuario_admin, name='detalle_usuario_admin'),
path('usuarios/detalle/<int:user_id>/empresa/guardar/', views.admin_guardar_empresa_trabajo, name='admin_guardar_empresa_trabajo'),
path('usuarios/empresa/eliminar/<int:id>/', views.admin_eliminar_empresa_trabajo, name='admin_eliminar_empresa_trabajo'),
path('preferencias/', views.admin_preferencias, name='admin_preferencias'), 
path('preferencias/nueva/', views.admin_guardar_preferencia, name='admin_guardar_preferencia'),
path('perfil/preferencias/guardar/', views.guardar_preferencias_usuario, name='guardar_preferencias_usuario'),
path('usuarios/empresa/editar/<int:trabajo_id>/', views.admin_editar_empresa_trabajo, name='admin_editar_empresa_trabajo'),
path('preferencias/editar/<int:pref_id>/', views.admin_editar_preferencia, name='admin_editar_preferencia'),
path('preferencias/eliminar/<int:pref_id>/', views.admin_eliminar_preferencia, name='admin_eliminar_preferencia'),

# Rutas para el CRUD de Descuentos Bancarios
    path('descuentos/', views.admin_descuentos, name='admin_descuentos'),
    path('descuentos/guardar/', views.admin_guardar_descuento, name='admin_guardar_descuento'),
    path('descuentos/eliminar/<int:desc_id>/', views.admin_eliminar_descuento, name='admin_eliminar_descuento'),
    
    path('administrador/membresias/', views.admin_membresias, name='admin_membresias'),
    path('mensajeria/', views.admin_mensajeria, name='admin_mensajeria'),
    
    path('tienda/', views.gestion_tienda, name='gestion_tienda'),
    path('tienda/crear/', views.crear_producto, name='crear_producto'),
    path('tienda/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('tienda/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),

]