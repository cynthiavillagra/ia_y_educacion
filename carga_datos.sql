-- Carga de Datos Iniciales (Ejemplo)

-- 1. Colecciones
INSERT INTO colecciones (nombre, descripcion) VALUES 
('UNESCO', 'Recursos educativos de la UNESCO'),
('UNIPE', 'Universidad Pedagógica Nacional'),
('OEI', 'Organización de Estados Iberoamericanos')
ON CONFLICT (nombre) DO NOTHING;

-- 2. Autores (Ejemplos)
INSERT INTO autores (nombre_autor) VALUES 
('Emily M. Bender'),
('Timnit Gebru'),
('Darío Sandrone')
ON CONFLICT (nombre_autor) DO NOTHING;

-- 3. Etiquetas (Ejemplos)
INSERT INTO etiquetas (nombre_etiqueta) VALUES 
('IA'),
('Educación'),
('Ética'),
('Política Pública')
ON CONFLICT (nombre_etiqueta) DO NOTHING;

-- 4. Recursos (Ejemplo)
-- Nota: Se requiere obtener los IDs de colecciones, autores y etiquetas primero.
-- En un script real, se haría dinámicamente o con IDs conocidos.
-- A continuación se muestra un bloque anónimo PL/PGSQL para insertar un recurso completo de ejemplo.

DO $$
DECLARE
  v_coleccion_id uuid;
  v_autor_id uuid;
  v_etiqueta_id uuid;
  v_recurso_id uuid;
BEGIN
  -- Obtener ID de colección
  SELECT id INTO v_coleccion_id FROM colecciones WHERE nombre = 'UNESCO' LIMIT 1;
  
  -- Insertar Recurso
  INSERT INTO recursos (titulo, resumen, año_publicacion, tipo_documento, estado_alojamiento, url_descarga, licencia_cc, id_coleccion)
  VALUES (
    'Guía sobre IA en educación',
    'Una guía completa sobre el uso de inteligencia artificial en las aulas.',
    2024,
    'INFORME',
    'ORIGINAL',
    'https://unesco.org/ia-edu',
    'CC BY 4.0',
    v_coleccion_id
  )
  RETURNING id INTO v_recurso_id;

  -- Asociar Autor
  SELECT id INTO v_autor_id FROM autores WHERE nombre_autor = 'Emily M. Bender' LIMIT 1;
  INSERT INTO recurso_autor (recurso_id, autor_id) VALUES (v_recurso_id, v_autor_id);

  -- Asociar Etiqueta
  SELECT id INTO v_etiqueta_id FROM etiquetas WHERE nombre_etiqueta = 'IA' LIMIT 1;
  INSERT INTO recurso_etiqueta (recurso_id, etiqueta_id) VALUES (v_recurso_id, v_etiqueta_id);

END $$;
