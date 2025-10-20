# -*- coding: utf-8 -*-
from odoo import models, fields,api,_
from odoo.exceptions import ValidationError,UserError


class LibraryRental(models.Model):
    _name = 'library.rental'
    _description = 'Library Rental'

    book_id = fields.Many2one('library.book', string='Book', required=True)
    borrower_id = fields.Many2one('res.partner', string='Borrower', required=True)
    rental_date = fields.Datetime(string='Rental Date', default=lambda self: fields.Datetime.now())
    return_date = fields.Datetime(string='Return Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('rented', 'Rented'),
        ('returned', 'Returned'),
        ('lost', 'Lost')
    ], string='State', default='draft')
    rental_line_ids = fields.One2many('library.rental.line', 'rental_id', string="Books Rented")

    def action_confirm_rental(self):
        for rental in self:
            if rental.state != 'draft':
                raise UserError("Only draft rentals can be confirmed.")

            existing_rental_line = self.env['library.rental.line'].search([
                ('book_id', '=', rental.book_id.id),
                ('state', '=', 'rented'),
            ], limit=1)
            if existing_rental_line:
                raise UserError("This book is already rented out and not yet returned.")

            if not rental.rental_date:
                rental.rental_date = fields.Datetime.now()

            self.env['library.rental.line'].create({
                'rental_id': rental.id,
                'book_id': rental.book_id.id,
                'rental_date': rental.rental_date,
                'state': 'rented',
                'return_date':rental.return_date
            })

            rental.state = 'rented'

    @api.constrains('book_id', 'state', 'return_date')
    def _check_duplicate_rental(self):
        for rental in self:
            if rental.state == 'rented' and not rental.return_date:
                existing = self.env['library.rental'].search([
                    ('book_id', '=', rental.book_id.id),
                    ('state', '=', 'rented'),
                    ('id', '!=', rental.id),
                    ('return_date', '=', False),
                ])
                if existing:
                    raise ValidationError("This book is already rented out and not returned yet.")

    def action_return_rental(self):
        for rental in self:
            if rental.state != 'rented':
                raise UserError("Only rented rentals can be returned.")

            rental.return_date = fields.Datetime.now()
            rental.state = 'returned'

            for line in rental.rental_line_ids:
                line.return_date = rental.return_date
                line.state = 'returned'

    def action_mark_as_lost(self):
        for rental in self:
            if rental.state != 'rented':
                raise UserError("Only rented rentals can be marked as lost.")

            rental.state = 'lost'

            for line in rental.rental_line_ids:
                line.state = 'lost'


class LibraryRentalLine(models.Model):
    _name = 'library.rental.line'
    _description = 'Rental Line'

    rental_id = fields.Many2one('library.rental', string="Rental", required=True, ondelete="cascade")
    book_id = fields.Many2one('library.book', string="Book", required=True)
    borrower_id = fields.Many2one(related='rental_id.borrower_id', store=True, readonly=True)

    rental_date = fields.Datetime(string='Rental Date', default=lambda self: fields.Datetime.now())
    return_date = fields.Datetime(string='Return Date')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('rented', 'Rented'),
        ('returned', 'Returned'),
        ('lost', 'Lost')
    ], string='State', default='draft', tracking=True)

    is_late = fields.Boolean(string='Is Late', compute='_compute_is_late', store=True)
    days_rented = fields.Integer(string="Days Rented", compute='_compute_days_rented', store=True)

    @api.depends('rental_date', 'return_date')
    def _compute_days_rented(self):
        for line in self:
            if line.return_date and line.rental_date:
                delta = line.return_date.date() - line.rental_date.date()
                line.days_rented = delta.days
            else:
                line.days_rented = 0

    @api.depends('return_date')
    def _compute_is_late(self):
        for line in self:
            if line.return_date and line.rental_date:
                line.is_late = (line.return_date - line.rental_date).days > 14
            else:
                line.is_late = False

    @api.constrains('book_id', 'state')
    def _check_duplicate_active_rental(self):
        for line in self:
            if line.state == 'rented':
                exists = self.search([
                    ('book_id', '=', line.book_id.id),
                    ('state', '=', 'rented'),
                    ('id', '!=', line.id)
                ])
                if exists:
                    raise ValidationError("This book is already rented and not yet returned.")

