BEGIN; -- Inicio de transacción

-- ---------------------------------------------------------
-- 1. ELIMINAR DATOS EXISTENTES
-- ---------------------------------------------------------
DELETE FROM citas_cita;
DELETE FROM pacientes_paciente;
DELETE FROM medicos_medico;
DELETE FROM medicos_especialidad;
DELETE FROM auth_user WHERE is_superuser = false;

-- ---------------------------------------------------------
-- 2. RESETEAR SECUENCIAS (Dinámico)
-- ---------------------------------------------------------
SELECT setval('citas_cita_id_seq', COALESCE((SELECT MAX(id) FROM citas_cita), 0) + 1, false);
SELECT setval('pacientes_paciente_id_seq', COALESCE((SELECT MAX(id) FROM pacientes_paciente), 0) + 1, false);
SELECT setval('medicos_medico_id_seq', COALESCE((SELECT MAX(id) FROM medicos_medico), 0) + 1, false);
SELECT setval('medicos_especialidad_id_seq', COALESCE((SELECT MAX(id) FROM medicos_especialidad), 0) + 1, false);
SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));

-- ---------------------------------------------------------
-- 3. INSERTAR ESPECIALIDADES
-- ---------------------------------------------------------
INSERT INTO medicos_especialidad (nombre, descripcion) VALUES
('Medicina General', 'Atención primaria y diagnóstico general'),
('Cardiología', 'Especialidad en enfermedades del corazón'),
('Pediatría', 'Atención médica para niños y adolescentes'),
('Dermatología', 'Especialidad en enfermedades de la piel'),
('Ginecología', 'Salud femenina y sistema reproductivo'),
('Ortopedia', 'Especialidad en huesos y articulaciones');

-- ---------------------------------------------------------
-- 4. CREAR USUARIOS MÉDICOS
-- ---------------------------------------------------------
INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES
('pbkdf2_sha256$600000$xyz123$hashed_password_1', false, 'dra.garcia', 'Ana', 'García', 'ana.garcia@clinica.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_2', false, 'dr.martinez', 'Carlos', 'Martínez', 'carlos.martinez@clinica.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_3', false, 'dra.lopez', 'María', 'López', 'maria.lopez@clinica.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_4', false, 'dr.rodriguez', 'José', 'Rodríguez', 'jose.rodriguez@clinica.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_5', false, 'dra.hernandez', 'Laura', 'Hernández', 'laura.hernandez@clinica.com', false, true, NOW());

-- ---------------------------------------------------------
-- 5. CREAR PERFILES MÉDICOS (Con casting ::time)
-- ---------------------------------------------------------
INSERT INTO medicos_medico (user_id, especialidad_id, telefono, horario_inicio, horario_fin, creado_en) 
SELECT 
    u.id, 
    e.id,
    tel.telefono,
    tel.horario_inicio::time, -- CASTING APLICADO AQUÍ
    tel.horario_fin::time,    -- CASTING APLICADO AQUÍ
    NOW()
FROM (VALUES
    ('dra.garcia', 'Medicina General', '555-1001', '08:00:00', '16:00:00'),
    ('dr.martinez', 'Cardiología', '555-1002', '09:00:00', '17:00:00'),
    ('dra.lopez', 'Pediatría', '555-1003', '08:30:00', '15:30:00'),
    ('dr.rodriguez', 'Dermatología', '555-1004', '10:00:00', '18:00:00'),
    ('dra.hernandez', 'Ginecología', '555-1005', '07:00:00', '14:00:00')
) AS tel(username, especialidad, telefono, horario_inicio, horario_fin)
JOIN auth_user u ON u.username = tel.username
JOIN medicos_especialidad e ON e.nombre = tel.especialidad;

-- ---------------------------------------------------------
-- 6. CREAR USUARIOS PACIENTES
-- ---------------------------------------------------------
INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES
('pbkdf2_sha256$600000$xyz123$hashed_password_6', false, 'juan.perez', 'Juan', 'Pérez', 'juan.perez@email.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_7', false, 'maria.gonzalez', 'María', 'González', 'maria.gonzalez@email.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_8', false, 'carlos.ramirez', 'Carlos', 'Ramírez', 'carlos.ramirez@email.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_9', false, 'ana.silva', 'Ana', 'Silva', 'ana.silva@email.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_10', false, 'roberto.diaz', 'Roberto', 'Díaz', 'roberto.diaz@email.com', false, true, NOW()),
('pbkdf2_sha256$600000$xyz123$hashed_password_11', false, 'sofia.castro', 'Sofía', 'Castro', 'sofia.castro@email.com', false, true, NOW());

-- ---------------------------------------------------------
-- 7. CREAR PERFILES PACIENTES (Con casting ::date)
-- ---------------------------------------------------------
INSERT INTO pacientes_paciente (user_id, dni, telefono, direccion, fecha_nacimiento, creado_en) 
SELECT 
    u.id,
    p.dni,
    p.telefono,
    p.direccion,
    p.fecha_nacimiento::date, -- CASTING PREVENTIVO
    NOW()
FROM (VALUES
    ('juan.perez', '001-123456-1000A', '555-2001', 'Avenida Central 123, Managua', '1985-03-15'),
    ('maria.gonzalez', '001-123456-1001B', '555-2002', 'Calle Norte 456, Granada', '1990-07-22'),
    ('carlos.ramirez', '001-123456-1002C', '555-2003', 'Barrio Sur 789, León', '1978-11-30'),
    ('ana.silva', '001-123456-1003D', '555-2004', 'Residencial Los Robles, Masaya', '1995-05-10'),
    ('roberto.diaz', '001-123456-1004E', '555-2005', 'Colonia Centroamérica, Chinandega', '1982-12-03'),
    ('sofia.castro', '001-123456-1005F', '555-2006', 'Sector Este, Estelí', '2000-08-18')
) AS p(username, dni, telefono, direccion, fecha_nacimiento)
JOIN auth_user u ON u.username = p.username;

-- ---------------------------------------------------------
-- 8. CREAR CITAS (Con casting ::date y ::time)
-- ---------------------------------------------------------
INSERT INTO citas_cita (paciente_id, medico_id, fecha, hora, motivo, estado, creada_en) 
SELECT 
    pac.id,
    med.id,
    c.fecha::date, -- CASTING PREVENTIVO
    c.hora::time,  -- CASTING PREVENTIVO
    c.motivo,
    c.estado,
    NOW()
FROM (VALUES
    ('001-123456-1000A', 'dra.garcia', '2024-12-20', '09:00:00', 'Consulta general por fiebre', 'confirmada'),
    ('001-123456-1001B', 'dr.martinez', '2024-12-20', '10:30:00', 'Control de presión arterial', 'pendiente'),
    ('001-123456-1002C', 'dra.lopez', '2024-12-21', '11:00:00', 'Vacunación infantil', 'confirmada'),
    ('001-123456-1003D', 'dr.rodriguez', '2024-12-21', '14:00:00', 'Revisión de erupción cutánea', 'pendiente'),
    ('001-123456-1004E', 'dra.hernandez', '2024-12-22', '08:30:00', 'Control ginecológico anual', 'confirmada'),
    ('001-123456-1000A', 'dr.martinez', '2024-12-23', '15:00:00', 'Dolor en el pecho', 'pendiente'),
    ('001-123456-1001B', 'dra.garcia', '2024-12-18', '13:00:00', 'Seguimiento de gripe', 'finalizada'),
    ('001-123456-1002C', 'dr.rodriguez', '2024-12-17', '16:30:00', 'Alergia en la piel', 'cancelada')
) AS c(paciente_dni, medico_username, fecha, hora, motivo, estado)
JOIN pacientes_paciente pac ON pac.dni = c.paciente_dni
JOIN medicos_medico med ON med.id IN (
    SELECT m.id 
    FROM medicos_medico m 
    JOIN auth_user u ON m.user_id = u.id 
    WHERE u.username = c.medico_username
);

COMMIT;