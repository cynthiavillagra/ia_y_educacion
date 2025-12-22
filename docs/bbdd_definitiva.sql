-- BBDD Definitiva - Esquema v2 (Metadatos Unificados)
-- Tabla única y ancha para facilitar portabilidad y búsquedas.

-- 0. LIMPIEZA TOTAL (Ejecutar con precaución: borra datos antiguos)
DROP TABLE IF EXISTS recurso_autor CASCADE;
DROP TABLE IF EXISTS recurso_etiqueta CASCADE;
DROP TABLE IF EXISTS relaciones CASCADE; -- Por si quedó alguna tabla intermedia vieja
DROP TABLE IF EXISTS autores CASCADE;
DROP TABLE IF EXISTS colecciones CASCADE;
DROP TABLE IF EXISTS etiquetas CASCADE;
DROP TABLE IF EXISTS recursos CASCADE;
DROP FUNCTION IF EXISTS buscar_recursos(text);


-- 1. Tabla Principal
CREATE TABLE public.recursos (
  -- 1) Identificación
  id text NOT NULL, -- ID visible (ej: SAIA-EDU-001)
  titulo text NOT NULL,
  titulo_original text,
  tipo_recurso text NOT NULL CHECK (tipo_recurso IN (
    'paper_academico', 'libro', 'capitulo_libro', 'informe', 'guia', 
    'normativa', 'diseno_curricular', 'articulo_web', 'web_institucional', 
    'material_docente', 'boletin', 'dataset', 'presentacion'
  )),
  descripcion_resumen text,
  
  -- 2) Autoría y fuente
  autores text, -- "Apellido, Nombre; Apellido, Nombre"
  institucion_autora text,
  institucion_fuente text NOT NULL,
  editorial_o_fuente text,
  
  -- 3) Publicación
  anio_publicacion integer,
  fecha_publicacion date,
  pais_origen text,
  idioma text,
  doi text,
  isbn_issn text,
  numero_paginas integer,
  
  -- 4) Acceso y archivos
  url_fuente_original text NOT NULL,
  url_pdf_directo text,
  archivo_local boolean NOT NULL DEFAULT false,
  url_archivo_local text,
  tipo_acceso text CHECK (tipo_acceso IN ('abierto', 'cerrado', 'mixto', 'desconocido')),
  licencia text,
  formato text CHECK (formato IN ('PDF', 'HTML', 'DOCX', 'PPTX', 'WEB', 'MIXTO')),
  
  -- 5) Clasificación
  palabras_clave text, -- CSV
  areas_tematicas text,
  nivel text CHECK (nivel IN ('introductorio', 'intermedio', 'avanzado')),
  tipo_publico text,
  contexto_geografico text,
  
  -- 6) Gobernanza
  proporcionado_por text CHECK (proporcionado_por IN ('SAIA', 'externo', 'mixto')),
  agregado_por text NOT NULL,
  fecha_incorporacion_repo date DEFAULT CURRENT_DATE,
  estado_revision text CHECK (estado_revision IN ('borrador', 'en_revision', 'publicado', 'archivado')),
  revisado_por text,
  observaciones text,
  
  -- Generado
  vector_busqueda tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('spanish'::regconfig, COALESCE(titulo, '')), 'A') || 
    setweight(to_tsvector('spanish'::regconfig, COALESCE(descripcion_resumen, '')), 'B') ||
    setweight(to_tsvector('spanish'::regconfig, COALESCE(palabras_clave, '')), 'C') ||
    setweight(to_tsvector('spanish'::regconfig, COALESCE(autores, '')), 'D')
  ) STORED,

  CONSTRAINT recursos_pkey PRIMARY KEY (id)
);

-- 2. Índices
CREATE INDEX idx_recursos_vector ON recursos USING GIN(vector_busqueda);
CREATE INDEX idx_recursos_anio ON recursos(anio_publicacion);
CREATE INDEX idx_recursos_tipo ON recursos(tipo_recurso);
CREATE INDEX idx_recursos_fuente ON recursos(institucion_fuente);

-- 3. Funciones de Búsqueda
CREATE OR REPLACE FUNCTION buscar_recursos(p_query TEXT)
RETURNS TABLE (
  id TEXT,
  titulo TEXT,
  anio_publicacion INTEGER,
  score REAL
) AS $$
BEGIN
  IF p_query IS NULL OR trim(p_query) = '' THEN
    RETURN QUERY
    SELECT r.id, r.titulo, r.anio_publicacion, 0.0::REAL
    FROM recursos r
    ORDER BY r.fecha_incorporacion_repo DESC;
  ELSE
    RETURN QUERY
    SELECT r.id, r.titulo, r.anio_publicacion,
           ts_rank(r.vector_busqueda, plainto_tsquery('spanish', p_query)) AS score
    FROM recursos r
    WHERE r.vector_busqueda @@ plainto_tsquery('spanish', p_query)
       OR r.autores ILIKE '%' || p_query || '%'
       OR r.institucion_fuente ILIKE '%' || p_query || '%'
    ORDER BY score DESC;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- 4. RLS (Seguridad)
ALTER TABLE public.recursos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Lectura pública" ON public.recursos FOR SELECT USING (true);
CREATE POLICY "Escritura admin" ON public.recursos FOR ALL USING (auth.role() = 'authenticated');
