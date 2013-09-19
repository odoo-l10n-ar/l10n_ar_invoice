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
import re

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'responsability_id': fields.many2one('afip.responsability', 'Resposability'),
        'document_type': fields.many2one('afip.document_type', 'Document type'),
        'document_number': fields.char('Document number', size=64, select=1),
        'iibb': fields.char('Ingresos Brutos', size=64),
        'start_date': fields.date('Inicio de actividades'),
    }

    def onchange_vat(self, cr, uid, ids, vat, document_type, document_number, context={}):
        obj_doc_type = self.pool.get('afip.document_type')

        cuit_document_type = obj_doc_type.search(cr, uid, [('code','=','CUIT')])

        if vat[:2]=='ar' and document_type==False and document_number==False:
            document_type = cuit_document_type
            document_number = vat[2:]
        elif document_type==False and document_number==False:
            country = vat[:2]

    def afip_validation(sefl, cr, uid, ids, context={}):
        """ Hay que validar si el partner no es de tipo 'consumidor final' tenga un CUIT asociado.
            - Si el cuit es extrangero, hay que asignar a document_number y document_type los correspondientes
            a la interpretación argentina del CUIT.
            - Si es responsable monotributo hay que asegurarse que tenga vat asignado. El documento y
            número de documento deberían ser DNI.
            - Si es responsable inscripto y persona juridica indicar el cuit copia del VAT.
            El objetivo es que en la generación de factura utilice la información de document_type y document_number.
            
            Otra opción es asignar a la argentina los prefijos: 'cuit' 'dni' 'ci', etc...
            
            Del prefijo se toma el número de documento. Que opinanará la comunidad?"""
        
        for part in self.read(cr, uid, ids, ['document_number', 'document_type', 'vat', 'is_vat_subject']):
            pass

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
