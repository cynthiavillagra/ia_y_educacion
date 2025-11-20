-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.autores (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  nombre_autor character varying NOT NULL UNIQUE,
  CONSTRAINT autores_pkey PRIMARY KEY (id)
);
CREATE TABLE public.colecciones (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  nombre character varying NOT NULL UNIQUE,
  descripcion text,
  CONSTRAINT colecciones_pkey PRIMARY KEY (id)
);
CREATE TABLE public.etiquetas (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  nombre_etiqueta character varying NOT NULL UNIQUE,
  CONSTRAINT etiquetas_pkey PRIMARY KEY (id)
);
CREATE TABLE public.recurso_autor (
  recurso_id uuid NOT NULL,
  autor_id uuid NOT NULL,
  orden integer DEFAULT 1,
  CONSTRAINT recurso_autor_pkey PRIMARY KEY (recurso_id, autor_id),
  CONSTRAINT recurso_autor_recurso_id_fkey FOREIGN KEY (recurso_id) REFERENCES public.recursos(id),
  CONSTRAINT recurso_autor_autor_id_fkey FOREIGN KEY (autor_id) REFERENCES public.autores(id)
);
CREATE TABLE public.recurso_etiqueta (
  recurso_id uuid NOT NULL,
  etiqueta_id uuid NOT NULL,
  CONSTRAINT recurso_etiqueta_pkey PRIMARY KEY (recurso_id, etiqueta_id),
  CONSTRAINT recurso_etiqueta_recurso_id_fkey FOREIGN KEY (recurso_id) REFERENCES public.recursos(id),
  CONSTRAINT recurso_etiqueta_etiqueta_id_fkey FOREIGN KEY (etiqueta_id) REFERENCES public.etiquetas(id)
);
CREATE TABLE public.recursos (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  titulo text NOT NULL,
  resumen text,
  codigo_documento character varying UNIQUE,
  año_publicacion integer NOT NULL CHECK ("año_publicacion" >= 1900 AND "año_publicacion"::numeric <= EXTRACT(year FROM now())),
-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.autores (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  nombre_autor character varying NOT NULL UNIQUE,
  CONSTRAINT autores_pkey PRIMARY KEY (id)
);
CREATE TABLE public.colecciones (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  nombre character varying NOT NULL UNIQUE,
  descripcion text,
  CONSTRAINT colecciones_pkey PRIMARY KEY (id)
);
CREATE TABLE public.etiquetas (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  nombre_etiqueta character varying NOT NULL UNIQUE,
  CONSTRAINT etiquetas_pkey PRIMARY KEY (id)
);
CREATE TABLE public.recurso_autor (
  recurso_id uuid NOT NULL,
  autor_id uuid NOT NULL,
  orden integer DEFAULT 1,
  CONSTRAINT recurso_autor_pkey PRIMARY KEY (recurso_id, autor_id),
  CONSTRAINT recurso_autor_recurso_id_fkey FOREIGN KEY (recurso_id) REFERENCES public.recursos(id),
  CONSTRAINT recurso_autor_autor_id_fkey FOREIGN KEY (autor_id) REFERENCES public.autores(id)
);
CREATE TABLE public.recurso_etiqueta (
  recurso_id uuid NOT NULL,
  etiqueta_id uuid NOT NULL,
  CONSTRAINT recurso_etiqueta_pkey PRIMARY KEY (recurso_id, etiqueta_id),
  CONSTRAINT recurso_etiqueta_recurso_id_fkey FOREIGN KEY (recurso_id) REFERENCES public.recursos(id),
  CONSTRAINT recurso_etiqueta_etiqueta_id_fkey FOREIGN KEY (etiqueta_id) REFERENCES public.etiquetas(id)
);
CREATE TABLE public.recursos (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  titulo text NOT NULL,
  resumen text,
  codigo_documento character varying UNIQUE,
  año_publicacion integer NOT NULL CHECK ("año_publicacion" >= 1900 AND "año_publicacion"::numeric <= EXTRACT(year FROM now())),
  fecha_ingreso timestamp with time zone NOT NULL DEFAULT now(),
  estado_alojamiento character varying NOT NULL CHECK (estado_alojamiento::text = ANY (ARRAY['ALOJADO'::character varying, 'ORIGINAL'::character varying]::text[])),
  url_descarga text NOT NULL,
  licencia_cc character varying NOT NULL,
  tipo_documento character varying NOT NULL CHECK (tipo_documento::text = ANY (ARRAY['ARTICULO'::character varying, 'TESIS'::character varying, 'LIBRO'::character varying, 'INFORME'::character varying, 'OTRO'::character varying]::text[])),
  id_coleccion uuid NOT NULL,
  vector_busqueda tsvector GENERATED ALWAYS AS (setweight(to_tsvector('spanish'::regconfig, COALESCE(titulo, ''::text)), 'A'::"char") || setweight(to_tsvector('spanish'::regconfig, COALESCE(resumen, ''::text)), 'B'::"char")) STORED,
  CONSTRAINT recursos_pkey PRIMARY KEY (id),
  CONSTRAINT recursos_id_coleccion_fkey FOREIGN KEY (id_coleccion) REFERENCES public.colecciones(id)
);

CREATE INDEX idx_recursos_vector ON recursos USING GIN(vector_busqueda);
CREATE INDEX idx_recursos_año ON recursos(año_publicacion);
CREATE INDEX idx_recursos_coleccion ON recursos(id_coleccion);
CREATE INDEX idx_recursos_tipo ON recursos(tipo_documento);
CREATE INDEX idx_autores_nombre ON autores(nombre_autor);

CREATE OR REPLACE FUNCTION buscar_recursos(p_query TEXT)
RETURNS TABLE (
  id UUID,
  titulo TEXT,
  año_publicacion INTEGER,
  score REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    r.id,
    r.titulo,
    r.año_publicacion,
    ts_rank(r.vector_busqueda, plainto_tsquery('spanish', p_query)) AS score
  FROM recursos r
  LEFT JOIN recurso_autor ra ON r.id = ra.recurso_id
  LEFT JOIN autores a ON ra.autor_id = a.id
  LEFT JOIN recurso_etiqueta re ON r.id = re.recurso_id
  LEFT JOIN etiquetas e ON re.etiqueta_id = e.id
  WHERE
    r.vector_busqueda @@ plainto_tsquery('spanish', p_query)
    OR a.nombre_autor ILIKE '%' || p_query || '%'
    OR e.nombre_etiqueta ILIKE '%' || p_query || '%'
  GROUP BY r.id
  ORDER BY score DESC;
END;
$$ LANGUAGE plpgsql;