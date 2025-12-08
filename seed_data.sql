-- seed_data.sql (VERSIÓN COMPLETAMENTE ACTUALIZADA)
BEGIN;

-- ---------------------------------------------------------
-- 1. ELIMINAR DATOS EXISTENTES (DE FORMA SEGURA)
-- ---------------------------------------------------------
-- IMPORTANTE: No eliminar usuarios superuser
DELETE FROM citas_cita;
DELETE FROM pacientes_paciente WHERE user_id IN (SELECT id FROM auth_user WHERE is_superuser = false);
DELETE FROM medicos_medico WHERE user_id IN (SELECT id FROM auth_user WHERE is_superuser = false);
DELETE FROM medicos_especialidad;
DELETE FROM autenticacion_perfilusuario WHERE user_id IN (SELECT id FROM auth_user WHERE is_superuser = false);

-- ---------------------------------------------------------
-- 2. RESETEAR SECUENCIAS (MANTENER ID AUTOINCREMENTAL)
-- ---------------------------------------------------------
SELECT setval('citas_cita_id_seq', COALESCE((SELECT MAX(id) FROM citas_cita), 0) + 1, false);
SELECT setval('pacientes_paciente_id_seq', COALESCE((SELECT MAX(id) FROM pacientes_paciente), 0) + 1, false);
SELECT setval('medicos_medico_id_seq', COALESCE((SELECT MAX(id) FROM medicos_medico), 0) + 1, false);
SELECT setval('medicos_especialidad_id_seq', COALESCE((SELECT MAX(id) FROM medicos_especialidad), 0) + 1, false);

-- ---------------------------------------------------------
-- 3. INSERTAR ESPECIALIDADES (CONSERVANDO IDs EXISTENTES)
-- ---------------------------------------------------------
INSERT INTO medicos_especialidad (id, nombre, descripcion) VALUES
(1, 'Medicina General', 'Atención primaria y diagnóstico general'),
(2, 'Cardiología', 'Especialidad en enfermedades del corazón'),
(3, 'Pediatría', 'Atención médica para niños y adolescentes'),
(4, 'Dermatología', 'Especialidad en enfermedades de la piel'),
(5, 'Ginecología', 'Salud femenina y sistema reproductivo'),
(6, 'Ortopedia', 'Especialidad en huesos y articulaciones');

-- Fuerza la secuencia a continuar después del último ID
SELECT setval('medicos_especialidad_id_seq', (SELECT MAX(id) FROM medicos_especialidad), true);

-- ---------------------------------------------------------
-- 4. CREAR USUARIOS MÉDICOS (EVITANDO DUPLICADOS)
-- Contraseña: '12345' (pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1)
-- ---------------------------------------------------------
INSERT INTO auth_user (id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
SELECT data.*
FROM (VALUES
    (100, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'dra.garcia', 'Ana', 'García', 'ana.garcia@clinica.com', false, true, NOW()),
    (101, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'dr.martinez', 'Carlos', 'Martínez', 'carlos.martinez@clinica.com', false, true, NOW()),
    (102, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'dra.lopez', 'María', 'López', 'maria.lopez@clinica.com', false, true, NOW()),
    (103, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'dr.rodriguez', 'José', 'Rodríguez', 'jose.rodriguez@clinica.com', false, true, NOW()),
    (104, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'dra.hernandez', 'Laura', 'Hernández', 'laura.hernandez@clinica.com', false, true, NOW())
) AS data(id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
WHERE NOT EXISTS (SELECT 1 FROM auth_user WHERE username = data.username);

-- ---------------------------------------------------------
-- 5. CREAR USUARIOS PACIENTES
-- Contraseña: '12345'
-- ---------------------------------------------------------
INSERT INTO auth_user (id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
SELECT data.*
FROM (VALUES
    (200, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'juan.perez', 'Juan', 'Pérez', 'juan.perez@email.com', false, true, NOW()),
    (201, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'maria.gonzalez', 'María', 'Gonzzález', 'maria.gonzalez@email.com', false, true, NOW()),
    (202, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'carlos.ramirez', 'Carlos', 'Ramírez', 'carlos.ramirez@email.com', false, true, NOW()),
    (203, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'ana.silva', 'Ana', 'Silva', 'ana.silva@email.com', false, true, NOW()),
    (204, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'roberto.diaz', 'Roberto', 'Díaz', 'roberto.diaz@email.com', false, true, NOW()),
    (205, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'sofia.castro', 'Sofía', 'Castro', 'sofia.castro@email.com', false, true, NOW()),
    (206, 'pbkdf2_sha256$600000$2J90q2$2Wb+M0/i+l/t+X/R/Z/x/C/V/B/N/m/1', false, 'dr_house', 'Gregory', 'House', 'dr.house@clinica.com', false, true, NOW())
) AS data(id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
WHERE NOT EXISTS (SELECT 1 FROM auth_user WHERE username = data.username);

-- Asegurar que la secuencia esté actualizada
SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user), true);

-- ---------------------------------------------------------
-- 6. CREAR/ACTUALIZAR PERFILES DE AUTENTICACIÓN
-- IMPORTANTE: Asegurar que médicos tengan tipo_usuario = 'medico'
-- ---------------------------------------------------------
INSERT INTO autenticacion_perfilusuario (user_id, tipo_usuario, creado_en, actualizado_en)
SELECT 
    u.id,
    CASE 
        WHEN u.username LIKE 'dr.%' OR u.username LIKE 'dra.%' OR u.username = 'dr_house' THEN 'medico'
        ELSE 'paciente'
    END,
    NOW(),
    NOW()
FROM auth_user u
WHERE u.is_superuser = false
    AND NOT EXISTS (SELECT 1 FROM autenticacion_perfilusuario p WHERE p.user_id = u.id);

-- ---------------------------------------------------------
-- 7. ACTUALIZAR PERFILES EXISTENTES (por si acaso)
-- ---------------------------------------------------------
UPDATE autenticacion_perfilusuario p
SET tipo_usuario = CASE 
    WHEN u.username LIKE 'dr.%' OR u.username LIKE 'dra.%' OR u.username = 'dr_house' THEN 'medico'
    ELSE 'paciente'
END,
actualizado_en = NOW()
FROM auth_user u
WHERE p.user_id = u.id 
    AND u.is_superuser = false
    AND (
        (u.username LIKE 'dr.%' OR u.username LIKE 'dra.%' OR u.username = 'dr_house') 
        AND p.tipo_usuario != 'medico'
    );

-- ---------------------------------------------------------
-- 8. CREAR DATOS MÉDICOS DETALLADOS
-- Asegurar que dr_house sea médico también
-- ---------------------------------------------------------
INSERT INTO medicos_medico (user_id, especialidad_id, telefono, horario_inicio, horario_fin, creado_en) 
SELECT 
    u.id, 
    e.id,
    tel.telefono,
    tel.horario_inicio::time,
    tel.horario_fin::time,
    NOW()
FROM (VALUES
    ('dra.garcia', 'Medicina General', '555-1001', '08:00:00', '16:00:00'),
    ('dr.martinez', 'Cardiología', '555-1002', '09:00:00', '17:00:00'),
    ('dra.lopez', 'Pediatría', '555-1003', '08:30:00', '15:30:00'),
    ('dr.rodriguez', 'Dermatología', '555-1004', '10:00:00', '18:00:00'),
    ('dra.hernandez', 'Ginecología', '555-1005', '07:00:00', '14:00:00'),
    ('dr_house', 'Medicina General', '555-1006', '13:00:00', '21:00:00')
) AS tel(username, especialidad, telefono, horario_inicio, horario_fin)
JOIN auth_user u ON u.username = tel.username
JOIN medicos_especialidad e ON e.nombre = tel.especialidad
WHERE NOT EXISTS (SELECT 1 FROM medicos_medico m WHERE m.user_id = u.id);

-- ---------------------------------------------------------
-- 9. CREAR DATOS PACIENTES DETALLADOS (EXCLUYENDO dr_house)
-- ---------------------------------------------------------
INSERT INTO pacientes_paciente (user_id, dni, telefono, direccion, fecha_nacimiento, creado_en) 
SELECT 
    u.id,
    p.dni,
    p.telefono,
    p.direccion,
    p.fecha_nacimiento::date,
    NOW()
FROM (VALUES
    ('juan.perez', '001-123456-1000A', '555-2001', 'Avenida Central 123, Managua', '1985-03-15'),
    ('maria.gonzalez', '001-123456-1001B', '555-2002', 'Calle Norte 456, Granada', '1990-07-22'),
    ('carlos.ramirez', '001-123456-1002C', '555-2003', 'Barrio Sur 789, León', '1978-11-30'),
    ('ana.silva', '001-123456-1003D', '555-2004', 'Residencial Los Robles, Masaya', '1995-05-10'),
    ('roberto.diaz', '001-123456-1004E', '555-2005', 'Colonia Centroamérica, Chinandega', '1982-12-03'),
    ('sofia.castro', '001-123456-1005F', '555-2006', 'Sector Este, Estelí', '2000-08-18')
) AS p(username, dni, telefono, direccion, fecha_nacimiento)
JOIN auth_user u ON u.username = p.username
WHERE u.username != 'dr_house'
    AND NOT EXISTS (SELECT 1 FROM pacientes_paciente pa WHERE pa.user_id = u.id);

-- ---------------------------------------------------------
-- 10. CREAR CITAS CON FECHAS FUTURAS Y PASADAS (PARA TESTING)
-- ---------------------------------------------------------
INSERT INTO citas_cita (paciente_id, medico_id, fecha, hora, motivo, estado, creada_en) 
SELECT 
    pac.id,
    med.id,
    c.fecha::date,
    c.hora::time,
    c.motivo,
    c.estado,
    NOW()
FROM (VALUES
    -- Citas pasadas (para historial)
    ('001-123456-1000A', 'dra.garcia', CURRENT_DATE - INTERVAL '5 days', '09:00:00', 'Consulta general por fiebre', 'finalizada'),
    ('001-123456-1001B', 'dr.martinez', CURRENT_DATE - INTERVAL '3 days', '10:30:00', 'Control de presión arterial', 'finalizada'),
    ('001-123456-1000A', 'dr_house', CURRENT_DATE - INTERVAL '2 days', '14:00:00', 'Caso diagnóstico complicado', 'finalizada'),
    
    -- Citas de hoy
    ('001-123456-1002C', 'dra.lopez', CURRENT_DATE, '11:00:00', 'Vacunación infantil', 'confirmada'),
    ('001-123456-1003D', 'dr.rodriguez', CURRENT_DATE, '14:00:00', 'Revisión de erupción cutánea', 'confirmada'),
    
    -- Citas futuras (próximos días)
    ('001-123456-1004E', 'dra.hernandez', CURRENT_DATE + INTERVAL '1 day', '08:30:00', 'Control ginecológico anual', 'confirmada'),
    ('001-123456-1000A', 'dr.martinez', CURRENT_DATE + INTERVAL '2 days', '15:00:00', 'Dolor en el pecho', 'pendiente'),
    ('001-123456-1005F', 'dra.garcia', CURRENT_DATE + INTERVAL '3 days', '13:00:00', 'Chequeo general', 'pendiente'),
    
    -- Citas canceladas
    ('001-123456-1002C', 'dr.rodriguez', CURRENT_DATE + INTERVAL '4 days', '16:30:00', 'Alergia en la piel', 'cancelada'),
    
    -- Más citas variadas
    ('001-123456-1001B', 'dr_house', CURRENT_DATE + INTERVAL '5 days', '17:00:00', 'Segunda opinión', 'pendiente'),
    ('001-123456-1003D', 'dra.lopez', CURRENT_DATE + INTERVAL '6 days', '09:30:00', 'Control pediátrico', 'pendiente'),
    ('001-123456-1004E', 'dr.martinez', CURRENT_DATE + INTERVAL '7 days', '11:30:00', 'Electrocardiograma', 'pendiente')
) AS c(paciente_dni, medico_username, fecha, hora, motivo, estado)
JOIN pacientes_paciente pac ON pac.dni = c.paciente_dni
JOIN medicos_medico med ON med.id IN (
    SELECT m.id 
    FROM medicos_medico m 
    JOIN auth_user u ON m.user_id = u.id 
    WHERE u.username = c.medico_username
)
WHERE NOT EXISTS (
    SELECT 1 FROM citas_cita ci 
    WHERE ci.paciente_id = pac.id 
        AND ci.medico_id = med.id 
        AND ci.fecha = c.fecha::date 
        AND ci.hora = c.hora::time
);

-- ---------------------------------------------------------
-- 11. VERIFICACIÓN FINAL
-- ---------------------------------------------------------
DO $$
DECLARE
    especialidades_count INT;
    medicos_count INT;
    pacientes_count INT;
    citas_count INT;
    perfiles_count INT;
BEGIN
    -- Contar registros
    SELECT COUNT(*) INTO especialidades_count FROM medicos_especialidad;
    SELECT COUNT(*) INTO medicos_count FROM medicos_medico;
    SELECT COUNT(*) INTO pacientes_count FROM pacientes_paciente;
    SELECT COUNT(*) INTO citas_count FROM citas_cita;
    SELECT COUNT(*) INTO perfiles_count FROM autenticacion_perfilusuario WHERE user_id IN (SELECT id FROM auth_user WHERE is_superuser = false);
    
    -- Mostrar resultados
    RAISE NOTICE '========================================';
    RAISE NOTICE 'SEED DATA COMPLETADO';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Especialidades: %', especialidades_count;
    RAISE NOTICE 'Médicos: %', medicos_count;
    RAISE NOTICE 'Pacientes: %', pacientes_count;
    RAISE NOTICE 'Citas: %', citas_count;
    RAISE NOTICE 'Perfiles (no superuser): %', perfiles_count;
    RAISE NOTICE '========================================';
END $$;

COMMIT;

-- ---------------------------------------------------------
-- 12. LISTAR DATOS PARA VERIFICACIÓN MANUAL (OPCIONAL)
-- ---------------------------------------------------------
/*
SELECT 'ESPECIALIDADES' as tipo, COUNT(*) as total FROM medicos_especialidad
UNION ALL
SELECT 'MÉDICOS', COUNT(*) FROM medicos_medico
UNION ALL
SELECT 'PACIENTES', COUNT(*) FROM pacientes_paciente
UNION ALL
SELECT 'CITAS', COUNT(*) FROM citas_cita
UNION ALL
SELECT 'PERFILES NO SUPERUSER', COUNT(*) FROM autenticacion_perfilusuario p JOIN auth_user u ON p.user_id = u.id WHERE u.is_superuser = false;
*/