# Política de tratamiento de datos personales — Actas (HedgeDoc) (Hefesto Studio)

Estado: vigente desde 2026-10-20. Responsable del tratamiento: el cliente que
opera el kit. Este documento describe qué datos guarda el kit, por qué, cuánto
tiempo los retiene y cómo se ejercen los derechos del titular (Ley 21.719).

## 1. Qué datos guarda este kit

El kit de actas (HedgeDoc) guarda, por documento:

- **El acta misma**: contenido en Markdown, con los acuerdos, las firmas
  asentadas, los asistentes (nombre, correo, cargo) y las referencias internas.
- **Cuentas de la aplicación**: usuario, hash de contraseña, rol y estado.
- **Historial de versiones del documento**: cada guardado anterior del acta.
- **Copias locales de respaldo**: `backups/<timestamp>/` con el dump de
  PostgreSQL (`public.dump`), los archivos adjuntos (`files.tar.gz`) y la
  configuración del kit.

Un acta de reunión identifica a personas concretas: son datos personales, aunque
el documento se llame "minuta".

## 2. Qué datos NO guarda este kit

- El `.env` **no** se copia en claro al respaldo: solo sus nombres de variable
  (`env.vars`) y, si hay un receptor `age` configurado, el `.env` cifrado
  (`env.age`). Ver `docs/CONTRATO-RESPALDO.md`, regla 5.
- El kit no guarda documentos de identidad ni datos de salud de los asistentes.

## 3. Base legal y deberes

- **Minimización**: el acta guarda solo lo necesario para dejar constancia de la reunión. No se pide RUT, domicilio ni número de documento de identidad, y esos datos no deben pegarse en el acta aunque la reunión los mencione.
- **Finalidad**: dejar constancia de los acuerdos de una reunión y who's quién看到她 asiste. Los datos no se usan para otros fines ni se ceden a terceros.
- **Seguridad**: los respaldos se cifran en reposo hacia el destino del
  operador, la clave privada no está en este servidor y el `.env` nunca sale
  en claro.
- **Auditoría**: cada respaldo y cada restauración dejan registro en
  `logs/restore.log` con origen, sha256 verificado, destino y resultado. Es
  registro de actividades de tratamiento: no guarda valores de secretos.

## 4. Retención

| Dato | Dónde | Retención por defecto | Quién lo borra |
|---|---|---|---|
| Actas y adjuntos | PostgreSQL (volumen `public`) y volumen `/files` | mientras el cliente los mantenga en el kit | el operador, desde la interfaz |
| Cuentas de la aplicación | PostgreSQL (volumen `public`) | mientras la cuenta exista | el operador |
| Historial de versiones | PostgreSQL (volumen `public`) | mientras el documento exista | el operador |
| Respaldos en disco | `backups/<timestamp>/` | **a definir por el operador**; el kit no borra nada por su cuenta | el operador |
| Registro de auditoría | `logs/restore.log` | append-only; se trunca por política del cliente | el operador |

**El kit no borra respaldos ni datos por su cuenta.** Borrar es una decisión del
operador, porque un respaldo borrado no se recupera.

## 5. Derechos del titular (acceso, rectificación y supresión)

1. **Acceso**: entregar los datos de un titular concreto desde la interfaz del
   kit o desde el dump de la base.
2. **Rectificación**: corregir los datos desde la interfaz del kit.
3. **Supresión**: eliminar el registro y dejar constancia de la supresión en el
   registro de auditoría.
4. **Revocación del consentimiento**: si el tratamiento depende del
   consentimiento, eliminar el registro.

El kit garantiza que los datos son localizables, corregibles y borrables; el
cliente es quien conoce la identidad de los titulares.

## 6. Verificación

- `bats tests/backup_restore.bats` comprueba, con datos sintéticos, que el
  `.env` no queda en claro, que el manifiesto lleva las cinco claves, que un
  artefacto alterado se rechaza y que un destino no vacío aborta la
  restauración.
- `gitleaks` corre en CI sobre el repositorio y su historial.
