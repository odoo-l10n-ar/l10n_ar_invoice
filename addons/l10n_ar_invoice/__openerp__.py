# -*- coding: utf-8 -*-
{'active': False,
 'author': 'Equipo de Localización Argentina',
 'category': 'Localization/Argentina',
 'data': ['data/document_class.xml',
          'data/responsability.xml',
          'data/responsability_class.xml',
          'data/journal_class.xml',
          'data/document_type.xml',
          'data/partner.xml',
          'data/invoice_workflow.xml',
          'data/country.xml',
          'data/res.currency.csv',
          'data/afip.journal_template.csv',
          'data/afip.concept_type.csv',
          'view/partner_view.xml',
          'view/country_view.xml',
          'view/afip_menuitem.xml',
          'view/afip_concept_type_view.xml',
          'view/afip_optional_type_view.xml',
          'view/afip_document_type_view.xml',
          'view/afip_document_class_view.xml',
          'view/afip_journal_class_view.xml',
          'view/afip_journal_template_view.xml',
          'view/afip_responsability_view.xml',
          'view/afip_responsability_class_view.xml',
          'view/afip_document_type_view.xml',
          'view/afip_journal_class_view.xml',
          'view/afip_responsability_view.xml',
          'view/afip_responsability_class_view.xml',
          'view/journal_view.xml',
          'view/invoice_view.xml',
          'view/invoice_config.xml',
          'view/res_config_view.xml',
          'view/report_invoice.xml',
          'view/afip_code_views.xml',
          'security/l10n_ar_invoice_security.xml',
          'security/ir.model.access.csv'],
 'demo_xml': [],
 'depends': ['base_setup',
             'account_voucher',
             'l10n_ar_base_vat',
             'l10n_ar_chart',
             'l10n_ar_states', 'web'],
 'description': '''
Soporte de Factura Argentina
============================

Funcionalidades:
----------------

* Soporte de Documentos Fiscales de tipo A, B, C, E y M.

  * Asociación de Diarios con Documentos Fiscales y Punstos de Venta.

* Soporte de Impuestos Argentinos.

  * Integración de códigos de impuestos con los oficiales de la AFIP.

* Parterns con Documentos Argentinos.

  * DNI, CUIT, CI, etc..
  * Todos con códigos permitidos por la AFIP.
  * Los países con códigos de CUIT

* Soporte de Productos codificados tal como lo pide la AFIP.

  * Productos, Servicios, Mixto.

* No incluye formateo de facturas.

 ''',
 'init_xml': [],
 'installable': True,
 'license': 'AGPL-3',
 'name': 'Argentina - Generador de Talonarios',
 'test': ['test/products.yml',
          'test/partners.yml',
          'test/com_ri1.yml',
          'test/com_ri2.yml',
          'test/inv_ri2ri.yml',
          'test/inv_ri2rm.yml',
          'test/bug_1042944.yml'],
 'version': '8.0.5.0',
 'website': 'https://github.com/odoo-l10n-ar/l10n_ar_invoice'}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
