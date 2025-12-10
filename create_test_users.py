# create_test_users.py
import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citas_medicas.settings')
django.setup()

from django.contrib.auth.models import User
from autenticacion.models import PerfilUsuario
from pacientes.models import Paciente
from medicos.models import Medico, Especialidad
from citas.models import Cita

# Limpiar datos existentes
print("🧹 Limpiando datos existentes...")
User.objects.all().delete()
Paciente.objects.all().delete()
Medico.objects.all().delete()
Especialidad.objects.all().delete()
Cita.objects.all().delete()

# 1. Crear superuser admin
print("👑 Creando superuser admin...")
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
    Especialidad.objects.create(nombre=nombre, descripcion=descripcion)

# 3. Crear médicos
print("👨‍⚕️ Creando médicos...")
medicos_data = [
    {
        'username': 'dr.perez',
        'password': 'doctor123',
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'especialidad': 'Cardiología',
        'telefono': '88888888',
        'horario_inicio': '08:00:00',
        'horario_fin': '16:00:00'
    },
    {
        'username': 'dra.garcia',
        'password': 'doctor123',
        'first_name': 'María',
        'last_name': 'García',
        'especialidad': 'Pediatría',
        'telefono': '77777777',
        'horario_inicio': '09:00:00',
        'horario_fin': '17:00:00'
    },
    {
        'username': 'dr.rodriguez',
        'password': 'doctor123',
        'first_name': 'Carlos',
        'last_name': 'Rodríguez',
        'especialidad': 'Dermatología',
        'telefono': '66666666',
        'horario_inicio': '10:00:00',
        'horario_fin': '18:00:00'
    },
]

medicos_objetos = []
for medico_data in medicos_data:
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

# 4. Crear pacientes
print("👤 Creando pacientes...")
pacientes_data = [
    {
        'username': 'ana.martinez',
        'password': 'paciente123',
        'first_name': 'Ana',
        'last_name': 'Martínez',
        'dni': '001-010101-1000A',
        'telefono': '55555555',
        'direccion': 'Managua, Nicaragua',
        'fecha_nacimiento': '1990-01-01'
    },
    {
        'username': 'jose.lopez',
        'password': 'paciente123',
        'first_name': 'José',
        'last_name': 'López',
        'dni': '002-020202-2000B',
        'telefono': '44444444',
        'direccion': 'León, Nicaragua',
        'fecha_nacimiento': '1985-05-15'
    },
    {
        'username': 'maria.gonzalez',
        'password': 'paciente123',
        'first_name': 'María',
        'last_name': 'González',
        'dni': '003-030303-3000C',
        'telefono': '33333333',
        'direccion': 'Granada, Nicaragua',
        'fecha_nacimiento': '1995-08-20'
    },
]

pacientes_objetos = []
for paciente_data in pacientes_data:
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

# 5. Crear citas con diferentes estados
print("📅 Creando citas con diferentes estados...")

# Obtener todos los pacientes y médicos
todos_pacientes = Paciente.objects.all()
todos_medicos = Medico.objects.all()

if len(todos_pacientes) > 0 and len(todos_medicos) > 0:
    # Estados posibles para las citas
    estados = ['pendiente', 'confirmada', 'cancelada', 'finalizada']
    
    # Motivos de consulta
    motivos = [
        "Consulta general",
        "Seguimiento de tratamiento",
        "Chequeo anual",
        "Dolor en el pecho",
        "Fiebre persistente",
        "Erupción cutánea",
        "Control prenatal",
        "Dolor articular"
    ]
    
    # Crear citas con diferentes estados y fechas
    for i in range(20):  # Crear 20 citas de ejemplo
        paciente = random.choice(todos_pacientes)
        medico = random.choice(todos_medicos)
        
        # Asignar un estado de forma controlada
        if i < 5:
            estado = 'pendiente'
        elif i < 10:
            estado = 'confirmada'
        elif i < 15:
            estado = 'finalizada'
        else:
            estado = 'cancelada'
        
        # Crear fecha de la cita (algunas en pasado, otras en futuro)
        if estado in ['finalizada', 'cancelada']:
            # Citas pasadas (ya ocurrieron)
            fecha_cita = datetime.now() - timedelta(days=random.randint(1, 30))
        else:
            # Citas futuras (por ocurrir)
            fecha_cita = datetime.now() + timedelta(days=random.randint(1, 30))
        
        # Generar hora aleatoria dentro del horario laboral (entre 8 AM y 6 PM)
        hora_cita = f"{random.randint(8, 17):02d}:{random.choice(['00', '30'])}"
        
        # Crear la cita
        cita = Cita.objects.create(
            paciente=paciente,
            medico=medico,
            fecha=fecha_cita.date(),
            hora=hora_cita,
            motivo=random.choice(motivos),
            estado=estado
        )
        
        print(f"  📝 Cita #{i+1} creada: {paciente.user.get_full_name()} con Dr. {medico.user.last_name} - {fecha_cita.date()} {hora_cita} - Estado: {estado}")

print("\n" + "="*50)
print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
print("="*50)
print("\n🔑 CREDENCIALES DE ACCESO:")
print("-" * 30)
print("👑 ADMINISTRADOR:")
print("  Usuario: admin")
print("  Contraseña: admin123")
print("\n👨‍⚕️ MÉDICOS:")
print("  Usuario: dr.perez")
print("  Usuario: dra.garcia")
print("  Usuario: dr.rodriguez")
print("  Contraseña: doctor123 (para todos)")
print("\n👤 PACIENTES:")
print("  Usuario: ana.martinez")
print("  Usuario: jose.lopez")
print("  Usuario: maria.gonzalez")
print("  Contraseña: paciente123 (para todos)")
print("\n📅 Citas creadas:")
print("  • 5 citas PENDIENTES (futuras)")
print("  • 5 citas CONFIRMADAS (futuras)")
print("  • 5 citas FINALIZADAS (pasadas)")
print("  • 5 citas CANCELADAS (pasadas)")
print("\n🏥 URL: http://localhost:8000/")
print("="*50)