import os
import io
import json
import base64
import mercadopago
from django.urls import reverse
import textwrap
import warnings
from django.utils import timezone
import os
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.mail import EmailMessage, get_connection
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from time import process_time_ns
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import traceback
# Evitamos que las advertencias llenen los logs de Render
warnings.filterwarnings("ignore")

# ==============================================================
# 2. CONFIGURACIÓN GRÁFICA (Matplotlib Agg)
# ==============================================================
# Configuramos esto al inicio para evitar errores de hilos, 
# pero NO importamos pyplot todavía para ahorrar RAM.
import matplotlib
matplotlib.use('Agg') 

# ==============================================================
# 3. IMPORTS DE DJANGO (Consolidados)
# ==============================================================
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, F
from django.core.mail import EmailMessage, get_connection, send_mail
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

# ==============================================================
# 4. MODELOS Y FORMULARIOS
# ==============================================================
from user.models import TrabajoEmpresa, Usuario, Preferencia
from .models import (
    Universidad, Facultad, Departamento, Carrera, 
    Etapa, RegistroActividad, Entrada, Salida, Oportunidades, Idea, 
    CVUsuario, Oferta, Necesidad, 
    Evento, Invitacion, PreguntaEvento, TransaccionPago,  
)
from .forms import EntradaForm, SalidaForm, OportunidadForm

# ==============================================================
# 5. INTELIGENCIA ARTIFICIAL (GEMINI)
# ==============================================================
import google.generativeai as genai
# DIAGNÓSTICO: Imprimir versión instalada en los logs de Render
print(f"VERSIÓN INSTALADA DE GEMINI: {genai.__version__}")

# Configuración segura: Si falla la variable de entorno, no rompe el deploy
API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", "")).strip()
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"Error Configuración Inicial: {e}")

import threading
from django.core.mail import send_mail
from django.conf import settings

class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.message,
                settings.DEFAULT_FROM_EMAIL,
                self.recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error enviando correo en hilo: {e}")
            
# Create your views here.
@login_required
def home(request):
    # LÓGICA PARA ADMINISTRADORES (Dashboard)
    if request.user.is_staff:
        
        # 1. UNIVERSIDADES
        universidades = Universidad.objects.all()
        
        # 2. USUARIOS
        # CAMBIO: Usamos .count() directo (sin filtro) para ver si al menos te cuenta a ti.
        # Si esto muestra 1 o más, la conexión es perfecta.
        total_usuarios = Usuario.objects.count() 
        
        # 3. EVENTOS
        total_eventos = Evento.objects.count() 

        # --- DEBUG EN CONSOLA (Mira tu terminal negra al recargar la página) ---
        print(f"--- DEBUG DASHBOARD ---")
        print(f"Universidades encontradas: {universidades.count()}")
        print(f"Usuarios encontrados: {total_usuarios}")
        print(f"Eventos encontrados: {total_eventos}")
        print(f"-----------------------")

        data = {
            'Universidads': universidades, 
            'total_usuarios': total_usuarios,
            'total_eventos': total_eventos,
        }
        return render(request, 'home_admin.html', data)

    # LÓGICA PARA USUARIOS NORMALEScv = CVUsuario.objects.filter(usuario=request.user).last()
    cv = CVUsuario.objects.filter(usuario=request.user).last()
    return render(request, 'home.html', {'cv': cv})

def autoDiagnostico(request, empresa_id=None): # Recibimos 'empresa_id' desde la URL

    if not request.user.is_authenticated:
        return render(request, 'autodiagnostico/auto_diagnostico.html')

    # Consultamos el modelo nuevo (Universidad)
    Universidads = Universidad.objects.all()  
    registros = RegistroActividad.objects.filter(usuario=request.user)

    Universidad_seleccionada = None
    Universidad_id_final = None

    # Usamos 'empresa_id' para filtrar la Universidad
    if request.user.is_staff and empresa_id:
        # Aquí está el truco: Filtramos id_universidad usando el valor de empresa_id
        Universidad_seleccionada = Universidad.objects.filter(id_universidad=empresa_id).first()
        if Universidad_seleccionada:
            Universidad_id_final = Universidad_seleccionada.id_universidad

    elif registros.exists():
        # Ruta larga corregida
        Universidad_id_final = registros.first().carrera.departamento.facultad.universidad.id_universidad

    # Enviamos al HTML con las claves viejas ('empresas', 'empresa_id')
    contexto = {
        'registros': registros,
        'empresas': Universidads, 
        'empresa_seleccionada': Universidad_seleccionada,
        'empresa_id': Universidad_id_final,
    }

    return render(request, 'autodiagnostico/auto_diagnostico.html', contexto)

def extraccionMateriaPrima(request):
    Universidad_id = request.GET.get("empresa")
    Universidad_seleccionada = None


    if Universidad_id:
            Universidad_seleccionada = Universidad.objects.get(id_Universidad=Universidad_id)

    Universidads = Universidad.objects.all()

    if request.user.is_authenticated:

        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Extraccion materia prima")
        entradas = Entrada.objects.filter(usuario=request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        print("La id de la etapa es!!!!!!!!: ", etapa)

        # data = {

        #     'form' : EntradaForm(),
        #     'registros':registros,
        #     'entradas':entradas,
        #     'formSalida': SalidaForm()

        # }
        print(f"la id del usuario es!!!!!!!!:", request.user.id)
        formulario = EntradaForm()
        formularioSalida = SalidaForm()

        if request.method == 'POST':
            formulario = EntradaForm(request.POST)
            formularioSalida = SalidaForm(request.POST)

            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                formulario = EntradaForm()

            if formularioSalida.is_valid():
                post = formularioSalida.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                formularioSalida.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                formulario = SalidaForm()
        return render(request, 'autodiagnostico/extraccion/home_extraccion.html', {'form': formulario,
         'registros': registros, 'entradas': entradas, 'empresas': Universidads, 'empresa_seleccionada': Universidad_seleccionada})
    else:
        return render(request, 'autodiagnostico/extraccion/home_extraccion.html')


def agregarEntradaExtraccion(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.filter(nombre="Extraccion materia prima").first()
        areaTrabajador = RegistroActividad.objects.filter(usuario=request.user).values_list("carrera", flat=True).first()

        entradas = Entrada.objects.filter(usuario=request.user, etapa=etapa)

        data = {
            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas,
            'areaTrabajador': areaTrabajador,
        }

        # ======== AGREGAR ENTRADA ========
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.usuario = request.user
                post.etapa = etapa
                post.carrera_id = areaTrabajador
                post.save()
                messages.success(request, "Entrada registrada con éxito.")
                return redirect('agregar_entrada_extraccion')
            else:
                data["form"] = formulario

        return render(request, 'autodiagnostico/extraccion/entrada/agregar_entrada.html', data)

    else:
        return render(request, 'autodiagnostico/extraccion/entrada/agregar_entrada.html')



def eliminarEntradaExtraccion(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_extraccion')


def agregarSalidaExtraccion(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Extraccion materia prima")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }
        print(f"la id del usuario es!!!!!!!!:", request.user.id)

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/extraccion/salida/agregar_salida.html', data)
    else:
        return render(request, 'autodiagnostico/extraccion/entrada/agregar_salida.html')

def eliminarSalidaExtraccion(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_extraccion')


def agregarOportunidadExtraccion(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)

        # ← ARREGLO AQUÍ
        etapa = Etapa.objects.get(nombre="Extraccion materia prima").id_etapa
        areaTrabajador = RegistroActividad.objects.get(usuario=request.user).carrera_id

        oportunidades = Oportunidades.objects.filter(usuario=request.user)

        data = {
            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades
        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa              # ← AHORA SÍ ES UN ENTERO
                post.carrera_id = areaTrabajador   # ← AHORA SÍ ES UN ENTERO
                post.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario

        return render(request,'autodiagnostico/extraccion/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/extraccion/oportunidad/agregar_oportunidad.html')

def eliminarOportunidadExtraccion(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_entrada=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_extraccion')




# Diseño y produccion

def diseño_Produccion(request):

    Universidad_id = request.GET.get("empresa")
    Universidad_seleccionada = None

    if Universidad_id:
        Universidad_seleccionada = Universidad.objects.filter(id_Universidad=Universidad_id).first()

    Universidads = Universidad.objects.all()

    registros = RegistroActividad.objects.filter(usuario=request.user)

    data = {
        'registros': registros,
        'empresas': Universidads,
        'empresa_seleccionada': Universidad_seleccionada,
        'empresa_id': Universidad_id,
    }

    return render(request, 'autodiagnostico/diseñoProduccion/home_diseño.html', data)



def agregarEntradaDiseño(request):
    if request.user.is_authenticated:

        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Diseño y produccion")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/diseñoProduccion/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/diseñoProduccion/entrada/agregar_entrada.html')


def eliminarEntradaDiseño(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_diseño')


def agregarSalidaDiseño(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Diseño y produccion")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/diseñoProduccion/salida/agregar_salida.html', data)
    else:
        return render(request, 'autodiagnostico/diseñoProduccion/entrada/agregar_salida.html')


def eliminarSalidaDiseño(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_diseño')


def agregarOportunidadDiseño(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Diseño y produccion")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/diseñoProduccion/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/diseñoProduccion/oportunidad/agregar_oportunidad.html')


def eliminarOportunidadDiseño(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_entrada=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_diseño')



# logistica

def logistica(request):
    Universidad_id = request.GET.get("empresa")
    Universidad_seleccionada = None

    if Universidad_id:
        Universidad_seleccionada = Universidad.objects.filter(id_Universidad=Universidad_id).first()

    Universidads = Universidad.objects.all()

    registros = RegistroActividad.objects.filter(usuario=request.user)

    data = {  
            'registros': registros, 
            'empresas': Universidads,
            'empresa_seleccionada': Universidad_seleccionada,
            'empresa_id': Universidad_id,
    }

    return render(request,'autodiagnostico/logistica/home_logistica.html', data)


def agregarEntradaLogistica(request):
    if request.user.is_authenticated:

        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Logistica")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/logistica/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/logistica/entrada/agregar_entrada.html')


def eliminarEntradaLogistica(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_logistica')


def agregarSalidaLogistica(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Logistica")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/logistica/salida/agregar_salida.html', data)
    else:
        return render(request, 'autodiagnostico/logistica/entrada/agregar_salida.html')


def eliminarSalidaLogistica(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_logistica')



def agregarOportunidadLogistica(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Logistica")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/logistica/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/logistica/oportunidad/agregar_oportunidad.html')

def eliminarOportunidadLogistica(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_entrada=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_logistica')



#compra

def compra(request):
    Universidad_id = request.GET.get("empresa")
    Universidad_seleccionada = None

    if Universidad_id:
        Universidad_seleccionada = Universidad.objects.filter(id_Universidad=Universidad_id).first()

    Universidads = Universidad.objects.all()

    registros = RegistroActividad.objects.filter(usuario=request.user)

    data = {  
            'registros': registros, 
            'empresas': Universidads,
            'empresa_seleccionada': Universidad_seleccionada,
            'empresa_id': Universidad_id,
    }

    return render(request,'autodiagnostico/compra/home_compra.html', data)


def agregarEntradaCompra(request):
    if request.user.is_authenticated:

        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Compra")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/compra/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/compra/entrada/agregar_entrada.html')   

def eliminarEntradaCompra(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_compra')


def agregarSalidaCompra(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Compra")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/compra/salida/agregar_salida.html', data)
    else:
        return render(request,'autodiagnostico/compra/salida/agregar_salida.html')  


def eliminarSalidaCompra(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_compra')



def agregarOportunidadCompra(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Compra")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/compra/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/compra/oportunidad/agregar_oportunidad.html') 

def eliminarOportunidadCompra(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_entrada=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_compra')



#Uso consumo

def usoConsumo(request):
    Universidad_id = request.GET.get("empresa")
    Universidad_seleccionada = None

    if Universidad_id:
        Universidad_seleccionada = Universidad.objects.filter(id_Universidad=Universidad_id).first()

    Universidads = Universidad.objects.all()

    registros = RegistroActividad.objects.filter(usuario=request.user)

    data = {  
            'registros': registros, 
            'empresas': Universidads,
            'empresa_seleccionada': Universidad_seleccionada,
            'empresa_id': Universidad_id,
    }

    return render(request,'autodiagnostico/usoConsumo/home_usoConsumo.html', data)        


def agregarEntradaUso(request):
    if request.user.is_authenticated:

        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Uso consumo")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/usoConsumo/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/usoConsumo/entrada/agregar_entrada.html')    


def eliminarEntradaUsoConsumo(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_uso_consumo')


def agregarSalidaUso(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Uso consumo")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/usoConsumo/salida/agregar_salida.html', data)
    else:
        return render(request,'autodiagnostico/usoConsumo/salida/agregar_salida.html')       


def eliminarSalidaUso(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_uso')



def agregarOportunidadUso(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Uso consumo")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/usoConsumo/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/usoConsumo/oportunidad/agregar_oportunidad.html')   

def eliminarOportunidadUso(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_entrada=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_uso')


# Fin de vida

def finVida(request):
    Universidad_id = request.GET.get("empresa")
    Universidad_seleccionada = None

    if Universidad_id:
        Universidad_seleccionada = Universidad.objects.filter(id_Universidad=Universidad_id).first()

    Universidads = Universidad.objects.all()

    registros = RegistroActividad.objects.filter(usuario=request.user)

    data = {  
            'registros': registros, 
            'empresas': Universidads,
            'empresa_seleccionada': Universidad_seleccionada,
            'empresa_id': Universidad_id,
    }

    return render(request,'autodiagnostico/finVida/home_finVida.html', data)


def agregarEntradaFin(request):
    if request.user.is_authenticated:

        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Fin de vida")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/finVida/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/finVida/entrada/agregar_entrada.html')  


def eliminarEntradaFinVida(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_fin_vida')


def agregarSalidaFin(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Fin de vida")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/finVida/salida/agregar_salida.html', data)
    else:
        return render(request,'autodiagnostico/finVida/salida/agregar_salida.html') 


def eliminarSalidaFinVida(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_fin_vida')



def agregarOportunidadFin(request):
    if request.user.is_authenticated:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Fin de vida")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroActividad.objects.values_list("carrera", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.carrera_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/finVida/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/finVida/oportunidad/agregar_oportunidad.html') 

def eliminarOportunidadFinVida(request, id):

    oportunidad = get_object_or_404(Oportunidades, id_entrada=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_fin_vida')


def ingresar_ideas(request, etapa_id=None):
    registros = RegistroActividad.objects.filter(usuario=request.user)
    registro = registros.first()

    etapas = Etapa.objects.filter(activo=True)
    etapa = None
    mensaje = None  # <-- para mostrar mensaje de éxito

    if etapa_id:
        etapa = get_object_or_404(Etapa, id_etapa=etapa_id)

        if request.method == "POST":
            texto = request.POST.get("texto")
            if not texto or texto.strip() == "":
                mensaje = "Debe ingresar una idea."
            else:
                Idea.objects.create(
                    usuario=request.user,
                    Universidad=registro.carrera.departamento.facultad.universidad,
                    etapa=etapa,
                    texto=texto
                )
                mensaje = "Idea guardada correctamente."

    return render(request, 'ideas/ingresar_ideas.html', {
        'registros': registros,
        'etapas': etapas,
        'etapa': etapa,
        'mensaje': mensaje
    })


@login_required
def mi_perfil(request):
    import io
    import base64
    
    # Intento de importar qrcode de forma segura
    try:
        import qrcode
    except ImportError:
        qrcode = None
        print("ADVERTENCIA: La librería 'qrcode' no está instalada.")

    try:
        registros = RegistroActividad.objects.filter(usuario=request.user)
        cv = CVUsuario.objects.filter(usuario=request.user).first()
        qr_base64 = None

        # --------------------------
        # PROCESAR FORMULARIOS POST
        # --------------------------
        if request.method == "POST":
            # 1. Actualizar URL de LinkedIn
            linkedin_url = request.POST.get("linkedin_url")
            if linkedin_url:
                cv, created = CVUsuario.objects.get_or_create(usuario=request.user)
                cv.linkedin_url = linkedin_url.strip()
                cv.save()
                messages.success(request, "URL de LinkedIn actualizada correctamente.")
                return redirect("mi_perfil")

            # 2. Guardar QR generado desde URL
            if request.POST.get("action") == "save_qr":
                if not qrcode:
                    messages.error(request, "Error del sistema: Falta librería qrcode.")
                elif cv and cv.linkedin_url:
                    qr = qrcode.make(cv.linkedin_url)
                    buffer = io.BytesIO()
                    qr.save(buffer, format="PNG")
                    cv.linkedin_qr = buffer.getvalue()
                    cv.save()
                    messages.success(request, "QR de LinkedIn generado y guardado correctamente.")
                else:
                    messages.error(request, "Primero debes guardar una URL de LinkedIn válida.")
                return redirect("mi_perfil")

            # 3. Subir/Cambiar QR manualmente
            linkedin_qr_file = request.FILES.get("linkedin_qr")
            if linkedin_qr_file:
                cv, created = CVUsuario.objects.get_or_create(usuario=request.user)
                qr_bytes = linkedin_qr_file.read()
                cv.linkedin_qr = qr_bytes
                cv.save()
                messages.success(request, "QR de LinkedIn actualizado correctamente.")
                return redirect("mi_perfil")

            # 4. Subir CV completo
            archivo = request.FILES.get("archivo")
            if archivo:
                # Asegúrate de que 'subir_cv' esté importada o definida
                try:
                    return subir_cv(request)
                except NameError:
                    messages.error(request, "Función subir_cv no encontrada.")

        # --------------------------
        # PREPARAR DATOS PARA LA VISTA
        # --------------------------
        palabras = []
        if cv:
            # Lista segura de atributos (evita error si falta alguno)
            attrs = ['palabra1', 'palabra2', 'palabra3', 'palabra4', 'palabra5',
                     'palabra6', 'palabra7', 'palabra8', 'palabra9', 'palabra10']
            for attr in attrs:
                val = getattr(cv, attr, None)
                if val: palabras.append(val)

            if cv.linkedin_qr:
                qr_base64 = base64.b64encode(cv.linkedin_qr).decode("utf-8")

        # Datos adicionales (Manejo de errores por si faltan campos en la BD)
        ultima_oferta = Oferta.objects.filter(creado_por=request.user).last()
        palabras_oferta = []
        if ultima_oferta:
            for i in range(1, 6): # palabra1 a palabra5
                val = getattr(ultima_oferta, f'palabra{i}', None)
                if val: palabras_oferta.append(val)


        ultima_necesidad = Necesidad.objects.filter(usuario=request.user).last()
        palabras_necesidad = []

        if ultima_necesidad:
            for i in range(1, 6):
                val = getattr(ultima_necesidad, f'palabra{i}', None)
                if val:
                    palabras_necesidad.append(val)

        # Consultamos las empresas/trabajos del usuario ordenados desde el más reciente
        trabajos_empresas = TrabajoEmpresa.objects.filter(usuario=request.user).order_by('-id')

        # --- PREFERENCIAS Y DESCUENTOS BANCARIOS SEGÚN UNIVERSIDAD ---
        from user.models import Preferencia, DescuentoBanco
        
        # 1. Averiguamos de qué universidad es el alumno a través de su carrera
        if request.user.carrera:
            mi_universidad = request.user.carrera.departamento.facultad.universidad
            
            # Filtramos ambas cosas (Preferencias y Bancos) solo para su universidad
            todas_las_preferencias = Preferencia.objects.filter(universidad=mi_universidad).order_by('id')
            todos_los_bancos = DescuentoBanco.objects.filter(universidad=mi_universidad).order_by('id')
        else:
            # Si no tiene carrera asignada aún, le mostramos vacío
            todas_las_preferencias = []
            todos_los_bancos = []

        mis_preferencias_ids = list(request.user.preferencias.values_list('id', flat=True))
        mis_bancos_ids = list(request.user.descuentos.values_list('id', flat=True))
        # -------------------------------------------------------------

        # NOTA: Verifica que la ruta 'mi_perfil/mi_perfil.html' sea correcta.
        return render(request, 'mi_perfil/mi_perfil.html', {
            "registros": registros,
            "cv": cv,
            "palabras": palabras,
            "palabras_oferta": palabras_oferta,
            "palabras_necesidad": palabras_necesidad,
            "ultima_oferta": ultima_oferta,
            "ultima_necesidad": ultima_necesidad,
            "qr_base64": qr_base64,
            "trabajos_empresas": trabajos_empresas,
            
            # Variables inyectadas al HTML para Preferencias y Bancos:
            "todas_las_preferencias": todas_las_preferencias,
            "mis_preferencias_ids": mis_preferencias_ids,
            "todos_los_bancos": todos_los_bancos,
            "mis_bancos_ids": mis_bancos_ids,
        })

    except Exception as e:
        print(f"ERROR CRÍTICO EN MI PERFIL: {e}") # Mira la consola para ver el error real
        messages.error(request, "Ocurrió un error al cargar tu perfil. Intenta nuevamente.")
        return render(request, 'mi_perfil.html', contexto)

#---- Match en coincidencia de palabras clave de una oferta con el cv ----
@login_required
def mis_matches(request):
    resultados = obtener_matches_usuario(request.user)

    return render(request, 'mis_matches.html', {
        'resultados': resultados
    })
    
@login_required
def subir_cv(request):
    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        if not archivo:
            messages.error(request, "No se subió archivo.")
            return redirect("mi_perfil")

        # 1. Leer archivo
        file_bytes = archivo.read()
        file_like = io.BytesIO(file_bytes)
        file_like.name = archivo.name
        texto = leer_archivo(file_like)

        # 2. SOLO GEMINI (10 palabras para CV)
        palabras = _obtener_keywords_gemini(texto, 10) 

        # --- CORRECCIÓN BASE DE DATOS (Anti Error 500) ---
        # Buscamos el último CV existente.
        cv = CVUsuario.objects.filter(usuario=request.user).last()
        
        # Si no existe, creamos la instancia (sin guardar todavía)
        if not cv:
            cv = CVUsuario(usuario=request.user)

        # Actualizamos los datos
        cv.archivo = file_bytes
        cv.nombre_archivo = archivo.name
        
        for i in range(10): 
            # Usamos "General" si la IA devolvió menos de 10 palabras
            val = palabras[i] if i < len(palabras) else "General"
            setattr(cv, f"palabra{i+1}", val)
        
        cv.save()
        # --------------------------------------------------
        
        if "Error-IA" in palabras:
            messages.warning(request, "CV subido, pero la IA no pudo leerlo.")
        else:
            messages.success(request, "CV analizado por IA exitosamente.")
            
            # Buscar ofertas con match >= 50% y notificar al usuario
            try:
                set_cv = set([str(p).strip().title() for p in palabras if p and p not in ['General', 'None', '']])
                ofertas_activas = Oferta.objects.filter(activa=True)
                ofertas_match = []

                for oferta in ofertas_activas:
                    raw_oferta = [oferta.palabra1, oferta.palabra2, oferta.palabra3, oferta.palabra4, oferta.palabra5]
                    set_oferta = set([str(p).strip().title() for p in raw_oferta if p and p not in ['General', 'None', '']])
                    
                    if not set_oferta:
                        continue
                    
                    coincidencias = set_oferta.intersection(set_cv)
                    porcentaje = int((len(coincidencias) / len(set_oferta)) * 100)
                    
                    if porcentaje >= 50:
                        ofertas_match.append({
                            'titulo': oferta.titulo,
                            'empresa': oferta.empresa,
                            'match': porcentaje,
                            'coincidencias': list(coincidencias)
                        })

                if ofertas_match:
                    # Construir el correo
                    asunto = "¡Encontramos ofertas que coinciden con tu CV!"
                    mensaje = f"Hola {request.user.first_name},\n\n"
                    mensaje += "Hemos analizado tu CV y encontramos las siguientes ofertas con más del 50% de coincidencia:\n\n"
                    
                    for o in ofertas_match:
                        mensaje += f"✅ {o['titulo']} - {o['empresa']} ({o['match']}% match)\n"
                        mensaje += f"   Palabras clave: {', '.join(o['coincidencias'])}\n\n"
                    
                    mensaje += "\nIngresa a la plataforma para ver los detalles:\n"
                    mensaje += "https://ciclo-circular.onrender.com/bolsa/oportunidades/\n\n"
                    mensaje += "Equipo Red Alumni"

                    EmailThread(asunto, mensaje, [request.user.email]).start()
                    messages.info(request, f"¡Se encontraron {len(ofertas_match)} ofertas con match! Te enviamos un correo.")

            except Exception as e:
                print(f"Error al buscar matches: {e}")
            
        return redirect("mi_perfil")
        
    return render(request, "mi_perfil/subir_cv.html")

@login_required
def eliminar_cv(request):
    CVUsuario.objects.filter(usuario=request.user).delete()
    messages.success(request, "CV eliminado correctamente.")
    return redirect('mi_perfil')

@login_required
def guardar_keywords_cv(request):
    if request.method == "POST":
        cv = CVUsuario.objects.filter(usuario=request.user).first()
        if cv:
            kw = request.POST.get("palabras_cv", "").split(",")[:10]
            for i in range(10): setattr(cv, f"palabra{i+1}", kw[i].strip() if i < len(kw) else None)
            cv.save()
            messages.success(request, "Etiquetas guardadas.")
    return redirect("mi_perfil")



def leer_archivo(file_like):
    """ 
    OPTIMIZACIÓN RAM: Importamos librerías pesadas SOLO aquí.
    Si nadie sube un CV, estas librerías nunca consumen memoria.
    """
    try:
        ext = file_like.name.split(".")[-1].lower()
        
        if ext == "docx":
            import docx # <--- Lazy Import
            doc = docx.Document(file_like)
            return "\n".join([p.text for p in doc.paragraphs])
            
        elif ext == "pdf":
            import fitz # <--- Lazy Import (PyMuPDF es pesado)
            texto = ""
            with fitz.open(stream=file_like.read(), filetype="pdf") as pdf:
                for page in pdf: texto += page.get_text()
            return texto
            
        elif ext == "txt":
            return file_like.read().decode("utf-8", errors="ignore")
            
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
    return ""



@login_required
def guardar_oferta(request):
    if request.method == "POST":
        texto = request.POST.get("texto_oferta")
        
        # Validación básica
        if not texto:
            messages.error(request, "El texto no puede estar vacío.")
            return redirect("mi_perfil")

        # 1. Llamamos a la IA
        palabras = _obtener_keywords_gemini(texto, 5)

        try:
            # CORRECCIÓN CRÍTICA:
            # Usamos .filter().last() para evitar el error "MultipleObjectsReturned"
            # si ya existen registros previos.
            oferta = Oferta.objects.filter(creado_por=request.user).last()
            
            if not oferta:
                # Si no existe ninguna, creamos una instancia nueva
                oferta = Oferta(usuario=request.user)

            # Actualizamos los datos
            oferta.texto_oferta = texto
            for i in range(5): 
                # Asignamos la palabra o "General" si la lista es corta
                val = palabras[i] if i < len(palabras) else "General"
                setattr(oferta, f"palabra{i+1}", val)
            
            oferta.save()

            if "Error-IA" in palabras:
                messages.warning(request, "Oferta guardada, pero la IA falló. Se usaron etiquetas genéricas.")
            else:
                messages.success(request, "Oferta actualizada y analizada correctamente.")
        
        except Exception as e:
            # Capturamos cualquier error de Base de Datos para que no salga pantalla 500
            print(f"🔥 Error al guardar Oferta: {e}")
            messages.error(request, "Hubo un problema guardando los datos. Intenta nuevamente.")
            
    return redirect("mi_perfil")

@login_required
def guardar_necesidad(request):
    if request.method == "POST":
        texto = request.POST.get("texto_necesita")
        
        if not texto:
            messages.error(request, "El texto no puede estar vacío.")
            return redirect("pagina_networking")

        # 1. Llamamos a la IA
        palabras = _obtener_keywords_gemini(texto, 5)

        try:
            # Siempre crea una nueva necesidad
            necesidad = Necesidad(usuario=request.user)
            necesidad.texto_necesita = texto
            for i in range(5): 
                val = palabras[i] if i < len(palabras) else None
                setattr(necesidad, f"palabra{i+1}", val)
            
            necesidad.save()

            if "Error-IA" in palabras:
                messages.warning(request, "Necesidad guardada, pero la IA falló.")
            else:
                messages.success(request, "Necesidad actualizada y analizada correctamente.")

        except Exception as e:
            print(f"🔥 Error al guardar Necesidad: {e}")
            messages.error(request, "Hubo un problema guardando los datos.")
            
    return redirect("pagina_networking")

@login_required
def seleccion_empresa_calendario(request):
    """
    Vista 'Semáforo':
    - Coordinador: Redirección automática a su calendario (Bypass).
    - Admin: Ve lista completa para elegir.
    - Alumno: Ve su universidad (o redirección si prefieres).
    """
    usuario = request.user
    
    # --- 1. LÓGICA COORDINADOR (EL CAMBIO IMPORTANTE) ---
    # Si es coordinador, NO le mostramos la pantalla de selección.
    # Lo enviamos directo a SU calendario.
    if usuario.es_coordinador and not usuario.is_superuser:
        if usuario.universidad_coordinador:
            return redirect(f"/calendario-corporativo/?empresa={usuario.universidad_coordinador.pk}")
        else:
            return redirect('home')

    # --- 2. LÓGICA RESTO DE USUARIOS (Mostrar Lista) ---
    lista_universidades = []

    # CASO ADMIN (Ve todas)
    if usuario.is_staff or usuario.is_superuser:
        lista_universidades = Universidad.objects.all()

    # CASO ALUMNO (Ve la suya basada en carrera)
    elif usuario.carrera:
        try:
            # Trepamos la jerarquía: Carrera -> Depto -> Facultad -> Universidad
            uni = usuario.carrera.departamento.facultad.universidad
            lista_universidades = [uni]
        except AttributeError:
            pass 

    context = {
        'empresas': lista_universidades,
        'titulo': 'Selecciona una Universidad'
    }
    
    return render(request, 'eventos/seleccion_empresa_calendario.html', context)

@login_required
def vista_calendario(request):  
    usuario = request.user
    universidad_obj = None
    es_editor = False

    # 1. Configuración de Diseño (Admin vs Público)
    base_template = 'base_admin.html'
    volver_url = 'home_admin' 

    if usuario.es_coordinador and not usuario.is_superuser:
        base_template = 'base_public.html'
        volver_url = 'panel_coordinador'

    # 2. Obtener ID de la URL
    uni_id_get = request.GET.get('empresa')

    # Admin: Siempre es editor y puede ver todo
    if usuario.is_staff or usuario.is_superuser:
        es_editor = True
        if uni_id_get:
            universidad_obj = get_object_or_404(Universidad, pk=uni_id_get)
    
    # Coordinador: Lógica Restrictiva
    elif usuario.es_coordinador:
        # A) Si intenta acceder a una U por URL
        if uni_id_get:
            solicitada = get_object_or_404(Universidad, pk=uni_id_get)
            
            # SEGURIDAD: ¿Es SU universidad?
            if usuario.universidad_coordinador == solicitada:
                universidad_obj = solicitada
                es_editor = True
            else:
                # Si intenta ver otra, lo forzamos a ver la suya
                return redirect(f"/calendario-corporativo/?empresa={usuario.universidad_coordinador.id}")
        
        # B) Si entra sin parámetros, le mostramos la suya
        else:
            if usuario.universidad_coordinador:
                universidad_obj = usuario.universidad_coordinador
                es_editor = True

    # Alumno / Usuario Normal (Solo lectura)
    else:
        # (Tu lógica de deducción para alumnos se mantiene igual...)
        if usuario.carrera:
            try: universidad_obj = usuario.carrera.departamento.facultad.universidad
            except: pass
        elif RegistroActividad.objects.filter(usuario=usuario).exists():
             registro = RegistroActividad.objects.filter(usuario=usuario).first()
             try: universidad_obj = registro.carrera.departamento.facultad.universidad
             except: pass

    # --- Renderizado ---
    if not universidad_obj:
        nombre_mostrar = "Seleccione una Universidad"
        id_final = 0
    else:
        nombre_mostrar = universidad_obj.nombre
        id_final = universidad_obj.pk

    context = {
        'nombre_empresa': nombre_mostrar, 
        'id_empresa': id_final,       
        'es_editor': es_editor,       
        'empresa': universidad_obj,
        'base_template': base_template,
        'volver_url': volver_url,
        # Variable para ocultar botón de asistencia al Coordinador
        'es_superadmin': usuario.is_staff 
    }
    
    if es_editor:
        return render(request, 'eventos/calendario_admin.html', context)
    else:
        return render(request, 'eventos/calendario_public.html', context)
    

@login_required
def listar_eventos(request):
    uni_id = request.GET.get('empresa_id')
    usuario = request.user
    
    # --- 1. LÓGICA DE FILTRADO INTELIGENTE (INTACTA) ---
    if uni_id and str(uni_id) != "0":
        eventos_qs = Evento.objects.filter(universidad_id=uni_id)
    else:
        if usuario.is_staff:
            eventos_qs = Evento.objects.all()
        elif hasattr(usuario, 'universidad_coordinador') and usuario.universidad_coordinador:
            eventos_qs = Evento.objects.filter(universidad=usuario.universidad_coordinador)
        elif hasattr(usuario, 'carrera') and usuario.carrera:
            try:
                uni_alumno = usuario.carrera.departamento.facultad.universidad
                eventos_qs = Evento.objects.filter(universidad=uni_alumno)
            except AttributeError:
                eventos_qs = Evento.objects.none()
        else:
            eventos_qs = Evento.objects.none()

    # --- 2. OPTIMIZACIÓN (INTACTA) ---
    eventos = eventos_qs.select_related(
        'carrera', 
        'departamento', 
        'facultad',
        'carrera__departamento__facultad', 
        'departamento__facultad'
    )

    # --- 3. SERIALIZACIÓN ---
    data = []
    for evento in eventos:
        # Obtención de objetos
        f_obj = evento.facultad
        d_obj = evento.departamento
        c_obj = evento.carrera

        # Lógica de Fallback
        if c_obj and not f_obj:
            try:
                d_temp = c_obj.departamento
                if d_temp:
                    d_obj = d_temp 
                    f_obj = d_temp.facultad 
            except AttributeError:
                pass
        elif d_obj and not f_obj:
            try:
                f_obj = d_obj.facultad
            except AttributeError:
                pass

        # Extracción de Datos
        f_id = f_obj.pk if f_obj else None
        f_nombre = f_obj.nombre if f_obj else "Nivel Central"
        d_id = d_obj.pk if d_obj else None
        d_nombre = d_obj.nombre if d_obj else None
        c_id = c_obj.pk if c_obj else None
        c_nombre = c_obj.nombre if c_obj else None

        # --- NUEVO BLOQUE: VERIFICAR ESTADO DEL USUARIO ---
        # Esto es lo que faltaba para que el calendario sepa si ya pagaste
        estado_usuario = None
        # Buscamos si existe una invitación para este evento y este usuario
        invitacion = Invitacion.objects.filter(evento=evento, usuario=usuario).first()
        if invitacion:
            estado_usuario = invitacion.estado
        # --------------------------------------------------

        data.append({
            'id': evento.pk,
            'title': evento.titulo,
            'start': evento.inicio.isoformat() if evento.inicio else None, 
            'end': evento.fin.isoformat() if evento.fin else None,
            'extendedProps': {
                'lugar': evento.lugar,
                'costo': evento.costo,
                'description': evento.descripcion,
                
                # Campos nuevos añadidos
                'pregunta_del_coordinador': evento.pregunta_del_coordinador,
                'preguntas_count': evento.contador_preguntas,
                'aportes_count': evento.contador_aportes,
                
                # --- AQUÍ INYECTAMOS EL ESTADO ---
                'user_response': estado_usuario, 
                # ---------------------------------
                
                'carrera_id': c_id,
                'departamento_id': d_id,
                'facultad_id': f_id,
                'facultad_nombre': f_nombre,
                'departamento_nombre': d_nombre,
                'carrera_nombre': c_nombre
            }
        })
    
    return JsonResponse(data, safe=False)


@login_required
def guardar_evento(request):
    # 1. Verificación inicial de método
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

    try:
        data = json.loads(request.body)
        user = request.user
        
        # 2. Obtener Universidad (Dato Obligatorio Base)
        uni_id = data.get('empresa_id')
        if not uni_id or str(uni_id) == "0":
             return JsonResponse({'status': 'error', 'message': 'Falta ID Universidad'})

        universidad_obj = get_object_or_404(Universidad, pk=uni_id)

        # 3. Validación de Permisos (Seguridad)
        es_admin = user.is_staff
        es_coordinador = hasattr(user, 'universidad_coordinador') and user.universidad_coordinador == universidad_obj
        
        if not (es_admin or es_coordinador):
             return JsonResponse({'status': 'error', 'message': 'No tienes permisos para esta Universidad'})

        id_evento = data.get('id')
        pregunta_coord = data.get('pregunta_del_coordinador')

        # --- GUARDADO RÁPIDO AUTOMÁTICO (SOLO PREGUNTA) ---
        if id_evento and data.get('solo_pregunta'):
            evento = get_object_or_404(Evento, pk=id_evento)
            if evento.universidad == universidad_obj:
                evento.pregunta_del_coordinador = pregunta_coord
                evento.save()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'No autorizado'})

        # 4. Obtener datos de la Jerarquía
        facultad_id = data.get('facultad_id') or None
        departamento_id = data.get('departamento_id') or None
        carrera_id = data.get('carrera_id') or None

        # 5. Obtener datos básicos del evento
        titulo = data.get('title')
        inicio_str = data.get('start')
        fin_str = data.get('end')
        
        if not titulo or not inicio_str or not fin_str:
            return JsonResponse({'status': 'error', 'message': 'Faltan datos obligatorios (título o fechas)'})

        inicio = parse_datetime(inicio_str)
        fin = parse_datetime(fin_str)
        lugar = data.get('lugar')
        costo = data.get('costo') or 0
        descripcion = data.get('description')

        # 6. Guardar en Base de Datos (Edición Completa o Creación)
        if id_evento:
            # --- EDICIÓN ---
            evento = get_object_or_404(Evento, pk=id_evento)
            
            if evento.universidad != universidad_obj:
                return JsonResponse({'status': 'error', 'message': 'No puedes mover eventos entre universidades'})

            evento.titulo = titulo
            evento.inicio = inicio
            evento.fin = fin
            evento.lugar = lugar
            evento.costo = costo
            evento.descripcion = descripcion
            evento.pregunta_del_coordinador = pregunta_coord
            
            evento.facultad_id = facultad_id
            evento.departamento_id = departamento_id
            evento.carrera_id = carrera_id
            
            evento.save()
        else:
            # --- CREACIÓN ---
            Evento.objects.create(
                universidad=universidad_obj,
                facultad_id=facultad_id,       
                departamento_id=departamento_id, 
                carrera_id=carrera_id,         
                titulo=titulo, 
                inicio=inicio, 
                fin=fin,
                lugar=lugar, 
                costo=costo, 
                descripcion=descripcion,
                pregunta_del_coordinador=pregunta_coord,
                creador=user
            )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        print(f"Error en guardar_evento: {e}") 
        return JsonResponse({'status': 'error', 'message': f"Error interno: {str(e)}"})
    
    
@login_required
def eliminar_evento(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

    try:
        data = json.loads(request.body)
        id_evento = data.get('id')
        user = request.user
        
        evento = get_object_or_404(Evento, pk=id_evento)

        # Validación de Permisos para Eliminar
        es_admin = user.is_staff
        # Verificamos si es coordinador de LA universidad dueña del evento
        es_coordinador_propio = hasattr(user, 'universidad_coordinador') and user.universidad_coordinador == evento.universidad

        if not (es_admin or es_coordinador_propio):
            return JsonResponse({'status': 'error', 'message': 'No tienes permisos para eliminar este evento'})

        evento.delete()
        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    

@login_required
def gestionar_asistencia(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    usuario_logueado = request.user
    
    # 1. PERMISOS Y NAVEGACIÓN
    permitido = False
    base_template = 'base_admin.html'
    volver_url = 'ver_calendario' # Retorno por defecto

    # A) Es Admin (Staff)
    if usuario_logueado.is_staff:
        permitido = True
        
    # B) Es Coordinador de la universidad del evento
    elif hasattr(usuario_logueado, 'universidad_coordinador') and usuario_logueado.universidad_coordinador == evento.universidad:
        permitido = True
        # Ajuste de diseño para Coordinador
        base_template = 'base_public.html'
        
    if not permitido:
        messages.error(request, "No tienes permisos para gestionar este evento.")
        return redirect('ver_calendario')

    # 2. LÓGICA DE AUTO-POBLADO DE INVITADOS
    # Filtramos solo usuarios activos y que no sean staff
    filtros_base = Q(is_active=True, is_staff=False)
    nombre_nivel = "" 

    # Determinamos el alcance del evento para buscar alumnos
    if evento.carrera:
        alumnos_objetivo = Usuario.objects.filter(filtros_base, carrera=evento.carrera)
        nombre_nivel = f"la carrera {evento.carrera.nombre}"
    elif evento.departamento:
        alumnos_objetivo = Usuario.objects.filter(filtros_base, carrera__departamento=evento.departamento)
        nombre_nivel = f"el departamento {evento.departamento.nombre}"
    elif evento.facultad:
        alumnos_objetivo = Usuario.objects.filter(filtros_base, carrera__departamento__facultad=evento.facultad)
        nombre_nivel = f"la facultad {evento.facultad.nombre}"
    else:
        alumnos_objetivo = Usuario.objects.filter(filtros_base, carrera__departamento__facultad__universidad=evento.universidad)
        nombre_nivel = f"toda la universidad"

    # Generamos las invitaciones si no existen
    nuevas_creadas = 0
    for alumno in alumnos_objetivo:
        invitacion, created = Invitacion.objects.get_or_create(
            evento=evento, usuario=alumno, defaults={'estado': 'SIN_ENVIAR'}
        )
        if created: nuevas_creadas += 1

    if nuevas_creadas > 0:
        messages.info(request, f"Se han añadido {nuevas_creadas} alumnos de {nombre_nivel}.")
    elif alumnos_objetivo.count() == 0:
        messages.warning(request, f"No se encontraron alumnos registrados en {nombre_nivel}.")

    # 3. ESTADÍSTICAS
    invitaciones = Invitacion.objects.filter(evento=evento).select_related('usuario', 'usuario__carrera')
    stats = invitaciones.aggregate(
        total=Count('id'),
        confirmados=Count('id', filter=Q(estado__in=['CONFIRMADO', 'ENTRADA_ENVIADA'])),
        pendientes=Count('id', filter=Q(estado='ENVIADO')),
        rechazados=Count('id', filter=Q(estado='RECHAZADO')),
        por_enviar=Count('id', filter=Q(estado='SIN_ENVIAR'))
    )
    
    context = {
        'evento': evento,
        'invitaciones': invitaciones,
        'stats': stats,
        # Variables dinámicas para el template
        'base_template': base_template,
        'volver_url': volver_url
    }
    
    return render(request, 'eventos/gestion_asistencia.html', context)


# --- FUNCIÓN 1: ENVIAR INVITACIÓN INICIAL ---
def enviar_solicitud_confirmacion(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    
    # --- VALIDACIÓN DE PERMISOS (NUEVO) ---
    es_admin = request.user.is_staff
    es_coordinador_propio = (
        hasattr(request.user, 'universidad_coordinador') and 
        request.user.universidad_coordinador == evento.universidad
    )
    
    if not (es_admin or es_coordinador_propio):
        messages.error(request, "No tienes permisos para gestionar invitaciones de esta universidad.")
        return redirect('ver_calendario')
    # --------------------------------------

    # Buscamos invitaciones SIN_ENVIAR
    invitaciones_a_enviar = Invitacion.objects.filter(evento=evento, estado='SIN_ENVIAR')

    if not invitaciones_a_enviar.exists():
        messages.info(request, "No hay nuevos usuarios para notificar.")
        return redirect('gestionar_asistencia', evento_id=evento.pk)

    try:
        connection = get_connection()
        connection.open()
    except Exception as e:
        messages.error(request, f"Error conexión SMTP: {e}")
        return redirect('gestionar_asistencia', evento_id=evento.pk)

    mensajes_para_enviar = []
    ids_para_actualizar = []
    link = request.build_absolute_uri('/eventos/mis-invitaciones/')

    for invitacion in invitaciones_a_enviar:
        if invitacion.usuario.email:
            try:
                asunto = f"Confirmación Asistencia: {evento.titulo}"
                cuerpo = f"""
                Hola {invitacion.usuario.first_name},
                Se realizará el evento "{evento.titulo}" el día {evento.inicio.strftime('%d/%m/%Y a las %H:%M')}.
                Lugar: {evento.lugar}
                Confirma aquí: {link}
                Saludos, Equipo {evento.universidad.nombre}
                """
                email = EmailMessage(asunto, textwrap.dedent(cuerpo).strip(), settings.EMAIL_HOST_USER, [invitacion.usuario.email], connection=connection)
                mensajes_para_enviar.append(email)
                ids_para_actualizar.append(invitacion.id)
            except: pass

    count = 0
    if mensajes_para_enviar:
        count = connection.send_messages(mensajes_para_enviar)
    
    connection.close()
    
    if ids_para_actualizar and count > 0:
        Invitacion.objects.filter(id__in=ids_para_actualizar).update(estado='ENVIADO')

    messages.success(request, f"Se enviaron {count} invitaciones.")
    return redirect('gestionar_asistencia', evento_id=evento.pk)

@login_required
def enviar_entrada_formal(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    # --- VALIDACIÓN DE PERMISOS ---
    es_admin = request.user.is_staff
    es_coordinador_propio = (
        hasattr(request.user, 'universidad_coordinador') and 
        request.user.universidad_coordinador == evento.universidad
    )
    if not (es_admin or es_coordinador_propio):
        messages.error(request, "No tienes permisos.")
        return redirect('ver_calendario')
    # ------------------------------

    confirmados = Invitacion.objects.filter(evento=evento, estado='CONFIRMADO')
    
    if not confirmados.exists():
        messages.warning(request, "No hay confirmados para enviar entrada.")
        return redirect('gestionar_asistencia', evento_id=evento.pk)

    try:
        connection = get_connection()
        connection.open()
    except:
        return redirect('gestionar_asistencia', evento_id=evento.pk)

    mensajes = []
    ids_act = []
    for inv in confirmados:
        if inv.usuario.email:
            try:
                asunto = f"ENTRADA: {evento.titulo}"
                cuerpo = f"""
                Detalles finales.
                Evento: {evento.titulo}
                Fecha: {evento.inicio.strftime('%d/%m/%Y a las %H:%M')}
                Lugar: {evento.lugar}
                ¡Te esperamos!
                """
                email = EmailMessage(asunto, textwrap.dedent(cuerpo).strip(), settings.EMAIL_HOST_USER, [inv.usuario.email], connection=connection)
                mensajes.append(email)
                ids_act.append(inv.id)
            except: pass

    count = 0
    if mensajes:
        count = connection.send_messages(mensajes)
        Invitacion.objects.filter(id__in=ids_act).update(estado='ENTRADA_ENVIADA')

    connection.close()
    messages.success(request, f"Entradas enviadas: {count}")
    return redirect('gestionar_asistencia', evento_id=evento.pk)


@login_required
def mis_invitaciones(request):
    mis_inv = Invitacion.objects.filter(usuario=request.user).order_by('-evento__inicio')
    return render(request, 'eventos/mis_invitaciones.html', {'invitaciones': mis_inv})

@login_required
def responder_invitacion(request, invitacion_id, respuesta):
    invitacion = get_object_or_404(Invitacion, pk=invitacion_id, usuario=request.user)
    
    if respuesta == 'confirmar':
        invitacion.estado = 'CONFIRMADO'
        messages.success(request, f"Has confirmado asistencia a {invitacion.evento.titulo}")
    elif respuesta == 'rechazar':
        invitacion.estado = 'RECHAZADO'
        messages.warning(request, f"Has rechazado la invitación a {invitacion.evento.titulo}")
        
    invitacion.save()
    return redirect('mis_invitaciones')


@login_required
def enviar_recordatorio_pendientes(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)

    # --- VALIDACIÓN DE PERMISOS ---
    es_admin = request.user.is_staff
    es_coordinador_propio = (
        hasattr(request.user, 'universidad_coordinador') and 
        request.user.universidad_coordinador == evento.universidad
    )
    
    if not (es_admin or es_coordinador_propio):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('ver_calendario')
    # ------------------------------

    invitaciones_pendientes = Invitacion.objects.filter(evento=evento, estado='ENVIADO')
    
    if not invitaciones_pendientes.exists():
        messages.warning(request, "No hay usuarios pendientes para recordar.")
        return redirect('gestionar_asistencia', evento_id=evento.pk)

    mensajes = []
    link = request.build_absolute_uri('/eventos/mis-invitaciones/')

    for invitacion in invitaciones_pendientes:
        if invitacion.usuario.email:
            asunto = f"RECORDATORIO: {evento.titulo}"
            cuerpo = f"""
                Hola {invitacion.usuario.first_name},
                
                Te enviamos un recordatorio para el evento "{evento.titulo}".
                
                📅 Fecha: {evento.inicio.strftime('%d/%m/%Y a las %H:%M')}
                
                Por favor, confirma tu asistencia aquí: {link}
                
                Saludos, 
                Equipo {evento.universidad.nombre}
            """
            email = EmailMessage(
                asunto, 
                textwrap.dedent(cuerpo).strip(), 
                settings.DEFAULT_FROM_EMAIL, 
                [invitacion.usuario.email]
            )
            mensajes.append(email)

    try:
        if mensajes:
            connection = get_connection()
            count = connection.send_messages(mensajes)
            messages.success(request, f"Se han enviado {count} recordatorios con éxito.")
        else:
            messages.info(request, "No se encontraron destinatarios con correos válidos.")
    except Exception as e:
        print(f"Error Anymail en APP: {e}")
        messages.error(request, "Hubo un problema al conectar con el servidor de correos.")

    # IMPORTANTE: Verifica que 'gestionar_asistencia' sea el nombre en app/urls.py
    return redirect('gestionar_asistencia', evento_id=evento.pk)


def get_facultades(request):
    """Devuelve las facultades de una universidad específica"""
    uni_id = request.GET.get('universidad_id')
    if uni_id:
        # values() crea una lista de diccionarios {'id': 1, 'nombre': '...'}
        facultades = list(Facultad.objects.filter(universidad_id=uni_id).values('id', 'nombre'))
        return JsonResponse(facultades, safe=False)
    return JsonResponse([], safe=False)

def get_departamentos(request):
    """Devuelve los departamentos de una facultad específica"""
    fac_id = request.GET.get('facultad_id')
    if fac_id:
        deptos = list(Departamento.objects.filter(facultad_id=fac_id).values('id', 'nombre'))
        return JsonResponse(deptos, safe=False)
    return JsonResponse([], safe=False)

def get_carreras(request):
    """Devuelve las carreras de un departamento específico"""
    dept_id = request.GET.get('departamento_id')
    if dept_id:
        # CORRECCIÓN AQUÍ:
        # Tu modelo usa 'id_carrera', no 'id'.
        # Pedimos los datos correctos a la BD:
        carreras_data = Carrera.objects.filter(departamento_id=dept_id).values('id_carrera', 'nombre')
        
        # TRUCO: Convertimos 'id_carrera' a 'id' para que el JavaScript (item.id) siga funcionando
        carreras_lista = [
            {'id': c['id_carrera'], 'nombre': c['nombre']} 
            for c in carreras_data
        ]
        
        return JsonResponse(carreras_lista, safe=False)
    
    return JsonResponse([], safe=False)

# ==========================================
#  LÓGICA DE IA Y MATCHING
# ==========================================

def _obtener_keywords_gemini(texto, cantidad=5):
    """ 
    >>> VERSIÓN MAESTRA: 
    1. Auto-detecta el mejor modelo (Flash/Pro).
    2. Prompt Inteligente: Si faltan skills técnicos, busca habilidades blandas o rubros.
    3. Seguridad DB: Corta palabras a 20 caracteres.
    """
    print(f"\n>>> INICIANDO ANÁLISIS IA (Texto: {len(texto)} chars) <<<")
    
    if not API_KEY:
        print("❌ ERROR: No hay API Key cargada.")
        return []

    try:
        # --- PASO 1: SELECCIÓN DE MODELO ROBUSTA ---
        print("🔍 Buscando modelos disponibles...")
        mis_modelos = []
        try:
            # Intenta listar los modelos habilitados en tu cuenta
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    mis_modelos.append(m.name)
        except Exception as e:
            print(f"⚠️ Error listando (usando default): {e}")
            mis_modelos = ['models/gemini-1.5-flash', 'models/gemini-pro']

        # Si la lista está vacía por error de API, usamos defaults
        if not mis_modelos:
            mis_modelos = ['models/gemini-1.5-flash', 'models/gemini-pro']

        # Priorizamos 'flash' por ser más rápido y barato
        modelo_final = next((m for m in mis_modelos if 'flash' in m), mis_modelos[0])
        print(f"🚀 Usando modelo: {modelo_final}")

        # --- PASO 2: EL PROMPT DE CASCADA (LA CLAVE) ---
        model = genai.GenerativeModel(modelo_final)
        
        prompt = (
            f"Analiza la siguiente oferta laboral y genera EXACTAMENTE {cantidad} etiquetas (tags) cortas."
            f"\n\nReglas de Relleno Obligatorio para llegar a {cantidad}:"
            f"\n1. PRIORIDAD MÁXIMA: Extrae Tecnologías y Herramientas (ej: Python, SAP, Grúa Horquilla)."
            f"\n2. SI FALTAN para llegar a {cantidad}: Extrae Habilidades Blandas o Competencias (ej: Liderazgo, Ventas, Orden)."
            f"\n3. SI AÚN FALTAN: Agrega la Categoría o Industria (ej: Logística, Salud, Informática)."
            f"\n4. IMPORTANTE: Devuelve SOLO las palabras separadas por comas. Sin numeración ni explicaciones."
            f"\n\nOferta: \"{texto[:3000]}\""
        )
        
        response = model.generate_content(prompt)
        
        # --- PASO 3: LIMPIEZA QUIRÚRGICA ---
        # Reemplazamos saltos de línea por comas y quitamos puntos extra
        limpio = response.text.replace("\n", ",").replace(".", "").strip()
        
        # Creamos la lista, quitamos espacios y cortamos a 20 chars (Seguridad BD)
        palabras = [p.strip().title()[:20] for p in limpio.split(",") if p.strip()]
        
        # --- PASO 4: RED DE SEGURIDAD FINAL ---
        # Si la IA falla catastróficamente y manda menos de 5, rellenamos con algo neutro
        # pero profesional, en lugar de "General".
        while len(palabras) < cantidad:
            palabras.append("Profesional")
            
        print(f"🌟 KEYWORDS FINALES: {palabras[:cantidad]}\n")
        return palabras[:cantidad]

    except Exception as e:
        print(f"💀 ERROR CRÍTICO IA: {e}")
        # En caso de error total, devolvemos lista vacía para no romper la web
        return []

def _calcular_porcentaje_match(oferta, cv):
    """
    Función interna: Compara las 5 palabras de la Oferta vs las 10 del CV.
    Devuelve un entero del 0 al 100.
    """
    if not oferta or not cv:
        return 0

    # 1. Sacamos las palabras de la OFERTA (5 campos) a un SET (conjunto único)
    lista_oferta = [
        oferta.palabra1, oferta.palabra2, oferta.palabra3, 
        oferta.palabra4, oferta.palabra5
    ]
    # Limpiamos nulos y espacios, convertimos a minúsculas
    set_oferta = set([p.lower().strip() for p in lista_oferta if p])

    # 2. Sacamos las palabras del CV (10 campos) a un SET
    lista_cv = [
        cv.palabra1, cv.palabra2, cv.palabra3, cv.palabra4, cv.palabra5,
        cv.palabra6, cv.palabra7, cv.palabra8, cv.palabra9, cv.palabra10
    ]
    set_cv = set([p.lower().strip() for p in lista_cv if p])

    # 3. Intersección: ¿Qué palabras están en ambos lados?
    coincidencias = set_oferta.intersection(set_cv)
    
    # 4. Cálculo: (Aciertos / Total palabras oferta) * 100
    # Como la oferta tiene 5 palabras, cada acierto vale 20 puntos.
    # 1 acierto = 20%, 5 aciertos = 100%
    porcentaje = (len(coincidencias) / 5) * 100
    
    return int(porcentaje)


# ==========================================
#  VISTAS (VIEWS)
# ==========================================

@login_required
def crear_oferta_laboral(request):
    """
    Vista: Dashboard de Mis Ofertas (Modo Depuración)
    """
    try:
        # --- LOGICA DE CREACIÓN (POST) ---
        if request.method == 'POST':
            texto = request.POST.get("texto_oferta")
            if texto:
                # VERIFICACIÓN 1: ¿Existe la función de Gemini?
                if '_obtener_keywords_gemini' not in globals():
                    raise Exception("Error: La función '_obtener_keywords_gemini' no está definida o importada.")

                # 1. Procesar con IA
                kw = _obtener_keywords_gemini(texto, 5)
                
                # VERIFICACIÓN 2: ¿La IA devolvió una lista válida?
                if not kw or len(kw) < 5:
                    # Rellenar con None si falló la IA para que no explote la BD
                    kw = [None] * 5 

                # 2. Crear nueva oferta
                Oferta.objects.create(
                    creado_por=request.user,
                    titulo="Oferta Laboral",
                    empresa="Sin empresa",
                    descripcion=texto,
                    palabra1=kw[0], palabra2=kw[1], palabra3=kw[2], palabra4=kw[3], palabra5=kw[4]
                )
                messages.success(request, "Oferta publicada y procesada.")
                return redirect('mis_ofertas') 

        # --- LOGICA DE VISUALIZACIÓN (GET) ---
        
        # VERIFICACIÓN 3: ¿Están importados los modelos?
        if 'Oferta' not in globals() or 'CVUsuario' not in globals():
             raise Exception("Error: Faltan importar los modelos Oferta o CVUsuario.")

        # 1. Mis Ofertas
        mis_ofertas = Oferta.objects.filter(creado_por=request.user).order_by('-creado')
        
        # 2. CVs de los demás
        otros_cvs = CVUsuario.objects.exclude(usuario=request.user)

        dashboard = []

        # VERIFICACIÓN 4: ¿Existe la función de Match?
        if '_calcular_porcentaje_match' not in globals():
             raise Exception("Error: La función '_calcular_porcentaje_match' no está definida. Copiala de nuestra conversación anterior.")

        for oferta in mis_ofertas:
            candidatos = []
            for cv in otros_cvs:
                # Calculamos match
                pct = _calcular_porcentaje_match(oferta, cv)
                
                if pct > 0:
                    # Definimos estilos visuales
                    if pct >= 80:
                        estilo = "border-emerald-500 text-emerald-600 bg-emerald-50"
                    elif pct >= 40:
                        estilo = "border-amber-500 text-amber-600 bg-amber-50"
                    else:
                        estilo = "border-red-500 text-red-600 bg-red-50"
                    
                    candidatos.append({
                        'usuario': cv.usuario,
                        'match': pct,
                        'estilo': estilo,
                        'cv_id': cv.id
                    })
            
            # Ordenar: Mejor candidato primero
            candidatos.sort(key=lambda x: x['match'], reverse=True)
            
            dashboard.append({
                'oferta': oferta,
                'candidatos': candidatos,
                'total': len(candidatos)
            })

        return render(request, 'bolsa/mis_ofertas.html', {'dashboard': dashboard})

    except Exception as e:
        # --- BLOQUE DE DEPURACIÓN (CHIVATO) ---
        # Si algo falla arriba, esto te mostrará el error en pantalla
        import sys
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_trace = traceback.format_exc()
        
        html_error = f"""
        <html>
        <body style="background-color: #1a1a1a; color: #ffcccc; font-family: monospace; padding: 20px;">
            <div style="border: 3px solid #ff4444; padding: 20px; background-color: #330000; border-radius: 10px;">
                <h1 style="color: #ff4444; border-bottom: 1px solid #ff4444;">🔥 ERROR DETECTADO (Error 500)</h1>
                <h2 style="color: white;">{str(e)}</h2>
                <div style="background-color: black; padding: 15px; overflow: auto; border-radius: 5px;">
                    <pre>{error_trace}</pre>
                </div>
                <p style="margin-top: 20px; color: yellow;">
                    <strong>¿Qué hacer?</strong><br>
                    1. Lee la última línea del 'Traceback' de arriba.<br>
                    2. Si dice 'NameError', te falta importar un modelo o copiar una función auxiliar.<br>
                    3. Si dice 'TemplateDoesNotExist', el archivo HTML no está en la carpeta correcta.<br>
                    4. Copia este error y envíaselo a tu asistente.
                </p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_error)

@login_required
def mis_oportunidades(request):
    """ 
    Vista: Mis Oportunidades (Modo Candidato)
    Calcula match y envía las palabras EXACTAS al template.
    """
    mi_cv = CVUsuario.objects.filter(usuario=request.user).last()
    
    if not mi_cv:
        messages.warning(request, "Sube tu CV primero.")
        return redirect('mi_perfil')

    # 1. Tu CV en un Set limpio
    raw_cv = [mi_cv.palabra1, mi_cv.palabra2, mi_cv.palabra3, mi_cv.palabra4, mi_cv.palabra5, 
              mi_cv.palabra6, mi_cv.palabra7, mi_cv.palabra8, mi_cv.palabra9, mi_cv.palabra10]
    set_cv = set([str(p).strip().title() for p in raw_cv if p and p not in ['General', 'None', '']])

    todas_ofertas = Oferta.objects.filter(activa=True).exclude(creado_por=request.user).order_by('-creado')
    lista_matches = []

    for oferta in todas_ofertas:
        # 2. Oferta en un Set limpio
        raw_oferta = [oferta.palabra1, oferta.palabra2, oferta.palabra3, oferta.palabra4, oferta.palabra5]
        set_oferta = set([str(p).strip().title() for p in raw_oferta if p and p not in ['General', 'None', '']])

        # 3. Intersección (Palabras que coinciden)
        coincidencias = set_oferta.intersection(set_cv)
        
        # 4. Cálculo de Porcentaje
        # Usamos el set_oferta real para evitar dividir por 0
        total_tags = len(set_oferta)
        if total_tags > 0:
            porcentaje = int((len(coincidencias) / total_tags) * 100)
        else:
            porcentaje = 0

        # Mostrar todas las ofertas, con o sin match
        lista_matches.append({
            'oferta': oferta, 
            'match': porcentaje,
            'coincidencias': list(coincidencias),
            'todas_tags': list(set_oferta)
        })

    lista_matches.sort(key=lambda x: x['match'], reverse=True)
    
    return render(request, 'bolsa/mis_oportunidades.html', {'matches': lista_matches})


# --- VISTA SOLO PARA ADMINISTRADORES ---
@user_passes_test(lambda u: u.is_staff)
def admin_ofertas(request):
    try:
        # Intenta cargar los datos
        ofertas = Oferta.objects.all().order_by('-creado')
        # Intenta dibujar el HTML
        return render(request, 'bolsa/admin_ofertas.html', {'ofertas': ofertas})
    except Exception as e:
        # Si falla, ¡muéstrame por qué!
        error_msg = f"""
        <div style="background: #fee; border: 2px solid red; padding: 20px; font-family: monospace;">
            <h1 style="color: red;">🔥 ERROR EN ADMIN OFERTAS</h1>
            <h3>{str(e)}</h3>
            <pre>{traceback.format_exc()}</pre>
        </div>
        """
        return HttpResponse(error_msg)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_necesidades(request):
    try:
        necesidades = Necesidad.objects.all().order_by('-creado')
        return render(request, 'bolsa/admin_necesidades.html', {'necesidades': necesidades})
    except Exception as e:
        import traceback
        return HttpResponse(f"""
            <div style='background: #330000; color: #ffcccc; border: 2px solid red; padding: 20px; font-family: monospace;'>
                <h1 style='color: red;'>ERROR</h1>
                <h3>{str(e)}</h3>
                <pre>{traceback.format_exc()}</pre>
            </div>
        """)


#---- NECESITO OFREZCO DE USUARIO -----
@login_required
def vista_networking(request):
    from .models import Oferta, Necesidad
    # HISTORIAL
    ofertas_user = Oferta.objects.filter(creado_por=request.user).order_by('-creado')
    necesidades_user = Necesidad.objects.filter(usuario=request.user).order_by('-creado')

    # ÚLTIMOS REGISTROS
    ultima_oferta = ofertas_user.first()
    ultima_necesidad = necesidades_user.first()

    # Construir listas de palabras para mostrar en HTML
    palabras_oferta = []
    if ultima_oferta:
        palabras_oferta = [getattr(ultima_oferta, f'palabra{i}', None) for i in range(1,6) if getattr(ultima_oferta, f'palabra{i}', None)]
    
    palabras_necesidad = []
    if ultima_necesidad:
        palabras_necesidad = [getattr(ultima_necesidad, f'palabra{i}', None) for i in range(1,6) if getattr(ultima_necesidad, f'palabra{i}', None)]

    contexto = {
            'ultima_oferta': ultima_oferta,
            'palabras_oferta': palabras_oferta,
            'ultima_necesidad': ultima_necesidad,
            'palabras_necesidad': palabras_necesidad,
            'historial_ofertas': ofertas_user,
            'historial_necesidades': necesidades_user,
        }

    print(f"DEBUG: ultima_oferta={ultima_oferta}, ultima_necesidad={ultima_necesidad}")
    return render(request, 'networking.html', contexto)
       


@login_required
def guardar_oferta(request):
    if request.method == 'POST':
        try:
            from .models import Oferta
            import threading

            texto_usuario = request.POST.get('texto_oferta', '').strip()
            p_raw = request.POST.get('palabras_manuales', '').split(',')
            p = [pal.strip() for pal in p_raw if pal.strip()]

            if not texto_usuario:
                messages.warning(request, "El campo de oferta no puede estar vacío.")
                return redirect('pagina_networking')

            # 1. Crear registro
            oferta = Oferta.objects.create(
                creado_por=request.user,
                titulo="Aporte de Networking",
                empresa="Networking Interno",
                descripcion=texto_usuario,
                palabra1=p[0] if len(p) > 0 else None,
                palabra2=p[1] if len(p) > 1 else None,
                palabra3=p[2] if len(p) > 2 else None,
                palabra4=p[3] if len(p) > 3 else None,
                palabra5=p[4] if len(p) > 4 else None,
                activa=True
            )

            # 2. IA en segundo plano
            def generar_keywords_background(oid):
                try:
                    obj = Oferta.objects.get(id_oferta=oid)
                    palabras_ia = _obtener_keywords_gemini(obj.descripcion, 5)
                    if isinstance(palabras_ia, list):
                        obj.palabra1 = palabras_ia[0] if len(palabras_ia) > 0 else None
                        obj.palabra2 = palabras_ia[1] if len(palabras_ia) > 1 else None
                        obj.palabra3 = palabras_ia[2] if len(palabras_ia) > 2 else None
                        obj.palabra4 = palabras_ia[3] if len(palabras_ia) > 3 else None
                        obj.palabra5 = palabras_ia[4] if len(palabras_ia) > 4 else None
                        obj.save()
                except Exception as e:
                    print(f"⚠️ Error IA background Networking: {e}")

            threading.Thread(target=generar_keywords_background, args=(oferta.id_oferta,)).start()

            messages.success(request, "¡Tu oferta de networking se ha guardado!")

        except Exception as e:
            print(f"ERROR AL GUARDAR: {e}")
            messages.error(request, f"Hubo un error al guardar: {e}")

    return redirect('pagina_networking')

@login_required
def ver_oferta(request, oferta_id):
    from django.shortcuts import get_object_or_404, render
    from .models import Oferta

    oferta = get_object_or_404(Oferta, id_oferta=oferta_id)

    # Opcional: puedes validar que solo el creador o staff pueda verla
    if request.user != oferta.creado_por and not request.user.is_staff:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, "No tienes permiso para ver esta oferta.")
        return redirect('pagina_networking')

    palabras_clave = [oferta.palabra1, oferta.palabra2, oferta.palabra3, oferta.palabra4, oferta.palabra5]
    palabras_clave = [p for p in palabras_clave if p]  # Filtra los None o vacíos

    contexto = {
        'oferta': oferta,
        'palabras_clave': palabras_clave,
    }
    return render(request, 'ver_oferta.html', contexto)

@login_required
def editar_networking_oferta(request, oferta_id):
    import threading
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
    from .models import Oferta

    try:
        # 1. Buscamos la oferta por ID
        oferta = get_object_or_404(Oferta, pk=oferta_id)
        
        # Permisos: Solo el dueño o staff
        if request.user != oferta.creado_por and not request.user.is_staff:
            messages.error(request, "No tienes permiso para editar esta oferta.")
            return redirect('pagina_networking')

        if request.method == 'POST':
            # 2. ACTUALIZACIÓN DEL TEXTO
            nuevo_texto = request.POST.get('texto_oferta')
            if nuevo_texto:
                oferta.descripcion = nuevo_texto
                oferta.save()  # guardamos primero el texto

            # 3. IA EN SEGUNDO PLANO (regenera palabras clave)
            def generar_keywords_background(oid):
                try:
                    obj = Oferta.objects.get(id=oid)
                    palabras = _obtener_keywords_gemini(obj.descripcion, 5)
                    if isinstance(palabras, list):
                        obj.palabra1 = palabras[0] if len(palabras) > 0 else None
                        obj.palabra2 = palabras[1] if len(palabras) > 1 else None
                        obj.palabra3 = palabras[2] if len(palabras) > 2 else None
                        obj.palabra4 = palabras[3] if len(palabras) > 3 else None
                        obj.palabra5 = palabras[4] if len(palabras) > 4 else None
                        obj.save()
                except Exception as e:
                    print(f"⚠️ Error IA background Networking: {e}")

            threading.Thread(target=generar_keywords_background, args=(oferta.id_oferta,)).start()

            messages.success(request, "Oferta de networking actualizada correctamente.")
            return redirect('pagina_networking')

        # 4. PREPARACIÓN PARA EL RENDER (GET)
        # Solo cargamos el texto para el formulario, las palabras clave se muestran automáticamente
        oferta.texto_oferta = oferta.descripcion
        return render(request, 'editar_oferta_networking.html', {'oferta': oferta})

    except Exception as e:
        import traceback
        from django.http import HttpResponse
        return HttpResponse(f"""
            <div style='background: #330000; color: #ffcccc; padding: 20px;'>
                <h1>🔥 ERROR AL EDITAR</h1>
                <pre>{traceback.format_exc()}</pre>
            </div>
        """)

@login_required
def eliminar_networking_oferta(request, oferta_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from .models import Oferta

    try:
        # 1. Buscamos la oferta asegurándonos de que existe
        oferta = get_object_or_404(Oferta, pk=oferta_id)
        
        # 2. Verificación de seguridad: Solo el creador o un administrador pueden borrarla
        if request.user == oferta.creado_por or request.user.is_staff:
            oferta.delete()
            messages.success(request, "La oferta de networking se ha eliminado correctamente.")
        else:
            messages.error(request, "No tienes permisos para eliminar esta oferta.")
        
        # 3. Redirigimos siempre a la página principal de networking
        return redirect('pagina_networking')

    except Exception as e:
        import traceback
        from django.http import HttpResponse
        # Estética de error para facilitar el debug si algo falla en la base de datos
        return HttpResponse(f"""
            <div style='background: #330000; color: #ffcccc; border: 2px solid red; padding: 20px; font-family: monospace;'>
                <h1 style='color: red;'>🔥 ERROR AL ELIMINAR NETWORKING</h1>
                <h3>{str(e)}</h3>
                <pre>{traceback.format_exc()}</pre>
                <a href="/ofrezco-necesito/" style="color: white; font-weight: bold;">Volver atrás</a>
            </div>
        """)
@login_required
def editar_networking_necesidad(request, necesidad_id):
    necesidad = get_object_or_404(Necesidad, pk=necesidad_id)
    
    if request.user != necesidad.usuario and not request.user.is_staff:
        messages.error(request, "No tienes permiso para editar esta necesidad.")
        return redirect('pagina_networking')

    if request.method == 'POST':
        nuevo_texto = request.POST.get('texto_necesita')
        if nuevo_texto:
            necesidad.texto_necesita = nuevo_texto
            try:
                palabras = _obtener_keywords_gemini(nuevo_texto, 5)
                for i in range(5):
                    setattr(necesidad, f'palabra{i+1}', palabras[i] if i < len(palabras) else None)
            except Exception as e:
                print(f"⚠️ Error IA: {e}")
            necesidad.save()
            messages.success(request, "Necesidad actualizada correctamente.")
            return redirect('pagina_networking')

    return render(request, 'mi_perfil/editar_necesidad_networking.html', {'necesidad': necesidad})


@login_required
def eliminar_networking_necesidad(request, necesidad_id):
    necesidad = get_object_or_404(Necesidad, pk=necesidad_id)
    
    if request.user == necesidad.usuario or request.user.is_staff:
        necesidad.delete()
        messages.success(request, "Necesidad eliminada correctamente.")
    else:
        messages.error(request, "No tienes permiso para eliminar esta necesidad.")
    
    return redirect('pagina_networking')

# --- LÓGICA DE EDICIÓN (Sirve para Admin y Usuario) ---
#------BOLSA DE EMPLEO -------
@login_required
def editar_oferta(request, oferta_id):
    try:
        oferta = get_object_or_404(Oferta, pk=oferta_id)
        
        # Permisos
        if request.user != oferta.creado_por and not request.user.is_staff:
            messages.error(request, "No tienes permiso para editar esta oferta.")
            return redirect('mis_ofertas')

        if request.method == 'POST':
            oferta.titulo = request.POST.get('titulo', oferta.titulo)
            oferta.empresa = request.POST.get('empresa', oferta.empresa)
            oferta.descripcion = request.POST.get('descripcion', oferta.descripcion)
            oferta.requisitos = request.POST.get('requisitos', oferta.requisitos)
            oferta.ubicacion = request.POST.get('ubicacion', oferta.ubicacion)
            oferta.modalidad = request.POST.get('modalidad', oferta.modalidad)
            oferta.jornada = request.POST.get('jornada', oferta.jornada)
            oferta.salario = request.POST.get('salario', oferta.salario)
            oferta.activa = request.POST.get('activa') == 'on'

            # Guardar primero (rápido, sin IA)
            oferta.save()

            # Fallback inmediato (por si IA falla o demora)
            oferta.palabra1 = request.POST.get('palabra1', oferta.palabra1)
            oferta.palabra2 = request.POST.get('palabra2', oferta.palabra2)
            oferta.palabra3 = request.POST.get('palabra3', oferta.palabra3)
            oferta.palabra4 = request.POST.get('palabra4', oferta.palabra4)
            oferta.palabra5 = request.POST.get('palabra5', oferta.palabra5)
            oferta.save()

            # 🔥 Ejecutar IA en segundo plano (NO bloquea)
            def generar_keywords_background(oferta_id):
                try:
                    oferta_bg = Oferta.objects.get(id_oferta=oferta_id)
                    texto = f"{oferta_bg.titulo} {oferta_bg.descripcion} {oferta_bg.requisitos or ''}"

                    palabras = _obtener_keywords_gemini(texto, 5)

                    if not isinstance(palabras, list):
                        return

                    oferta_bg.palabra1 = palabras[0] if len(palabras) > 0 else None
                    oferta_bg.palabra2 = palabras[1] if len(palabras) > 1 else None
                    oferta_bg.palabra3 = palabras[2] if len(palabras) > 2 else None
                    oferta_bg.palabra4 = palabras[3] if len(palabras) > 3 else None
                    oferta_bg.palabra5 = palabras[4] if len(palabras) > 4 else None

                    oferta_bg.save()

                except Exception as e:
                    print(f"⚠️ Error IA background: {e}")

            threading.Thread(
                target=generar_keywords_background,
                args=(oferta.id_oferta,)
            ).start()

            messages.success(request, "Oferta actualizada correctamente.")

            if request.user.is_staff:
                return redirect('gestion-bolsa')
            return redirect('mis_ofertas')

        return render(request, 'bolsa/editar_oferta.html', {'oferta': oferta})

    except Exception as e:
        import traceback
        return HttpResponse(f"""
            <div style='background: #330000; color: #ffcccc; border: 2px solid red; padding: 20px; font-family: monospace;'>
                <h1 style='color: red;'>🔥 ERROR AL EDITAR</h1>
                <h3>{str(e)}</h3>
                <pre>{traceback.format_exc()}</pre>
            </div>
        """)

@login_required
def eliminar_oferta(request, oferta_id):
    try:
        oferta = get_object_or_404(Oferta, pk=oferta_id)
        
        # Seguridad
        if request.user == oferta.creado_por or request.user.is_staff:
            oferta.delete()
            messages.success(request, "Oferta eliminada correctamente.")
        else:
            messages.error(request, "No tienes permiso para eliminar esta oferta.")
            return redirect('mis_ofertas')
        
        # REDIRECCIÓN CORRECTA
        if request.user.is_staff:
            return redirect('gestion-bolsa')
            
        return redirect('mis_ofertas')

    except Exception as e:
        import traceback
        return HttpResponse(f"""
            <div style='background: #330000; color: #ffcccc; border: 2px solid red; padding: 20px; font-family: monospace;'>
                <h1 style='color: red;'>🔥 ERROR AL ELIMINAR</h1>
                <h3>{str(e)}</h3>
                <pre>{traceback.format_exc()}</pre>
            </div>
        """)
@login_required
def ver_necesidad(request, necesidad_id):
    necesidad = get_object_or_404(Necesidad, pk=necesidad_id)
    
    if request.user != necesidad.usuario and not request.user.is_staff:
        messages.error(request, "No tienes permiso para ver esta necesidad.")
        return redirect('pagina_networking')
    
    palabras = [getattr(necesidad, f'palabra{i}', None) for i in range(1,6) if getattr(necesidad, f'palabra{i}', None)]
    
    return render(request, 'mi_perfil/ver_necesidad_networking.html', {
        'necesidad': necesidad,
        'palabras': palabras
    })
    
@login_required
def ver_oferta(request, oferta_id):
    oferta = get_object_or_404(Oferta, pk=oferta_id)
    return render(request, 'bolsa/ver_oferta.html', {'oferta': oferta})

def descargar_plantilla(request):
    # Definimos la ruta al archivo Excel dentro de la carpeta static
    file_path = os.path.join(settings.BASE_DIR, 'static', 'ejemplo_carga_usuarios.xlsx')
    
    # Verificamos si el archivo existe
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            # Preparamos la respuesta con el tipo de contenido correcto para Excel
            response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            # Forzamos la descarga con el nombre 'plantilla_carga_usuarios.xlsx'
            response['Content-Disposition'] = 'attachment; filename="plantilla_carga_usuarios.xlsx"'
            return response
    
    # Si no existe, lanzamos un error 404
    raise Http404("El archivo de plantilla no se encuentra en la carpeta static.")

@login_required
def ver_calendario_view(request):
    # 1. Definir valores por defecto
    id_empresa = 0 
    nombre_empresa = "Calendario General"

    # 2. Lógica para Coordinador
    if hasattr(request.user, 'universidad_coordinador') and request.user.universidad_coordinador:
        id_empresa = request.user.universidad_coordinador.pk 
        nombre_empresa = request.user.universidad_coordinador.nombre
    
    # 3. Lógica para Alumno
    elif hasattr(request.user, 'carrera') and request.user.carrera:
         try:
             id_empresa = request.user.carrera.departamento.facultad.universidad.pk
             nombre_empresa = request.user.carrera.departamento.facultad.universidad.nombre
         except AttributeError:
             pass

    context = {
        'base_template': 'base_public.html', 
        'es_editor': False, 
        'id_empresa': id_empresa,
        'nombre_empresa': nombre_empresa
    }
    
    # CORRECCIÓN AQUÍ: Cambia 'app/' por 'eventos/' (o donde tengas guardado el HTML)
    return render(request, 'eventos/calendario_public.html', context)



@login_required
def responder_invitacion_ajax(request, evento_id, accion):
    if request.method == 'GET': # O POST si prefieres seguridad estricta
        evento = get_object_or_404(Evento, pk=evento_id)
        
        # Buscamos la invitación o la creamos si es la primera vez que interactúa
        invitacion, created = Invitacion.objects.get_or_create(
            usuario=request.user,
            evento=evento,
            defaults={'estado': 'PENDIENTE'}
        )

        if accion == 'confirmar':
            invitacion.estado = 'CONFIRMADO' # O el estado que uses en tu modelo
        elif accion == 'rechazar':
            invitacion.estado = 'RECHAZADO'
        
        invitacion.save()
        
        return JsonResponse({'status': 'success', 'nuevo_estado': invitacion.estado})
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@login_required
def enviar_pregunta(request):
    if request.method == 'POST':
        evento_id = request.POST.get('evento_id')
        tipo = request.POST.get('tipo')
        texto = request.POST.get('texto')
        
        if not evento_id or not tipo or not texto:
            return JsonResponse({'status': 'error', 'message': 'Faltan datos'})

        evento = get_object_or_404(Evento, pk=evento_id)
        
        # 1. Guardar la pregunta en el historial para la IA
        PreguntaEvento.objects.create(
            evento=evento,
            tipo=tipo,
            texto=texto
        )
        
        # 2. ¡EL PASO CLAVE! Sumar +1 al contador en la Base de Datos
        if tipo == 'expositor':
            Evento.objects.filter(pk=evento.pk).update(contador_preguntas=F('contador_preguntas') + 1)
        else:
            Evento.objects.filter(pk=evento.pk).update(contador_aportes=F('contador_aportes') + 1)

        return JsonResponse({'status': 'success'})
        
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

@login_required
def ver_calendario_view(request):
    id_empresa = 0 
    nombre_empresa = "Calendario General"

    if hasattr(request.user, 'universidad_coordinador') and request.user.universidad_coordinador:
        id_empresa = request.user.universidad_coordinador.pk 
        nombre_empresa = request.user.universidad_coordinador.nombre
        
    elif hasattr(request.user, 'carrera') and request.user.carrera:
         try:
             id_empresa = request.user.carrera.departamento.facultad.universidad.pk
             nombre_empresa = request.user.carrera.departamento.facultad.universidad.nombre
         except AttributeError:
             pass

    context = {
        'base_template': 'base_public.html', 
        'es_editor': False, # <--- ESTO FUERZA MODO SOLO LECTURA
        'id_empresa': id_empresa,
        'nombre_empresa': nombre_empresa
    }
    
    # Renderiza la vista de alumnos
    return render(request, 'eventos/calendario_public.html', context)


def ping(request):
    return HttpResponse("pong", status=200)


from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings


def ejecutar_recordatorios_cron(request, token):
    # 1. SEGURIDAD: Solo tú (o el robot) con este token exacto puede ejecutar esto
    TOKEN_SECRETO = "super_secreto_cron_2026_dii"
    
    if token != TOKEN_SECRETO:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    # 2. Buscar invitaciones pendientes de eventos que AÚN NO han pasado
    ahora = timezone.now()
    invitaciones_pendientes = Invitacion.objects.filter(
        estado='ENVIADO', # <--- CORREGIDO: Ajustado a tu modelo real
        evento__inicio__gt=ahora # Solo eventos futuros
    ).select_related('usuario', 'evento')

    correos_enviados = 0

    # 3. Recorrer y enviar correos
    for inv in invitaciones_pendientes:
        usuario = inv.usuario
        evento = inv.evento
        
        if usuario.email:
            asunto = f'⏳ Recordatorio: Tienes una invitación pendiente para "{evento.titulo}"'
            
            # Formateamos la fecha para que se vea bonita
            fecha_str = evento.inicio.strftime("%d de %B, %Y a las %H:%M")
            
            mensaje = f"""Hola {usuario.first_name or usuario.username},

Te recordamos que tienes una invitación PENDIENTE de confirmar para el siguiente evento:

📌 Evento: {evento.titulo}
📅 Fecha: {fecha_str}
📍 Lugar: {evento.lugar}

Por favor, ingresa a la plataforma Red de Ex Alumnos DII para confirmar tu asistencia o indicar que no podrás asistir.

Saludos cordiales,
Equipo de Coordinación.
"""
            try:
                send_mail(
                    asunto,
                    mensaje,
                    # CORREGIDO: Usamos DEFAULT_FROM_EMAIL (que configuraremos en settings)
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'javierluciano14@gmail.com'), 
                    [usuario.email],
                    fail_silently=False,
                )
                correos_enviados += 1
            except Exception as e:
                print(f"Error enviando correo a {usuario.email}: {e}")

    # Retornamos un JSON para que cron-job.org sepa que todo salió bien
    return JsonResponse({
        'status': 'success', 
        'mensaje': f'Se enviaron {correos_enviados} recordatorios con éxito.'
    })



@login_required
def iniciar_pago_evento(request, evento_id):
    try:
        # 1. Buscar el evento
        evento = get_object_or_404(Evento, pk=evento_id)
        
        if evento.costo <= 0:
            return HttpResponse("Este evento es gratuito.", status=400)
            
        # 2. Inicializar SDK
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        # ⚠️ CORRECCIÓN AQUÍ: Usamos id_evento
        referencia_interna = f"evt_{evento.id_evento}_usr_{request.user.id}"
        host = request.scheme + "://" + request.get_host()
        
        # 3. Datos del comprador
        nombre = request.user.first_name if request.user.first_name else "Usuario"
        apellido = request.user.last_name if request.user.last_name else "Alumni"
        email = request.user.email if request.user.email else "correo_temporal@tu-sitio.com"

        preference_data = {
            "items": [
                {
                    "title": f"Entrada: {evento.titulo}",
                    "quantity": 1,
                    "currency_id": "CLP",
                    "unit_price": float(evento.costo)
                }
            ],
            "payer": {
                "name": nombre,
                "surname": apellido,
                "email": email,
            },
            "back_urls": {
                "success": f"{host}/pagos/exito/",
                "failure": f"{host}/pagos/fallo/",
                "pending": f"{host}/pagos/pendiente/"
            },
            "auto_return": "approved",
            "external_reference": referencia_interna,
        }
        
        # 4. Crear Preferencia
        preference_response = sdk.preference().create(preference_data)
        
        # 5. Validación estricta
        if "response" in preference_response and "init_point" in preference_response["response"]:
            return redirect(preference_response["response"]["init_point"])
        else:
            error_msg = f"Mercado Pago rechazó la petición: {preference_response}"
            print(error_msg)
            return HttpResponse(error_msg, status=500)
            
    except Exception as e:
        print(f"Error crítico en iniciar_pago_evento: {e}")
        return HttpResponse(f"Error interno del servidor de Django: {e}", status=500)
    

# --- VISTAS DE RETORNO (Lo que ve el usuario tras pagar) ---
@login_required
def pago_exitoso(request):
    # 1. Capturamos los datos que Mercado Pago pone en la URL al volver
    payment_status = request.GET.get('status')
    external_reference = request.GET.get('external_reference') # ej: evt_21_usr_5
    payment_id = request.GET.get('payment_id')

    # 2. Si el pago dice 'approved', actualizamos la base de datos AHORA MISMO
    if payment_status == 'approved' and external_reference:
        try:
            # Desarmamos el texto "evt_21_usr_5" para sacar los IDs
            partes = external_reference.split('_')
            evento_id = int(partes[1])
            usuario_id = int(partes[3])

            # A) BUSCAMOS O CREAMOS LA INVITACIÓN (Aquí estaba el fallo)
            # Usamos update_or_create para cubrir ambos casos: si ya existía o si es nuevo
            invitacion, created = Invitacion.objects.update_or_create(
                evento_id=evento_id, 
                usuario_id=usuario_id,
                defaults={'estado': 'PAGADO'} # Forzamos el estado a PAGADO
            )
            
            print(f"✅ Invitación {'creada' if created else 'actualizada'} a PAGADO para evento {evento_id}")

            # B) Guardamos el respaldo en TransaccionPago
            TransaccionPago.objects.get_or_create(
                id_transaccion=payment_id,
                defaults={
                    'usuario_id': usuario_id,
                    'evento_id': evento_id,
                    'monto': invitacion.evento.costo, 
                    'estado': 'approved'
                }
            )

        except Exception as e:
            print(f"⚠️ Error crítico actualizando pago al retorno: {e}")

    # 3. Mostramos la pantalla verde
    return render(request, 'eventos/pago_exitoso.html')


@login_required
def pago_fallido(request):
    return render(request, 'eventos/pago_fallido.html')

@login_required
def pago_pendiente(request):
    return render(request, 'eventos/pago_pendiente.html')


@csrf_exempt 
def webhook_mercadopago(request):
    if request.method == "POST":
        data_id = request.GET.get('data.id')
        topic = request.GET.get('type') or request.GET.get('topic')
        
        if topic == 'payment' and data_id:
            import mercadopago
            from django.conf import settings
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(data_id)
            pago = payment_info["response"]
            
            if pago.get("status") == "approved":
                ref = pago.get("external_reference", "")
                
                # --------------------------------------------------
                # ESCENARIO 1: EL USUARIO PAGÓ UN EVENTO
                # --------------------------------------------------
                if ref.startswith("evt_"):
                    partes = ref.split("_")
                    try:
                        e_id = int(partes[1])
                        u_id = int(partes[3])
                        
                        TransaccionPago.objects.update_or_create(
                            id_transaccion=str(data_id),
                            defaults={
                                'usuario_id': u_id,
                                'evento_id': e_id,
                                'monto': int(pago.get("transaction_amount", 0)),
                                'estado': 'approved'
                            }
                        )
                        
                        Invitacion.objects.filter(evento_id=e_id, usuario_id=u_id).update(estado='PAGADO')
                    except Exception as e:
                        print(f"Error procesando webhook MP (Evento): {e}")

                # --------------------------------------------------
                # ESCENARIO 2: EL USUARIO PAGÓ SU MEMBRESÍA
                # --------------------------------------------------
                elif ref.startswith("mem_"):
                    partes = ref.split("_")
                    try:
                        p_id = int(partes[1]) # ID del plan
                        u_id = int(partes[3]) # ID del usuario
                        
                        from user.models import SuscripcionUsuario
                        
                        # Buscamos la suscripción del usuario y ejecutamos la función robusta
                        suscripcion, created = SuscripcionUsuario.objects.get_or_create(usuario_id=u_id)
                        suscripcion.renovar_por_un_ano() # Esto suma los 365 días exactos

                        # Opcional: Si quieres registrar esto en TransaccionPago, 
                        # asegúrate de que tu modelo permita dejar 'evento_id' en null/blank.
                        
                    except Exception as e:
                        print(f"Error procesando webhook MP (Membresía): {e}")
                        
        return HttpResponse(status=200) 
    return HttpResponse(status=405)






def obtener_categoria_con_ia(nombre_empresa, descripcion):
    """
    Usa Gemini para analizar la empresa y asignar una categoría general.
    """
    try:
        # Asegúrate de tener tu API KEY en settings.py
        genai.configure(api_key=settings.OPENAI_API_KEY) # O GEMINI_API_KEY según como lo llames
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Actúa como un clasificador de industrias para una red de networking. 
        Lee la siguiente empresa y descríbela en UNA sola categoría general (máximo 2 palabras).
        Ejemplos de salida: Tecnología, Salud, Gastronomía, Educación, Logística, Marketing.
        
        Empresa: {nombre_empresa}
        Descripción: {descripcion}
        
        Categoría:"""
        
        respuesta = model.generate_content(prompt)
        return respuesta.text.strip().title()
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return "General" # Categoría por defecto si falla la IA 



@login_required
def guardar_empresa_trabajo(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        nombre_empresa = request.POST.get('nombre_empresa')
        url = request.POST.get('url')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        whatsapp = request.POST.get('whatsapp')
        descripcion_breve = request.POST.get('descripcion_breve')

        # 1. Llamamos a Gemini para que nos dé la categoría mágicamente
        categoria_ia = obtener_categoria_con_ia(nombre_empresa, descripcion_breve)

        # 2. Guardamos en la base de datos
        TrabajoEmpresa.objects.create(
            usuario=request.user,
            tipo=tipo,
            nombre_empresa=nombre_empresa,
            url=url,
            email=email,
            telefono=telefono,
            whatsapp=whatsapp,
            descripcion_breve=descripcion_breve,
            categoria_ia=categoria_ia
        )
        
        messages.success(request, f'¡Registro agregado con éxito bajo la categoría "{categoria_ia}"!')
        
    # Cambia 'subir_cv' por el name de la URL donde se muestra el perfil del usuario
    return redirect('mi_perfil') 

@login_required
def eliminar_empresa_trabajo(request, id):
    if request.method == 'POST':
        # Nos aseguramos de que solo el dueño pueda borrar su propia empresa
        trabajo = get_object_or_404(TrabajoEmpresa, id=id, usuario=request.user)
        trabajo.delete()
        messages.success(request, 'Registro eliminado correctamente.')
        
    return redirect('mi_perfil')



@login_required
def guardar_preferencias_usuario(request):
    if request.method == 'POST':
        from user.models import Preferencia
        
        # Capturamos todos los IDs de los checkboxes que el usuario marcó
        preferencias_ids = request.POST.getlist('preferencias_seleccionadas')
        
        # Limpiamos las preferencias anteriores
        request.user.preferencias.clear()
        
        if preferencias_ids:
            # SEGURIDAD CRÍTICA: Verificamos que las IDs enviadas pertenezcan a la universidad del alumno
            if request.user.carrera:
                mi_univ = request.user.carrera.departamento.facultad.universidad
                # Filtramos las IDs válidas
                preferencias_validas = Preferencia.objects.filter(id__in=preferencias_ids, universidad=mi_univ).values_list('id', flat=True)
                
                # Guardamos solo las que pasaron el filtro de seguridad
                request.user.preferencias.add(*preferencias_validas)

        messages.success(request, 'Tus preferencias han sido guardadas y actualizadas correctamente.')
        
    return redirect('mi_perfil')


@login_required
def guardar_bancos_usuario(request):
    if request.method == 'POST':
        from user.models import DescuentoBanco
        
        # Capturamos todos los IDs de los checkboxes que el usuario marcó
        bancos_ids = request.POST.getlist('bancos_seleccionados')
        
        # Limpiamos los bancos seleccionados anteriormente
        request.user.descuentos.clear()
        
        if bancos_ids:
            # SEGURIDAD CRÍTICA: Verificamos que los bancos enviados pertenezcan a la universidad del alumno
            if request.user.carrera:
                mi_univ = request.user.carrera.departamento.facultad.universidad
                # Filtramos las IDs válidas para evitar inyecciones de código
                bancos_validos = DescuentoBanco.objects.filter(id__in=bancos_ids, universidad=mi_univ).values_list('id', flat=True)
                
                # Guardamos solo los que pasaron el filtro de seguridad
                request.user.descuentos.add(*bancos_validos)

        messages.success(request, 'Tus bancos han sido guardados y actualizados correctamente.')
        
    return redirect('mi_perfil')


@login_required
def mi_membresia(request):
    from user.models import PlanMembresia, SuscripcionUsuario
    
    # Obtenemos la suscripción del usuario
    suscripcion, created = SuscripcionUsuario.objects.get_or_create(usuario=request.user)
    
    # --- LA MAGIA: CAPTURAR EL RETORNO DE MERCADOPAGO EN TIEMPO REAL ---
    estado_pago = request.GET.get('status')
    referencia = request.GET.get('external_reference', '')
    
    # Si la URL dice que fue aprobado y es un pago de membresía...
    if estado_pago == 'approved' and referencia.startswith('mem_'):
        # Activamos la membresía inmediatamente
        suscripcion.renovar_por_un_ano()
        messages.success(request, "¡Pago exitoso! Tu membresía ha sido activada.")
        
        # Redirigimos a la misma página para limpiar la URL (quitar el ?status=...)
        return redirect('mi_membresia')
    # -------------------------------------------------------------------
    
    # Obtenemos el plan de su universidad
    plan = None
    if request.user.carrera:
        mi_univ = request.user.carrera.departamento.facultad.universidad
        plan = PlanMembresia.objects.filter(universidad=mi_univ).first()

    return render(request, 'mi_perfil/mi_membresia.html', {
        'suscripcion': suscripcion,
        'plan': plan
    })





@login_required
def iniciar_pago_membresia(request, plan_id):
    from user.models import PlanMembresia
    plan = get_object_or_404(PlanMembresia, id=plan_id)
    
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    preference_data = {
        "items": [
            {
                "title": f"Membresía Anual - {plan.universidad.nombre}",
                "quantity": 1,
                "unit_price": float(plan.valor_anual),
            }
        ],
        "payer": {
            "email": request.user.email,
        },
        "back_urls": {
            "success": request.build_absolute_uri(reverse('mi_membresia')),
            "failure": request.build_absolute_uri(reverse('mi_membresia')),
            "pending": request.build_absolute_uri(reverse('mi_membresia'))
        },
        "auto_return": "approved",
        # LA MAGIA ESTÁ AQUÍ: Le decimos a MP que esto es una membresía (mem_)
        "external_reference": f"mem_{plan.id}_usr_{request.user.id}" 
    }
    
    preference_response = sdk.preference().create(preference_data)
    init_point = preference_response.get("response", {}).get("init_point")
    if not init_point:
        messages.error(request, "No se pudo iniciar el pago. Contacta al administrador.")
        return redirect('mi_membresia')
