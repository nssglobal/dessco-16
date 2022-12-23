# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'

    location_qty_3 = fields.Float(compute='cal_available_qty_3',string="SNY Stock")
    location_qty_4 = fields.Float(compute='cal_available_qty_4',string="MCT Stock")
    location_qty_5 = fields.Float(compute='cal_available_qty_5',string="HLT Stock")

    @api.depends('qty_available')
    def cal_available_qty_5(self):
        for rec in self:
            total = 0
            quants = self.get_quant_lines()
            quants = self.env['stock.quant'].browse(quants)
            for line in quants:
                if line.product_tmpl_id.id == rec.id and line.location_id.name == 'HLT Stock':
                    total = total + line.available_quantity
            rec.location_qty_5 = total

    @api.depends('qty_available')
    def cal_available_qty_4(self):
        for rec in self:
            total = 0
            quants = self.get_quant_lines()
            quants = self.env['stock.quant'].browse(quants)
            for line in quants:
                if line.product_tmpl_id.id == rec.id and line.location_id.name == 'MCT Stock':
                    total = total + line.available_quantity
            rec.location_qty_4 = total

    @api.depends('qty_available')
    def cal_available_qty_3(self):
        for rec in self:
            total = 0
            quants = self.get_quant_lines()
            quants = self.env['stock.quant'].browse(quants)
            for line in quants:
                if line.product_tmpl_id.id == rec.id and line.location_id.name == 'SNY Stock':
                    total = total + line.available_quantity
            rec.location_qty_3 = total


    def get_quant_lines(self):
        domain_loc = self.env['product.product']._get_domain_locations()[0]
        quant_ids = [l['id'] for l in self.env['stock.quant'].search_read(domain_loc, ['id'])]
        return quant_ids
