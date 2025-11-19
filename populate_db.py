import os
import django
from datetime import datetime, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citas_medicas.settings')
django.setup()

from django.contrib.auth.models import User
from pacientes.models import Paciente
from medicos.models import Medico, Especialidad
from citas.models import Cita

def populate_database():
    print("Iniciando población de base de datos...")
    
    # 1. Crear especialidades (usando nombre como referencia única)
    especialidades_data = [
        {'nombre': 'Medicina General', 'descripcion': 'Atención primaria y diagnóstico general'},
        {'nombre': 'Cardiología', 'descripcion': 'Especialidad en enfermedades del corazón'},
        {'nombre': 'Pediatría', 'descripcion': 'Atención médica para niños y adolescentes'},
        {'nombre': 'Dermatología', 'descripcion': 'Especialidad en enfermedades de la piel'},
        {'nombre': 'Ginecología', 'descripcion': 'Salud femenina y sistema reproductivo'},
        {'nombre': 'Ortopedia', 'descripcion': 'Especialidad en huesos y articulaciones'},
    ]
    
    especialidades_creadas = []
    for esp_data in especialidades_data:
        especialidad, created = Especialidad.objects.get_or_create(
            nombre=esp_data['nombre'],
            defaults={'descripcion': esp_data['descripcion']}
        )
        especialidades_creadas.append(especialidad)
        if created:
            print(f"Especialidad creada: {especialidad.nombre}")
        else:
            print(f"Especialidad ya existente: {especialidad.nombre}")
    
    print("---")

    # 2. Crear usuarios y médicos
    medicos_data = [
        {'username': 'dra.garcia', 'first_name': 'Ana', 'last_name': 'García', 'email': 'ana.garcia@clinica.com', 'especialidad': 'Medicina General', 'telefono': '555-1001', 'horario_inicio': '08:00:00', 'horario_fin': '16:00:00'},
        {'username': 'dr.martinez', 'first_name': 'Carlos', 'last_name': 'Martínez', 'email': 'carlos.martinez@clinica.com', 'especialidad': 'Cardiología', 'telefono': '555-1002', 'horario_inicio': '09:00:00', 'horario_fin': '17:00:00'},
        {'username': 'dra.lopez', 'first_name': 'María', 'last_name': 'López', 'email': 'maria.lopez@clinica.com', 'especialidad': 'Pediatría', 'telefono': '555-1003', 'horario_inicio': '08:30:00', 'horario_fin': '15:30:00'},
        {'username': 'dr.rodriguez', 'first_name': 'José', 'last_name': 'Rodríguez', 'email': 'jose.rodriguez@clinica.com', 'especialidad': 'Dermatología', 'telefono': '555-1004', 'horario_inicio': '10:00:00', 'horario_fin': '18:00:00'},
        {'username': 'dra.hernandez', 'first_name': 'Laura', 'last_name': 'Hernández', 'email': 'laura.hernandez@clinica.com', 'especialidad': 'Ginecología', 'telefono': '555-1005', 'horario_inicio': '07:00:00', 'horario_fin': '14:00:00'},
    ]

    for med_data in medicos_data:
        # Buscar o crear usuario
        user, user_created = User.objects.get_or_create(
            username=med_data['username'],
            defaults={
                'first_name': med_data['first_name'],
                'last_name': med_data['last_name'],
                'email': med_data['email'],
                'is_active': True
            }
        )
        
        if user_created:
            user.set_password('password123')  # Contraseña simple para testing
            user.save()
            print(f"Usuario médico creado: {user.username}")
        else:
            print(f"Usuario médico ya existente: {user.username}")

        # Buscar especialidad
        try:
            especialidad = Especialidad.objects.get(nombre=med_data['especialidad'])
        except Especialidad.DoesNotExist:
            print(f"Error: Especialidad {med_data['especialidad']} no encontrada")
            continue

        # Crear médico
        medico, medico_created = Medico.objects.get_or_create(
            user=user,
            defaults={
                'especialidad': especialidad,
                'telefono': med_data['telefono'],
                'horario_inicio': med_data['horario_inicio'],
                'horario_fin': med_data['horario_fin']
            }
        )
        
        if medico_created:
            print(f"Médico creado: Dr. {user.first_name} {user.last_name} - {especialidad.nombre}")
        else:
            print(f"Médico ya existente: Dr. {user.first_name} {user.last_name}")
    
    print("---")

    # 3. Crear usuarios y pacientes
    pacientes_data = [
        {'username': 'juan.perez', 'first_name': 'Juan', 'last_name': 'Pérez', 'email': 'juan@email.com', 'dni': '001-123456-1000A', 'telefono': '555-2001', 'direccion': 'Avenida Central 123, Managua', 'fecha_nacimiento': '1985-03-15'},
        {'username': 'maria.gonzalez', 'first_name': 'María', 'last_name': 'González', 'email': 'maria@email.com', 'dni': '001-123456-1001B', 'telefono': '555-2002', 'direccion': 'Calle Norte 456, Granada', 'fecha_nacimiento': '1990-07-22'},
        {'username': 'carlos.ramirez', 'first_name': 'Carlos', 'last_name': 'Ramírez', 'email': 'carlos@email.com', 'dni': '001-123456-1002C', 'telefono': '555-2003', 'direccion': 'Barrio Sur 789, León', 'fecha_nacimiento': '1978-11-30'},
        {'username': 'ana.silva', 'first_name': 'Ana', 'last_name': 'Silva', 'email': 'ana@email.com', 'dni': '001-123456-1003D', 'telefono': '555-2004', 'direccion': 'Residencial Los Robles, Masaya', 'fecha_nacimiento': '1995-05-10'},
        {'username': 'roberto.diaz', 'first_name': 'Roberto', 'last_name': 'Díaz', 'email': 'roberto@email.com', 'dni': '001-123456-1004E', 'telefono': '555-2005', 'direccion': 'Colonia Centroamérica, Chinandega', 'fecha_nacimiento': '1982-12-03'},
    ]

    for pac_data in pacientes_data:
        # Buscar o crear usuario
        user, user_created = User.objects.get_or_create(
            username=pac_data['username'],
            defaults={
                'first_name': pac_data['first_name'],
                'last_name': pac_data['last_name'],
                'email': pac_data['email'],
                'is_active': True
            }
        )
        
        if user_created:
            user.set_password('password123')
            user.save()
            print(f"Usuario paciente creado: {user.username}")
        else:
            print(f"Usuario paciente ya existente: {user.username}")

        # Crear paciente
        paciente, paciente_created = Paciente.objects.get_or_create(
            dni=pac_data['dni'],
            defaults={
                'user': user,
                'telefono': pac_data['telefono'],
                'direccion': pac_data['direccion'],
                'fecha_nacimiento': pac_data['fecha_nacimiento']
            }
        )
        
        if paciente_created:
            print(f"Paciente creado: {user.first_name} {user.last_name} - DNI: {pac_data['dni']}")
        else:
            print(f"Paciente ya existente: {user.first_name} {user.last_name}")
    
    print("---")

    # 4. Crear citas de ejemplo
    try:
        paciente1 = Paciente.objects.get(dni='001-123456-1000A')
        paciente2 = Paciente.objects.get(dni='001-123456-1001B')
        paciente3 = Paciente.objects.get(dni='001-123456-1002C')
        
        medico_general = Medico.objects.get(user__username='dra.garcia')
        medico_cardiologo = Medico.objects.get(user__username='dr.martinez')
        medico_pediatra = Medico.objects.get(user__username='dra.lopez')

        citas_data = [
            {'paciente': paciente1, 'medico': medico_general, 'fecha': '2024-12-20', 'hora': '09:00:00', 'motivo': 'Consulta general por fiebre', 'estado': 'confirmada'},
            {'paciente': paciente2, 'medico': medico_cardiologo, 'fecha': '2024-12-20', 'hora': '10:30:00', 'motivo': 'Control de presión arterial', 'estado': 'pendiente'},
            {'paciente': paciente3, 'medico': medico_pediatra, 'fecha': '2024-12-21', 'hora': '11:00:00', 'motivo': 'Vacunación infantil', 'estado': 'confirmada'},
            {'paciente': paciente1, 'medico': medico_cardiologo, 'fecha': '2024-12-23', 'hora': '15:00:00', 'motivo': 'Dolor en el pecho', 'estado': 'pendiente'},
        ]

        citas_creadas = 0
        for cita_data in citas_data:
            # Verificar si ya existe una cita similar
            cita_existente = Cita.objects.filter(
                paciente=cita_data['paciente'],
                medico=cita_data['medico'],
                fecha=cita_data['fecha'],
                hora=cita_data['hora']
            ).exists()
            
            if not cita_existente:
                Cita.objects.create(**cita_data)
                citas_creadas += 1
                print(f"Cita creada: {cita_data['paciente'].user.first_name} con Dr. {cita_data['medico'].user.last_name} - {cita_data['fecha']} {cita_data['hora']}")
            else:
                print(f"Cita ya existente: {cita_data['paciente'].user.first_name} con Dr. {cita_data['medico'].user.last_name}")

        print(f"Total citas creadas: {citas_creadas}")

    except (Paciente.DoesNotExist, Medico.DoesNotExist) as e:
        print(f"Error al crear citas: {e}")
        print("Asegúrate de que existen pacientes y médicos antes de crear citas")

    print("---")
    print("Población de base de datos completada!")
    print("\nResumen:")
    print(f"- Especialidades: {Especialidad.objects.count()}")
    print(f"- Médicos: {Medico.objects.count()}")
    print(f"- Pacientes: {Paciente.objects.count()}")
    print(f"- Citas: {Cita.objects.count()}")

if __name__ == '__main__':
    populate_database()