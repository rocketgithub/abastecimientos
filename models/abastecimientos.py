# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

class Rutas(models.Model):
    _name = "abastecimientos.ruta"

    name = fields.Char('Nombre')
    employee_id = fields.Many2one('hr.employee', 'Empleado')

class Despacho(models.Model):
    _name = "abastecimientos.despacho"

    location_id = fields.Many2one('stock.location', 'Despacho')
    dia_semana = fields.Selection([
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miercoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sabado'),
    ])
    ruta_id = fields.Many2one('abastecimientos.ruta', 'Ruta')
