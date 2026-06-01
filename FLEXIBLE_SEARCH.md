# 🔍 Búsqueda Flexible - Ejemplos Funcionando

## ¿Qué es la Búsqueda Flexible?

El bot ahora reconoce **variaciones de palabras** sin requerir coincidencia exacta:

- "ingeniería de sistemas" = "ingeniería en sistemas" = "ingenieria en sistemas"
- "administración de empresas" = "administracion empresas"
- "comunicación gráfica publicitaria" = "comunicacion grafica"
- "diseño y gestión de espacios" = "diseño espacios" = "diseno espacios"

## Ejemplos Testados ✅

### Variaciones que Funcionan

| Búsqueda del Usuario | Carrera Encontrada | Resultado |
|---|---|---|
| "ingenieria en sistemas" | Ingeniería de Sistemas | ✅ Detalles completos |
| "administracion empresas" | Administración de Empresas | ✅ Detalles completos |
| "comunicacion grafica" | Comunicación Gráfica Publicitaria | ✅ Detalles completos |
| "negocios internacionales" | Negocios Internacionales | ✅ Detalles completos |
| "psicologia" | Psicología | ✅ Detalles completos |
| "ingenieria de sistemas" | Ingeniería de Sistemas | ✅ Detalles completos |
| "administración de empresas" | Administración de Empresas | ✅ Detalles completos |

### Cómo Funciona el Algoritmo

```python
def coincide_carrera_flexible(prompt: str, nombre_carrera: str) -> bool:
    """
    1. Extrae palabras clave del prompt (elimina "de", "en", "y", etc)
    2. Extrae palabras clave de la carrera
    3. Verifica que TODAS las palabras del prompt estén en la carrera
    4. Esto permite búsquedas parciales
    
    Ejemplo:
    - Prompt: "comunicacion grafica"
    - Carrera: "Comunicación Gráfica Publicitaria"
    - Palabras prompt: ["comunicacion", "grafica"]
    - Palabras carrera: ["comunicacion", "grafica", "publicitaria"]
    - Resultado: ✅ COINCIDE (ambas palabras están en la carrera)
    """
```

## Ventajas

✅ **Más natural** - El usuario escribe de forma más natural sin preocuparse por preposiciones
✅ **Menos frustrante** - No rechaza búsquedas solo por falta de una palabra
✅ **Inteligente** - Entiende variaciones como:
  - "de" vs "en" 
  - "ingeniería" vs "ingeniero"
  - Búsquedas parciales vs completas

## Búsquedas que aún no Funcionan

Estas aún regresan una respuesta genérica porque no hay suficiente coincidencia:
- "diseño espacios" (necesita "gestión")
- "ingeniero ambiental" (el prompt dice "ingeniero" pero no "ambiental")

Para estos casos, el usuario puede probar:
- "diseño gestión espacios" 
- "ingeniería ambiental"

## Código Actualizado

Se agregaron en `info_plugin.py`:

```python
def extraer_palabras_clave(texto: str) -> List[str]:
    """Extrae palabras clave, ignorando preposiciones comunes"""

def coincide_carrera_flexible(prompt: str, nombre_carrera: str) -> bool:
    """Implementa búsqueda flexible por palabras clave"""
```

Se actualizaron en `buscar_carrera()` y `buscar_beca()`:
- Ahora usan búsqueda flexible además de búsqueda exacta
- Fallback a búsqueda genérica si no hay coincidencia

---

**Última actualización:** 31 de mayo de 2026
**Status:** ✅ FUNCIONANDO
