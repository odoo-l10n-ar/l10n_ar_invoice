# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from datetime import date
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning


def _all_taxes(x):
    return True


def _all_except_vat(x):
    return x.tax_code_id.parent_id.name != 'IVA'


class account_invoice_line(models.Model):
    """
    Line of an invoice. Compute pirces with and without vat,
    for unit or line quantity.
    """
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('quantity', 'discount', 'price_unit', 'invoice_line_tax_id',
                 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id')
    def compute_price(self, context=None):
        self.price_unit_vat_included = self.price_calc(use_vat=True, quantity=1)
        self.price_subtotal_vat_included = self.price_calc(use_vat=True)
        self.price_unit_not_vat_included = self.price_calc(use_vat=False,
                                                           quantity=1)
        self.price_subtotal_not_vat_included = self.price_calc(use_vat=False)

    price_unit_vat_included = fields.Float(compute='compute_price')
    price_subtotal_vat_included = fields.Float(compute='compute_price')
    price_unit_not_vat_included = fields.Float(compute='compute_price')
    price_subtotal_not_vat_included = fields.Float(compute='compute_price')

    @api.v8
    def price_calc(self, use_vat=True, tax_filter=None, quantity=None,
                   discount=None, context=None):
        assert len(self) == 1, "Use price_calc with one instance"
        _tax_filter = tax_filter or (use_vat and _all_taxes) or _all_except_vat
        _quantity = quantity if quantity is not None else self.quantity
        _discount = discount if discount is not None else self.discount
        _price = self.price_unit * (1-(_discount or 0.0)/100.0)

        taxes = self.invoice_line_tax_id.filtered(_tax_filter).compute_all(
            _price, _quantity,
            product=self.product_id,
            partner=self.invoice_id.partner_id
        )
        return self.invoice_id.currency_id.round(taxes['total_included']) \
            if self.invoice_id else taxes['total_included']

    @api.v8
    def compute_all(self, tax_filter=lambda tax: True, context=None):
        res = {}
        for line in self:
            _quantity = line.quantity
            _discount = line.discount
            _price = line.price_unit * (1-(_discount or 0.0)/100.0)
            taxes = line.invoice_line_tax_id.filtered(tax_filter).compute_all(
                _price, _quantity,
                product=line.product_id,
                partner=line.invoice_id.partner_id)

            if line.invoice_id:
                def _round(x):
                    return line.invoice_id.currency_id.round(x)
            else:
                def _round(x):
                    return x

            res[line.id] = {
                'amount_untaxed': _round(taxes['total']),
                'amount_tax': _round(taxes['total_included']) -
                _round(taxes['total']),
                'amount_total': _round(taxes['total_included']),
                'taxes': taxes['taxes'],
            }
        return res.get(len(self) == 1 and res.keys()[0], res)

account_invoice_line()


def _calc_concept(product_types):
    if product_types == set(['consu']):
        concept = '1'
    elif product_types == set(['service']):
        concept = '2'
    elif product_types == set(['consu', 'service']):
        concept = '3'
    else:
        raise Warning(
            _('Cant compute AFIP concept from product types %s.') %
            product_types
        )
    return concept


class account_invoice(models.Model):
    """
    Argentine invoice functions.
    """
    _name = "account.invoice"
    _inherit = "account.invoice"

    @api.depends('invoice_line.product_id.type')
    def _get_concept(self):
        """
        Compute concept type from selected products in invoice.
        """
        concept_obj = self.env['afip.concept_type']

        for inv in self:
            product_types = set([
                line.product_id.type for line in inv.invoice_line
            ])
            inv.afip_concept = concept_obj.get_code(product_types) \
                if False not in product_types \
                else False

    def _get_service_begin_date(self):
        try:
            period = self.period_id.find()
            if not self.env.context.get('is_prepaid', False):
                period = period.find(date.today() + relativedelta(months=-1))
            return period.date_start
        except:
            return False

    def _get_service_end_date(self):
        try:
            period = self.period_id.find()
            if not self.env.context.get('is_prepaid', False):
                period = period.find(date.today() + relativedelta(months=-1))
            return period.date_stop
        except:
            return False

    afip_concept = fields.Selection(
        [('1', 'Consumible'), ('2', 'Service'), ('3', 'Mixted')],
        compute="_get_concept",
        store=False,
        help="AFIP invoice concept.")
    afip_service_start = fields.Date(
        'Service Start Date', default=_get_service_begin_date)
    afip_service_end = fields.Date(
        'Service End Date', default=_get_service_end_date)

    @api.multi
    def _afip_test_journal(self):
        """
        Check if you choose the right journal.
        """
        for invoice in self:
            if invoice.type == 'out_invoice' and \
                    invoice.journal_id.journal_class_id.afip_code not in\
                    [1, 6, 11, 51, 19, 2, 7, 12, 52, 20]:
                raise Warning(
                    _('Wrong Journal\n'
                      'Out invoice journal must have a valid journal class.'))
            if invoice.type == 'out_refund' and \
                    invoice.journal_id.journal_class_id.afip_code not in\
                    [3, 8, 13, 53, 21]:
                raise Warning(
                    _('Wrong Journal\n'
                      'Out invoice journal must have a valid journal class.'))

    @api.multi
    def _afip_test_document(self):
        """
        Test documentation
        """
        for invoice in self:
            # Partner responsability ?
            partner = invoice.partner_id
            if not partner.responsability_id:
                raise Warning(
                    _('No responsability\n'
                      'Your partner have not afip responsability assigned.'
                      ' Assign one please.'))

            # Take responsability classes for this journal
            invoice_class = \
                invoice.journal_id.journal_class_id.document_class_id
            company = invoice.journal_id.company_id.partner_id
            resp_class = \
                self.env['afip.responsability_relation'].search(
                    [('document_class_id', '=', invoice_class.id),
                     ('issuer_id.code', '=', company.responsability_id.code)])

            # You can emmit this document?
            if not resp_class:
                raise Warning(
                    _('Invalid emisor\n'
                      'Your responsability with AFIP dont let you generate'
                      ' this kind of document.'))

            # Partner can receive this document?
            resp_class = \
                self.env['afip.responsability_relation'].search([
                    ('document_class_id', '=', invoice_class.id),
                    ('receptor_id.code', '=', partner.responsability_id.code)
                ])
            if not resp_class:
                raise Warning(
                    _('Invalid receptor\n'
                      'Your partner (%s) can\'t receive this document (%s).'
                      ' Check AFIP responsability of the partner,'
                      ' or Journal Account of the invoice.') %
                    (partner.responsability_id.name, invoice_class.name))

    @api.multi
    def _afip_test_limits(self):
        """
        Test limits
        """
        for invoice in self:
            # If Final Consumer have pay more than 1000$,
            # you need more information to generate document.
            if invoice.partner_id.responsability_id.code == 'CF' \
                    and invoice.amount_total > 1000 and \
                    (invoice.partner_id.document_type_id.code in [None, 'Sigd']
                     or invoice.partner_id.document_number is None):
                raise Warning(_('Partner without Identification for total'
                                ' invoices > $1000.-\n'
                                'You must define valid document type and'
                                ' number for this Final Consumer.'))

    @api.multi
    def _afip_test_lines(self):
        """
        Test invoice lines
        """
        for invoice in self:
            # Afip concept must be defined
            if invoice.afip_concept is False:
                if any(l.product_id is False for l in invoice.invoice_line):
                    raise Warning(_('All lines must have a product'))
                if any(l.product_id.type is False
                       for l in invoice.invoice_line):
                    raise Warning(_('One product has not type'))
            elif invoice.afip_concept != 1:
                # Check if concept is service then start and end must be set
                if invoice.afip_service_start is False or \
                        invoice.afip_service_end is False:
                    raise Warning(_('Please set afip service dates'))
                if invoice.afip_service_start > invoice.afip_service_end:
                    raise Warning(_('Service dates are wrong'))

    @api.multi
    def afip_validation(self):
        """
        Check basic AFIP request to generate invoices.
        """
        for invoice in self:
            # If company is not in Argentina, ignore it.
            if invoice.company_id.partner_id.country_id.name != 'Argentina':
                continue

            self._afip_test_journal()
            self._afip_test_document()
            self._afip_test_limits()
            self._afip_test_lines()

        return True

    def compute_all(self, cr, uid, ids, line_filter=lambda line: True,
                    tax_filter=lambda tax: True, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            amounts = []
            for line in inv.invoice_line:
                if line_filter(line):
                    amounts.append(line.compute_all(tax_filter=tax_filter,
                                                    context=context))

            s = {
                'amount_total': 0,
                'amount_tax': 0,
                'amount_untaxed': 0,
                'taxes': []
            }
            for amount in amounts:
                for key, value in amount.items():
                    s[key] = s.get(key, 0) + value

            res[inv.id] = s

        return res.get(len(ids) == 1 and ids[0], res)

    @api.multi
    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        # Set list of valid journals by partner responsability
        # partner_obj = self.pool.get('res.partner')
        partner = self.partner_id
        company = self.company_id
        responsability = partner.responsability_id
        result = {}

        if not responsability:
            msg = {
                'title': _('The partner has not set any fiscal responsability'),
                'message': _('Please, set partner fiscal responsability in the'
                             ' partner form before continuing.')
            }
            return {'warning', msg}

        if responsability.issuer_relation_ids is None:
            return {}

        if not company.partner_id.responsability_id.id:
            msg = {
                'title': _('Your company has not set any fiscal'
                           ' responsability'),
                'message': _('Please, set your company responsability in the'
                             ' company form before continuing.')
            }
            return {'warning', msg}

        accepted_journal_ids = self.partner_id.prefered_journals(
            self.company_id.id, self.type)

        if accepted_journal_ids:
            result['domain'].update({
                'journal_id': [('id', 'in', accepted_journal_ids)],
            })
            self.journal_id = accepted_journal_ids[0]
        else:
            result['domain'].update({
                'journal_id': [('id', 'in', [])],
            })
            self.journal_id = False

        return result

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
