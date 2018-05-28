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
    categoria_insumos_id = fields.Many2one('product.category', 'Categoria de consumibles')

    def crear_abastecimiento(self, location_id, location_dest_id, picking_type_id, ubicacion_consumibles_id, ruta_id):
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
                    #'product_uom_qty': orderpoint.product_max_qty - existencias,
                    'product_uom': orderpoint.product_id.uom_po_id.id,
                    'product_uom_qty': orderpoint.product_id.uom_id._compute_quantity(orderpoint.product_max_qty - existencias, orderpoint.product_id.uom_po_id),
                    'location_id': location_id,
                    'location_dest_id': ubicacion_destino_id,
                    #'ruta_id': ruta_id,
                    'state': 'draft',
                }))
        
        if len(lineas) > 0:
            picking = self.env['stock.picking'].create({
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'picking_type_id': picking_type_id,
                'ruta_id': ruta_id,
                'generado':True,
            })

            picking.move_lines = lineas



    @api.multi
    def generar_abastecimiento_planificado(self, location_id, location_dest_id=None):
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

            if hoy < 4:
                dia_semana = str(hoy + 2)
            elif hoy >= 4:
                dia_semana = str(hoy - 4)

            despachos = []
            filtro = [('dia_semana', '=', dia_semana)]
            if location_dest_id:
                filtro.append(('location_id','=',location_dest_id))

            for despacho in self.env['abastecimientos.despacho'].search(filtro):
                despachos.append({'ubicacion_id': despacho.location_id, 'ruta_id': despacho.ruta_id})

            logging.warn(despachos)
            for despacho in despachos:
                self.crear_abastecimiento(location_id, despacho['ubicacion_id'].id, despacho['ubicacion_id'].picking_type_id.id, despacho['ubicacion_id'].ubicacion_consumibles_id.id, despacho['ruta_id'].id)


class Picking(models.Model):
    _inherit = "stock.picking"

    generado = fields.Boolean('Generado')
    ruta_id = fields.Many2one('abastecimientos.ruta', 'Ruta de despacho')