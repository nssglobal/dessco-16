from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlwt
from io import BytesIO
import base64
from xlwt import easyxf
from datetime import datetime, timedelta


class SaleReportWizard(models.TransientModel):
    _name = 'sale.wizard'

    date_from = fields.Date()
    date_to = fields.Date()

    def export_excel(self):
        main_header_style = easyxf('font:height 400;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")
        main_date_style = easyxf('font:height 300;'
                                 'align: horiz center;font: color black; font:bold True;'
                                 "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")
        header_style_name = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz left;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        text_left = easyxf('font:height 200; align: horiz left;' "borders: top thin,bottom thin")
        text_center = easyxf('font:height 200; align: horiz center;' "borders: top thin,bottom thin")
        text_left_bold = easyxf(
            'font:height 200; align: horiz left;font:bold True;' "borders: top thin,bottom thin")
        text_right_bold = easyxf(
            'font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin",
                            num_format_str='0.00')
        workbook = xlwt.Workbook()
        worksheet = []
        for l in range(0, 1):
            worksheet.append(l)
        work = 0
        date_from = self.date_from.strftime("%d-%m-%Y")
        date_to = self.date_from.strftime("%d-%m-%Y")
        worksheet[work] = workbook.add_sheet('POS Sale Person Report')
        # dates = date_from + " To " + date_to
        # worksheet[work].write_merge(0, 1, 6, 10, self.company_id.name, main_header_style)
        worksheet[work].write_merge(3, 4, 2, 5, date_from + " To " + date_to, main_date_style)

        worksheet[work].write(6, 1, 'Product Name', header_style)
        worksheet[work].write(6, 2, 'QTY Purchase', header_style)
        worksheet[work].write(6, 3, 'QTY Sold', header_style)
        worksheet[work].write(6, 4, 'UOM', header_style)
        worksheet[work].write(6, 5, 'Unit Price', header_style)
        worksheet[work].write(6, 6, 'Cost Price', header_style)
        worksheet[work].write(6, 7, 'Sale Price', header_style)

        worksheet[work].col(1).width = 256 * 20
        worksheet[work].col(2).width = 256 * 20
        worksheet[work].col(3).width = 256 * 20
        worksheet[work].col(4).width = 256 * 20
        worksheet[work].col(5).width = 256 * 20
        worksheet[work].col(6).width = 256 * 20
        worksheet[work].col(7).width = 256 * 20

        i = 7
        products = self.env['stock.move'].search([('date', '>=', self.date_from), ('date', '<=', self.date_to)]).mapped('product_id').ids
        products = list(dict.fromkeys(products))

        for product in products:
            purchase = sum(self.env['stock.move'].search(
                [('picking_type_id.code', '=', 'incoming'),('product_id', '=', product), ('date', '>=', self.date_from), ('date', '<=', self.date_to)]).mapped('quantity_done'))
            sale = sum(self.env['stock.move'].search(
                [('picking_type_id.code', '=', 'outgoing'),('product_id', '=', product), ('date', '>=', self.date_from),
                 ('date', '<=', self.date_to)]).mapped('quantity_done'))
            product_name = self.env['product.product'].browse([product])
            worksheet[work].write(i, 1, product_name.name, text_left)
            worksheet[work].write(i, 2, purchase, text_center)
            worksheet[work].write(i, 3, sale, text_center)
            worksheet[work].write(i, 4, product_name.uom_id.name, text_center)
            worksheet[work].write(i, 5, product_name.list_price, text_center)
            worksheet[work].write(i, 6, product_name.standard_price, text_center)
            worksheet[work].write(i, 7, product_name.list_price, text_center)

            i = i + 1
        # worksheet[work].write(i, 1, "Total", header_style)
        # worksheet[work].write(i, 20, total_qty, header_style)
        # worksheet[work].write(i, 21, total_sale, header_style)

        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['sale.excel'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': 'Sale/Purchase Report.xls'})

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=sale.excel&field=excel_file&download=true&id=%s&filename=Sale/Purchase Report.xls' % (
                export_id.id),
            'target': 'new', }



class bulk_export_excel(models.TransientModel):
    _name = "sale.excel"

    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('Excel Name', size=64)

