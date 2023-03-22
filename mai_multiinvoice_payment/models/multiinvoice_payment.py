from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date, timedelta

class AccountPaymentInvoices(models.Model):
	_name = 'account.payment.invoice'

	invoice_id = fields.Many2one('account.move', string='Invoice')
	payment_id = fields.Many2one('account.payment', string='Payment')
	currency_id = fields.Many2one(related='invoice_id.currency_id')
	origin = fields.Char(related='invoice_id.invoice_origin')
	date_invoice = fields.Date(related='invoice_id.invoice_date')
	date_due = fields.Date(related='invoice_id.invoice_date_due')
	payment_state = fields.Selection(related='payment_id.state', store=True)
	reconcile_amount = fields.Monetary(string='Reconcile Amount')
	amount_total = fields.Monetary(related="invoice_id.amount_total")
	residual = fields.Monetary(related="invoice_id.amount_residual")


class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	invoice_id = fields.Many2one('account.move', string='Invoice')

	def reconcile(self):
		''' Reconcile the current move lines all together.
		:return: A dictionary representing a summary of what has been done during the reconciliation:
				* partials:             A recorset of all account.partial.reconcile created during the reconciliation.
				* full_reconcile:       An account.full.reconcile record created when there is nothing left to reconcile
										in the involved lines.
				* tax_cash_basis_moves: An account.move recordset representing the tax cash basis journal entries.
		'''
		results = {'exchange_partials': self.env['account.partial.reconcile']}

		if not self:
			return results

		# List unpaid invoices
		not_paid_invoices = self.move_id.filtered(
			lambda move: move.is_invoice(include_receipts=True) and move.payment_state not in ('paid', 'in_payment')
		)

		# ==== Check the lines can be reconciled together ====
		company = None
		account = None
		for line in self:
			if line.reconciled:
				raise UserError(_("You are trying to reconcile some entries that are already reconciled."))
			if not line.account_id.reconcile and line.account_id.internal_type != 'liquidity':
				raise UserError(_("Account %s does not allow reconciliation. First change the configuration of this account to allow it.")
								% line.account_id.display_name)
			if line.move_id.state != 'posted':
				raise UserError(_('You can only reconcile posted entries.'))
			if company is None:
				company = line.company_id
			elif line.company_id != company:
				raise UserError(_("Entries doesn't belong to the same company: %s != %s")
								% (company.display_name, line.company_id.display_name))
			if account is None:
				account = line.account_id
			elif line.account_id != account:
				raise UserError(_("Entries are not from the same account: %s != %s")
								% (account.display_name, line.account_id.display_name))

		sorted_lines = self.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id))

		# ==== Collect all involved lines through the existing reconciliation ====

		involved_lines = sorted_lines
		involved_partials = self.env['account.partial.reconcile']
		current_lines = involved_lines
		current_partials = involved_partials
		while current_lines:
			current_partials = (current_lines.matched_debit_ids + current_lines.matched_credit_ids) - current_partials
			involved_partials += current_partials
			current_lines = (current_partials.debit_move_id + current_partials.credit_move_id) - current_lines
			involved_lines += current_lines

		# ==== Create partials ====
		partial_no_exch_diff = bool(self.env['ir.config_parameter'].sudo().get_param('account.disable_partial_exchange_diff'))
		sorted_lines_ctx = sorted_lines.with_context(no_exchange_difference=self._context.get('no_exchange_difference') or partial_no_exch_diff)
		partial_amount = self.env.context.get('amount', False)
		if partial_amount:
			partials = sorted_lines_ctx._create_reconciliation_partials()
			if partials:
				partials[0].update({
					'amount': partial_amount, 
					'debit_amount_currency': partial_amount, 
					'credit_amount_currency': partial_amount,
				})
		else:
			partials = sorted_lines_ctx._create_reconciliation_partials()

		# partials = self.env['account.partial.reconcile'].create(reconcile)
		# Track newly created partials.
		results['partials'] = partials
		involved_partials += partials
		exchange_move_lines = partials.exchange_move_id.line_ids.filtered(lambda line: line.account_id == account)
		involved_lines += exchange_move_lines
		exchange_diff_partials = exchange_move_lines.matched_debit_ids + exchange_move_lines.matched_credit_ids
		involved_partials += exchange_diff_partials
		results['exchange_partials'] += exchange_diff_partials
		# ==== Create entries for cash basis taxes ====

		is_cash_basis_needed = account.company_id.tax_exigibility and account.account_type in ('asset_receivable', 'liability_payable')
		if is_cash_basis_needed and not self._context.get('move_reverse_cancel'):
			tax_cash_basis_moves = partials._create_tax_cash_basis_moves()
			results['tax_cash_basis_moves'] = tax_cash_basis_moves

		# ==== Check if a full reconcile is needed ====

		def is_line_reconciled(line):
			# Check if the journal item passed as parameter is now fully reconciled.
			return line.reconciled \
				   or line.currency_id.is_zero(line.amount_residual_currency) \
				   or line.company_currency_id.is_zero(line.amount_residual)

		if all(is_line_reconciled(line) for line in involved_lines):

			# ==== Create the exchange difference move ====
			# This part could be bypassed using the 'no_exchange_difference' key inside the context. This is useful
			# when importing a full accounting including the reconciliation like Winbooks.

			exchange_move = None
			if not self._context.get('no_exchange_difference'):
				# In normal cases, the exchange differences are already generated by the partial at this point meaning
				# there is no journal item left with a zero amount residual in one currency but not in the other.
				# However, after a migration coming from an older version with an older partial reconciliation or due to
				# some rounding issues (when dealing with different decimal places for example), we could need an extra
				# exchange difference journal entry to handle them.
				exchange_lines_to_fix = self.env['account.move.line']
				amounts_list = []
				exchange_max_date = date.min
				for line in involved_lines:
					if not line.company_currency_id.is_zero(line.amount_residual):
						exchange_lines_to_fix += line
						amounts_list.append({'amount_residual': line.amount_residual})
					elif not line.currency_id.is_zero(line.amount_residual_currency):
						exchange_lines_to_fix += line
						amounts_list.append({'amount_residual_currency': line.amount_residual_currency})
					exchange_max_date = max(exchange_max_date, line.date)
				exchange_diff_vals = exchange_lines_to_fix._prepare_exchange_difference_move_vals(
					amounts_list,
					company=involved_lines[0].company_id,
					exchange_date=exchange_max_date,
				)

				# Exchange difference for cash basis entries.
				if is_cash_basis_needed:
					involved_lines._add_exchange_difference_cash_basis_vals(exchange_diff_vals)

				# Create the exchange difference.
				if exchange_diff_vals['move_vals']['line_ids']:
					exchange_move = involved_lines._create_exchange_difference_move(exchange_diff_vals)
					if exchange_move:
						exchange_move_lines = exchange_move.line_ids.filtered(lambda line: line.account_id == account)

						# Track newly created lines.
						involved_lines += exchange_move_lines

						# Track newly created partials.
						exchange_diff_partials = exchange_move_lines.matched_debit_ids \
												 + exchange_move_lines.matched_credit_ids
						involved_partials += exchange_diff_partials
						results['exchange_partials'] += exchange_diff_partials

			# ==== Create the full reconcile ====

			results['full_reconcile'] = self.env['account.full.reconcile'].create({
				'exchange_move_id': exchange_move and exchange_move.id,
				'partial_reconcile_ids': [(6, 0, involved_partials.ids)],
				'reconciled_line_ids': [(6, 0, involved_lines.ids)],
			})

		not_paid_invoices.filtered(lambda move:
			move.payment_state in ('paid', 'in_payment')
		)._invoice_paid_hook()

		return results

		return results


class AccountPayment(models.Model):
	_inherit = 'account.payment'

	payment_invoice_ids = fields.One2many('account.payment.invoice', 'payment_id',string="Customer Invoices")

	@api.onchange('payment_type', 'partner_type', 'partner_id', 'currency_id')
	def _onchange_to_get_vendor_invoices(self):
		if self.payment_type in ['inbound', 'outbound'] and self.partner_type and self.partner_id and self.currency_id:
			self.payment_invoice_ids = [(6, 0, [])]
			if self.payment_type == 'inbound' and self.partner_type == 'customer':
				invoice_type = 'out_invoice'
			elif self.payment_type == 'outbound' and self.partner_type == 'customer':
				invoice_type = 'out_refund'
			elif self.payment_type == 'outbound' and self.partner_type == 'supplier':
				invoice_type = 'in_invoice'
			else:
				invoice_type = 'in_refund'
			invoice_recs = self.env['account.move'].search([
				('partner_id', 'child_of', self.partner_id.id), 
				('state', '=', 'posted'), 
				('move_type', '=', invoice_type), 
				('payment_state', '!=', 'paid'), 
				('currency_id', '=', self.currency_id.id)])
			payment_invoice_values = []
			for invoice_rec in invoice_recs:
				payment_invoice_values.append([0, 0, {'invoice_id': invoice_rec.id}])
			self.payment_invoice_ids = payment_invoice_values

	def action_post(self):
		super(AccountPayment, self).action_post()
		for payment in self:
			if payment.payment_invoice_ids:
				if payment.amount < sum(payment.payment_invoice_ids.mapped('reconcile_amount')):
					raise UserError(_("The sum of the reconcile amount of listed invoices are greater than payment's amount."))

			for line_id in payment.payment_invoice_ids:
				if not line_id.reconcile_amount:
					continue
				if line_id.amount_total <= line_id.reconcile_amount:
					self.ensure_one()
					if payment.payment_type == 'inbound':
						lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0)
						lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
						lines.reconcile()
					elif payment.payment_type == 'outbound':
						lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0)
						lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
						lines.reconcile()
				else:
					self.ensure_one()
					if payment.payment_type == 'inbound':
						lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0)
						lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
						lines.with_context(amount=line_id.reconcile_amount).reconcile()
					elif payment.payment_type == 'outbound':
						lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0)
						lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
						lines.with_context(amount=line_id.reconcile_amount).reconcile()
		return True
