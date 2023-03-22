# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountReport(models.Model):
    _inherit = 'account.report'

    def _fully_unfold_lines_if_needed(self, lines, options):
        def line_need_expansion(line_dict):
            return line_dict.get('unfolded') and line_dict.get('expand_function')

        custom_unfold_all_batch_data = None

        # If it's possible to batch unfold and we're unfolding all lines, compute the batch, so that individual expansions are more efficient
        if (self._context.get('print_mode') or options.get('unfold_all')) and self.custom_handler_model_id:
            lines_to_expand_by_function = {}
            for line_dict in lines:
                if line_need_expansion(line_dict):
                    lines_to_expand_by_function.setdefault(line_dict['expand_function'], []).append(line_dict)

            custom_unfold_all_batch_data = self.env[self.custom_handler_model_name]._custom_unfold_all_batch_data_generator(
                self, options, lines_to_expand_by_function)

        i = 0
        while i < len(lines):
            # We iterate in such a way that if the lines added by an expansion need expansion, they will get it as well
            line_dict = lines[i]
            # if self.display_name != 'Aged Receivable':
            if line_need_expansion(line_dict):
                groupby = line_dict.get('groupby')
                progress = line_dict.get('progress')
                # if self.display_name != 'Aged Receivable':
                to_insert = self._expand_unfoldable_line(line_dict['expand_function'], line_dict['id'], groupby, options,
                                                         progress, 0,
                                                         unfold_all_batch_data=custom_unfold_all_batch_data)
                lines = lines[:i + 1] + to_insert + lines[i + 1:]
            i += 1
        k = 0
        dic = []
        if self.display_name == 'Aged Receivable':
            for line in lines:

                if 'INV' not in line['name']:
                    dic.append(line)

        if dic != None:
            return dic
        else:
            return lines
