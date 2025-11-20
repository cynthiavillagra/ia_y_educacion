-- MIGRACIÓN V2.0
-- Ejecuta este script en el Editor SQL de Supabase para actualizar tu base de datos existente.

-- 1. Actualizar la columna vector_busqueda para que sea automática (GENERATED ALWAYS)
-- Primero eliminamos la columna antigua (los datos se regenerarán automáticamente)
ALTER TABLE public.recursos DROP COLUMN IF EXISTS vector_busqueda;

-- La recreamos con la nueva definición
ALTER TABLE public.recursos ADD COLUMN vector_busqueda tsvector
GENERATED ALWAYS AS (
  setweight(to_tsvector('spanish'::regconfig, COALESCE(titulo, ''::text)), 'A'::"char") ||
  setweight(to_tsvector('spanish'::regconfig, COALESCE(resumen, ''::text)), 'B'::"char")
) STORED;

-- 2. Crear Índices de Rendimiento (usamos IF NOT EXISTS por seguridad)
CREATE INDEX IF NOT EXISTS idx_recursos_vector ON public.recursos USING GIN(vector_busqueda);
CREATE INDEX IF NOT EXISTS idx_recursos_año ON public.recursos(año_publicacion);
CREATE INDEX IF NOT EXISTS idx_recursos_coleccion ON public.recursos(id_coleccion);
CREATE INDEX IF NOT EXISTS idx_recursos_tipo ON public.recursos(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_autores_nombre ON public.autores(nombre_autor);

-- 3. Crear la Función de Búsqueda
CREATE OR REPLACE FUNCTION buscar_recursos(p_query TEXT)
RETURNS TABLE (
  id UUID,
  titulo TEXT,
  año_publicacion INTEGER,
  score REAL
) AS $$
BEGIN
  IF p_query IS NULL OR TRIM(p_query) = '' THEN
    RETURN QUERY
    SELECT
      r.id,
      r.titulo,
      r.año_publicacion,
      0.0::REAL AS score
    FROM recursos r
    ORDER BY r.fecha_ingreso DESC;
  ELSE
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
  END IF;
END;
$$ LANGUAGE plpgsql;
