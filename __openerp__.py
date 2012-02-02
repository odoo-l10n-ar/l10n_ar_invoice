# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2014  Cristian S. Rocha
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Argentina - Generador de Talonarios',
    'version': '2.0',
    'author': 'Moldeo Interactive',
    'category': 'Argentina/Invoices',
    'website': 'http://www.moldeointeractive.com/',
    'license': 'GPL-3',
    'description': """
Generador de Talonarios para la Argentina.

    Permite generar talonarios para comprobanetes según requerimientos del AFIP.
""",
    'depends': [
        'l10n_chart_ar_generic',
    ],
    'init_xml': [],
    'demo_xml': [],
    'test': [
        'test/wizard_installer.yml',
    ],
    'update_xml': [
        'data/invoice_installer.xml',
        'data/reports.xml',
    ],
    'active': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
