# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class account_journal(osv.osv):
    _inherit = "account.journal"
    _columns = {
        'code': fields.char('Code', size=10, required=True,
                            help='The code will be used to generate the'
                            ' numbers of the journal entries of this journal.'),
        'journal_class_id': fields.many2one('afip.journal_class',
                                            'Document class'),
        'point_of_sale': fields.integer('Point of sale ID'),
    }
account_journal()


class res_currency(osv.osv):
    _inherit = "res.currency"
    _columns = {
        'afip_code': fields.char('AFIP Code', size=4),
    }
res_currency()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
