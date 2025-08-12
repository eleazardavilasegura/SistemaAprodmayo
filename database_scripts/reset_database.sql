-- Script para resetear la base de datos de APRODMAYO
-- ADVERTENCIA: Este script eliminará todos los datos existentes

-- Desconectar a todos los usuarios
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'aprodmayo'
  AND pid <> pg_backend_pid();

-- Eliminar la base de datos existente
DROP DATABASE IF EXISTS aprodmayo;

-- Crear la base de datos nuevamente
CREATE DATABASE aprodmayo
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'es_ES.utf8'
    LC_CTYPE = 'es_ES.utf8'
    TEMPLATE = template0;

-- Nota: Después de ejecutar el comando anterior, conectar a la base de datos "aprodmayo"
-- y ejecutar el siguiente código para crear las extensiones necesarias:
/*
-- Crear extensiones necesarias (ejecutar esto después de conectarse a la base de datos aprodmayo)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

*/
-- Mensaje final
SELECT 'Base de datos APRODMAYO ha sido reseteada correctamente.' as message;
