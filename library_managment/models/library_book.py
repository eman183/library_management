# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string='Book Title', required=True)
    isbn = fields.Char(string='ISBN')
    author_ids = fields.Many2many('library.author', string='Authors')
    publish_date = fields.Date(string='Published Date')
    cover_image = fields.Binary(string='Cover Image')
    summary = fields.Text(string='Summary')
    rental_ids = fields.One2many('library.rental', 'book_id', string='Rentals')
    is_available = fields.Boolean(string='Is Available', compute='_compute_is_available', store=True)
    rental_line_ids = fields.One2many('library.rental.line', 'book_id', string='Rental History')

    @api.depends('rental_ids.state')
    def _compute_is_available(self):
        for book in self:
            book.is_available = not any(rental.state == 'rented' for rental in book.rental_ids)

    def open_active_rentals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Rentals',
            'res_model': 'library.rental',
            'view_mode': 'tree,form',
            'domain': [
                ('book_id', '=', self.id),
                ('state', '=', 'rented')
            ],
            'context': dict(self.env.context),
            'target': 'current',
        }
