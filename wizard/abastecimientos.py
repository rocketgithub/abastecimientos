# -*- coding: utf-8 -*-

from odoo import api, models, fields
import logging
import datetime

class CrearAbastecimiento(models.TransientModel):
    _name = 'abastecimientos.crear_abastecimiento'

    location_id = fields.Many2one('stock.location', 'Ubicación origen', required=True)
#    picking_type_id = fields.Many2one('stock.picking.type', 'Tipo de albarán', required=True)

    @api.multi
    def crear_abastecimiento(self):

        if self._context.get('active_id'):
            location_dest_id = self._context.get('active_id')
            ubicacion = self.env['stock.location'].search([('id', '=', location_dest_id)])[0]
            for wizard in self:
                self.env['stock.location'].generar_abastecimiento_planificado(wizard.location_id.id, location_dest_id)

