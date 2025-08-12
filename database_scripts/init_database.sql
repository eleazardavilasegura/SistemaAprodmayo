-- Script de inicialización de base de datos para APRODMAYO
-- Ejecutar este script en pgAdmin 4 para crear la base de datos

-- Crear la base de datos
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
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- Para búsquedas de texto eficientes
CREATE EXTENSION IF NOT EXISTS unaccent; -- Para búsquedas sin acentos

-- Comentario: Las tablas y relaciones serán creadas por Django cuando ejecutemos
-- los comandos 'makemigrations' y 'migrate'
-- Este script solo configura la base de datos inicial

-- Opcional: Crear roles y permisos
-- CREATE ROLE aprodmayo_app WITH LOGIN PASSWORD 'contraseña_segura';
-- GRANT ALL PRIVILEGES ON DATABASE aprodmayo TO aprodmayo_app;

*/
-- Mensaje final
SELECT 'Base de datos APRODMAYO inicializada correctamente.' as message;
