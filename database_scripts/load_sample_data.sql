-- Script para cargar datos de prueba en la base de datos APRODMAYO
-- Ejecutar este script después de haber aplicado las migraciones de Django
-- Nota: Este script debe ejecutarse en la base de datos aprodmayo

-- Insertar usuario administrador (la contraseña será 'admin', pero Django la manejará)
-- Nota: En un entorno de producción real, este enfoque no se recomienda para contraseñas
INSERT INTO usuarios_usuario (
    password, 
    is_superuser, 
    username, 
    first_name, 
    last_name, 
    email, 
    is_staff, 
    is_active, 
    date_joined, 
    role, 
    telefono, 
    imagen_perfil, 
    fecha_ultimo_acceso, 
    permiso_beneficiarias, 
    permiso_finanzas, 
    permiso_talleres, 
    permiso_reportes
) VALUES (
    'pbkdf2_sha256$600000$fcq8EmaXQFwKhiGgXkrKz9$ntc9DE9Ygxa669e1uDcD7+jryql8Nw7jDnnd+ACuybM=', -- 'admin' codificada
    TRUE, -- is_superuser
    'admin', -- username
    'Administrador', -- first_name
    'Sistema', -- last_name
    'admin@aprodmayo.org', -- email
    TRUE, -- is_staff
    TRUE, -- is_active
    NOW(), -- date_joined
    'administrador', -- role
    '123456789', -- telefono
    NULL, -- imagen_perfil
    NULL, -- fecha_ultimo_acceso
    TRUE, -- permiso_beneficiarias
    TRUE, -- permiso_finanzas
    TRUE, -- permiso_talleres
    TRUE -- permiso_reportes
) ON CONFLICT (username) DO NOTHING;

-- Insertar algunas categorías de finanzas
INSERT INTO finanzas_categoria (nombre, descripcion, tipo, activo) VALUES
('Donaciones', 'Donaciones de organizaciones o personas', 'INGRESO', TRUE),
('Cuotas', 'Pagos de cuotas de socios', 'INGRESO', TRUE),
('Subsidios', 'Subsidios gubernamentales', 'INGRESO', TRUE),
('Eventos', 'Ingresos por eventos', 'INGRESO', TRUE),
('Personal', 'Pagos a personal', 'EGRESO', TRUE),
('Materiales', 'Materiales para talleres', 'EGRESO', TRUE),
('Servicios', 'Servicios básicos', 'EGRESO', TRUE),
('Alquiler', 'Alquiler de locales', 'EGRESO', TRUE),
('Transporte', 'Gastos de transporte', 'EGRESO', TRUE),
('Alimentación', 'Gastos de alimentación', 'EGRESO', TRUE)
ON CONFLICT (id) DO NOTHING;

-- Insertar algunos socios
INSERT INTO finanzas_socio (nombres, apellidos, documento_identidad, fecha_registro, telefono, correo, direccion, estado, cuota_mensual, observaciones) VALUES
('Ana María', 'Gómez Pérez', '12345678', '2024-01-01', '987654321', 'ana.gomez@email.com', 'Av. Principal 123', 'ACTIVO', 50.00, 'Socia fundadora'),
('Luis', 'Rodríguez Vega', '23456789', '2024-01-15', '976543210', 'luis.rodriguez@email.com', 'Jr. Libertad 456', 'ACTIVO', 30.00, 'Socio regular'),
('Carmen', 'Torres López', '34567890', '2024-02-01', '965432109', 'carmen.torres@email.com', 'Calle Nueva 789', 'ACTIVO', 50.00, 'Socia contribuyente')
ON CONFLICT (id) DO NOTHING;

-- Insertar algunos talleres
INSERT INTO talleres_taller (nombre, descripcion, fecha_inicio, fecha_fin, horario, lugar, capacidad, facilitador, estado, notas, creado, actualizado) VALUES
('Taller de Costura', 'Taller básico de costura y patronaje', '2025-09-01', '2025-10-30', 'Lunes y Miércoles de 9:00 a 12:00', 'Sede Central APRODMAYO', 15, 'María López', 'PROGRAMADO', 'Traer materiales básicos', NOW(), NOW()),
('Autoestima y Desarrollo Personal', 'Taller para fortalecer la autoestima y habilidades personales', '2025-09-15', '2025-10-15', 'Martes y Jueves de 15:00 a 17:00', 'Centro Comunitario Los Olivos', 20, 'Carmen Ruiz', 'PROGRAMADO', NULL, NOW(), NOW()),
('Emprendimiento y Negocios', 'Taller para aprender a iniciar un pequeño negocio', '2025-10-01', '2025-11-30', 'Viernes de 14:00 a 18:00', 'Sede Central APRODMAYO', 12, 'Pedro Mamani', 'PROGRAMADO', 'Se entregarán certificados', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insertar algunas beneficiarias
INSERT INTO beneficiarias_beneficiaria (fecha_ingreso, hora_ingreso, nombres, apellidos, edad, fecha_nacimiento, documento_identidad, tipo_documento, direccion, telefono, correo, estado_civil, nivel_educativo, ocupacion, situacion_laboral, motivo_consulta, tipo_violencia, descripcion_situacion, problemas_salud, medicacion, tiene_hijos, numero_hijos, situacion_vivienda, seguimiento_requerido, notas_seguimiento, recibido_por) VALUES
('2024-05-15', '10:00', 'Juana', 'Flores Mendoza', 28, '1997-03-15', '45678901', 'DNI', 'Jr. Los Lirios 234', '987123456', 'juana.flores@email.com', 'SOLTERA', 'SECUNDARIA_COMPLETA', 'Vendedora', 'EMPLEADA', 'Apoyo económico y emocional', 'PSICOLOGICA', 'Situación de vulnerabilidad económica', 'Ninguno', '', TRUE, 2, 'ALQUILADA', TRUE, 'Necesita seguimiento mensual', 'Rosa Quintana'),
('2024-06-20', '11:30', 'Luisa', 'Paredes Gonzales', 35, '1990-07-10', '34567890', 'DNI', 'Av. Las Flores 567', '976543211', 'luisa.paredes@email.com', 'DIVORCIADA', 'TECNICO_COMPLETO', 'Secretaria', 'DESEMPLEADA', 'Busca empleo y apoyo', 'ECONOMICA', 'Perdió su empleo hace 3 meses', 'Hipertensión', 'Losartan', TRUE, 1, 'FAMILIAR', TRUE, 'Priorizar capacitación laboral', 'Carlos Medina'),
('2024-07-05', '09:15', 'Marta', 'Quispe Huaman', 42, '1983-11-22', '23456789', 'DNI', 'Jr. Ayacucho 789', '965432100', 'marta.quispe@email.com', 'CASADA', 'PRIMARIA_COMPLETA', 'Ama de casa', 'AMA_DE_CASA', 'Apoyo familiar', 'FISICA', 'Violencia doméstica', 'Ansiedad', 'Ninguna', TRUE, 3, 'PROPIA', TRUE, 'Requiere atención psicológica urgente', 'Laura Torres')
ON CONFLICT (id) DO NOTHING;

-- Mensaje final
SELECT 'Datos iniciales cargados correctamente.' as message;
