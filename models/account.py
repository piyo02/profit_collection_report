from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ProfitCollectionReport(models.TransientModel):
    _name = 'account.profit.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    
    @api.multi
    def print_profit_coll_report(self):
        invoices = self.env['account.invoice'].search(
            [ 
                ('date_invoice', '<=', self.end_date),
                ('date_invoice', '>=', self.start_date),
                ('state', '=', 'paid'),
                ('type', '=', 'out_invoice'),
            ], 
            order="date_invoice asc")

        invoice_data = []
        for invoice in invoices:
            temp = []
            hpp_invoice = 0
            total_disc = 0
            
            so = self.env['sale.order'].search([
                ('name', '=', invoice.origin)
            ])

            total_so = so.amount_total
            percent = (invoice.amount_total*100) / total_so

            for order_line in so.order_line:
                modal = order_line.product_id.product_tmpl_id.standard_price
                quantity = order_line.product_uom_qty
                
                hpp_per_product = modal*quantity
                hpp_invoice += hpp_per_product

            for invoice_line in invoice.invoice_line_ids:
                total_disc += invoice_line.discount
        
            if percent != 100:
                hpp_invoice = (hpp_invoice*percent)/100
            
            margin = invoice.amount_total - hpp_invoice

            temp.append(invoice.number) #0
            temp.append(invoice.origin) #1
            temp.append(invoice.date_invoice) #2
            temp.append(invoice.partner_id.display_name) #3
            temp.append(total_disc) #4
            temp.append(invoice.amount_total) #5
            temp.append(hpp_invoice) #6
            temp.append(margin) #7
            
            invoice_data.append(temp)
            
        datas = {
            'ids': self.ids,
            'model': 'invoice.profit.report',
            'form': invoice_data,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'profit_collection_report.account_report_temp', data=datas)
