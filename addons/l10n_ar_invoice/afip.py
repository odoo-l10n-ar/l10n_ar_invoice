# -*- coding: utf-8 -*-
from openerp import api, models, _
from openerp import fields
from openerp import exceptions


class afip_journal_template(models.Model):
    _name = 'afip.journal_template'
    _description = 'AFIP Document template'

    name = fields.Char('Name', size=120)
    code = fields.Integer('Code')

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!')]


class afip_document_class(models.Model):
    _name = 'afip.document_class'
    _description = 'Document class'

    name = fields.Char('Name', size=64, required=True)
    description = fields.Text('Description')
    responsability_relation_ids = fields.One2many(
        'afip.responsability_relation', 'document_class_id',
        'Reponsability relations')
    journal_class_ids = fields.One2many(
        'afip.journal_class', 'document_class_id',
        'Journal classes')

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!')]


class afip_responsability(models.Model):
    _name = 'afip.responsability'
    _description = 'VAT Responsability'

    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=8, required=True)
    active = fields.Boolean('Active', default=True)
    issuer_relation_ids = fields.One2many(
        'afip.responsability_relation', 'issuer_id',
        'Issuer relation')
    receptor_relation_ids = fields.One2many(
        'afip.responsability_relation', 'receptor_id',
        'Receptor relation')

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!'),
                        ('code', 'unique(code)', 'Not repeat code!')]


class afip_responsability_relation(models.Model):
    _name = 'afip.responsability_relation'
    _description = 'Responsability relation'

    name = fields.Char('Name', size=64)
    issuer_id = fields.Many2one(
        'afip.responsability', 'Issuer', required=True)
    receptor_id = fields.Many2one(
        'afip.responsability', 'Receptor', required=True)
    document_class_id = fields.Many2one(
        'afip.document_class', 'Document class', required=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('main_constraints',
         'unique(issuer_id, receptor_id, document_class_id)',
         'Not configuration!'),
        ('name', 'unique(name)', 'Not repeat name!')]


class afip_journal_class(models.Model):
    _name = 'afip.journal_class'
    _description = 'AFIP Journal types'

    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=8, required=True)
    sequence = fields.Integer('Sequence', required=True, default=0)
    document_class_id = fields.Many2one(
        'afip.document_class', 'Document Class')
    type = fields.Selection([
        ('sale', 'Sale'),
        ('sale_refund', 'Sale Refund'),
        ('purchase', 'Purchase'),
        ('purchase_refund', 'Purchase Refund'),
        ('cash', 'Cash'),
        ('bank', 'Bank and Cheques'),
        ('general', 'General'),
        ('situation', 'Opening/Closing Situation'),
        ], 'Type', size=32, required=True,
        help="Select 'Sale' for Sale journal to be used at the time"
        " of making invoice."
        " Select 'Purchase' for Purchase Journal to be used at the"
        " time of approving purchase order."
        " Select 'Cash' to be used at the time of making payment."
        " Select 'General' for miscellaneous operations."
        " Select 'Opening/Closing Situation' to be used at the time"
        " of new fiscal year creation or end of year entries generation.")
    afip_code = fields.Integer('AFIP Code', required=True)
    journal_ids = fields.One2many(
        'account.journal', 'journal_class_id',
        'Journals')
    active = fields.Boolean('Active', default=True)
    product_types = fields.Char(
        'Product types',
        help='Only use products with this product types in this journals. '
        'Types must be a subset of adjust, consu and service separated'
        ' by commas.')

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!')]


class afip_document_type(models.Model):
    _name = 'afip.document_type'
    _description = 'AFIP document types'

    name = fields.Char('Name', size=120, required=True)
    code = fields.Char('Code', size=16, required=True)
    afip_code = fields.Integer('AFIP Code', required=True)
    active = fields.Boolean('Active', default=True)


class afip_concept_type(models.Model):
    _name = 'afip.concept_type'
    _description = 'AFIP concept types'

    name = fields.Char('Name', size=120, required=True)
    afip_code = fields.Integer('AFIP Code', required=True)
    active = fields.Boolean('Active', default=True)
    product_types = fields.Char(
        'Product types',
        help='Translate this product types to this AFIP concept. '
        'Types must be a subset of adjust, consu and service'
        ' separated by commas.',
        required=True)

    @api.model
    def get_code(self, types):
        types = set(types)
        if not types:
            return False
        if False in types:
            types.remove(False)
            types.add('undefined')
        for concept in self.search([]):
            product_types = set([s.strip()
                                 for s in concept.product_types.split(',')])
            if product_types == types:
                return str(concept.afip_code)
	return False

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!')]


class afip_tax_code(models.Model):
    _inherit = 'account.tax.code'

    afip_code = fields.Integer('AFIP Code')
    parent_afip_code = fields.Integer(compute='_get_parent_afip_code',
                                      string='Parent AFIP Code')

    @api.multi
    def _get_parent_afip_code(self):
        for tc in self:
            if tc.afip_code:
                tc.parent_afip_code = tc.afip_code
            elif tc.parent_id:
                tc.parent_afip_code = tc.parent_id._get_parent_afip_code()
            else:
                tc.parent_afip_code = False

    @api.multi
    def get_afip_name(self):
        r = {}

        for tc in self:
            if tc.afip_code:
                r[tc.id] = tc.name
            elif tc.parent_id:
                r[tc.id] = tc.parent_id.get_afip_name()[tc.parent_id.id]
            else:
                r[tc.id] = False

        return r


class afip_optional_type(models.Model):
    _name = 'afip.optional_type'
    _description = 'AFIP optional types'

    name = fields.Char('Name', size=120, required=True)
    afip_code = fields.Integer('AFIP Code', required=True)
    apply_rule = fields.Char('Apply rule')
    value_computation = fields.Char('Value computation')
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!')]


class afip_uom(models.Model):
    _name = 'afip.uom'

    name = fields.Char('Name')
    afip_code = fields.Integer('AFIP Code')
    valid_from = fields.Date('Valid from')
    valid_to = fields.Date('Valid to')

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!')]


class afip_product_uom(models.Model):
    _inherit = 'product.uom'

    afip_uom_id = fields.Many2one('afip.uom', string='AFIP Unit')
    afip_code = fields.Integer(compute='_get_afip_code', string='AFIP Code')

    @api.depends('afip_uom_id.afip_code', 'category_id.afip_uom_id.afip_code')
    def _get_afip_code(self):
        for uom in self:
            if uom.afip_uom_id:
                uom.afip_code = uom.afip_uom_id.afip_code
            elif uom.category_id.afip_uom_id:
                uom.afip_code = uom.category_id.afip_uom_id.afip_code
            else:
                uom.afip_code = False


class afip_product_uom_category(models.Model):
    _inherit = 'product.uom.categ'

    afip_uom_id = fields.Many2one('afip.uom', string='AFIP Unit')
    afip_code = fields.Integer(related=['afip_uom_id', 'afip_code'],
                               string='AFIP Code')


class afip_language(models.Model):
    _inherit = 'res.lang'

    afip_code = fields.Integer('AFIP Code')


class afip_destination(models.Model):
    _name = 'afip.destination'

    name = fields.Char('Name', required=True)
    afip_code = fields.Integer('Code', required=True)
    afip_cuit_person = fields.Char('Person AFIP ID')
    afip_cuit_company = fields.Char('Company AFIP ID')
    afip_cuit_other = fields.Char('Other AFIP ID')
    country_ids = fields.Many2many('res.country',
                                   string='Associated Countries')
    state_ids = fields.Many2many('res.country.state',
                                 string='Associated States')
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!')]


class afip_incoterm(models.Model):
    _name = 'afip.incoterm'

    name = fields.Char('Name', required=True)
    afip_code = fields.Char('Code', size=5)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [('name', 'unique(name)', 'Not repeat name!')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
