# ZyEdit — hallazgos

> **Qué es este documento.** El registro de lo que ZyEdit descubre sobre **el lenguaje**, no
> sobre el editor. Es el artefacto primario del proyecto (`zymbol-design/LDV.md` § 3, punto 6).
>
> **Forma.** La canónica de `LDV.md` § 5.2: secciones `BUG` / `GAP` / `ERROR` / `IDEA`, tabla
> resumen arriba e identificadores con ámbito de proyecto desde la primera entrada. El ámbito es
> `ZYE`. Como en GoL, la numeración es **una sola secuencia para todos los tipos**, así que
> `ZYE-005` nombra un único hallazgo sea cual sea su tipo.
>
> **Un tipo más: `DIS`, hallazgo de diseño.** Lo propuso el autor el 2026-10-20 para los
> hallazgos que aparecen **al diseñar la aplicación, antes de escribirla**. Salen de sondear el
> lenguaje con un programa mínimo que pregunta lo que la aplicación va a necesitar. No es el
> método LDV en sentido estricto: allí el hallazgo sale de escribir la aplicación como si el
> lenguaje lo permitiera (`LDV.md` § 4, «RED»). Pero se tratan igual en todo lo demás:
> - llevan un programa que los reproduce;
> - se cierran con un cambio del lenguaje o con un rechazo razonado;
> - no se dan por cerrados hasta que un caso mínimo vive en `zyquality/` o en ZyDDT (punto 7
>   del decálogo).
>
> Se separan para que nadie lea un `DIS` como algo que la aplicación encontró escribiéndose.
>
> **Estado del ciclo.** Abierto el 2026-10-20, antes de la primera línea del editor. Hay cinco
> hallazgos de diseño, **los cinco abiertos y sin decidir**. DIS-ZYE-001 bloquea la etapa 1
> del `README.md` (Supr, Inicio/Fin, RePág/AvPág) y DIS-ZYE-002 la selección de la etapa 2.
>
> **La evidencia vive en [`hypotheses/`](hypotheses/)**: un programa por pregunta, un `check.py`
> que da un veredicto por hallazgo (`HOLDS` o `FIXED`) y la respuesta guardada en
> `evidence/<fecha>.txt` con el binario y el commit. Después del arreglo, la misma comprobación
> confirma que está corregido. Luego la pregunta pasa a `zyquality/tui/` o a ZyDDT, y solo
> entonces se cierra el hallazgo. `hypotheses/README.md` describe ese ciclo.

---

## Resumen

| ID | Tipo | Módulo | Contexto | Estado |
|----|------|--------|----------|--------|
| [DIS-ZYE-001](#dis-zye-001) | DIS | entrada de teclado (los 2 motores con terminal) | Inicio, Fin, RePág, AvPág, Supr, F1–F12 y Shift+Tab llegan **todas como `0d0`**, el mismo valor con el que `<<\|?` dice «no hay tecla» | **abierto** · sin decidir |
| [DIS-ZYE-002](#dis-zye-002) | DIS | entrada de teclado | un modificador sobre una tecla que no es letra **se pierde**: Shift+→ y Ctrl+→ llegan como → | **abierto** · sin decidir |
| [DIS-ZYE-003](#dis-zye-003) | DIS | entrada de teclado | tres combinaciones llegan **disfrazadas de una tecla imprimible**: Ctrl+/ como `7`, Ctrl+Espacio como espacio, Alt+x como `x` | **abierto** · sin decidir |
| [DIS-ZYE-004](#dis-zye-004) | DIS | `>>\|` | dentro de `>>\|` el cursor del terminal está **oculto**, y nada en el lenguaje lo muestra ni lo coloca | **abierto** · sin decidir |
| [DIS-ZYE-005](#dis-zye-005) | DIS | procesos / el lenguaje | las comprobaciones de las hipótesis **no se pueden escribir en Zymbol**: ningún programa puede arrancar otro en un terminal, mandarle teclas y leer lo que dibuja | **abierto** · sin decidir |

---

## Las hipótesis

Las comprobaciones viven en [`hypotheses/`](hypotheses/), una carpeta por pregunta:

| carpeta | hallazgos | qué pregunta |
|---|---|---|
| [`hypotheses/keys/`](hypotheses/keys/) | 001, 002, 003 | qué devuelve `<<\|` para cada tecla que necesita un editor con atajos de GUI |
| [`hypotheses/cursor/`](hypotheses/cursor/) | 004 | si dentro de `>>\|` se llega a mostrar el cursor del terminal |

Cada `check.py` arranca el programa por un **pty de verdad** en los dos motores, les manda los
bytes que manda xterm (que son los que manda casi cualquier emulador) y da un veredicto por
hallazgo. Falla si los motores no coinciden antes de dar ninguno. No se puede hacer con
`zymbol run --keys`: el guion entrega al programa teclas ya decodificadas, y lo que se pregunta
es justamente la decodificación. Que estas comprobaciones sean Python es DIS-ZYE-005.

```bash
bash hypotheses/run.sh                      # todas; sale con 1 mientras alguna siga en pie
python3 hypotheses/keys/check.py --table    # y el valor de cada tecla
```

Medido el 2026-10-20 con el binario de release de `interpreter` en `c3468c1` (rama `v0.0.11`),
y guardado en `hypotheses/*/evidence/2026-10-20.txt`. **Los dos motores dan la misma
respuesta**, como era de esperar: los dos traducen la tecla con una función `map_key_code` que
debe coincidir. Están en `crates/zymbol-host/src/lib.rs` (VM) y
`crates/zymbol-interpreter/src/io.rs` (tree-walker).

| tecla | bytes enviados | `<<\|` devuelve | |
|---|---|---|---|
| Ctrl+Z | `1a` | 26 | correcto |
| Ctrl+S | `13` | 19 | correcto |
| Ctrl+C | `03` | 3 | correcto: en modo raw no hay SIGINT |
| Ctrl+Q | `11` | 17 | correcto: en modo raw no hay XON/XOFF |
| Ctrl+V | `16` | 22 | correcto |
| Ctrl+H | `08` | 8 | correcto, y distinto del retroceso (127) |
| Ctrl+I | `09` | 9 | es el tabulador: el terminal manda el mismo byte (ver abajo) |
| Inicio | `1b 5b 48` | **0** | DIS-ZYE-001 |
| Fin | `1b 5b 46` | **0** | DIS-ZYE-001 |
| Supr | `1b 5b 33 7e` | **0** | DIS-ZYE-001 |
| RePág | `1b 5b 35 7e` | **0** | DIS-ZYE-001 |
| AvPág | `1b 5b 36 7e` | **0** | DIS-ZYE-001 |
| F1 | `1b 4f 50` | **0** | DIS-ZYE-001 |
| Shift+Tab | `1b 5b 5a` | **0** | DIS-ZYE-001 |
| Shift+→ | `1b 5b 31 3b 32 43` | **8594** (→) | DIS-ZYE-002 |
| Ctrl+→ | `1b 5b 31 3b 35 43` | **8594** (→) | DIS-ZYE-002 |
| Ctrl+/ | `1f` | **55** (`7`) | DIS-ZYE-003 |
| Ctrl+Espacio | `00` | **32** (espacio) | DIS-ZYE-003 |
| Alt+x | `1b 78` | **120** (`x`) | DIS-ZYE-003 |

Las siete primeras filas también se comprueban, y en sentido contrario: si un arreglo las
rompiera, `keys/check.py` sale con 4 («regresión») aunque los tres hallazgos estén corregidos.

**Lo que el autor temía no ocurre.** Ctrl+Z, Ctrl+S y el resto de Ctrl+letra llegan bien desde
la v0.0.9, cuando se corrigió BUG-ZYB-006 (`ZyBank/HALLAZGOS.md`). Ese arreglo enseñó a
`map_key_code` el modificador Control **sobre una letra** y nada más. Los tres primeros
hallazgos son el resto de aquella misma función.

---

## DIS-ZYE-001

**Inicio, Fin, RePág, AvPág, Supr, F1–F12 y Shift+Tab llegan todas como `0d0`.**

`map_key_code` termina en `_ => '\0'`. Cualquier tecla que no sea una letra, una flecha, Enter,
Esc, Tab o retroceso cae ahí. Se pierde información de dos maneras:

1. **Siete teclas, un valor.** Un programa no puede distinguir Inicio de Supr, ni RePág de F1.
2. **Ese valor ya significa otra cosa.** `GUIDE.md` § 3b dice que `<<|?` devuelve `'\0'` cuando
   no hay ninguna tecla pendiente. En un bucle que sondea con `<<|?`, pulsar Supr es
   indistinguible de no pulsar nada.

Para ZyEdit esto deja fuera de la etapa 1 cuatro cosas que cualquier editor tiene: borrar hacia
delante, ir al principio y al final de la línea, y avanzar y retroceder una pantalla. Para un
editor «con los atajos de una GUI», que es lo que el autor pidió, son las teclas más usadas
después de las flechas.

**`--keys` tiene el mismo hueco.** Su guion admite `UP`, `DOWN`, `LEFT`, `RIGHT`, `ENTER`, `ESC`,
`TAB`, `BACKSPACE`, `SPACE` y `CTRL+letra`. Un arreglo que solo tocase `<<|` dejaría las teclas
nuevas sin forma de probarse en la puerta. Los dos tienen que cambiar juntos.

**Lo esperable** sería que cada una de estas teclas llegase con un valor propio, distinto de
`0d0`. Cómo se escribe ese valor lo decide el autor. Las flechas ya llegan como glifos
(`↑ ↓ ← →`), y ese es el precedente más cercano dentro del propio lenguaje.

---

## DIS-ZYE-002

**Un modificador sobre una tecla que no es letra se pierde: Shift+→ y Ctrl+→ llegan como →.**

`map_key_code` solo mira los modificadores cuando la tecla es una letra con Control. En el
resto los descarta. Shift+→ llega como →, y lo mismo Ctrl+→ y, por la misma rama, Alt+→,
Shift+↑ y cualquier otra combinación con flecha.

Esto es peor que no llegar. Un editor tipo GUI selecciona con Shift+flecha y salta por palabras
con Ctrl+flecha. En ZyEdit, hoy, Shift+→ **movería el cursor sin seleccionar nada**: el usuario
pide una cosa y obtiene otra, sin aviso. Es la misma clase que BUG-ZYB-006: la tecla llega
disfrazada de otra.

La selección es el corazón de la etapa 2 (copiar, cortar, pegar), así que este hallazgo la
bloquea entera mientras siga abierto.

**Lo esperable** sería poder preguntar por el modificador. Un carácter por tecla no basta para
eso: las flechas son cuatro, los modificadores tres, y sus combinaciones no caben en una tabla
de glifos razonable. La forma de la respuesta, incluido si `<<|` debe devolver algo más que un
carácter, es una decisión de diseño del autor.

---

## DIS-ZYE-003

**Tres combinaciones llegan disfrazadas de una tecla imprimible.**

| combinación | el terminal manda | crossterm la entrega como | `<<\|` devuelve |
|---|---|---|---|
| Ctrl+/ | `1f` | `Char('7')` + Control | `7` |
| Ctrl+Espacio | `00` | `Char(' ')` + Control | espacio |
| Alt+x | `1b 78` | `Char('x')` + Alt | `x` |

En los tres casos `map_key_code` ve un `Char` cuyo modificador no es «Control sobre una letra»,
lo descarta y devuelve el carácter. Para un editor eso significa **escribir texto**:
- Ctrl+/, el atajo de comentar una línea en VS Code, insertaría un `7`;
- Ctrl+Espacio, el de pedir sugerencias (que importará en la etapa 4), insertaría un espacio;
- cualquier atajo con Alt insertaría su letra.

Es exactamente el fallo que BUG-ZYB-006 describió para Ctrl+letra: *«llega, disfrazada de otra
tecla, que es peor — un atajo `Ctrl+X` se dispararía al escribir una `x` en un campo de texto»*.
Aquí ocurre al revés: el atajo escribe la letra.

Que Ctrl+/ salga como `7` lo decide la tabla de crossterm, no Zymbol: `1f` es también lo que
manda Ctrl+7 en muchos terminales. Que llegue como un `7` imprimible sí es de Zymbol.

**Lo esperable**, como mínimo, es que una combinación con modificador no llegue nunca como un
carácter imprimible que el programa vaya a insertar. Lo más probable es que el arreglo sea el
mismo que el de DIS-ZYE-002.

---

## DIS-ZYE-004

**Dentro de `>>|` el cursor del terminal está oculto, y nada en el lenguaje lo muestra ni lo
coloca.**

Los dos motores ejecutan `cursor::Hide` al entrar en `>>|` (`zymbol-host/src/lib.rs`,
`zymbol-interpreter/src/io.rs`). Solo lo vuelven a mostrar mientras dura una lectura de línea
`<<` dentro del bloque, y al salir. `>>~` coloca la *salida*, no el cursor visible, y
`GUIDE.md` § 3b no tiene ninguna primitiva para el cursor.

Para un juego es lo correcto: ningún juego quiere un cursor parpadeando sobre el tablero. Para
un editor no lo es. El cursor es el sitio donde va a caer la siguiente letra, y el terminal sabe
dibujarlo con la forma, el parpadeo y el color que el usuario configuró.

Sin él, ZyEdit tiene que **dibujar su propio caret**, una celda pintada con color de fondo
mediante `>>~`. Funciona y se puede escribir hoy, pero:
- no parpadea ni respeta la forma que el usuario eligió (barra, bloque o subrayado);
- obliga a redibujar dos celdas en cada movimiento;
- un lector de pantalla, que sigue el cursor del terminal, no sabe dónde está el usuario.

Que el caret dibujado se pueda escribir hace que este hallazgo no bloquee la etapa 1. Por eso
queda como `DIS` y no como incapacidad. Escribir a mano la secuencia de escape (`ESC [ ? 25 h`)
con `>>` sería salir del lenguaje y contaría como rojo (decálogo, punto 4); no se hace.

**Lo esperable** sería poder decir, dentro de `>>|`, «muestra el cursor aquí».

---

## DIS-ZYE-005

**Las comprobaciones de las hipótesis no se pueden escribir en Zymbol.**

`hypotheses/keys/check.py` y `hypotheses/cursor/check.py` son Python, y no por comodidad. Hacen
cuatro cosas, y ninguna tiene equivalente en el lenguaje:

1. **Arrancar otro programa con un terminal propio** (`pty.fork`). Lo único que arranca algo
   en Zymbol es `<\ cmd \>`, que ejecuta una orden del sistema hasta el final y devuelve su
   salida, y `</ app.zy />`, que ejecuta un programa Zymbol y captura lo que imprime. Ninguno
   de los dos le da un terminal, así que el programa hijo no puede entrar en `>>|`.
2. **Darle un tamaño a ese terminal** (`TIOCSWINSZ`), para que `>>?` conteste algo real.
3. **Escribirle bytes mientras corre**, intercalados con la lectura: una tecla, esperar lo que
   dibuja, la siguiente.
4. **Leer lo que escribe sin bloquearse para siempre**, con un plazo (`select`).

Leer las secuencias de escape que vuelven (`ESC [ fila ; col H`, `ESC [ ? 25 h`) sí se podría
escribir en Zymbol. Lo que falta es todo lo anterior.

**No es el primer hallazgo de esta familia.**
[GAP-GOL-009](../GoL/HALLAZGOS.md#gap-gol-009) decía lo mismo desde el otro lado: *«an
interactive Zymbol program cannot be tested from Zymbol»*. Se cerró el 2026-09-30 con
`zymbol run --keys`, la pantalla virtual. Esa solución resolvió lo que GoL necesitaba: probar
lo que su editor *dibuja*. Por diseño dejó fuera la decodificación real del terminal, y la
resolución lo dice: *«`zyquality/tui/`'s pty driver stays: it tests the real terminal path —
how crossterm decodes an arrow — which a virtual screen by design does not touch»*. Los
hallazgos 001 a 003 están exactamente en ese camino, así que sus pruebas no pueden usar
`--keys` y tienen que salir del lenguaje. Su tercer punto (*«nothing in the language or in
`std/*` starts another process at all, let alone one with a terminal attached»*) sigue tal
cual.

**Por qué importa más allá de las pruebas.** Lo que hacen estos dos `check.py` es, en pequeño,
lo que tendrá que hacer ZyEdit:
- **la etapa 5** (un panel de terminal al estilo de VS Code) necesita los cuatro puntos:
  arrancar un shell en un pty, darle tamaño, mandarle las teclas del usuario y leer lo que
  dibuja sin congelar el editor;
- **la etapa 4** (el cliente de `zymbol lsp`) necesita el 1, el 3 y el 4, sin pty: un proceso
  vivo con el que se habla por su entrada y su salida.

Así que este hallazgo aparece tres veces: en las pruebas de hoy y en dos etapas del editor. Si
se aceptara solo como «las pruebas de terminal se quedan en Python», como en GAP-GOL-009, las
etapas 4 y 5 lo reabrirían.

**Lo esperable** sería que un programa Zymbol pudiera arrancar otro, hablar con él mientras
corre y, cuando haga falta, darle un terminal. Si eso es un módulo de `std/`, un símbolo o nada
en absoluto lo decide el autor, y un símbolo nuevo pasaría primero por
`zymbol-design/SYMBOLS.md` § 17, las reglas de diseño de operadores nuevos.

**Su «después»** es uno de los dos `check.py` reescrito en Zymbol, con el mismo veredicto que el
de Python.

---

## Lo que impone el terminal, y no es un hallazgo

Se apunta aquí para que nadie lo archive como fallo del lenguaje. Son límites del protocolo de
teclado de los terminales, iguales para cualquier programa en cualquier lenguaje:

- **Ctrl+Shift+letra es el mismo byte que Ctrl+letra.** Ctrl+Shift+S no se distingue de Ctrl+S.
  Por eso ZyEdit rehará con **Ctrl+Y**, no con Ctrl+Shift+Z.
- **Ctrl+I es Tab, Ctrl+M es Enter y Ctrl+[ es Esc**: el terminal manda el mismo byte. Ninguno de
  los tres puede ser un atajo propio.
- **El emulador se queda algunas combinaciones antes de que lleguen**: Ctrl+Shift+C/V (copiar y
  pegar del propio emulador), Ctrl+RePág/AvPág y Ctrl+Tab (sus pestañas), F11 (pantalla
  completa). Cuáles depende del emulador; ZyEdit no debe depender de ninguna de ellas.
- **El portapapeles del sistema no es del terminal.** Pegar desde fuera llega como teclas
  escritas, y copiar hacia fuera necesita OSC 52, que no todos los emuladores aceptan. La etapa 2
  empieza con un portapapeles interno.

El protocolo de teclado de kitty, que ya aceptan varios emuladores, resuelve las dos primeras
(distingue Ctrl+Shift+S y Ctrl+I de Tab). Pedírselo al terminal sería un cambio del lenguaje,
no de ZyEdit, y se plantearía junto a DIS-ZYE-002 si el autor lo considera.
