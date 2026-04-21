from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Universidad, Facultad, Departamento, Carrera,
    Etapa, RegistroActividad, Entrada, Salida, Oportunidades,
    Idea, CVUsuario, Oferta, Necesidad, Evento, Invitacion
)

# -------------------------
# REGISTRO ACTIVIDAD IMPORT/EXPORT (Antes RegistroTrabajador)
# -------------------------

class RegistroActividadResource(resources.ModelResource):
    class Meta:
        model = RegistroActividad
        # Actualizado: 'carrera' en lugar de 'id_area'
        fields = ('id', 'usuario', 'descripcion', 'carrera')


@admin.register(RegistroActividad)
class RegistroActividadAdmin(ImportExportModelAdmin):
    resource_class = RegistroActividadResource
    list_display = ("id", "usuario", "descripcion", "carrera")


# -------------------------
# ESTRUCTURA ACADÉMICA (NUEVA JERARQUÍA)
# -------------------------

@admin.register(Universidad)
class UniversidadAdmin(admin.ModelAdmin):
    # Antes Empresa
    list_display = ("id_universidad", "nombre", "calle", "comuna", "lat", "long")

@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    # Nuevo Modelo
    list_display = ("id", "nombre", "universidad")
    list_filter = ("universidad",)

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    # Nuevo Modelo
    list_display = ("id", "nombre", "facultad")
    list_filter = ("facultad",)

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    # Antes AreaEmpresa
    # Actualizado: 'departamento' en lugar de 'id_empresa'
    list_display = ("id_carrera", "nombre", "departamento", "calle", "comuna", "lat", "long")
    list_filter = ("departamento__facultad",) # Filtro útil para navegar


# -------------------------
# GESTIÓN DE TIEMPO
# -------------------------

@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ("id_etapa", "nombre", "fecha_inicio", "fecha_termino", "activo")


# -------------------------
# FLUJOS (Entrada, Salida, Oportunidades)
# -------------------------

@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    # Actualizado: 'carrera' en lugar de 'id_area'
    list_display = ("id_entrada", "nombre", "fecha", "etapa", "usuario", "carrera")

@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):
    # Actualizado: 'carrera' en lugar de 'id_area'
    list_display = ("id_salida", "nombre", "fecha", "etapa", "usuario", "carrera")

@admin.register(Oportunidades)
class OportunidadesAdmin(admin.ModelAdmin):
    # Actualizado: 'carrera' en lugar de 'id_area'
    list_display = ("id_oportunidad", "nombre", "fecha", "etapa", "usuario", "carrera")


# -------------------------
# INNOVACIÓN
# -------------------------

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    # Actualizado: 'universidad' en lugar de 'empresa'
    list_display = ("id_idea", "usuario", "universidad", "etapa", "texto", "fecha_creacion")


# -------------------------
# RECLUTAMIENTO (CV, Ofertas)
# -------------------------

@admin.register(CVUsuario)
class CVUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "id", "usuario", "nombre_archivo",
        "palabra1", "palabra2", "linkedin_url", "timestamp"
    )

@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ("id_oferta", "titulo", "empresa", "creado_por", "modalidad", "jornada", "activa", "creado")
    list_filter = ("modalidad", "jornada", "activa", "universidad")
    search_fields = ("titulo", "empresa")

@admin.register(Necesidad)
class NecesidadAdmin(admin.ModelAdmin):
    list_display = ("id_necesidad", "usuario", "texto_necesita", "creado")


# -------------------------
# EVENTOS Y CALENDARIO
# -------------------------

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    # Actualizado: 'universidad' y 'carrera'
    list_display = ('titulo', 'universidad', 'carrera', 'inicio', 'fin', 'creador')
    list_filter = ('universidad', 'carrera')
    search_fields = ('titulo',)

@admin.register(Invitacion)
class InvitacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'evento', 'estado', 'fecha_actualizacion')
    list_filter = ('estado', 'evento')

from .models import Producto, OrdenCompra

admin.site.register(Producto)
admin.site.register(OrdenCompra)

from app.models import DocumentoBiblioteca
@admin.register(DocumentoBiblioteca)
class DocumentoBibliotecaAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'titulo', 'universidad', 'fecha')
    list_filter = ('universidad',)
    search_fields = ('titulo', 'descripcion')