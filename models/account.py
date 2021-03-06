from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ProfitCollectionReport(models.TransientModel):
    _name = 'account.profit.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    
    @api.multi
    def print_profit_coll_report(self):
        payments = self.env['account.payment'].search(
            [ 
                ('payment_date', '<=', self.end_date),
                ('payment_date', '>=', self.start_date),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
            ], 
            order="payment_date asc")

        payment_data = []
        for payment in payments:
            temp = []
            hpp_payment = 0
            total_disc = 0
            
            if payment.has_invoices:
                memo_type = payment.communication

                if 'INV' in memo_type:
                    invoices = self.env['account.invoice'].search([
                        ('number', '=', memo_type),
                        ('state', '=', 'paid')
                    ])
                    so = self.env['sale.order'].search([
                        ('name', '=', invoices.origin)
                    ])

                elif 'SO' in memo_type:
                    so = self.env['sale.order'].search([
                        ('name', '=', memo_type)
                    ])
                    invoices = self.env['account.invoice'].search([
                        ('origin', '=', so.name),
                        ('state', '=', 'paid')
                    ])

                for invoice in invoices:
                    for invoice_line in invoice.invoice_line_ids:
                        
                        account_move = self.env['account.move'].search([
                            ('name', '=', invoice.number),
                        ])
                        for line in account_move.line_ids:
                            if(line.account_id.code[0] == '5' and line.product_id.name == invoice_line.product_id.name):
                                hpp_payment += line.debit

                        total_disc += invoice_line.discount

                    total_so = so.amount_total or invoice.amount_total
                    percent = (invoice.amount_total*100) / total_so

                    if percent != 100:
                        hpp_payment = (hpp_payment*percent)/100
                    
                    margin = payment.amount - hpp_payment

                    payment_number = payment.communication
                    origin = invoice.origin

                    temp.append(invoice.number) #0
                    temp.append(origin) #1
                    temp.append(payment.payment_date) #2
                    temp.append(payment.partner_id.display_name) #3
                    temp.append(total_disc) #4
                    temp.append(payment.amount) #5
                    temp.append(hpp_payment) #6
                    temp.append(margin) #7
                    
                    payment_data.append(temp)
            else:
                margin = payment.amount - hpp_payment
                payment_number = payment.name
                origin = ""

                temp.append(payment_number) #0
                temp.append(origin) #1
                temp.append(payment.payment_date) #2
                temp.append(payment.partner_id.display_name) #3
                temp.append(total_disc) #4
                temp.append(payment.amount) #5
                temp.append(hpp_payment) #6
                temp.append(margin) #7
            
                payment_data.append(temp)
            
        giros = self.env['vit.giro'].search(
            [ 
                ('clearing_date', '<=', self.end_date),
                ('clearing_date', '>=', self.start_date),
                ('type', '=', 'receipt'),
                ('state', '=', 'close'),
            ], 
            order="clearing_date asc")
        
        for giro in giros:
            temp = []
            temp.append(giro.name) #0
            temp.append("") #1
            temp.append(giro.clearing_date) #2
            temp.append(giro.partner_id.display_name) #3
            temp.append(0) #4
            temp.append(giro.amount) #5
            temp.append(0) #6
            temp.append(giro.amount) #7
        
            payment_data.append(temp)
        
        datas = {
            'ids': self.ids,
            'model': 'invoice.profit.report',
            'form': payment_data,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'profit_collection_report.account_report_temp', data=datas)
