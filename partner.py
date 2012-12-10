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

from osv import fields, osv
import re

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'responsability_id': fields.many2one('afip.responsability', 'Resposability'),
        'document_type': fields.many2one('afip.document_type', 'Document type'),
        'document_number': fields.char('Document number', size=64, select=1),
    }

    """
    # TODO: Dont work.
    _defaults = {
        'responsability_id': lambda self, cr, uid, *a: self.pool.get('ir.model.data').get_object(cr, uid, 'afip.responsability', 'res_CF'),
        'document_type': lambda self, cr, uid, *a: self.pool.get('ir.model.data').get_object(cr, uid, 'afip.document_type', 'dt_Sigd'),
        'document_number': '0',
    }
    """

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