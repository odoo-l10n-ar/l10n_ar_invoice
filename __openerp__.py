# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name':     'Argentina - Generador de Talonarios',
    'version':  '2.7.155',
    'author':   'OpenERP - Team de Localización Argentina',
    'category': 'Localization/Argentina',
    'website':  'https://launchpad.net/~openerp-l10n-ar-localization',
    'license':  'AGPL-3',
    'description': """
Módulo de Facturación de la localización Argentina

Incluye:

  - Configuración de libros, diarios y otros detalles para facturación argentina.
  - Wizard para configurar los talonarios necesarios para facturar.
""",
    'depends': [
        'base_setup',
        'l10n_ar_base_vat',
        'l10n_ar_chart_generic',
        'l10n_ar_states',
    ],
    'init_xml': [
    ],
    'demo_xml': [],
    'test': [
        'test/partners.yml',
        'test/com_ri1.yml',
        'test/com_ri2.yml',
        'test/com_mon.yml',
        'test/inv_ri2ri.yml',
        'test/inv_rm2ri.yml',
        'test/inv_ri2rm.yml',
        #'test/bug_1042944.yml',
    ],
    'update_xml': [
        'data/responsability.xml',
        'data/responsability_class.xml',
        'data/journal_class.xml',
        'data/document_type.xml',
        'data/partner.xml',
        'data/invoice_config.xml',
        'data/invoice_workflow.xml',
        'data/reports.xml',
        'data/country.xml',
        'view/partner_view.xml',
        'view/country_view.xml',
        'view/afip_menuitem.xml',
        'view/afip_document_type_view.xml',
        'view/afip_journal_class_view.xml',
        'view/afip_responsability_view.xml',
        'view/afip_responsability_class_view.xml',
        'view/afip_document_type_view.xml',
        'view/afip_journal_class_view.xml',
        'view/afip_responsability_view.xml',
        'view/afip_responsability_class_view.xml',
        'view/journal_view.xml',
        'security/l10n_ar_invoice_security.xml',
        'security/ir.model.access.csv',
    ],
    'active': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
