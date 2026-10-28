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
> **Decisión (2026-10-26):** los hallazgos se atienden en la **v0.0.12**; ZyEdit sigue
> escribiéndose con apaños declarados.
>
> **Estado del ciclo (2026-10-27).** Abierto el 2026-10-20, antes de la primera línea del
> editor, con cinco hallazgos de diseño. Escribir las etapas 1 y 2 (2026-10-26 y 27) trajo
> nueve más, y usarlo uno (el 015). Son **quince, todos abiertos y para la v0.0.12**; el 008 está retirado como
> incapacidad y sigue abierto como error sin guía. Ninguno bloquea ya una etapa: donde el
> lenguaje no llega, ZyEdit usa un apaño declarado en la ficha (teclas Ctrl provisionales para
> 001 y 002, caret dibujado para 004, sondeo para 012…).
>
> **La evidencia vive en [`hypotheses/`](hypotheses/)**: un programa por pregunta, una
> comprobación que da un veredicto por hallazgo (`HOLDS` o `FIXED`) y la respuesta guardada en
> `evidence/<fecha>.txt` con el binario y el commit. Después del arreglo, la misma comprobación
> confirma que está corregido. Luego la pregunta pasa a `zyquality/tui/`, a `zyquality/cost/` o
> a ZyDDT, y solo entonces se cierra el hallazgo. `hypotheses/README.md` describe ese ciclo.

---

## Resumen

| ID | Tipo | Módulo | Contexto | Estado |
|----|------|--------|----------|--------|
| [DIS-ZYE-001](#dis-zye-001) | DIS | entrada de teclado (los 2 motores con terminal) | Inicio, Fin, RePág, AvPág, Supr, F1–F12 y Shift+Tab llegan **todas como `0d0`**, el mismo valor con el que `<<\|?` dice «no hay tecla» | **abierto** · para v0.0.12 |
| [DIS-ZYE-002](#dis-zye-002) | DIS | entrada de teclado | un modificador sobre una tecla que no es letra **se pierde**: Shift+→ y Ctrl+→ llegan como → | **abierto** · para v0.0.12 |
| [DIS-ZYE-003](#dis-zye-003) | DIS | entrada de teclado | tres combinaciones llegan **disfrazadas de una tecla imprimible**: Ctrl+/ como `7`, Ctrl+Espacio como espacio, Alt+x como `x` | **abierto** · para v0.0.12 |
| [DIS-ZYE-004](#dis-zye-004) | DIS | `>>\|` | dentro de `>>\|` el cursor del terminal está **oculto**, y nada en el lenguaje lo muestra ni lo coloca | **abierto** · para v0.0.12 |
| [DIS-ZYE-005](#dis-zye-005) | DIS | procesos / el lenguaje | las comprobaciones de las hipótesis **no se pueden escribir en Zymbol**: ningún programa puede arrancar otro en un terminal, mandarle teclas y leer lo que dibuja | **abierto** · para v0.0.12 |
| [GAP-ZYE-006](#gap-zye-006) | GAP | `std/io` | un fichero que no es UTF-8 válido **no se puede abrir**: `io::read` devuelve `##IO(stream did not contain valid UTF-8)` y no hay lectura de bytes | **abierto** · para v0.0.12 |
| [GAP-ZYE-007](#gap-zye-007) | GAP | cadenas / `std/term` | el lenguaje no segmenta en **clústeres de grafemas**: un `Char` es un punto de código, y el editor tiene que aproximar el clúster a mano con `t::width(c) == 0` | **abierto** · para v0.0.12 |
| [GAP-ZYE-008](#gap-zye-008) | GAP | texto → número | ~~no hay forma de leer `"42"` como Int~~ — `#\|texto\|` lo hace; lo que falla es que `###"42"` y `##."42"` no dicen que existe | **retirado como incapacidad** · el error sin guía sigue abierto para v0.0.12 |
| [BUG-ZYE-009](#bug-zye-009) | BUG | parser | ~~`lines$-[r1 + 1..r2]` y~~ `@ i:r1 + 1..r2 - 1` falla en los dos motores de Rust con *«ranges can only be used in for-each loops»*: el `..` toma por la izquierda sólo el último operando; zyjs lo acepta | **abierto** · para v0.0.12 |
| [GAP-ZYE-010](#gap-zye-010) | GAP | cadenas | no se encuentra conversión de mayúsculas a minúsculas (ni al revés): buscar sin distinguirlas exige una tabla propia, y sólo ASCII | **abierto** · para v0.0.12 |
| [BUG-ZYE-011](#bug-zye-011) | BUG | `zymbol-vm` | tras `(a, k) = v[1]` y `v[1]$~ otra`, la VM copia entero el array `a` en la primera edición; el tree-walker no copia nada | **abierto** · para v0.0.12 |
| [GAP-ZYE-012](#gap-zye-012) | GAP | `<<\|` / terminal | un programa bloqueado en `<<\|` no se entera de que la ventana cambió de tamaño: no sale ningún valor ni señal hasta la tecla siguiente | **abierto** · para v0.0.12 |
| [BUG-ZYE-013](#bug-zye-013) | BUG | `zyjs` (lexer) | dentro de una cadena, `"\r"` se lee como la letra `r`; los dos motores de Rust, y el propio zyjs en un literal de carácter `'\r'`, dan el retorno de carro | **abierto** · para v0.0.12 |
| [BUG-ZYE-014](#bug-zye-014) | BUG | colecciones (los 2 motores de Rust) | insertar en una posición (`a$+[i] v`) y quitar un rango (`a$-[i..j]`) **cuestan el array entero** aunque tenga un solo dueño: el tree-walker copia sus n valores y la VM reserva n huecos; `a$-[i]` y `a[i]$~ v` cuestan uno | **abierto** · para v0.0.12 |
| [GAP-ZYE-015](#gap-zye-015) | GAP | `>>\|` / salida | no hay **fotograma**: cada `>>~` llega al terminal por separado y ningún programa puede enseñar una pantalla entera de una vez, así que un repintado se ve mientras se dibuja (desde el 2026-10-27, una escritura por `>>~` y no cuatro) | **abierto** · la 2 para v0.0.12 |

---

## Las hipótesis

Las comprobaciones viven en [`hypotheses/`](hypotheses/), una carpeta por pregunta:

| carpeta | hallazgos | qué pregunta |
|---|---|---|
| [`hypotheses/keys/`](hypotheses/keys/) | 001, 002, 003 | qué devuelve `<<\|` para cada tecla que necesita un editor con atajos de GUI |
| [`hypotheses/cursor/`](hypotheses/cursor/) | 004 | si dentro de `>>\|` se llega a mostrar el cursor del terminal |
| [`hypotheses/replaced_tuple/`](hypotheses/replaced_tuple/) | 011 | cuánto copia cada motor al editar lo que había en una tupla cuyo hueco se reemplazó |
| [`hypotheses/resize/`](hypotheses/resize/) | 012 | si un programa que espera en `<<\|` se entera de que la ventana cambió de tamaño |
| [`hypotheses/string_cr/`](hypotheses/string_cr/) | 013 | qué hace cada motor con `"\r"` dentro de una cadena |
| [`hypotheses/mid_array/`](hypotheses/mid_array/) | 014 | cuánto cuesta una edición en medio de un array de 10 000 elementos |
| [`hypotheses/frame/`](hypotheses/frame/) | 015 | en cuántas escrituras llega al terminal un fotograma dibujado con `>>!` y `>>~` |

Las cuatro de terminal (`keys`, `cursor`, `resize`, `frame`) arrancan el programa por un **pty de verdad**
en los dos motores, les mandan los bytes que manda xterm (que son los que manda casi cualquier
emulador) y dan un veredicto por hallazgo. Fallan si los motores no coinciden antes de dar
ninguno. No se pueden hacer con `zymbol run --keys`: el guion entrega al programa teclas ya
decodificadas, y lo que se pregunta es justamente la decodificación. Que sean Python es
DIS-ZYE-005. Las dos de coste (`replaced_tuple`, `mid_array`) miden con `--count`, que es exacto,
y llevan programas de control que deben seguir costando lo mismo. `string_cr` compara la salida
de los tres motores.

```bash
bash hypotheses/run.sh                      # todas; sale con 1 mientras alguna siga en pie
python3 hypotheses/keys/check.py --table    # y el valor de cada tecla
```

Medido el 2026-10-20 con el binario de release de `interpreter` en `9666867` (rama `v0.0.11`),
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

**Lo que ZyEdit hace mientras tanto** (2026-10-26), y cuenta como rojo (decálogo, punto 4):
teclas Ctrl propias. Ctrl+D borra hacia delante, Ctrl+U y Ctrl+E van al principio y al final
de la línea, y Ctrl+P y Ctrl+L suben y bajan una pantalla. Son cinco letras que un editor de GUI
usa para otra cosa, y por eso lo que se usa poco vive detrás de Ctrl+G (`README.md`, «The keys
that stand in until v0.0.12»).

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
habría bloqueado entera.

**Lo que ZyEdit hace mientras tanto** (2026-10-27, rojo): Ctrl+B empieza y termina una
selección, y mientras está activa las flechas la extienden, en lugar de Shift+flecha. Mover el
cursor por palabras y buscar hacia atrás no tienen tecla, y esperan a Ctrl+flecha.

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

**Lo que ZyEdit hace mientras tanto** (2026-10-26): dibujar el caret. `render` pinta con colores
invertidos el clúster que hay bajo el cursor, o un espacio al final de la línea, y
`tests/pty/check.py` comprueba en un terminal de verdad que se dibuja así.

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

## GAP-ZYE-006

**Un fichero que no es UTF-8 válido no se puede abrir, ni leer como bytes.**

Salió al escribir la etapa 1 (2026-10-26), con `tests/roundtrip.zy` (abre y guarda sin tocar) sobre
cinco ficheros. Cuatro vuelven byte a byte iguales en los dos motores: CRLF, sin salto final,
con marca BOM y con tabuladores y líneas vacías al final. El quinto, `bad \xff\xfe utf8\n`:

```
txt = io::read("bad.txt")      // ##IO(stream did not contain valid UTF-8)
```

Es un error suave, no corrompe nada, y eso está bien: **fallar cerrado es lo correcto**. Pero un
editor que sólo abre texto UTF-8 válido no puede abrir un Latin-1 antiguo, un binario ni un log
con una línea rota, y la promesa de ZyEdit era *devolver los bytes que recibió*. No existe en
`std/io` una lectura de bytes (ni una lectura con sustitución, que perdería los originales).

**Lo que ZyEdit hace mientras tanto** (2026-10-27): no abre ese fichero como un buffer vacío, que
Ctrl+S habría escrito encima del original; lo marca como no guardable, lo dice en la barra y
ofrece guardar en otro nombre (`tests/screen/locked.keys`; `tests/run.sh` comprueba además que el
original queda intacto). Se puede escribir en ese buffer vacío y guardarlo con otro nombre, pero
el contenido del fichero no se ve.

**Lo esperable:** una forma de leer y escribir bytes sin interpretarlos, y que lo que se lea con
ella sobreviva al viaje de vuelta. Si es una función de `std/io`, una variante de `read` o nada
(ZyEdit rechazaría esos ficheros con un mensaje) lo decide el autor.

---

## GAP-ZYE-007

**El lenguaje no segmenta en clústeres de grafemas, y un editor lo necesita en cada tecla.**

Salió al escribir el movimiento del cursor (2026-10-26). `"é"` escrito como `e` + U+0301 tiene
`$#` = 2, ancho 1, y el caret debe saltarlo de una vez; igual la familia 👨‍👩‍👧 (5 puntos de código,
ancho 2). `Char` es un punto de código a propósito (`##!` da ese número), así que nada del
lenguaje dice dónde acaba un clúster.

**El apaño, que cuenta como rojo** (decálogo, punto 4): `buffer.zy` (`continues`) decide que un
`Char` continúa al anterior si `t::width(c) == 0` (marca combinante o unión) o si el anterior es
U+200D. Con él, `tests/buffer.zy` mueve y borra por clústeres y los tres motores
coinciden en esos casos. Pero es una aproximación y falla donde el ancho no basta: pares de indicadores regionales (🇪🇸 son
dos puntos de código de ancho 2 cada uno), secuencias de jamo de hangul y modificadores de
tono de piel (que tienen ancho 2). Un clúster correcto es la regla UAX #29 y no está en el
lenguaje.

**Lo esperable:** una forma de recorrer o medir una cadena por clústeres (un operador, una
función de `std/term` o una variante de `$#` y de `$[..]`). Lo decide el autor; el módulo
`std/term` ya mide en el mismo sentido (columnas), así que sería su sitio natural.

**Su «después»:** `continues` desaparece de `buffer.zy`, y los mismos casos de `tests/buffer.zy`
más uno de banderas y otro de tono de piel dan el mismo golden.

---

## GAP-ZYE-008

> **CORREGIDO el mismo día (2026-10-26), y el enunciado era falso.** El lenguaje **sí** convierte
> un texto en número: `#|texto|` devuelve el Int, el Float o el texto intacto si no lo es.
> Lo ejecuta `corpus/casts/cifra_de_cualquier_escritura.zy`. Lo señaló el autor al preguntar si
> otro proyecto no lo había resuelto ya.
>
> ```zymbol
> #|"42"| → 42     #|"4.5"| → 4.5     #|"1x"| → "1x"     #|"-3"| → -3
> ```
>
> Es otro caso de lo que anota `GAP-ZYB-012`: se probó el operador contiguo al que respondía la
> pregunta. Aquí `###` y `##.`, que son *casts* de **números**, en vez de `#|…|`, la lectura.
> El hallazgo se queda, y no como una nota al pie, porque **que quien lo probó llegara a esa
> conclusión es evidencia de que la forma no se encuentra**.

**Lo que decía:** que no hay manera de convertir un texto en un número.

Salió con «Ir a línea» (Ctrl+G, 2026-10-26): el número llega tecleado, como texto. Se probó lo que
sugiere la forma de los casts hermanos:

```
###"42"      // Runtime error: ### requires a numeric value, got String
##."42"      // Runtime error: ##. requires a numeric value, got String
"12" + 1     // + is arithmetic only — use juxtaposition to concatenate strings
```

Con eso se escribió `to_number` sumando los dígitos a mano (`##!ch - 48`), un apaño rojo.

**Lo que pasa de verdad:** la conversión existe, y `to_number` es hoy una línea: `n = #|text|` y
un `? (n#?)[1] <> "###"` para aceptar sólo enteros. El apaño desapareció.

**Lo que sigue abierto**, y es de descubribilidad: los tres errores de arriba dicen *qué* falló y
ninguno dice *qué escribir*. Un cast con tres formas hermanas (`###`, `##.`, `##!`) y una cuarta
con otra sintaxis (`#|…|`) es un sitio donde buscar y no encontrar es lo esperable. Lo esperable,
de menos a más, a elegir por el autor:
1. **Un error que diga cómo se escribe**, como el `help:` de rustc o de clippy. Cuando `###` o
   `##.` reciben un String que no es un número: `= help: to read a text as a number, write
   #|texto|`. El mismo `help` en `"12" + 1`. No cambia el lenguaje.
2. **Un aviso estático** en `zymbol check` cuando el operando es un String conocido (un
   literal o una variable inferida), antes de ejecutar, con la misma ayuda.
3. **Reevaluar la forma**: que `###"42"` convierta, y `#|…|` quede como la variante segura que
   no falla. Es un cambio de lenguaje; se anota sólo como alternativa.

**Su «después»:** la sonda de arriba da un error con la línea de ayuda, y un caso en `zyquality/`
(o una celda de ZyDDT sobre mensajes) la sujeta.

---

## BUG-ZYE-009

> **CORREGIDO EN PARTE el 2026-10-27, al volver a ejecutarlo.** La primera línea del enunciado
> era falsa: `lines$-[r1 + 1..r2]` se parsea y da lo esperado en los tres motores, y es la forma
> que usa `buffer.zy` (`delete_range`) desde el principio. Lo que se sostiene es el bucle, y con
> un dato que entonces no se miró: zyjs **acepta** `@ i:r1 + 1..r2 - 1` y cuenta `2 3`, de modo
> que los tres motores no coinciden en qué programa es válido. La puerta no lo ve porque ningún
> caso del corpus escribe esa forma.
>
> ```zymbol
> r1 = 1
> r2 = 4
> @ i:r1 + 1..r2 - 1 { >> i " " }   // zyvm, zytw: error: ranges can only be used in for-each loops
> >> ¶                             // zyjs: 2 3
> ```

**Lo que decía:** que un rango con aritmética en el extremo izquierdo no se parsea, ni en un
`$-[…]` ni en un bucle:

```
lines = lines$-[r1 + 1..r2]        // decía: ranges can only be used in for-each loops
@ i:r1 + 1..r2 - 1 { }             // idem
@ i:(r1 + 1)..(r2 - 1) { }         // bien
```

**Lo que pasa de verdad:** sólo falla el bucle, y sólo en los dos motores de Rust. Allí
`r1 + 1..r2 - 1` se lee como `r1 + (1..r2) - 1`, y el mensaje, que habla de bucles, se da
precisamente dentro de uno, lo que lo hace más difícil de entender. Con paréntesis funciona en
los tres.

**Su «después»:** la línea sin paréntesis compila en los dos motores de Rust, como ya hace en
zyjs, o los tres la rechazan con un mensaje que diga que hay que parentizar los extremos. Lo
decide el autor; las dos salidas cierran la divergencia.

---

## GAP-ZYE-010

**No hay conversión de mayúsculas a minúsculas, y «buscar sin distinguir mayúsculas» la necesita.**

Salió al escribir el comando `case` de la búsqueda (2026-10-27). Se buscó en `GUIDE.md`,
`REFERENCE.md`, `SYMBOLS.md`, la tabla de `std/` (`math`, `random`, `json`, `io`, `net`, `db`,
`term`, `time`) y el corpus, y no apareció ninguna forma de pasar `"CAT"` a `"cat"`. **Si existe y
no se encontró, este hallazgo se corrige como se corrigió el 008**: la búsqueda fue esa, y la
descubribilidad sería lo que queda.

**El apaño** (rojo): `fold` en `buffer.zy` recorre el texto y suma 32 a los códigos 65–90 con
`##'(n + 32)`. Sólo ASCII: `À` no pasa a `à`, y el plegado de mayúsculas de Unicode no es una
resta (`ß`, `İ`, la sigma final). Conserva la longitud, lo que permite usar las mismas posiciones
en el texto original.

**Lo esperable:** una función de `std/` o un operador que convierta caso, con la regla de Unicode,
y una versión que pliegue para comparar. Lo decide el autor.

---

## BUG-ZYE-011

**La VM mantiene compartido el array de una tupla cuyo hueco se ha reemplazado.**

Salió al medir el coste de cambiar de buffer (`--count`, 2026-10-27): con dos ficheros, la primera
edición del buffer activo copia sus n líneas (`copied=5002` con 5 000), con uno no copia nada, y
en el tree-walker tampoco. El programa mínimo está en
[`hypotheses/replaced_tuple/`](hypotheses/replaced_tuple/):

```
bufs = [(big, 1), ([""], 0)]
(lines, k) = bufs[1]
bufs[1]$~ ([""], 0)            // la tupla vieja ya no está en bufs
lines[500]$~ "edited"          // VM: copia las 1 000 líneas · tree-walker: ninguna
```

Con un array de arrays en vez de tuplas, los dos motores copian 0 (`control_arrays.zy`), y
reasignar `bufs` entero tampoco copia (`control_reassign.zy`): lo que retiene la referencia es
el hueco reemplazado con `$~` cuando contenía una tupla. `through_function.zy` es el mismo fallo
con la forma que tiene en el editor, el cambio de buffer a través de una función. No es una divergencia de salida (el gate no la ve) sino de coste: la misma que
`HLZ-012` y `HLZ-014` fueron en el tree-walker.

**Efecto en ZyEdit:** una copia de n punteros una vez por sesión, no por tecla. Se acepta; no se
rodea con arrays paralelos porque taparía la prueba.

**Su «después»:** `hypotheses/replaced_tuple/check.sh` da `FIXED` (`probe.zy` y
`through_function.zy` en 0, con los dos controles en 0), y un caso de `zyquality/cost/` lo sujeta.

---

## GAP-ZYE-012

**Un cambio de tamaño de la ventana no llega al programa que espera una tecla.**

Era la hipótesis «Resizing» del README, sin comprobar desde el 2026-10-20. Se comprobó el
2026-10-27 con un pty de verdad (`tests/pty/check.py`, `hypotheses/resize/`). `>>?` contesta el
tamaño nuevo en cuanto se le pregunta, en los dos motores, así que **el dato existe**. Lo que
falta es enterarse: `<<|` sigue bloqueado y nada más lo despierta, de modo que el editor deja la
pantalla dibujada para el tamaño viejo hasta que se pulse una tecla.

**El apaño** (rojo): `wait_key` en `zyedit.zy` no usa `<<|`; sondea con `<<|?` cada 40 ms
(`@~ 40`), compara `>>?` con el tamaño anterior y, si cambió, vuelve para redibujar. Funciona
(`tests/pty/check.py` lo comprueba en ambos motores), pero cuesta una espera activa que `<<|` no
tiene, y un guion de `--keys` agotado ya no falla con «ran out» sino que sondea para siempre,
por lo que `tests/run.sh` corre con `--timeout`.

**Lo esperable:** que `<<|` pueda devolver «la ventana cambió» (un valor propio, no `'\0'`, que
ya significa «sin tecla»), o que haya una forma de preguntar si cambió. Lo decide el autor.

**Su «después»:** `hypotheses/resize/check.py` da `FIXED`, y `wait_key` vuelve a ser `<<| k`.

---

## BUG-ZYE-013

**zyjs lee `"\r"` dentro de una cadena como la letra `r`.**

Salió al pasar los módulos puros por los tres motores, como pide la decisión 3 del README
(2026-10-27). `history.zy` coincide en los tres; `buffer.zy` diverge sólo en las dos líneas que
dibujan un `\r`. El programa mínimo está en [`hypotheses/string_cr/`](hypotheses/string_cr/):

```zymbol
s = "a\rb"
>> s$# " " ##!s[2] ¶      // zyvm, zytw: 3 13    zyjs: 3 114
c = '\r'
>> ##!c ¶                 // los tres: 13
>> ("x\r" $? '\r') ¶      // zyvm, zytw: #1      zyjs: #0
```

La causa está en el lexer de zyjs (`web/src/zymbol/zymbol.js`, la lectura de cadenas): su tabla
de escapes tiene `\n` y `\t`, y cualquier otro carácter detrás de la barra queda tal cual, así
que `\r` da `r`. La de los literales de carácter, unas líneas más abajo, sí tiene `\r` y `\0`.
El lexer de Rust tiene `\r` en los dos. Ningún `.zy` del corpus escribe `\r` dentro de una
cadena, y por eso la puerta no lo ve.

Al lado, sin registrar: en los motores de Rust una cadena acepta un escape que no conoce y lo
deja como la letra (`"\0"` da `0`), mientras que un literal de carácter lo rechaza con *invalid
escape sequence*. No es una divergencia, pero sí una asimetría entre los dos literales.

**Lo que hace ZyEdit:** nada en el editor, que no corre en el navegador. `tests/run.sh` pasa
`buffer.zy` por zyjs y compara con `tests/buffer.zyjs.known`, la salida de hoy: `KNOWN`
mientras sea esa, y un fallo en cuanto coincida con el golden, para que alguien cierre el
hallazgo.

**Su «después»:** `hypotheses/string_cr/check.sh` da `FIXED`, `buffer.zyjs.known` desaparece y
un caso de `zyquality/corpus/` con `\r` dentro de una cadena lo sujeta.

---

## BUG-ZYE-014

**Insertar en una posición y quitar un rango cuestan el array entero, aunque tenga un solo
dueño.**

Salió al convertir `tests/cost.sh` en un veredicto y medir también el tree-walker
(2026-10-27). Un carácter tecleado en medio de un buffer de 10 000 líneas cuesta lo mismo que en
uno de 100, en los dos motores; un Enter no. El programa mínimo está en
[`hypotheses/mid_array/`](hypotheses/mid_array/): edita una vez y dos veces en medio de un array
de 10 000 cadenas, y la diferencia es lo que cuesta una edición.

| edición | forma | zyvm, bytes | zytw, valores copiados |
|---|---|---|---|
| quitar uno | `lines$-[50]` | 0 | 0 |
| reemplazar uno | `lines[50]$~ "Z"` | 0 | 0 |
| insertar uno | `lines$+[50] "Z"` | 480 088 | 10 001 |
| quitar un rango | `lines$-[50..51]` | 160 008 | 9 998 |

Las cuatro están escritas en la forma descartada, la que modifica en vez de construir
(`zymbol-design/COLLECTIONS.md`), y el array no tiene otro dueño. Aun así insertar y quitar un
rango cuestan n. El tree-walker copia los n valores. La VM, cuyo `copied` se queda en 0, reserva
del orden de 48 bytes por elemento al insertar y 16 al quitar el rango, en **cada** edición y no
una vez amortizada: con 1, 2, 4 y 8 inserciones crece en línea recta. La forma con el resultado
usado (`lines = lines$+[50] "Z"`) cuesta lo mismo, y un rango de un solo elemento
(`lines$-[50..50]`) también.

Mover n huecos es lo que cuesta insertar en medio de un array en cualquier lenguaje (el
`list.insert` de Python también es O(n)). Lo que no es inevitable es reservar un array nuevo en
cada inserción, como hace la VM, ni copiar los n valores, como hace el tree-walker.

**Efecto en ZyEdit:** cada Enter y cada pegado de varias líneas inserta líneas con `$+[…]`, y
cada unión de dos líneas (Retroceso al principio de una línea, Ctrl+D al final) las quita con
`$-[r1 + 1..r2]`, un rango aunque sea de una. Todas cuestan el buffer entero. `tests/cost.sh` lo
da como `KNOWN` en los dos motores. No se rodea: partir el buffer en bloques para esquivarlo
mediría el apaño y no el editor, como dice la decisión 1.

**Su «después»:** `hypotheses/mid_array/check.sh` da `FIXED`, `tests/cost.sh` falla con *«close
BUG-ZYE-014»* hasta que se cierre la ficha, y un caso de `zyquality/cost/` lo sujeta.

---

## GAP-ZYE-015

**No hay fotograma: cada `>>~` llega al terminal por separado, y un repintado se ve mientras
se dibuja.**

Salió de usar el editor (2026-10-27): el autor describió la pantalla como *estroboscópica* al
moverse por el texto sin desplazarlo. Tenía dos causas, una del editor y otra del lenguaje.

**La del editor, corregida el mismo día.** `render` empezaba cada fotograma con `>>!` y volvía a
dibujar las 24 filas, aunque sólo se hubiera movido el caret. Ahora hace lo que hacen serpiente
(`dibujo.zy`, «renderizado delta») y GO (`升描画` sobre las dos casillas que cambian al mover el
cursor): guarda una clave por fila de pantalla y sólo dibuja las filas cuya clave cambió, cada
una entera y rellenada hasta el ancho, sin borrar la pantalla. Medido por un pty con
`/proc/<pid>/io`, igual en los dos motores, sobre un fichero de 60 líneas:

| tecla | antes: escrituras · bytes · borrados | ahora |
|---|---|---|
| → | 147 · 2 252 · 1 | 14 · 260 · 0 |
| ↓ | 147 · 2 252 · 1 | 20 · 376 · 0 |
| una letra | 147 · 2 253 · 1 | 14 · 260 · 0 |
| Ctrl+L (una página) | 147 · 2 254 · 1 | 146 · 2 841 · 0 |

Ninguno de los 51 goldens cambió: lo que queda en pantalla en cada `SHOW` es lo mismo que con el
repintado completo. Los goldens sí atraparon un fallo del primer intento: una línea vacía y una
fila más allá del final del texto tenían la misma clave.

**La del lenguaje, abierta.** Dentro de `>>|`, los dos motores hacen un `execute!` de crossterm por
cada pieza de un `>>~` (mover el cursor, el color de letra, el de fondo, el reinicio del estilo)
y además vacían la salida al final. Cada `execute!` vacía la salida, así que un `>>~` con
colores son unas cuatro escrituras, y `>>!` es otra. Ningún programa puede decir «esto es una
pantalla: enséñala entera». El terminal es libre de pintar cada estado intermedio, y lo hace:
en un repintado completo, el primero es la pantalla en blanco. El programa mínimo está en
[`hypotheses/frame/`](hypotheses/frame/):

```zymbol
>>| {
    @ {
        <<| k
        ? k == 'q' { @! }
        code = ##!k
        >>!
        @ i:1..23 { >>~ (i, 1, 0, 244, 0) > "row {i} after key {code}" }
    }
}
```

Un borrado y 23 `>>~` llegan al terminal en **93 escrituras**, en los dos motores. El dibujo por
diferencias del editor lo reduce, pero no lo quita: al pasar de página cambian todas las filas.
Ya no hay pantalla en blanco, pero sí 146 escrituras y una pantalla a medio dibujar.

**Lo que no sirve sin más: vaciar la salida sólo cuando el programa espera.** Sería invisible
para el lenguaje y haría de cada fotograma una sola escritura, pero GO pinta «考慮中» y la piedra
recién puesta y se pone a pensar sin esperar ninguna tecla (`対局.zy`, líneas 518–519 y
585–586), y Chaturanga hace lo mismo con «thinking…» (`क्रीडा.zy`, líneas 277–279). Con esa
regla, el aviso y la jugada aparecerían cuando la máquina ya hubiera terminado.

**Lo esperable**, de menos a más, a elegir por el autor:
1. **Una escritura por `>>~` y por `>>!`** en los dos motores: `queue!` en lugar de `execute!`, y un
   solo vaciado al final. No cambia nada de lo que se ve ni de lo que un programa puede decir;
   la sonda pasa de 93 escrituras a 24 y la página del editor, de 146 a unas 48. Es un arreglo
   de implementación, no de lenguaje.
2. **Fotograma implícito, con una forma de decir «enséñalo ya».** Dentro de `>>|` la salida se
   acumula y se vacía al esperar (`<<|`, `<<|?`, `@~`, `<<`) y al salir, envuelta en la
   actualización sincronizada que entienden los terminales modernos (`ESC [ ? 2026 h` … `l`:
   kitty, WezTerm o foot pintan el fotograma de una vez; los demás la ignoran). Cada programa
   gana sin tocarlo, salvo los que dibujan y luego calculan sin esperar: GO y Chaturanga
   tendrían que escribir el «enséñalo ya» antes de pensar. Cambio de lenguaje.
3. **Fotograma explícito**: el programa marca dónde empieza y dónde acaba una pantalla, y todo
   lo demás sigue como hoy. Cambio de lenguaje, y sólo lo gana quien lo escribe.

Un símbolo nuevo pasaría antes por `zymbol-design/SYMBOLS.md` § 17; una función de `std/term`,
no.

**Decisión del autor (2026-10-27): la 1 ahora, en la v0.0.11, y la 2 en la v0.0.12.** La forma
del «enséñalo ya» queda por decidir.

**La 1, hecha el mismo día** en los dos motores (`emit_positioned` en el tree-walker,
`print_at` en `zymbol-host`): los mismos bytes, en una escritura por `>>~`. El tree-walker
evalúa ahora los elementos de un `>>~` antes de escribir nada, como siempre hizo la VM. Con los
dos motores reconstruidos (`hypotheses/frame/evidence/2026-10-27-one-write.txt`):

| | antes | con la 1 |
|---|---|---|
| la sonda: un borrado y 23 `>>~` | 93 escrituras | 24 |
| ZyEdit, → o una letra | 14 | 4 |
| ZyEdit, ↓ | 20 | 6 |
| ZyEdit, una página | 146 | 48 |
| ZyEdit antes del dibujo por diferencias, cualquier tecla | 147 | 49 |

La última fila es la que dice que la 1 la gana cualquier programa sin tocarlo. Los bytes
coinciden en todas: 260, 376, 2 841 y 2 252.

**Su «después»:** `hypotheses/frame/check.py` da `FIXED` (un fotograma, una escritura) con la
salida 2. Con la 1 baja de 93 a 24, y el hallazgo sigue en pie.

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
