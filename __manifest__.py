# -*- coding: utf-8 -*-
{
    'name': "ELEFANTE Facturación",

    'summary': """
        Agrega los formatos de facturas de ELEFANTE""",

    'description': """
        Agrega los formatos de facturas de ELEFANTE
    """,

    'author': "Grupo Treming",
    'website': "http://www.treming.com",

    'category': 'Accounting/Accounting',
    'version': '0.1',

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
}
