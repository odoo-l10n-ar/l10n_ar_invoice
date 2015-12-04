# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import re


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'responsability_id': fields.many2one(
            'afip.responsability',
            'Responsability'
        ),
        'document_type_id': fields.many2one(
            'afip.document_type',
            'Document type',
            on_change="onchange_document(vat,document_type_id,document_number)"
        ),
        'document_number': fields.char(
            'Document number',
            size=64, select=1,
            on_change="onchange_document(vat,document_type_id,document_number)"
        ),
        'iibb': fields.char('Ingresos Brutos', size=64),
        'start_date': fields.date('Inicio de actividades'),
    }

    def onchange_document(self, cr, uid, ids, vat, document_type,
                          document_number, context={}):
        v = {}
        m = None
        mod_obj = self.pool.get('ir.model.data')
        if document_number and \
                (u'afip.document_type', document_type) == \
                mod_obj.get_object_reference(
                    cr, uid, 'l10n_ar_invoice', 'dt_CUIT'):
            document_number = re.sub('[^1234567890]', '', str(document_number))
            if not self.check_vat_ar(document_number):
                m = {'title': _('Warning!'),
                     'message': _('VAT Number is wrong.\n'
                                  ' Please verify the number before continue.')}
            if vat is False:
                v['vat'] = 'AR%s' % document_number
            v['document_number'] = document_number
        return {'value': v,
                'warning': m}

    # TODO: v8
    # def onchange_vat(self, cr, uid, ids, vat, document_type, document_number,
    #                  context={}):
    #     """
    #     Not used because is complex to integrate.
    #     Could be associated to country?
    #     """
    #     country_obj = self.pool.get('res.country')
    #     doc_type_obj = self.pool.get('afip.document_type')

    #     cuit_document_type_id = doc_type_obj.search(cr, uid,
    #                                                 [('code', '=', 'CUIT')])

    #     v = {}
    #     if vat[:2].lower() == 'ar' and document_type is False and \
    #             document_number is False:
    #         v['document_type'] = cuit_document_type_id
    #         v['document_number'] = vat[2:]
    #     elif document_type is False and document_number is False:
    #         country_ids = country_obj.search(cr, uid,
    #                                          [('code', '=', vat[:2].upper())])
    #         iva_data = country_obj.read(cr, uid,
    #                                     country_ids,
    #                                     ['cuit_juridica', 'cuit_fisica'])
    #         v['document_type'] = cuit_document_type_id
    #         v['document_number'] = iva_data['cuit_juridica'
    #                                         if is_company else 'cuit_fisica']
    #     return { 'value': v }

    def afip_validation(self, cr, uid, ids, context={}):
        """
        Hay que validar si:
        - El partner no es de tipo 'consumidor final' tenga un CUIT asociado.
        - Si el CUIT es extranjero, hay que asignar a document_number y
          document_type los correspondientes a la interpretación argentina del
          CUIT.
        - Si es responsable monotributo hay que asegurarse que tenga VAT
          asignado. El documento y número de documento deberían ser DNI.
        - Si es Responsable Inscripto y Persona Jurídica indicar el CUIT copia
          del VAT.

        El objetivo es que en la generación de factura utilice la información de
        document_type y document_number.

        Otra opción es asignar a la argentina los prefijos: 'cuit' 'dni' 'ci',
        etc...

        Del prefijo se toma el número de documento. Que opinanará la comunidad?
        """

        for part in self.read(cr, uid, ids,
                              ['document_number', 'document_type_id',
                               'vat', 'is_vat_subject']):
            pass

    def prefered_journals(self, cr, uid, ids, type, context=None):
        """
        Devuelve la lista de journals disponibles para este partner.
        """
        # Set list of valid journals by partner responsability
        partner_pool = self.pool.get('res.partner')
        journal_class_pool = self.pool.get('afip.journal_class')

        context = context or {}

        if 'company_id' in context:
            company_pool = self.pool.get('res.company')
            company = company_pool.browse(cr, uid, context['company_id'])
        else:
            company = self.pool.get('res.users').browse(cr, uid, uid).company_id

        if not company.partner_id:
            raise Warning(_('Error!\n'
                            'Your company has not setted any partner'))

        if not company.partner_id.responsability_id:
            raise Warning(_('Error!\n'
                            'Your company has not setted any responsability'))

        result = {}

        type_map = {
            'out_invoice': ['sale'],
            'out_refund': ['sale_refund'],
            'in_invoice': ['purchase'],
            'in_refund': ['purchase_refund'],
        }

        for partner in self.browse(cr, uid, ids):
            partner_id = partner.id
            partner = partner_pool.browse(cr, uid, partner_id)

            if not partner.responsability_id:
                raise Warning(
                    _('Error!\n'
                      'This partner has not setted any responsability')
                )

            journal_data = journal_class_pool.search_read(
                cr, uid, [
                    ('type', 'in', type_map[type]),
                    ('document_class_id.responsability_relation_ids'
                     '.issuer_id', '=',
                     company.partner_id.responsability_id.id),
                    ('document_class_id.responsability_relation_ids'
                     '.receptor_id', '=',
                     partner.responsability_id.id),
                ], ['journal_ids'], order="sequence asc")

            journal_ids = reduce(lambda a, b: a + b,
                                 [jc['journal_ids'] for jc in journal_data])

            result[partner_id] = journal_ids

        return result

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
