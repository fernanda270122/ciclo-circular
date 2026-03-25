from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializers
from rest_framework import status
from django.http import Http404, HttpResponse, JsonResponse
from user.models import Usuario
from app.models import RegistroActividad, Evento, PreguntaEvento, Oferta
import json
import os
from django.db.models import F 
import google.generativeai as genai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .serializers import OfertaSerializer
from rest_framework.decorators import api_view

try:
    API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", "")).strip()
    if API_KEY:
        genai.configure(api_key=API_KEY)
except:
    pass
# Create your views here.

def home_api(request):
    data = {}
    if request.user.is_authenticated:
        # CAMBIO: Usamos RegistroActividad
        registros = RegistroActividad.objects.filter(usuario=request.user)
        data = {
            'registros': registros
        }
        
    return render(request, 'home_api.html', data)


class User_APIView(APIView):
    def get(self, request, format=None, *args, **kwarqs):
        usuario = Usuario.objects.filter(is_staff=False)
        serializer = UserSerializers(usuario, many=True)
        return Response(serializer.data)


class Ubicacion_APIView(APIView):
    def get(self, request, format=None, *args, **kwarqs):
        
        # Creo un diccionario vacio
        datos = {}
        
        # Creo un conjunto de datos llamada ubicacion
        datos['ubicacion'] = []

        # --- DATOS ACTUALIZADOS A LA TERMINOLOGÍA UNIVERSITARIA ---
        
        ubicacion1 = {
            "type": "Feature", 
            "geometry": {"type": "Point", "coordinates": [289.3263383, -33.4409602]}, 
            "properties": {
                "UNIVERSIDAD": "Universidad Central", # Antes EMPRESA
                "CARRERA": "Casa Central",            # Antes AREA
                "Direccion": "Calle 1 Oficina 1", 
                "COMUNA": "Santiago Centro"
            }
        }

        ubicacion2 = {
            "type": "Feature", 
            "geometry": {"type": "Point", "coordinates": [289.1893511, -33.3549203]}, 
            "properties": {
                "UNIVERSIDAD": "Universidad Central", 
                "CARRERA": "Facultad Ingeniería", 
                "Direccion": "Calle 2 Oficina 2", 
                "COMUNA": "Quilicura"
            }
        }

        ubicacion3 = {
            "type": "Feature", 
            "geometry": {"type": "Point", "coordinates": [289.2523086, -33.5022488]}, 
            "properties": {
                "UNIVERSIDAD": "Universidad Central", 
                "CARRERA": "Campus Deportivo", 
                "Direccion": "Calle 3 Oficina 3", 
                "COMUNA": "Cerrillos"
            }
        }

        # Agrego los elementos
        datos['ubicacion'].append(ubicacion1)
        datos['ubicacion'].append(ubicacion2)
        datos['ubicacion'].append(ubicacion3)

        # Ruta segura para guardar el JSON (asegura que la carpeta exista)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, 'api', 'ubicacion', 'ubicacion_json.json')
        
        # Asegurarnos de que el directorio existe
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        # Escribir los datos en un json
        with open(json_path, 'w') as f:
            json.dump(datos, f)
      
        # Lectura de datos del archivo json
        with open(json_path, 'r') as j:
            mydata = json.load(j)
    
        return Response(mydata)
    


@csrf_exempt
def enviar_pregunta_api(request):
    if request.method == 'POST':
        evento_id = request.POST.get('evento_id')
        tipo = request.POST.get('tipo')
        texto = request.POST.get('texto')

        if evento_id and texto:
            evento = get_object_or_404(Evento, pk=evento_id)
            
            # 1. Creamos el registro de la pregunta
            PreguntaEvento.objects.create(
                evento=evento,
                tipo=tipo,
                texto=texto
            )
            
            # 2. ¡LA MAGIA AQUÍ! Actualizamos el contador real en la base de datos
            if tipo == 'expositor':
                Evento.objects.filter(pk=evento.pk).update(contador_preguntas=F('contador_preguntas') + 1)
            elif tipo == 'publico':
                Evento.objects.filter(pk=evento.pk).update(contador_aportes=F('contador_aportes') + 1)

            # 3. Si es pregunta al expositor, generar respuesta automática con IA
            if tipo == 'expositor':
                import threading
                def generar_respuesta_ia(evento_id, pregunta_texto):
                    try:
                        print(f"🤖 Iniciando respuesta IA para evento {evento_id}")
                        evento_obj = Evento.objects.get(pk=evento_id)
                        
                        preguntas_anteriores = PreguntaEvento.objects.filter(
                            evento=evento_obj,
                            tipo='expositor'
                        ).exclude(texto=pregunta_texto).values_list('texto', flat=True)[:5]
                        
                        contexto_evento = f"""
                        Evento: {evento_obj.titulo}
                        Descripción: {evento_obj.descripcion or 'Sin descripción'}
                        Pregunta del coordinador: {evento_obj.pregunta_del_coordinador or ''}
                        """
                        
                        preguntas_ctx = "\n".join(preguntas_anteriores) if preguntas_anteriores else "No hay preguntas anteriores"
                        
                        prompt = f"""
                        Eres el expositor de un evento académico. Responde la siguiente pregunta de forma breve, clara y profesional (máximo 2 oraciones).
                        
                        Contexto del evento:
                        {contexto_evento}
                        
                        Preguntas similares de otros asistentes:
                        {preguntas_ctx}
                        
                        Pregunta a responder: {pregunta_texto}
                        
                        Si la pregunta es similar a las anteriores, da una respuesta genérica que aplique a todos.
                        Responde solo con el texto de la respuesta, sin saludos ni firmas.
                        """
                        
                        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or getattr(settings, 'GEMINI_API_KEY', None)
                        if not api_key:
                            print("⚠️ No hay API key de Gemini")
                            return
                        
                        genai.configure(api_key=api_key)
                        modelos = []
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                modelos.append(m.name)
                        
                        modelo = next((m for m in modelos if 'flash' in m), modelos[0] if modelos else None)
                        if not modelo:
                            print("⚠️ No hay modelos disponibles")
                            return
                        
                        model = genai.GenerativeModel(modelo)
                        response = model.generate_content(prompt)
                        respuesta_texto = response.text.strip()
                        
                        if respuesta_texto:
                            PreguntaEvento.objects.create(
                                evento=evento_obj,
                                tipo='publico',
                                texto=f"🤖 {respuesta_texto}"
                            )
                            Evento.objects.filter(pk=evento_id).update(contador_aportes=F('contador_aportes') + 1)
                            print(f"✅ Respuesta IA guardada para evento {evento_id}")
                            
                    except Exception as e:
                        print(f"⚠️ Error IA respuesta automática: {e}")
                
                threading.Thread(target=generar_respuesta_ia, args=(evento_id, texto)).start()

            return HttpResponse('<div class="text-emerald-500 text-xs font-bold mt-2 text-center fade-out">¡Enviado con éxito!</div>')
    
    return HttpResponse('Error', status=400)



def obtener_top_preguntas_api(request, evento_id):
    # 1. Obtener todas las preguntas del evento
    preguntas_expositor = list(PreguntaEvento.objects.filter(evento_id=evento_id, tipo='expositor').values_list('texto', flat=True))
    respuestas_publico = list(PreguntaEvento.objects.filter(evento_id=evento_id, tipo='publico').values_list('texto', flat=True))

    # --- LÓGICA DE SELECCIÓN ---
    
    # A) Si hay pocas preguntas (menos de 5), las mostramos todas sin gastar IA
    top_expositor = preguntas_expositor
    top_publico = respuestas_publico

    # B) Si hay MUCHAS, usamos Gemini para filtrar
    if len(preguntas_expositor) > 5 or len(respuestas_publico) > 5:
        try:
            # --- SELECCIÓN DE MODELO DINÁMICA ---
            genai.configure(api_key=settings.GOOGLE_API_KEY) # Aseguramos la conexión
            
            mis_modelos = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        mis_modelos.append(m.name)
            except Exception as e:
                print(f"⚠️ Error listando modelos (usando default): {e}")
                mis_modelos = ['models/gemini-1.5-flash', 'models/gemini-pro']
            
            if not mis_modelos:
                mis_modelos = ['models/gemini-1.5-flash', 'models/gemini-pro']

            # Priorizamos 'flash', si no, el primero disponible
            modelo_final = next((m for m in mis_modelos if 'flash' in m), mis_modelos[0])
            print(f"🚀 [Eventos] Usando modelo para top preguntas: {modelo_final}")
            
            # Inicializamos el modelo detectado
            model = genai.GenerativeModel(modelo_final)
            # ------------------------------------
            
            prompt = f"""
            Actúa como un moderador de eventos experto. Tengo dos listas de textos recibidos en un evento.
            
            Lista A (Preguntas al expositor): {json.dumps(preguntas_expositor)}
            Lista B (Respuestas/Aportes del público): {json.dumps(respuestas_publico)}

            Tu tarea:
            1. Analiza la profundidad, relevancia y calidad de redacción.
            2. Selecciona las 5 MEJORES de la Lista A.
            3. Selecciona las 5 MEJORES de la Lista B.
            
            Responde SOLO con un objeto JSON válido con este formato exacto, sin markdown:
            {{
                "top_expositor": ["texto 1", "texto 2"],
                "top_publico": ["texto 1", "texto 2"]
            }}
            """
            
            response = model.generate_content(prompt)
            texto_limpio = response.text.replace('```json', '').replace('```', '')
            data = json.loads(texto_limpio)
            
            # Actualizamos las listas con la selección de la IA
            if 'top_expositor' in data:
                top_expositor = data['top_expositor']
            if 'top_publico' in data:
                top_publico = data['top_publico']

        except Exception as e:
            print(f"Error Gemini: {e}")
            # Si falla la IA, mostramos las últimas 5 por defecto (fallback)
            top_expositor = preguntas_expositor[-5:]
            top_publico = respuestas_publico[-5:]

    # Renderizamos el HTML parcial para HTMX
    # Creamos un template string simple aquí para no crear otro archivo, 
    # o puedes crear 'api/partials/preguntas_list.html'
    
    html_response = """
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-white/5 p-4 rounded-xl border border-emerald-100 dark:border-emerald-500/20">
            <h5 class="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase mb-3 flex items-center gap-2">
                <i class="fa-solid fa-star"></i> Top Preguntas al Expositor
            </h5>
            <ul class="space-y-2">
    """
    
    if not top_expositor:
        html_response += '<li class="text-xs text-slate-400 italic">Esperando preguntas...</li>'
    
    for p in top_expositor:
        html_response += f'<li class="p-2 bg-slate-50 dark:bg-slate-800 rounded text-sm text-slate-700 dark:text-slate-300 border-l-2 border-emerald-500">{p}</li>'

    html_response += """
            </ul>
        </div>

        <div class="bg-white dark:bg-white/5 p-4 rounded-xl border border-blue-100 dark:border-blue-500/20">
            <h5 class="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase mb-3 flex items-center gap-2">
                <i class="fa-solid fa-users"></i> Top Aportes del Público
            </h5>
            <ul class="space-y-2">
    """

    if not top_publico:
        html_response += '<li class="text-xs text-slate-400 italic">Esperando aportes...</li>'

    for p in top_publico:
        html_response += f'<li class="p-2 bg-slate-50 dark:bg-slate-800 rounded text-sm text-slate-700 dark:text-slate-300 border-l-2 border-blue-500">{p}</li>'

    html_response += """
            </ul>
        </div>
    </div>
    """

    return HttpResponse(html_response)

@api_view(['GET', 'POST'])
def ofertas_list(request):

    # 🔹 LISTAR
    if request.method == 'GET':
        ofertas = Oferta.objects.all()
        serializer = OfertaSerializer(ofertas, many=True)
        return Response(serializer.data)

    # 🔹 CREAR
    elif request.method == 'POST':
        serializer = OfertaSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(creado_por=request.user)  # 👈 AQUÍ VA TU LÍNEA
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def oferta_detail(request, pk):

    try:
        oferta = Oferta.objects.get(pk=pk)
    except Oferta.DoesNotExist:
        return Response({'error': 'No existe'}, status=404)

    # 🔹 VER
    if request.method == 'GET':
        serializer = OfertaSerializer(oferta)
        return Response(serializer.data)

    # 🔹 EDITAR
    elif request.method == 'PUT':
        serializer = OfertaSerializer(oferta, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # 🔹 ELIMINAR
    elif request.method == 'DELETE':
        oferta.delete()
        return Response({'mensaje': 'Eliminado'})
    
@api_view(['GET'])
def networking_ver_oferta(request, pk):
    try:
        oferta = Oferta.objects.get(pk=pk)
    except Oferta.DoesNotExist:
        return Response({'error': 'No existe'}, status=404)

    serializer = OfertaSerializer(oferta)
    return Response(serializer.data)

@api_view(['GET'])
def networking_ofertas_list(request):
    ofertas = Oferta.objects.all()
    serializer = OfertaSerializer(ofertas, many=True)
    return Response(serializer.data)

