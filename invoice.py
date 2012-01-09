# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2010 Moldeo Interactive
#    (<http://www.moldeointeractive.com.ar>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import decimal_precision as dp

_all_taxes = lambda x: True
_all_except_vat = lambda x: x not in ['IVA Ventas 21%', 'IVA Compras 21%']

class account_tax(osv.osv):
    """
    Esta extensión resuelve el problema de mezclar impuestos sobre el valor agregado y 
    sobre los ingresos brutos. El problema del código original es que al estar incluido
    el impuesto al ingreso bruto en el valor del precio, el IVA se calcula sobre el
    precio sin el impuesto al valor agregado. En argentina se lo aplica al
    precio de lista sin importar los impuestos involucrados.
    """
    _inherit = "account.tax"

    _columns = {
        'belong_to_gross_price': fields.boolean('Tax belong to gross price'),
    }

    def compute_all(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None):
        """
        RETURN: {
                'total': 0.0,                # Total without taxes
                'total_included: 0.0,        # Total with taxes
                'taxes': []                  # List of taxes, see compute for the format
            }
        """
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        totalin = totalex = round(price_unit * quantity, precision)
        tin = []
        tex = []
        gross = []
        for tax in taxes:
            if tax.price_include:
                tin.append(tax)
            else:
                tex.append(tax)
            if tax.belong_to_gross_price:
                gross.append(tax.id)
        tin = self.compute_inv(cr, uid, tin, price_unit, quantity, address_id=address_id, product=product, partner=partner)
        for r in tin:
            totalex -= r.get('amount', 0.0)
        totlex_qty = 0.0
        try:
            totlex_qty=totalex/quantity
        except:
            pass
        tex = self._compute(cr, uid, tex, totlex_qty, quantity, address_id=address_id, product=product, partner=partner)
        for r in tex:
            if not r['id'] in gross:
                totalin += r.get('amount', 0.0)
        print totalex, totalin, tin + tex
        return {
            'total': totalex,
            'total_included': totalin,
            'taxes': tin + tex
        }
account_tax()

class account_invoice_line(osv.osv):
    """
    En argentina como no se diferencian los impuestos en las facturas, excepto el IVA
    agrego funciones que ignoran el iva solamenta a la hora de imprimir los valores.
    """
    def _amount_calc_taxes(self, cr, uid, ids, tax_filter, default_quantity):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            tax_ids = filter(tax_filter, line.invoice_line_tax_id)
            quantity = default_quantity if default_quantity is not None else line.quantity
            taxes = tax_obj.compute_all(cr, uid,
                                        tax_ids, price, quantity,
                                        product=line.product_id,
                                        address_id=line.invoice_id.address_invoice_id,
                                        partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total_included']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    def _amount_unit_vat_included(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return self._amount_calc_taxes(cr, uid, ids, _all_taxes, 1)

    def _amount_subtotal_vat_included(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return self._amount_calc_taxes(cr, uid, ids, _all_taxes, None)

    def _amount_unit_not_vat_included(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return self._amount_calc_taxes(cr, uid, ids, _all_except_vat, 1)

    def _amount_subtotal_not_vat_included(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        return self._amount_calc_taxes(cr, uid, ids, _all_except_vat, None)

    _inherit = "account.invoice.line"
    _columns = {
        'price_unit_vat_included': fields.function(_amount_unit_vat_included, method=True,
                                               string='Unit Price with VAT', type="float",
                                               digits_compute= dp.get_precision('Account'), store=False),
        'price_subtotal_vat_included': fields.function(_amount_subtotal_vat_included, method=True,
                                               string='Subtotal with VAT', type="float",
                                               digits_compute= dp.get_precision('Account'), store=False),
        'price_unit_not_vat_included': fields.function(_amount_unit_not_vat_included, method=True,
                                               string='Unit Price without VAT', type="float",
                                               digits_compute= dp.get_precision('Account'), store=False),
        'price_subtotal_not_vat_included': fields.function(_amount_subtotal_not_vat_included, method=True,
                                               string='Subtotal without VAT', type="float",
                                               digits_compute= dp.get_precision('Account'), store=False),
    }

account_invoice_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

