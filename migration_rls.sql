-- Migración: Agregar Row Level Security (RLS)
-- Ejecutar este script en Supabase SQL Editor para aplicar RLS a una base de datos existente

-- 1. ACTIVAR RLS en todas las tablas
ALTER TABLE public.recursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.autores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.etiquetas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.colecciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recurso_autor ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recurso_etiqueta ENABLE ROW LEVEL SECURITY;

-- 2. POLÍTICAS PARA RECURSOS
-- Todos pueden ver recursos
CREATE POLICY "Público puede ver recursos" ON public.recursos
  FOR SELECT
  USING (true);

-- Solo usuarios autenticados pueden insertar
CREATE POLICY "Solo admins insertan recursos" ON public.recursos
  FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

-- Solo usuarios autenticados pueden actualizar
CREATE POLICY "Solo admins actualizan recursos" ON public.recursos
  FOR UPDATE
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

-- Solo usuarios autenticados pueden eliminar
CREATE POLICY "Solo admins eliminan recursos" ON public.recursos
  FOR DELETE
  USING (auth.role() = 'authenticated');

-- 3. POLÍTICAS PARA AUTORES
CREATE POLICY "Público puede ver autores" ON public.autores
  FOR SELECT
  USING (true);

CREATE POLICY "Solo admins modifican autores" ON public.autores
  FOR ALL
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

-- 4. POLÍTICAS PARA ETIQUETAS
CREATE POLICY "Público puede ver etiquetas" ON public.etiquetas
  FOR SELECT
  USING (true);

CREATE POLICY "Solo admins modifican etiquetas" ON public.etiquetas
  FOR ALL
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

-- 5. POLÍTICAS PARA COLECCIONES
CREATE POLICY "Público puede ver colecciones" ON public.colecciones
  FOR SELECT
  USING (true);

CREATE POLICY "Solo admins modifican colecciones" ON public.colecciones
  FOR ALL
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

-- 6. POLÍTICAS PARA RECURSO_AUTOR
CREATE POLICY "Público puede ver recurso_autor" ON public.recurso_autor
  FOR SELECT
  USING (true);

CREATE POLICY "Solo admins modifican recurso_autor" ON public.recurso_autor
  FOR ALL
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

-- 7. POLÍTICAS PARA RECURSO_ETIQUETA
CREATE POLICY "Público puede ver recurso_etiqueta" ON public.recurso_etiqueta
  FOR SELECT
  USING (true);

CREATE POLICY "Solo admins modifican recurso_etiqueta" ON public.recurso_etiqueta
  FOR ALL
  USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

-- NOTA: Después de ejecutar este script, verifica que las políticas se aplicaron correctamente:
-- SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';
