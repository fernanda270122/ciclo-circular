from django.db import models
from user.models import Usuario

# --- ESTRUCTURA PRINCIPAL (JERARQUÍA ACADÉMICA) ---

class Universidad(models.Model):
    # Antes: Empresa
    id_universidad = models.AutoField(primary_key=True)
    nombre  = models.CharField(max_length=50) 
    calle = models.CharField(max_length=250)
    comuna = models.CharField(max_length=150) 
    lat = models.IntegerField()
    long = models.IntegerField()

    def __str__(self):
        return self.nombre

class Facultad(models.Model):
    # NUEVO MODELO
    nombre = models.CharField(max_length=100)
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE, related_name='facultades')

    def __str__(self):
        return f"{self.nombre} - {self.universidad.nombre}"

class Departamento(models.Model):
    # NUEVO MODELO
    nombre = models.CharField(max_length=100)
    facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE, related_name='departamentos')

    def __str__(self):
        return f"{self.nombre} - {self.facultad.nombre}"

class Carrera(models.Model):
    # Antes: AreaEmpresa
    id_carrera = models.AutoField(primary_key=True)
    nombre  = models.CharField(max_length=100)   
    
    # CAMBIO CRÍTICO: Ahora depende de Departamento, no de la raíz
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='carreras')
    
    # Mantengo ubicación por si la carrera tiene una sede específica
    calle = models.CharField(max_length=250, blank=True, null=True)
    comuna = models.CharField(max_length=150, blank=True, null=True)
    lat = models.IntegerField(default=0)
    long = models.IntegerField(default=0)  

    def __str__(self):
        return self.nombre    


# --- GESTIÓN DE TIEMPO Y PROCESOS ---

class Etapa(models.Model):
    # Se mantiene igual (ej: Semestre 1, Trimestre 2)
    id_etapa = models.AutoField(primary_key=True)
    nombre  = models.CharField(max_length=50)
    fecha_inicio  = models.DateField() 
    fecha_termino  = models.DateField()
    activo = models.BooleanField()

    def __str__(self):
        return self.nombre    


# --- REGISTROS Y ACTIVIDAD ---

class RegistroActividad(models.Model):
    # Antes: RegistroTrabajador
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    descripcion = models.TextField(max_length=160)                
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE) 

    def __str__(self):
        return f"{self.usuario} - {self.carrera}" 

class Entrada(models.Model):
    id_entrada = models.AutoField(primary_key=True)
    nombre  = models.CharField(max_length=50) 
    fecha =  models.DateField(auto_now_add=True)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE) 

    def __str__(self):
        return self.nombre

class Salida(models.Model):
    id_salida = models.AutoField(primary_key=True)
    nombre  = models.CharField(max_length=50) 
    fecha =  models.DateField(auto_now_add=True)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE) 

    def __str__(self):
        return self.nombre

class Oportunidades(models.Model):
    id_oportunidad = models.AutoField(primary_key=True) 
    nombre  = models.CharField(max_length=50) 
    fecha =  models.DateField(auto_now_add=True)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE) 

    def __str__(self):
        return self.nombre


class Idea(models.Model):
    id_idea = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE) 
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Idea de {self.usuario} en {self.universidad.nombre}"


# --- RECLUTAMIENTO / BOLSA DE TRABAJO ---

class CVUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    archivo = models.BinaryField()
    nombre_archivo = models.CharField(max_length=255)
    
    # Palabras clave
    palabra1 = models.CharField(max_length=200, null=True, blank=True)
    palabra2 = models.CharField(max_length=200, null=True, blank=True)
    palabra3 = models.CharField(max_length=200, null=True, blank=True)
    palabra4 = models.CharField(max_length=200, null=True, blank=True)
    palabra5 = models.CharField(max_length=200, null=True, blank=True)
    palabra6 = models.CharField(max_length=200, null=True, blank=True)
    palabra7 = models.CharField(max_length=200, null=True, blank=True)
    palabra8 = models.CharField(max_length=200, null=True, blank=True)
    palabra9 = models.CharField(max_length=200, null=True, blank=True)
    palabra10 = models.CharField(max_length=200, null=True, blank=True)

    linkedin_url = models.URLField(max_length=500, null=True, blank=True)
    linkedin_qr = models.BinaryField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CV de {self.usuario.username}"

class Oferta(models.Model):
    MODALIDAD_CHOICES = [
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('hibrido', 'Híbrido'),
    ]
    JORNADA_CHOICES = [
        ('completa', 'Jornada Completa'),
        ('parcial', 'Jornada Parcial'),
        ('practica', 'Práctica'),
    ]

    id_oferta = models.AutoField(primary_key=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ofertas_creadas')
    
    titulo = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200)
    descripcion = models.TextField()
    requisitos = models.TextField(blank=True, null=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='presencial')
    jornada = models.CharField(max_length=20, choices=JORNADA_CHOICES, default='completa')
    salario = models.CharField(max_length=100, blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    # Palabras clave para matching con CV
    palabra1 = models.CharField(max_length=200, null=True, blank=True)
    palabra2 = models.CharField(max_length=200, null=True, blank=True)
    palabra3 = models.CharField(max_length=200, null=True, blank=True)
    palabra4 = models.CharField(max_length=200, null=True, blank=True)
    palabra5 = models.CharField(max_length=200, null=True, blank=True)

    # Filtros por institución (opcional)
    universidad = models.ForeignKey(Universidad, on_delete=models.SET_NULL, null=True, blank=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.empresa}"

class Necesidad(models.Model):
    id_necesidad = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto_necesita = models.TextField()
    
    # Palabras clave existentes
    palabra1 = models.CharField(max_length=200, null=True, blank=True)
    palabra2 = models.CharField(max_length=200, null=True, blank=True)
    palabra3 = models.CharField(max_length=200, null=True, blank=True)
    palabra4 = models.CharField(max_length=200, null=True, blank=True)
    palabra5 = models.CharField(max_length=200, null=True, blank=True)
    # -------------------------------
    
    creado = models.DateTimeField(auto_now_add=True)

# --- EVENTOS Y CALENDARIO ---

class Evento(models.Model):
    id_evento = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200, verbose_name="Título del Evento")
    inicio = models.DateTimeField(verbose_name="Fecha de Inicio")
    fin = models.DateTimeField(verbose_name="Fecha de Fin")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    # --- JERARQUÍA ACADÉMICA ---
    
    # 1. Universidad: SIEMPRE obligatoria (Raíz)
    universidad = models.ForeignKey(
        'app.Universidad', 
        on_delete=models.CASCADE, 
        related_name='eventos'
    ) 

    # 2. Facultad: Opcional
    facultad = models.ForeignKey(
        'app.Facultad', 
        on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name='eventos_facultad'
    )

    # 3. Departamento: Opcional
    departamento = models.ForeignKey(
        'app.Departamento', 
        on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name='eventos_departamento'
    )
    
    # 4. Carrera: Opcional
    carrera = models.ForeignKey(
        'app.Carrera', 
        on_delete=models.CASCADE, 
        related_name='eventos',
        verbose_name="Carrera Organizadora",
        null=True, blank=True
    ) 
    
    # --- OTROS CAMPOS ---

    creador = models.ForeignKey(
        'user.Usuario', 
        on_delete=models.CASCADE, 
        related_name='eventos_creados'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    lugar = models.CharField(max_length=200, blank=True, null=True, verbose_name="Lugar del Evento")
    costo = models.IntegerField(default=0, verbose_name="Costo Estimado")
    
    # Campo para imagen
    imagen = models.ImageField(upload_to='eventos/', blank=True, null=True)

    # --- NUEVOS CAMPOS AÑADIDOS ---
    
    # 1. La pregunta que el coordinador configura para el público
    pregunta_del_coordinador = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        default="¿Qué opinas de este tema?",
        verbose_name="Pregunta Dinámica del Coordinador"
    )

    # 2. Contadores Persistentes (Se guardan en BD para no recalcular siempre)
    contador_preguntas = models.PositiveIntegerField(default=0, verbose_name="Total Preguntas al Expositor")
    contador_aportes = models.PositiveIntegerField(default=0, verbose_name="Total Respuestas del Público")

    # --- NUEVO CAMPO PARA AUTOMATIZACIÓN ---
    # Este campo evita que se envíen correos duplicados por el script automático
    recordatorio_24h_enviado = models.BooleanField(default=False, verbose_name="Recordatorio Auto Enviado")

    class Meta:
        verbose_name = "Evento Académico"
        verbose_name_plural = "Eventos Académicos"

    def __str__(self):
        if self.carrera:
            return f"[CARRERA] {self.titulo} ({self.carrera.nombre})"
        elif self.departamento:
            return f"[DEPTO] {self.titulo} ({self.departamento.nombre})"
        elif self.facultad:
            return f"[FACULTAD] {self.titulo} ({self.facultad.nombre})"
        else:
            return f"[UNIVERSIDAD] {self.titulo} ({self.universidad.nombre})"

class Invitacion(models.Model):
    ESTADOS = [
        ('SIN_ENVIAR', 'No Notificado'),
        ('ENVIADO', 'Esperando Confirmación'),
        ('CONFIRMADO', 'Asistencia Confirmada'),
        ('PAGADO', 'Entrada Pagada'), # <--- NUEVO ESTADO PARA MERCADO PAGO
        ('RECHAZADO', 'No Asistirá'),
        ('ENTRADA_ENVIADA', 'Invitación Formal Enviada'),
    ]

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='invitaciones')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='SIN_ENVIAR')
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('evento', 'usuario')

    def __str__(self):
        return f"{self.usuario} - {self.evento} - {self.estado}"
    


class PreguntaEvento(models.Model):
    TIPO_CHOICES = [
        ('expositor', 'Pregunta al Expositor'),
        ('publico', 'Respuesta al Público'),
    ]
    
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Campo opcional para guardar el puntaje si quisieras guardarlo después
    score_ia = models.FloatField(default=0.0) 

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.texto[:30]}..."
    

class TransaccionPago(models.Model):
    ESTADO_PAGO = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    # Guardamos el ID larguísimo que nos devuelve Mercado Pago
    id_transaccion = models.CharField(max_length=255, primary_key=True, verbose_name="ID de Transacción MP")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    monto = models.IntegerField(verbose_name="Monto Pagado")
    estado = models.CharField(max_length=50, choices=ESTADO_PAGO, default='pending', verbose_name="Estado del Pago")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Transacción de Pago"
        verbose_name_plural = "Transacciones de Pago"

    def __str__(self):
        return f"Pago {self.id_transaccion} - {self.usuario.username} - {self.estado}"    
    


class LogCorreo(models.Model):
    remitente = models.ForeignKey('user.Usuario', on_delete=models.SET_NULL, null=True)
    asunto = models.CharField(max_length=255)
    cuerpo = models.TextField()
    archivo_adjunto = models.FileField(upload_to='correos_adjuntos/', null=True, blank=True)
    filtros_aplicados = models.CharField(max_length=255)
    cantidad_destinatarios = models.IntegerField(default=0)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asunto} - {self.fecha_envio.strftime('%d/%m/%Y')}"
<<<<<<< HEAD

# SECCION DE VENTAS
=======
    
>>>>>>> desarrollo
class Producto(models.Model):
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE, related_name='productos')
    creado_por = models.ForeignKey('user.Usuario', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.universidad.nombre}"

class OrdenCompra(models.Model):
    ESTADOS = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    usuario = models.ForeignKey('user.Usuario', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    total = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pending')
    id_transaccion = models.CharField(max_length=255, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} - {self.estado}"