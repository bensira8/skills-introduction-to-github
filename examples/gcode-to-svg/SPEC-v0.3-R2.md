# SPEC v0.3-R2 (CROQ2D)

Estado: congelado para compilación determinista.

## Cambios aceptados
- P10: `ARRAY` con dirección explícita de crecimiento.
- P11: soporte de `paso_x` y `paso_y` (con prioridad sobre `paso`).
- P12: contrato geométrico explícito para `ORIGIN=CENTER`.

## Reglas normativas

### 1) ARRAY determinista
Cuando `ARRAY` use `ref`, el campo `dir` es obligatorio.

Ejemplo válido:

```text
ARRAY cmd=CIRCLE ref=B1 cx=40 cy=40 d=10 nx=2 ny=2 paso=80 dir=LEFT_DOWN layer=CUT_INNER
```

Semántica de `dir=LEFT_DOWN`:
- columnas: avance en `-X`
- filas: avance en `-Y`

Si falta `dir` con `ref` presente, el compilador **debe fallar** con error:
`E_ARRAY_DIR_REQUIRED`.

### 2) Paso unificado
- Si existe `paso`, se interpreta como:
  - `paso_x = paso`
  - `paso_y = paso`
- Si existen `paso_x` y/o `paso_y`, **dominan** sobre `paso`.

Errores sugeridos:
- `E_ARRAY_STEP_INVALID` si algún paso es `<= 0`.
- `E_ARRAY_STEP_MISSING` si no hay `paso` ni (`paso_x`,`paso_y`).

### 3) Anclaje explícito
Para evitar ambigüedad en `ref`, se define `anchor` explícito.
Valores recomendados: `TOP_LEFT`, `TOP_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_RIGHT`, `CENTER`.

Si `ref` existe y no se puede inferir anclaje de forma inequívoca, exigir `anchor` o fallar con:
`E_ARRAY_ANCHOR_REQUIRED`.

### 4) Contrato de coordenadas con ORIGIN=CENTER
Con `ORIGIN=CENTER`, `x,y` siempre representa el centro geométrico del objeto.

Ejemplo:

```text
RECT x=0 y=0 w=310 h=130
```

Implica:
- límites X: `-155 .. +155`
- límites Y: `-65 .. +65`

### 5) Intención geométrica por capa
- `CUT_OUTER`, `CUT_INNER`: geometría de fabricación (corte).
- `MARK`: geometría de referencia visual/no cortable.

Regla: si un elemento no debe cortar material, usar `MARK`.

## Bloque canónico v0.3-R2

```text
PIECE id=panel_frontal W=310 H=130 UNIT=mm ORIGIN=CENTER Y_AXIS=UP KERF=0.15 STROKE=0.1
RECT x=0 y=0 w=310 h=130 layer=CUT_OUTER
CIRCLE cx=0 cy=0 d=68 layer=CUT_INNER
ARRAY cmd=CIRCLE ref=B1 cx=40 cy=40 d=10 nx=2 ny=2 paso=80 dir=LEFT_DOWN layer=CUT_INNER
END
```

## Errores comunes
- Usar `ref` sin `dir`.
- Definir `paso` con valor no positivo.
- Mezclar intención de fabricación (`CUT_*`) con referencia visual (debe ser `MARK`).
