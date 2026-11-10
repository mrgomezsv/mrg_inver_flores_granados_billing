# -*- coding: utf-8 -*-
{
    'name': "ELEFANTE Facturación",

    'summary': "Formatos PDF ELEFANTE (CF, CCF, FE y NC) para imprimir documentos de El Salvador en formularios preimpresos",

    'description': """
ELEFANTE Facturación (formatos preimpresos)
=============================================

Agrega cuatro formatos de impresión PDF sobre facturas y notas de crédito (``account.move``):
**ELEFANTE CF**, **ELEFANTE CCF**, **ELEFANTE FE** y **ELEFANTE NC**. Los formatos imprimen solo valores
(sin rótulos de campo, logotipo ni datos del emisor, salvo unos pocos textos fijos) en posiciones absolutas
medidas en milímetros sobre una hoja de 216 x 356 mm (tamaño legal), es decir, están hechos para llenar
formularios físicos preimpresos. El módulo no contiene código Python ni pantallas: solo formatos de papel,
acciones de reporte, plantillas QWeb y hojas de estilo. Los datos salen de campos estándar de Odoo y de
campos y métodos que aportan sus dependencias ``treming_*``. Importante: las plantillas provienen de
versiones anteriores de Odoo y, sin adaptarlas, en Odoo 20 la mayoría de los valores se imprimen en
blanco (ver Notas importantes).

¿Cuándo instalarlo?
---------------------

- Cuando la empresa imprime Facturas de Consumidor Final (CF), Comprobantes de Crédito Fiscal (CCF),
  Notas de Crédito (NC) o documentos FE sobre formularios preimpresos con la misma distribución para la
  que se calibró este módulo (formularios de ELEFANTE / Inver Flores Granados).
- Cuando ya se usan los módulos de facturación de Grupo Treming de los que depende
  (``treming_sv_billing``, ``treming_municipalities``, ``treming_subtotal_product``,
  ``treming_print_format_account`` y ``fya_applied_to``).

¿Cuándo NO instalarlo?
------------------------

- Si lo que necesita es la factura electrónica (DTE): este módulo no genera, firma, transmite ni
  imprime DTE y no depende de ``mrg_dte_core_sv``, que es el módulo que emite el DTE desde Odoo.
- Si sus formularios preimpresos tienen otra distribución: las posiciones están fijas en las hojas de
  estilo del módulo y cambiarlas requiere modificar el código.
- Si no dispone de las dependencias ``treming_*`` y ``fya_applied_to``: sin ellas no se puede instalar.
- Si espera que reemplace la factura estándar o que aparezca por sí solo en el botón Imprimir: no
  reemplaza ningún reporte y sus reportes se crean sin enlace al menú Imprimir (ver Configuración).
- Si necesita usarlo en Odoo 20 de inmediato, sin adaptar antes las plantillas: con el código actual
  la mayoría de los valores salen en blanco (ver las advertencias sobre ``t-esc`` y ``display_type`` en
  Notas importantes).

Funcionalidades
---------------

Lo que sigue describe lo que definen las plantillas. En Odoo 20, con el código actual, buena parte de
esos valores no llega al papel (ver Notas importantes).

**Comportamiento común de los cuatro formatos**

- Encabezado del cliente: nombre (``business_name`` si el contacto es empresa, ``name`` si es persona;
  máximo 60 caracteres), fecha de la factura (``invoice_date``), dirección armada con
  ``res.partner.get_partner_addr`` a partir de calle, calle 2 y ciudad (máximo 70 caracteres) y
  municipio (``municipality_tr_id``).
- Detalle: recorre las líneas de la factura (``invoice_line_ids``) e imprime por cada una la cantidad
  (con 1 decimal), la descripción (``name``), el precio unitario ``priceu_w_taxes`` con el símbolo de la
  moneda y tantos decimales como indique el registro ``treming_sv_billing.extra_prc_currency``, y el
  valor de la línea (``price_subtotal_no_discount``) en una de tres columnas según ``sale_type``:
  No sujeta (``non_subject``), Exenta (``exempt``) o Gravada (``taxed``).
- Secciones y notas: la cantidad, el precio unitario y los valores de la línea solo se imprimen cuando
  ``display_type`` está vacío (condición ``not l.display_type``), criterio de versiones anteriores para
  dejar solo el texto en secciones y notas. En Odoo 20 ``display_type`` es obligatorio y las líneas de
  producto llevan el valor ``product``, así que con el código actual esas columnas no se imprimen en
  ninguna línea: solo la descripción.
- Productos totalizadores: si el producto de la línea tiene marcado ``totalizing_product_tr``, la línea
  se imprime como fila de subtotal: su texto, la palabra SUBTOTAL, el valor de la línea y, debajo, en
  negrita y con línea superior, un subtotal igual a ``partial_subtotal_tr`` de la factura más el valor de
  esa línea.
- Total en letras: ``total_in_letters`` de la factura seguido de ``description`` de la moneda.
- Dos copias: cada plantilla imprime el mismo documento dos veces, una debajo de la otra, en dos
  bloques (``detail_container`` y ``detail_container_2``) con márgenes y alturas propios en el CSS.
- Tipografía ``saxMono`` incrustada en base64 (WOFF2 y WOFF) en ``common.css``; el tamaño de 14 px de
  ``common.css`` lo fija en 12 px la hoja de estilo de cada formato.
- Usa ``web.basic_layout``: no imprime logotipo, encabezado ni pie de página de la compañía.
- Posición de cada dato: fijada en milímetros en ``cf.css``, ``ccf.css``, ``fe.css`` y ``nc.css``;
  además, los datos del encabezado, las celdas de las líneas normales y los totales reciben el atributo
  ``style`` que devuelve el método ``calc_item_style_tr`` de la factura con la clave del dato
  (``cliente``, ``fecha``, ``nit``, ``total``, etc.). Las filas de productos totalizadores no lo usan.
- Nombre del archivo PDF: el número del documento sin barras; si queda vacío, ``CF``, ``CCF``, ``FE``
  o ``NC``. En Odoo 20 una factura en borrador que nunca se publicó no tiene número (``name`` vacío) y
  la expresión ``(object.name).replace(...)`` falla, por lo que descargar el PDF de un solo borrador da
  error; con documentos publicados no ocurre.

**ELEFANTE CF (Factura de Consumidor Final)**

- Encabezado: cliente, fecha, dirección, NIT (``nit``), municipio, DUI (``dui``), departamento
  (``state_id``) y condición de pago: «Credito» si ``days_of_credit`` es mayor que 0; si no, «Contado».
- Totales: total en letras, suma gravada (``taxed_amount``), subtotal (exenta más gravada), IVA
  retenido (valor absoluto de ``get_display_taxes()['ret']``), suma no sujeta (``non_subject_amount``),
  suma exenta (``exempt_amount``) y total (``amount_total``).

**ELEFANTE CCF (Comprobante de Crédito Fiscal)**

- Encabezado: cliente, fecha, dirección, NRC (``nrc``), municipio, NIT, DUI, departamento, giro
  (``business_nature``, máximo 20 caracteres) y condición de pago. También escribe los textos fijos
  «Remision» y «Fecha», que ``ccf.css`` pinta en color blanco, por lo que no se ven en el papel.
- Totales: total en letras; fila de sumas no sujeta, exenta y gravada; IVA
  (``get_display_taxes()['iva']``); subtotal (``subtotal_amount``); ventas exentas; ventas no sujetas;
  IVA retenido y total. La percepción está comentada en la plantilla y no se imprime.

**ELEFANTE NC (Nota de Crédito)**

- Mismo encabezado, detalle y totales que el CCF; su hoja ``nc.css`` es idéntica a ``ccf.css``.

**ELEFANTE FE**

- El código no indica el significado de la sigla. Encabezado: cliente, fecha, dirección, municipio,
  país (``country_id``) y el texto fijo «Remision», que no tiene regla de posición propia en ``fe.css``
  y, a diferencia del CCF, no se pinta en blanco.
- No imprime NIT, DUI, NRC, departamento, giro ni condición de pago (``fe.css`` conserva reglas para
  algunos de esos identificadores, que la plantilla no usa). Totales: total en letras, suma gravada y
  total.

Módulos requeridos
------------------

Las plantillas usan campos y métodos que este módulo no define y que deben aportar sus dependencias:

- ``treming_sv_billing``: se usa de forma explícita su registro ``extra_prc_currency`` (decimales del
  precio unitario); por su nombre, es la base de facturación salvadoreña de Grupo Treming.
- ``treming_municipalities``: por su nombre, aporta el municipio del contacto (``municipality_tr_id``).
- ``treming_subtotal_product``: por su nombre, aporta los productos totalizadores
  (``totalizing_product_tr`` y ``partial_subtotal_tr``).
- ``treming_print_format_account``: por su nombre, aporta los estilos de impresión
  (``calc_item_style_tr``).
- ``fya_applied_to``: las plantillas no usan ningún campo que se pueda atribuir a este módulo.

Campos y métodos externos que leen las plantillas:

- **Factura** (``account.move``): ``calc_item_style_tr()``, ``days_of_credit``, ``total_in_letters``,
  ``taxed_amount``, ``exempt_amount``, ``non_subject_amount``, ``subtotal_amount``,
  ``partial_subtotal_tr`` y ``get_display_taxes()`` (con las claves ``iva`` y ``ret``).
- **Línea de factura** (``account.move.line``): ``sale_type``, ``price_subtotal_no_discount`` y
  ``priceu_w_taxes``.
- **Producto** (``product.product``): ``totalizing_product_tr``.
- **Contacto** (``res.partner``): ``business_name``, ``nit``, ``dui``, ``nrc``, ``business_nature``,
  ``municipality_tr_id`` y el método ``get_partner_addr``.
- **Moneda** (``res.currency``): ``description`` (no existe en el modelo estándar de Odoo 20).

Qué modifica de Odoo
--------------------

- No extiende modelos (no hay ``_inherit``), no sobrescribe métodos y no hereda vistas.
- Solo crea registros de datos: 4 formatos de papel (``report.paperformat``), 4 acciones de reporte
  (``ir.actions.report``) sobre ``account.move`` y 16 plantillas QWeb (``ir.ui.view``), cuatro por
  formato: documento, encabezado, líneas y totales.

Campos que agrega
-----------------

Ninguno.

Modelos nuevos
--------------

Ninguno.

Elementos que elimina, oculta o reemplaza
-----------------------------------------

Ninguno: los reportes estándar de factura siguen disponibles y los formatos ELEFANTE se suman como
alternativas.

Menús, reportes y asistentes
----------------------------

- Reportes PDF (``qweb-pdf``) sobre ``account.move``:

  - ``elefante_cf_report`` (ELEFANTE CF): plantilla ``tmp_cf``, papel ``elefante_cf_paper_format``.
  - ``elefante_ccf_report`` (ELEFANTE CCF): plantilla ``tmp_ccf``, papel ``elefante_ccf_paper_format``.
  - ``elefante_fe_report`` (ELEFANTE FE): plantilla ``tmp_fe``, papel ``elefante_fe_paper_format``.
  - ``elefante_nc_report`` (ELEFANTE NC): plantilla ``tmp_nc``, papel ``elefante_nc_paper_format``.

- Formatos de papel ELEFANTE CF, CCF, FE y NC: tamaño personalizado de 216 x 356 mm, orientación
  vertical, margen superior de 24 mm, márgenes inferior, izquierdo y derecho en 0 y sin línea de
  encabezado.
- Los reportes no definen ``binding_model_id``, así que no aparecen en el botón Imprimir hasta que se
  agreguen manualmente (ver Configuración).
- No agrega menús, asistentes, acciones automáticas (cron), controladores ni pruebas.

Restricciones, validaciones y permisos
--------------------------------------

- No define grupos, permisos (``ir.model.access.csv``) ni reglas de registro, y no agrega restricciones
  ni validaciones.
- Los reportes no tienen ``group_ids`` ni ``domain``: cualquier usuario que pueda ver el documento puede
  imprimirlos, y sirven para cualquier ``account.move`` sin comprobar si es factura, CCF o nota de
  crédito; elegir el formato correcto queda a cargo del usuario.
- Con el código actual, al imprimir se evalúan (y la impresión falla si no existen) el registro
  ``treming_sv_billing.extra_prc_currency`` (leído con ``env.ref``), los métodos ``calc_item_style_tr``
  y ``get_display_taxes`` de la factura, ``partial_subtotal_tr``, ``totalizing_product_tr`` y
  ``sale_type``.
- Si se migran los ``t-esc`` a ``t-out`` (ver Notas importantes), la impresión también fallará cuando un
  cliente marcado como empresa no tenga ``business_name``, cuando el documento no tenga
  ``total_in_letters``, cuando ``res.currency`` no tenga el campo ``description`` o cuando
  ``get_display_taxes()`` no devuelva las claves ``iva`` y ``ret``: la plantilla recorta o concatena
  esos valores sin comprobar si están vacíos.

Configuración después de instalar
---------------------------------

1. Completar en los clientes los datos que imprimen los formatos: ``business_name`` (clientes
   empresa), NIT, DUI, NRC, giro, municipio, departamento y, para el FE, país.
2. Activar el modo desarrollador, entrar a Ajustes > Técnico > Acciones > Acciones del reporte, abrir
   ELEFANTE CF, ELEFANTE CCF, ELEFANTE FE y ELEFANTE NC y pulsar «Agregar al menú de impresión» en cada
   uno para que aparezcan en Imprimir dentro de la factura.
3. Hacer una impresión de prueba sobre el formulario real. Los márgenes se ajustan en Ajustes > Técnico >
   Reportes > Formato de papel (registros ELEFANTE CF, CCF, FE y NC); las posiciones finas, en las hojas
   CSS del módulo o en los estilos que devuelve ``calc_item_style_tr``.
4. Confirmar que el motor de PDF pueda descargar las hojas de estilo (ver Integraciones).
5. Antes de usarlo en producción con Odoo 20, adaptar las plantillas (``t-esc`` y ``display_type``,
   ver Notas importantes); sin ese cambio la impresión de prueba saldrá casi en blanco.

Integraciones y requisitos técnicos
-----------------------------------

- No se conecta a servicios externos (ni Hacienda, ni Resend, ni APIs de terceros).
- Usa el motor de PDF de Odoo (wkhtmltopdf por defecto). Las hojas de estilo se cargan con etiquetas
  ``link`` directas a ``/mrg_inver_flores_granados_billing/static/src/css/`` y no mediante los paquetes
  de recursos (assets) de Odoo, por lo que el motor debe poder acceder al servidor por la URL de
  ``report.url`` o ``web.base.url``; si no, el PDF sale sin posiciones ni tipografía.
- No requiere librerías Python adicionales.

Notas importantes
-----------------

- Compatibilidad con Odoo 20 (``t-esc``): la mayoría de los valores se imprimen con la directiva QWeb
  ``t-esc``, que el QWeb de Odoo 20 ya no reconoce (para mostrar valores solo quedan ``t-out`` y
  ``t-field``). El motor la trata como atributo desconocido: no evalúa la expresión, deja el elemento
  vacío y registra en el log «Unknown directives or unused attributes». Mientras no se migren a
  ``t-out``, salen en blanco el nombre del cliente, la dirección, la condición de pago, el NIT en CCF y
  NC, el giro, los textos fijos «Remision» y «Fecha», los precios unitarios, los valores por tipo de
  venta y de las filas totalizadoras, el total en letras y todos los totales. Solo se imprimen los
  datos con ``t-field``: fecha, NIT en CF, DUI, NRC, municipio, departamento, país y descripción de las
  líneas.
- Compatibilidad con Odoo 20 (``display_type``): la cantidad usa ``t-field``, pero tampoco se imprime
  por la condición ``not l.display_type`` descrita en Funcionalidades; al migrar las plantillas hay que
  cambiar esa condición para excluir solo secciones y notas.
- Al migrar los ``t-esc`` a ``t-out`` empezarán a evaluarse expresiones que hoy no se ejecutan (ver
  Restricciones). Haga una impresión de prueba antes de usarlo.
- Las dependencias ``treming_*`` y ``fya_applied_to`` no forman parte de los repositorios
  ``addons-servidor`` ni ``addons-custom``; deben obtenerse por separado.
- El módulo nació con el nombre técnico ``elefante_billing``; por eso sus identificadores XML conservan
  el prefijo ``elefante_``.
- Al desinstalarlo se eliminan los formatos de papel, los reportes y las plantillas; no se borra ni se
  altera ningún dato de facturas, clientes o productos.
- ``common.css`` define las clases ``detail_container_3`` y ``detail_container_4``, que ninguna
  plantilla usa.
""",

    'author': "Grupo Treming",
    'website': "http://www.treming.com",

    'category': 'Accounting/Accounting',
    'version': '20.0.1.0.0',
    'license': 'LGPL-3',

    'depends': ['treming_sv_billing', "treming_municipalities", "fya_applied_to", "treming_subtotal_product", "treming_print_format_account"],

    'data': [
        "reports/documents.xml",
        "reports/cf_layout.xml",
        "reports/cf_tmp.xml",
        "reports/ccf_layout.xml",
        "reports/ccf_tmp.xml",
        "reports/fe_layout.xml",
        "reports/fe_tmp.xml",
        "reports/nc_layout.xml",
        "reports/nc_tmp.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
