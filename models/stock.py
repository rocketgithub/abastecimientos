# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import date

class Location(models.Model):
    _inherit = "stock.location"

    picking_type_id = fields.Many2one('stock.picking.type', 'Tipo orden abastecimiento')
    dia_semana = fields.Selection([
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miercoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sabado'),
    ])
    dias_despacho_ids = fields.One2many('abastecimientos.despacho', 'location_id', string='Dias de despacho')
    ubicacion_consumibles_id = fields.Many2one('stock.location', 'Ubicación de consumibles')
    categoria_insumos_id = fields.Many2one('product.category', 'Categoria de insumos')

    def crear_abastecimiento(self, location_id, location_dest_id, picking_type_id, ubicacion_consumibles_id):
        lineas = []
        for orderpoint in self.env['stock.warehouse.orderpoint'].search([('location_id', '=', location_dest_id)]):
            existencias = orderpoint.product_id.with_context({'location' : location_dest_id}).qty_available
#            if orderpoint.product_id.type == 'consu' and ubicacion_consumibles_id:
            if orderpoint.product_id.categ_id == self.categoria_insumos_id and ubicacion_consumibles_id:
                ubicacion_destino_id = ubicacion_consumibles_id
            else:
                ubicacion_destino_id = location_dest_id

            if orderpoint.product_min_qty >= existencias:
                lineas.append((0, 0, {
                    'name': '/',
                    'product_id': orderpoint.product_id.id,
                    'product_uom_qty': orderpoint.product_max_qty - existencias,
                    'product_uom': orderpoint.product_id.uom_po_id.id,
                    'location_id': location_id,
                    'location_dest_id': ubicacion_destino_id,
                    'state': 'draft',
                }))
        
        if len(lineas) > 0:
            picking = self.env['stock.picking'].create({
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'picking_type_id': picking_type_id,
                'generado':True,
            })

            picking.move_lines = lineas



    @api.multi
    def generar_abastecimiento_planificado(self, location_id=""):
        if location_id != "":
            hoy = date.today().weekday()

            # dia_semana = str(hoy + 2)
            # 0 - Lunes     0 + 2 -> Miercoles
            # 1 - Martes    1 + 2 -> Jueves
            # 2 - Miercoles 2 + 2 -> Viernes
            # 3 - Jueves    3 + 2 -> Sabado

            # dia_semana = str(hoy - 4)
            # 4 - Viernes   4 - 4 -> Lunes
            # 5 - Sabado    5 - 4 -> Martes
            # 6 - Domingo   6 - 4 -> Miercoles (No deberia aplicar)

#            for despacho_id in self.dias_despacho_ids
            if hoy < 4:
                dia_semana = str(hoy + 2)
            elif hoy >= 4:
                dia_semana = str(hoy - 4)

            ubicacion_ids = []
            for despacho in self.env['abastecimientos.despacho'].search([('dia_semana', '=', dia_semana)]):
                ubicaciones_ids.append(despacho.location_id.id)
            for ubicacion in self.browse(ubicacion_ids):
                self.crear_abastecimiento(location_id, ubicacion.id, ubicacion.picking_type_id.id, ubicacion.ubicacion_consumibles_id.id)


class Picking(models.Model):
    _inherit = "stock.picking"

    generado = fields.Boolean('Generado')