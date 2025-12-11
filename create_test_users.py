# create_test_users.py
import os
import django
import random
from datetime import datetime, timedelta

# Configuración de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citas_medicas.settings')
django.setup()

# Importaciones normales
from django.contrib.auth.models import User
from autenticacion.models import PerfilUsuario
from pacientes.models import Paciente
from medicos.models import Medico, Especialidad
from citas.models import Cita

# --- 🛠️ FIX DE INGENIERÍA: CONTROL DE SEÑALES ---
# Importamos la señal y el receptor para desconectarlos temporalmente
from django.db.models.signals import post_delete, pre_delete
# Intentamos importar la función específica que causa el error
try:
    from pacientes.models import eliminar_usuario_paciente
    print("🔧 Desconectando señal conflictiva 'eliminar_usuario_paciente' para limpieza segura...")
    # Desconectamos la señal del modelo Paciente para evitar el bucle infinito
    post_delete.disconnect(eliminar_usuario_paciente, sender=Paciente)
    pre_delete.disconnect(eliminar_usuario_paciente, sender=Paciente)
except ImportError:
    print("⚠️ No se pudo importar la señal específica, continuando con riesgo de recursión...")
except Exception as e:
    print(f"ℹ️ Nota sobre señales: {e}")
# ------------------------------------------------

# Limpiar datos existentes
print("🧹 Limpiando datos existentes...")
try:
    # Orden de borrado seguro: Hijos primero, Padres después
    Cita.objects.all().delete()
    Medico.objects.all().delete()
    Paciente.objects.all().delete()
    Especialidad.objects.all().delete()
    User.objects.all().delete()
    print("✅ Datos eliminados correctamente.")
except Exception as e:
    print(f"❌ Error durante la limpieza (puede ser ignorado si la base estaba vacía): {e}")

# 1. Crear superuser admin
print("👑 Creando superuser admin...")
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@clinica.com',
        password='admin123'
    )
    admin_user.first_name = 'Administrador'
    admin_user.last_name = 'Sistema'
    admin_user.save()

    # Asegurar perfil admin
    perfil_admin, _ = PerfilUsuario.objects.get_or_create(user=admin_user)
    perfil_admin.tipo_usuario = 'admin'
    perfil_admin.save()
else:
    print("   El admin ya existe, omitiendo...")

# 2. Crear especialidades
print("🏥 Creando especialidades...")
especialidades = [
    ('Cardiología', 'Especialidad del corazón'),
    ('Pediatría', 'Especialidad para niños'),
    ('Dermatología', 'Especialidad de la piel'),
    ('Ginecología', 'Especialidad femenina'),
    ('Traumatología', 'Especialidad de huesos'),
]

for nombre, descripcion in especialidades:
    Especialidad.objects.get_or_create(nombre=nombre, defaults={'descripcion': descripcion})

# 3. Crear médicos
print("👨‍⚕️ Creando médicos...")
medicos_data = [
    {
        'username': 'dr.perez', 'password': 'doctor123',
        'first_name': 'Juan', 'last_name': 'Pérez',
        'especialidad': 'Cardiología', 'telefono': '88888888',
        'horario_inicio': '08:00:00', 'horario_fin': '16:00:00'
    },
    {
        'username': 'dra.garcia', 'password': 'doctor123',
        'first_name': 'María', 'last_name': 'García',
        'especialidad': 'Pediatría', 'telefono': '77777777',
        'horario_inicio': '09:00:00', 'horario_fin': '17:00:00'
    },
    {
        'username': 'dr.rodriguez', 'password': 'doctor123',
        'first_name': 'Carlos', 'last_name': 'Rodríguez',
        'especialidad': 'Dermatología', 'telefono': '66666666',
        'horario_inicio': '10:00:00', 'horario_fin': '18:00:00'
    },
]

medicos_objetos = []
for medico_data in medicos_data:
    if not User.objects.filter(username=medico_data['username']).exists():
        user = User.objects.create_user(
            username=medico_data['username'],
            email=f"{medico_data['username']}@clinica.com",
            password=medico_data['password'],
            first_name=medico_data['first_name'],
            last_name=medico_data['last_name']
        )
        
        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        perfil.tipo_usuario = 'medico'
        perfil.save()
        
        especialidad = Especialidad.objects.get(nombre=medico_data['especialidad'])
        medico_obj = Medico.objects.create(
            user=user,
            especialidad=especialidad,
            telefono=medico_data['telefono'],
            horario_inicio=medico_data['horario_inicio'],
            horario_fin=medico_data['horario_fin']
        )
        medicos_objetos.append(medico_obj)
    else:
        # Recuperar el médico si ya existe para usarlo en las citas
        user = User.objects.get(username=medico_data['username'])
        try:
            medicos_objetos.append(user.medico)
        except:
            pass # Si el usuario existe pero no es médico (raro en test)

# 4. Crear pacientes
print("👤 Creando pacientes...")
pacientes_data = [
    {
        'username': 'ana.martinez', 'password': 'paciente123',
        'first_name': 'Ana', 'last_name': 'Martínez',
        'dni': '001-010101-1000A', 'telefono': '55555555',
        'direccion': 'Managua, Nicaragua', 'fecha_nacimiento': '1990-01-01'
    },
    {
        'username': 'jose.lopez', 'password': 'paciente123',
        'first_name': 'José', 'last_name': 'López',
        'dni': '002-020202-2000B', 'telefono': '44444444',
        'direccion': 'León, Nicaragua', 'fecha_nacimiento': '1985-05-15'
    },
    {
        'username': 'maria.gonzalez', 'password': 'paciente123',
        'first_name': 'María', 'last_name': 'González',
        'dni': '003-030303-3000C', 'telefono': '33333333',
        'direccion': 'Granada, Nicaragua', 'fecha_nacimiento': '1995-08-20'
    },
]

pacientes_objetos = []
for paciente_data in pacientes_data:
    if not User.objects.filter(username=paciente_data['username']).exists():
        user = User.objects.create_user(
            username=paciente_data['username'],
            email=f"{paciente_data['username']}@clinica.com",
            password=paciente_data['password'],
            first_name=paciente_data['first_name'],
            last_name=paciente_data['last_name']
        )
        
        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        perfil.tipo_usuario = 'paciente'
        perfil.save()
        
        paciente_obj = Paciente.objects.create(
            user=user,
            dni=paciente_data['dni'],
            telefono=paciente_data['telefono'],
            direccion=paciente_data['direccion'],
            fecha_nacimiento=paciente_data['fecha_nacimiento']
        )
        pacientes_objetos.append(paciente_obj)
    else:
         user = User.objects.get(username=paciente_data['username'])
         try:
            pacientes_objetos.append(user.paciente)
         except:
            pass

# 5. Crear citas
print("📅 Creando citas...")

# Recargamos las listas desde la DB para asegurar que tenemos todos
todos_pacientes = list(Paciente.objects.all())
todos_medicos = list(Medico.objects.all())

if len(todos_pacientes) > 0 and len(todos_medicos) > 0:
    # Motivos de consulta
    motivos = [
        "Consulta general", "Seguimiento", "Chequeo anual",
        "Dolor en el pecho", "Fiebre", "Erupción", "Control", "Dolor articular"
    ]
    
    for i in range(20):
        paciente = random.choice(todos_pacientes)
        medico = random.choice(todos_medicos)
        
        # Lógica de estados
        if i < 5: estado = 'pendiente'
        elif i < 10: estado = 'confirmada'
        elif i < 15: estado = 'finalizada'
        else: estado = 'cancelada'
        
        # Lógica de fechas
        days_offset = random.randint(1, 30)
        if estado in ['finalizada', 'cancelada']:
            fecha_cita = datetime.now() - timedelta(days=days_offset)
        else:
            fecha_cita = datetime.now() + timedelta(days=days_offset)
            
        hora_cita = f"{random.randint(8, 17):02d}:{random.choice(['00', '30'])}"
        
        Cita.objects.create(
            paciente=paciente,
            medico=medico,
            fecha=fecha_cita.date(),
            hora=hora_cita,
            motivo=random.choice(motivos),
            estado=estado
        )
        print(f"  📝 Cita #{i+1} creada ({estado})")

print("\n" + "="*50)
print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
print("="*50)