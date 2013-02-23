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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

_all_taxes = lambda x: True
_all_except_vat = lambda x: x.name not in [u'IVA Ventas 21%', u'IVA Compras 21%']

class account_invoice_line(osv.osv):
    """
    En argentina como no se diferencian los impuestos en las facturas, excepto el IVA
    agrego funciones que ignoran el iva solamenta a la hora de imprimir los valores.

    En esta nueva versión se cambia las tres variables a una única función 'price_calc'
    que se reemplaza de la siguiente manera:

        'price_unit_vat_included'         -> price_calc(use_vat=True, quantity=1, discount=True)[id]
        'price_subtotal_vat_included'     -> price_calc(use_vat=True, discount=True)[id]
        'price_unit_not_vat_included'     -> price_calc(use_vat=False, quantity=1, discount=True)[id]
        'price_subtotal_not_vat_included' -> price_calc(use_vat=False, discount=True)[id]

    Y ahora puede imprimir sin descuento:

        price_calc(use_vat=True, quantity=1, discount=False)
    """

    _inherit = "account.invoice.line"

    def price_calc(self, cr, uid, ids, use_vat=True, tax_filter=None, quantity=None, discount=None, context=None):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        _tax_filter = tax_filter or ( use_vat and _all_taxes ) or _all_except_vat
        for line in self.browse(cr, uid, ids):
            _quantity = quantity if quantity is not None else line.quantity
            _discount = discount if discount is not None else line.discount
            _price = line.price_unit * (1-(_discount or 0.0)/100.0)
            _tax_ids = filter(_tax_filter, line.invoice_line_tax_id)
            taxes = tax_obj.compute_all(cr, uid,
                                        _tax_ids, _price, _quantity,
                                        product=line.product_id,
                                        partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total_included']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

account_invoice_line()

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def afip_validation(self, cr, uid, ids, context={}):
        obj_resp_class = self.pool.get('afip.responsability_class')

        for invoice in self.browse(cr, uid, ids):
            # If parter is not in Argentina, ignore it.
            if invoice.partner_id.country.name != 'Argentina':
                continue

            # Partner responsability ?
            if isinstance(invoice.partner_id.responsability_id, orm.browse_null):
                raise osv.except_osv(_('No responsability'),
                                     _('Your partner have not afip responsability assigned. Assign one please.'))

            # Take responsability classes for this journal
            invoice_class = invoice.journal_id.journal_class_id.document_class
            resp_class_ids = obj_resp_class.search(cr, uid, [('document_class','=', invoice_class)])

            # You can emmit this document?
            resp_class = [ rc.emisor_id.code for rc in obj_resp_class.browse(cr, uid, resp_class_ids) ]
            if invoice.journal_id.company_id.partner_id.responsability_id.code not in resp_class:
                raise osv.except_osv(_('Invalid emisor'),
                                     _('Your responsability with AFIP dont let you generate this kind of document.'))

            # Partner can receive this document?
            resp_class = [ rc.receptor_id.code for rc in obj_resp_class.browse(cr, uid, resp_class_ids) ]
            if invoice.partner_id.responsability_id.code not in resp_class:
                raise osv.except_osv(_('Invalid receptor'),
                                     _('Your partner cant recive this document. Check AFIP responsability of the partner, or Journal Account of the invoice.'))

            # If Final Consumer have pay more than 1000$, you need more information to generate document.
            if invoice.partner_id.responsability_id.code == 'CF' and invoice.amount_total > 1000 and \
               (invoice.partner_id.document_type.code in [ None, 'Sigd' ] or invoice.partner_id.document_number is None):
                raise osv.except_osv(_('Partner without Identification for total invoices > $1000.-'),
                                     _('You must define valid document type and number for this Final Consumer.'))
        return True

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

