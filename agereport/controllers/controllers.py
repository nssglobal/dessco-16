# -*- coding: utf-8 -*-
# from odoo import http


# class Agereport(http.Controller):
#     @http.route('/agereport/agereport', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/agereport/agereport/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('agereport.listing', {
#             'root': '/agereport/agereport',
#             'objects': http.request.env['agereport.agereport'].search([]),
#         })

#     @http.route('/agereport/agereport/objects/<model("agereport.agereport"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('agereport.object', {
#             'object': obj
#         })
