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
from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)
_schema = logging.getLogger(__name__ + '.schema')

class l10n_ar_invoice_del_journal(osv.osv_memory):
    _name = 'l10n_ar_invoice.del_journal'
    _description = 'Journal to delete'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'builder_id': fields.many2one('l10n_ar_invoice.config', 'Builder Wizard')
    }

    def doit(self, cr, uid, ids, context=None):
        """
        Delete journals.
        """
        obj_journal = self.pool.get('account.journal')
        obj_cb_line = self.pool.get('account.journal.cashbox.line')

        to_delete = self.read(cr, uid, ids, ['name', 'journal_id'])
        jids = [ j['journal_id'][0] for j in to_delete ]
        names = [ j['name'] for j in to_delete ]

        # Remove dependencies
        cb_line_ids = obj_cb_line.search(cr, uid, [('journal_id','in',jids)])
        obj_cb_line.unlink(cr, uid, cb_line_ids)

        # Remove journals
        obj_journal.unlink(cr, uid, jids)
        _logger.info('Deleted journal %s' % ','.join(names))

l10n_ar_invoice_del_journal()

def _selection_code_get(self, cr, uid, context={}):
    cr.execute('select code, name from ir_sequence_type')
    return cr.fetchall()

class l10n_ar_invoice_new_sequence(osv.osv_memory):
    _name = 'l10n_ar_invoice.new_sequence'
    _description = 'Sequence to create'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.selection(_selection_code_get, 'Sequence type', size=64, required=True),
        'number_next': fields.integer('First number'),
        'prefix': fields.char('Prefix', size=64),
        'suffix': fields.char('Suffix', size=64),
        'padding': fields.integer('Padding'),
        'company_id': fields.many2one('res.company', 'Company'),
        'builder_id': fields.many2one('l10n_ar_invoice.config', 'Builder Wizard'),
    }

    def doit(self, cr, uid, ids, context=None):
        """
        Create sequences.
        """
        obj_sequence = self.pool.get('ir.sequence')

        vals = self.read(cr, uid, ids, ['name', 'code', 'number_next', 'prefix', 'suffix', 'padding'])
        names = [ v['name'] for v in vals ]
        for val in vals:
            del val['id']
            val['implementation'] = 'no_gap'
            sid = obj_sequence.create(cr, uid, val)
        _logger.info('Sequences created %s' % ','.join(names))

l10n_ar_invoice_new_sequence()

class l10n_ar_invoice_new_journal(osv.osv_memory):
    _name = 'l10n_ar_invoice.new_journal'
    _description = 'Journal to create'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=10, required=True),
        'type': fields.selection([('sale', 'Sale'),('sale_refund','Sale Refund'),
                                  ('purchase', 'Purchase'), ('purchase_refund','Purchase Refund')],
                                 'Type', size=32, required=True,
                                 help="Select 'Sale' for Sale journal to be used at the time of making invoice."\
                                 " Select 'Purchase' for Purchase Journal to be used at the time of approving purchase order."),
        'journal_class_id': fields.many2one('afip.journal_class', 'Document class'),
        'point_of_sale': fields.integer('Point of sale'),
        'sequence_name': fields.char('Sequence Name', size=64),
        'company_id': fields.many2one('res.company', 'Compania'),
        'currency': fields.many2one('res.currency', 'Moneda'),
        'builder_id': fields.many2one('l10n_ar_invoice.config', 'Builder Wizard'),
        'update_posted': fields.boolean('Allow Cancelling Entries'),
    }

    def doit(self, cr, uid, ids, context=None):
        obj_journal = self.pool.get('account.journal')
        obj_sequence = self.pool.get('ir.sequence')

        vals = self.read(cr, uid, ids, ['name', 'code', 'type', 'company_id',
                                        'journal_class_id', 'point_of_sale', 'sequence_name',
                                        'currency', 'update_posted'])
        names = [ v['name'] for v in vals ]
        for val in vals:
            val['sequence_id'] = obj_sequence.search(cr, uid, [('name','=',val['sequence_name'])]).pop()
            del val['id']
            del val['sequence_name']
            val = dict( (k, v[0]) if type(v) is tuple else (k, v) for k,v in val.items() )
            sid = obj_journal.create(cr, uid, val)
        _logger.info('Journals created %s' % ','.join(names))

l10n_ar_invoice_new_journal()

class l10n_ar_invoice_config(osv.osv_memory):
    def _default_company(self, cr, uid, c, context=None):
        return self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id

    def _default_responsability(self, cr, uid, c, context=None):
        resp_obj = self.pool.get('afip.responsability')
        ids = resp_obj.search(cr, uid, [('name','=','Responsable Monotributo')])
        return ids.pop()

    _name = 'l10n_ar_invoice.config'
    _inherit = 'res.config'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'cuit': fields.char('CUIT', size=12, required=True),
        'iibb': fields.char('IIBB', size=12, required=True),
        'start_date': fields.date('Inicio de Actividades', required=True),
        'responsability_id': fields.many2one('afip.responsability', 'Resposability', required=True, domain=[('code','!=','CF')]),
        'do_export': fields.boolean(u'Realiza o realizará operaciones de Exportación'),
        'remove_old_journals': fields.boolean('Eliminar los diarios existentes',
            help=u'Si es su primera instalación indique que necesita borrar los diarios existentes. Si agrega un nuevo punto de ventas indique que no va a eliminar los journals. Igual, puede indicar cuales borra y cuales no en el próximo paso.'),
        'point_of_sale': fields.integer(u'Número de Punto de Venta',
            help=u'Este es el número que aparecerá como prefijo del número de la factura. Si solo tiene un solo talonario ese número es 1. Si necesita agregar un nuevo punto de venta debe acceder a opciones Administración/Configuración/Wizards de Configuración/Wizards de Configuración y ejecutar nuevamente el wizard de "Configuración de Facturación".'),
        'purchase_by_class': fields.boolean(u'Diario de Facturas de Compra diferenciado por tipo',
            help=u'Puede indicar tener un diario de facturación de compras por cada tipo de facturas que puede recibir, o simplemente usar un solo diario de facturación que será identificado con una X en su nombre'),
        'sequence_by': fields.selection([('type', 'Type'),('sub_type', 'Sub type'),('class', 'Class'),('journal', 'Journal')],
                                        'Sequence by', size=32, required=True,
                                        help="Select 'Type' for different sequence by 'sale' and 'puchase'"\
                                        "Select 'Sub type' for different sequence by 'sale', 'sale refund', 'purchase' and 'purchase refund'"\
                                        "Select 'Class' for different sequence by class of document (A, B, C, M or E) "\
                                        "Select 'Journal' for different sequence by Journal "),
        'journals_to_delete': fields.one2many('l10n_ar_invoice.del_journal', 'builder_id', 'Journals to delete'),
        'sequences_to_create': fields.one2many('l10n_ar_invoice.new_sequence', 'builder_id', 'Sequence to delete'),
        'journals_to_create': fields.one2many('l10n_ar_invoice.new_journal', 'builder_id', 'Journals to create'),
    }

    _defaults= {
        'company_id': _default_company,
        'do_export': False,
        'remove_old_journals': True,
        'sequence_by': 'type',
        'point_of_sale': 1,
        'purchase_by_class': False,
        'journals_to_delete': lambda self, cr, uid, c, context=None: self.update_del_journals(
            cr, uid, [],
            self._default_company(cr, uid, c, context),
            self._default_responsability(cr, uid, c, context),
            False, True, 'type', 1, False, context=context),
        'sequences_to_create': lambda self, cr, uid, c, context=None: self.update_new_journals(
            cr, uid, [],
            self._default_company(cr, uid, c, context),
            self._default_responsability(cr, uid, c, context),
            False, True, 'type', 1, False, context=context)[1],
        'journals_to_create': lambda self, cr, uid, c, context=None: self.update_new_journals(
            cr, uid, [],
            self._default_company(cr, uid, c, context),
            self._default_responsability(cr, uid, c, context),
            False, True, 'type', 1, False, context=context)[0],
    }

    def _get_account_properties(self, cr, uid, company_id):
        """
        Return id of accounts from properties
        """
        obj_property = self.pool.get('ir.property')
        properties = {
            'sale': 'property_account_income_categ',
            'sale_refund': 'property_account_income_categ',
            'purchase': 'property_account_expense_categ',
            'purchase_refund': 'property_account_expense_categ',
        }
        property_ids = obj_property.search(cr, uid, [('name','in',properties.values()),
                                                     ('company_id','=',company_id)])


        prop = obj_property.read(cr, uid, property_ids, ['name', 'value_reference'])
        d = dict( (p['name'].encode('ascii'), int(p['value_reference'].split(',')[1])) for p in prop )
        r = dict( (k, d[v]) for k,v in properties.items() )
        return r

    def update_company_id(self, cr, uid, ids, company_id, context=None):
        """
        Set cuit & iibb
        """
        v = {}
        if company_id:
            company_obj = self.pool.get('res.company')
            company = company_obj.browse(cr, uid, company_id)
            v = {
                'cuit': company.partner_id.document_number,
                'iibb': company.partner_id.iibb,
                'start_date': company.partner_id.start_date,
                'responsability_id': company.partner_id.responsability_id.id,
            }
        return { 'value': v }

    def update_del_journals(self, cr, uid, ids, company_id, responsability_id, do_export, remove_old_journals, sequence_by, point_of_sale, purchase_by_class, context=None):
        """
        Remove Sale Journal, Purchase Journal, Sale Refund Journal, Purchase Refund Journal.
        """
        ret = []
        djis = []

        if company_id and responsability_id and point_of_sale:

            obj_journal = self.pool.get('account.journal')
            obj_del_journal = self.pool.get('l10n_ar_invoice.del_journal')

            if remove_old_journals:
                jou_ids = obj_journal.search(cr, uid, [
                    ('type','in',['sale','purchase','sale_refund','purchase_refund']),
                    ('company_id','=',company_id)]
                )
                jous = obj_journal.read(cr, uid, jou_ids, ['name'])
                for jou in jous:
                    dj = {'name': jou['name'], 'journal_id': jou['id'], 'builder_id': ids }
                    ret.append(dj)

        return ret

    def update_new_journals(self, cr, uid, ids, company_id, responsability_id, do_export, remove_old_journals, sequence_by, point_of_sale, purchase_by_class, update_posted=False, context=None):
        """
        Create Journals for Argentinian Invoices.
        """
        ret = []
        seq = []
        rel = {}

        if company_id and responsability_id and point_of_sale:
 
            account_ids = self._get_account_properties(cr, uid, company_id)
            
            obj_company = self.pool.get('res.company')
            obj_seq_type = self.pool.get('ir.sequence.type')

            currency_id = obj_company.browse(cr, uid, company_id).currency_id.id

            cr.execute("""select row_number() over () as row,
                          JC.name as name, max(JC.code) as code,
                          JC.type as type, JC.document_class as document_class,
                          max(JC.id) as document_class_id
                       from afip_responsability_class as RC
                       left join afip_responsability as Re on (RC.emisor_id=Re.id)
                       left join afip_responsability as Rr on (RC.receptor_id = Rr.id)
                       left join afip_journal_class  as JC on (RC.document_class = JC.document_class or JC.document_class = 'X')
                       where (Re.id = %s and type in ('sale', 'sale_refund')) or (Rr.id = %s and type in ('purchase','purchase_refund')) and
                        case when %s then (not JC.document_class = 'X')
                                     else (JC.document_class = 'X' or JC.type in ('sale','sale_refund'))
                        end
                       group by JC.name, JC.type, JC.document_class order by type, document_class
                       """,
                       (responsability_id, responsability_id, purchase_by_class))

            fetch_items = list(cr.fetchall())
            items = [ dict(zip([c.name for c in cr.description], item)) for item in fetch_items ]

            if do_export:
                cr.execute("""select code, name, document_class, %i + (row_number() over ()) as row, type, id as document_class_id
                           from afip_journal_class where document_class = 'E'""" % len(items))
                fetch_items = list(cr.fetchall())
                items.extend([ dict(zip([c.name for c in cr.description], item)) for item in fetch_items ])

            # Create sequence
            if sequence_by == 'journal':
                _code_to_type = {
                    'sale': 'journal_sale_vou',
                    'sale_refund': 'journal_sale_vou',
                    'purchase': 'journal_pur_vou',
                    'purchase_refund': 'journal_pur_vou',
                }
                #_code_to_type = dict( (k, obj_seq_type.search(cr, uid, [('code','=',v)])[0] ) for k,v in _code_to_type.items() )

                for item in items:
                    sequence = {
                        'name': u"%s (%04i-%s)" % (item['name'], point_of_sale, item['code']),
                        'code': _code_to_type[item['type']],
                        'number_next': 1,
                        'prefix': '%04i-' % (point_of_sale,),
                        'suffix': '',
                        'padding': 8,
                        'company_id': company_id,
                    }
                    seq.append(sequence)
                    rel[item['row']]= sequence['name']

            elif sequence_by == 'class':
                _code_to_type = {
                    'sale': 'journal_sale_vou',
                    'sale_refund': 'journal_sale_vou',
                    'purchase': 'journal_pur_vou',
                    'purchase_refund': 'journal_pur_vou',
                }
                #_code_to_type = dict( (k, obj_seq_type.search(cr, uid, [('code','=',v)])[0] ) for k,v in _code_to_type.items() )
                _name = lambda item: u"Document class %s (%04i)" % (item['document_class'], point_of_sale)
                group = {}
                for item in items:
                    group[item['document_class']] = item
                    rel[item['row']]= _name(item)

                for key, item in group.items():
                    sequence = {
                        'name': _name(item),
                        'code': _code_to_type[item['type']],
                        'number_next': 1,
                        'prefix': '%04i-' % (point_of_sale,),
                        'suffix': '',
                        'padding': 8,
                        'company_id': company_id,
                    }
                    seq.append(sequence)

            elif sequence_by == 'sub_type':
                _code_to_type = {
                    'sale': 'account.invoice.out_invoice',
                    'sale_refund': 'account.invoice.out_refund',
                    'purchase': 'account.invoice.in_invoice',
                    'purchase_refund': 'account.invoice.in_refund',
                }
                #_code_to_type = dict( (k, obj_seq_type.search(cr, uid, [('code','=',v)])[0] ) for k,v in _code_to_type.items() )
                _name = lambda item: u"Document type %s (%04i)" % (item['type'], point_of_sale)
                group = {}
                for item in items:
                    group[item['type']] = item
                    rel[item['row']]= _name(item)

                for key, item in group.items():
                    sequence = {
                        'name': _name(item),
                        'code': _code_to_type[item['type']],
                        'number_next': 1,
                        'prefix': '%04i-' % (point_of_sale,),
                        'suffix': '',
                        'padding': 8,
                        'company_id': company_id,
                    }
                    seq.append(sequence)

            elif sequence_by == 'type':
                _code_to_type = {
                    'sale': 'journal_sale_vou',
                    'sale_refund': 'journal_sale_vou',
                    'purchase': 'journal_pur_vou',
                    'purchase_refund': 'journal_pur_vou',
                }
                #_code_to_type = dict( (k, obj_seq_type.search(cr, uid, [('code','=',v)])[0] ) for k,v in _code_to_type.items() )
                _group_type = {
                    'sale': 'sale',
                    'sale_refund': 'sale',
                    'purchase': 'purchase',
                    'purchase_refund': 'purchase',
                }
                _name = lambda item: u"Document type %s (%04i)" % (_group_type[item['type']], point_of_sale)
                group = {}
                for item in items:
                    group[_group_type[item['type']]] = item
                    rel[item['row']]= _name(item)

                for key, item in group.items():
                    sequence = {
                        'name': _name(item),
                        'code': _code_to_type[item['type']],
                        'number_next': 1,
                        'prefix': '%04i-' % (point_of_sale,),
                        'suffix': '',
                        'padding': 8,
                        'company_id': company_id,
                    }
                    seq.append(sequence)

            # Create journal
            for item in items:
                journal = {
                    'name': u"%s (%04i-%s)" % (item['name'], point_of_sale, item['code']),
                    'code': u"%s%04i" % (item['code'], point_of_sale),
                    'journal_class_id': item['document_class_id'],
                    'company_id': company_id,
                    'currency': currency_id,
                    'point_of_sale': point_of_sale,
                    'sequence_name': rel[item['row']],
                    'type': item['type'],
                    'update_posted': update_posted
                }
                ret.append(journal)

        return ret, seq

    def update_journals(self, cr, uid, ids, company_id, responsability_id, do_export, remove_old_journals, sequence_by, point_of_sale, purchase_by_class, update_posted=False, context=None):

        v = {
            'journals_to_delete': self.update_del_journals (cr, uid, ids, company_id, responsability_id, do_export, remove_old_journals, sequence_by, point_of_sale, purchase_by_class),
        }
        j, s = self.update_new_journals (cr, uid, ids, company_id,
                                         responsability_id, do_export,
                                         remove_old_journals, sequence_by,
                                         point_of_sale, purchase_by_class,
                                         update_posted)
        v.update({
            'sequences_to_create': s,
            'journals_to_create': j,
        })
        return { 'value': v }

    def delete_journals(self, cr, uid, ids, context=None):
        """
        Delete all journals selected in journals_to_delete.
        """
        obj_del_journal = self.pool.get('l10n_ar_invoice.del_journal')

        for i in self.read(cr, uid, ids, ['journals_to_delete']):
            obj_del_journal.doit(cr, uid, i['journals_to_delete'])

        return

    def create_sequences(self, cr, uid, ids, context=None):
        obj_new_sequence = self.pool.get('l10n_ar_invoice.new_sequence')

        for i in self.read(cr, uid, ids, ['sequences_to_create']):
            obj_new_sequence.doit(cr, uid, i['sequences_to_create'])

        return

    def create_journals(self, cr, uid, ids, context=None):
        """
        Generate Items to generate Sequences and Journals associated to Invoices Types
        """
        obj_new_journal = self.pool.get('l10n_ar_invoice.new_journal')

        for i in self.read(cr, uid, ids, ['journals_to_create']):
            obj_new_journal.doit(cr, uid, i['journals_to_create'])

    def execute(self, cr, uid, ids, context=None):
        """
        Execute Configure button
        """
        if context is None:
            context = {}

        obj_partner = self.pool.get('res.partner')
        obj_document_type = self.pool.get('afip.document_type')

        document_type_cuit = obj_document_type.search(cr, uid, [('code','=','CUIT')])[0]

        for wzd in self.browse(cr, uid, ids):
            partner_id = wzd.company_id.partner_id.id
            obj_partner.write(cr, uid, partner_id,
                                               {'responsability_id': wzd.responsability_id.id,
                                                'document_number': wzd.cuit,
                                                'document_type': document_type_cuit,
                                                'iibb': wzd.iibb,
                                                'start_date': wzd.start_date,
                                                'vat': 'ar%s' % wzd.cuit,
                                               })
            obj_partner.check_vat(cr, uid, [partner_id])

        self.delete_journals(cr, uid, ids, context=context)
        self.create_sequences(cr, uid, ids, context=context)
        self.create_journals(cr, uid, ids, context=context)

        # We dont need install any addon at this point.
        #super(l10n_ar_invoice_config, self).execute(cr, uid, ids, context)

l10n_ar_invoice_config()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
