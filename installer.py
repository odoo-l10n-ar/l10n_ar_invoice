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

_invoice_types = {
    'XXX': { 'name': 'Fact A' },
}

_invoice_types = [ ('A', 'A'), ('B', 'B'), ('C','C'), ('E','E'), ('M','M'), ('X','X')]
_action_types = [
    ('FV', 'Ventas', 'sale'),
    ('RV', 'Reembolso de Ventas', 'sale_refund'),
    ('FC', 'Compras', 'purchase'),
    ('RC', 'Reembolso de Compras', 'purchase_refund') ]
_currency_types = [ ('ARS', 'A'), ('USD', 'U') ]
_situation_invoices = {
    'monotributo': { 'sent': 'C', 'receive': 'BCX' },
    'responsableinscripto': { 'sent': 'ABEMX', 'receive': 'ABCMX' },
    'noresponsableinscripto': { 'sent': 'ABEMX', 'receive': 'ABCMX' },
}

class account_invoice_ar_installer(osv.osv_memory):
    _name = 'account.invoice.ar.installer'
    _inherit = 'res.config.installer'
    _columns = {
        'situation': fields.selection([
            ('monotributo','Monotributista'),
            ('responsableinscripto','Responsable Inscripto'),
            ('noresponsableinscripto','No Responsable Inscripto')],
            'Situación ante la AFIP', required=True),
        'do_export': fields.boolean('Realiza o realizará operaciones de Exportación', required=True),
        'currency': fields.selection([
            ('ARS','Pesos'),
            ('ARS+USD','Pesos y Dolares')],
            'Opera con monedas', required=True),
    }

    _defaults= {
        'situation': 'monotributo',
        'do_export': False,
        'currency': 'ARS',
    }

    def generate_invoice_journals(self, cr, uid, ids, situation, export, currency, context=None):
        """
        Generate Sequences and Journals associated to Invoices Types
        """
        obj_sequence = self.pool.get('ir.sequence')
        obj_currency = self.pool.get('res.currency')
        obj_acc_account = self.pool.get('account.account')
        obj_acc_journal_view = self.pool.get('account.journal.view')
        obj_acc_chart_template = self.pool.get('account.chart.template')
        obj_acc_template = self.pool.get('account.account.template')
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        obj_journal = self.pool.get('account.journal')
        mod_obj = self.pool.get('ir.model.data')

        result = mod_obj.get_object_reference(cr, uid, 'l10n_chart_ar_generic', 'l10nAR_chart_template')
        id = result and result[1] or False
        obj_multi = obj_acc_chart_template.browse(cr, uid, id, context=context)

        # Remove Sale Journal, Purchase Journal, Sale Refund Journal, Purchase Refund Journal.
        jou_ids = obj_journal.search(cr, uid, [('type','in',['sale','purchase','sale_refund','purchase_refund'])])
        obj_journal.unlink(cr, uid, jou_ids)

        # Create Jounals for Argentinian Invoices.
        s = lambda v: obj_acc_account.search(cr, uid, [('code', '=', '%s0' % v)], context=context)[0]

        account_id = {
            'A': s(obj_multi.property_account_receivable.code),
            'B': s(obj_multi.property_account_payable.code),
            'sale': s(obj_multi.property_account_income_categ.code),
            'sale_refund': s(obj_multi.property_account_income_categ.code),
            'purchase': s(obj_multi.property_account_expense_categ.code),
            'purchase_refund': s(obj_multi.property_account_expense_categ.code),
        }

        invoices_filter = {
            'FV': _situation_invoices[situation]['sent'],
            'FC': _situation_invoices[situation]['receive'],
            'RV': _situation_invoices[situation]['sent'],
            'RC': _situation_invoices[situation]['receive'],
        }
        if export:
            invoices_filter['FV'] += 'E'

        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id
        view_id_invoice = obj_acc_journal_view.search(cr, uid, [('name', '=', 'Sale/Purchase Journal View')], context=context)[0]
        view_id_refund = obj_acc_journal_view.search(cr, uid, [('name', '=', 'Sale/Purchase Refund Journal View')], context=context)[0]
        view_id = {
            'sale': view_id_invoice, 
            'purchase': view_id_invoice, 
            'sale_refund': view_id_refund, 
            'purchase_refund': view_id_refund, 
        }

        for action_code, action_name, action_type in _action_types:
            for invoice_code, invoice_name in _invoice_types:
                if not invoice_code in invoices_filter[action_code]:
                    continue

                data = {'act_name': action_name,
                        'act_code': action_code,
                        'inv_name': invoice_name,
                        'inv_code': invoice_code,
                        'journal_type': action_type}
                # Create Sequences
                vals_seq = {
                    'name': '%(act_name)s Fact %(inv_code)s' % data,
                    'code': 'account.journal',
                    'prefix': '%(inv_code)s/' % data,
                    'company_id': company_id.id,
                    'padding': 5,
                }
                seq_id = obj_sequence.create(cr, uid, vals_seq, context=context)

                for currency_code, currency_name in _currency_types:
                    if not currency_code in currency:
                        continue
                    data.update({'cur_name': currency_name,
                                 'cur_code': currency_code })
                    currency_id = obj_currency.search(cr, uid, [('name', '=', currency_code)], context=context)[0]
                    # Create Journals
                    analitical_ids = analytic_journal_obj.search(cr, uid, [('type', '=', data['journal_type'])], context=context)
                    analitical_journal = analitical_ids and analitical_ids[0] or False
                    vals_journal = {}
                    vals_journal = {
                        'name': "%(act_name)s Fact %(inv_code)s (%(cur_code)s)" % data,
                        'code': "%(act_code)s%(inv_code)s%(cur_name)s" % data,
                        'sequence_id': seq_id,
                        'type': "%(journal_type)s" % data, #'cash',
                        'company_id': company_id.id,
                        'analytic_journal_id': analitical_journal,
                        'view_id': view_id[data['journal_type']],
                        'currency': currency_id,
                        'default_credit_account_id': account_id[data['journal_type']],
                        'default_debit_account_id': account_id[data['journal_type']],
                    }
                    obj_journal.create(cr, uid, vals_journal, context=context)

        pass

    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        r = super(account_invoice_ar_installer, self).execute(cr, uid, ids, context)
        record = self.browse(cr, uid, ids, context=context)[0]

        for res in self.read(cr, uid, ids, context=context):
            self.generate_invoice_journals(cr, uid, ids,
                                           record.situation,
                                           record.do_export,
                                           record.currency.split('+'),
                                           context=None)

account_invoice_ar_installer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
