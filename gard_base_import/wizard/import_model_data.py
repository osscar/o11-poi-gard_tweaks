#!/usr/bin/env python
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Poiesis Consulting (<http://www.poiesisconsulting.com>).
#    Autor: Nicolas Bustillos
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

import csv
from io import StringIO

from odoo import models, fields, api, _, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)

import csv
from io import StringIO
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ImportModelDataWizard(models.TransientModel):
    _name = 'import.model.data.wizard'
    _description = 'Import Model Data Wizard'

    csv_file = fields.Binary(string='CSV File', required=True)
    target_model = fields.Char(string='Target Model', required=True, readonly=True)
    export_template_id = fields.Many2one('ir.exports', string='Export Template', domain="[('is_import_friendly', '=', True)]", required=True)

    def default_get(self, fields):
        res = super(GenericImportWizard, self).default_get(fields)
        context = self.env.context
        target_model = context.get('active_model', False)
        if target_model:
            res['target_model'] = target_model
        return res
    
    def _get_preview_data(self, csv_data):
        # Read a few lines from the CSV data to generate a preview
        preview_lines = []
        try:
            csv_reader = csv.reader(StringIO(csv_data.decode('utf-8')))
            for i, row in enumerate(csv_reader):
                if i >= 5:  # Limit the preview to the first 5 rows
                    break
                preview_lines.append(','.join(row))
        except Exception as e:
            preview_lines.append(f"Error reading CSV: {e}")
        return '\n'.join(preview_lines)
    
    def export_template(self):
        for wizard in self:
            export_template = wizard.export_template_id

            # Retrieve the fields and field labels from the export list
            field_labels = []
            field_names = []
            for field in export_template.mapped('export_fields_id.field_id'):
                field_labels.append(field.field_description)
                field_names.append(field.name)

            # Create a CSV template with header row
            csv_data = StringIO()
            csv_writer = csv.writer(csv_data, quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(field_labels)

            # Encode the CSV data as a binary file
            csv_content = csv_data.getvalue().encode('utf-8')

            # Save the CSV data to the import_template field as a binary file
            wizard.import_template = base64.b64encode(csv_content)

    def clear_export_data(self):
        self.import_template = False

    def import_data(self):
        for wizard in self:
            csv_data = wizard.csv_file
            target_model = wizard.target_model
            export_template = wizard.export_template_id
            preview_data = self._get_preview_data(csv_data)
            wizard.preview_data = preview_data

            # Process CSV data
            try:
                decoded_data = base64.b64decode(csv_data)
                csv_data = decoded_data.decode('utf-8')
                csv_file = StringIO(csv_data)
                csv_reader = csv.DictReader(csv_file)
            except Exception as e:
                raise ValidationError(f"Error reading CSV file: {e}")

            # Create records based on CSV data
            created_records = []
            for row in csv_reader:
                # Map CSV columns to target model fields
                mapped_data = {
                    'field1': row.get('Column1'),  # Replace with actual mapping
                    'field2': row.get('Column2'),  # Replace with actual mapping
                    # Add more field mappings as needed
                }

                # Validate data or perform additional transformations as required
                # For example, you can add data validation logic here

                # Create a record in the target model
                record = self.env[target_model].create(mapped_data)

                # Append the created record to the list
                created_records.append(record)

            # Add import date and time to the note field of created records
            current_datetime = fields.Datetime.now()
            note = f"Imported on {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
            for record in created_records:
                record.note = note
                
                
            # Delete the attachment after processing
            attachment = self.env['ir.attachment'].search([('res_model', '=', 'import.from.export.list.wizard'), ('res_id', '=', wizard.id)])
            if attachment:
                attachment.unlink()

            # You can return a message or perform other actions as needed
            # For example:
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'title': 'Import Completed',
            #         'message': 'Data imported successfully.',
            #         'sticky': True,
            #     }
            # }


from odoo import models, fields, api

class GenericImportWizard(models.TransientModel):
    _name = 'generic.import.wizard'
    _description = 'Generic Import Wizard'

    csv_file = fields.Binary(string='CSV File', required=True)
    target_model = fields.Char(string='Target Model', required=True, readonly=True)
    export_template_id = fields.Many2one('ir.exports', string='Export Template', domain="[('is_import_friendly', '=', True)]", required=True)

    def import_data(self):
        for wizard in self:
            csv_data = wizard.csv_file
            target_model = wizard.target_model
            export_template = wizard.export_template_id

            # Implement your import logic here, using target_model and export_template
            # Example: Create records based on the CSV data
            # created_records = self.env[target_model].create([...])

            # Add import date and time to the note field of created records
            current_datetime = fields.Datetime.now()
            note = f"Imported on {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}"

            # Update the note field for created records
            # for record in created_records:
            #     record.note = note


from odoo import models, fields


class ImportFromExportListWizard(models.TransientModel):
    _name = 'import.from.export.list.wizard'

    model_id = fields.Many2one('ir.model', string='Model', required=True)
    export_list_id = fields.Many2one('export.list', string='Export List', required=True)
    csv_file = fields.Binary(string="CSV File", required=True)
    preview_data = fields.Text(string="Preview Data", readonly=True)
    
    def export_csv_template(self):
        for wizard in self:
            export_list = wizard.export_list_id

            if export_list:
                # Get selected fields from the export list
                selected_fields = export_list.export_fields

                # Create a CSV header row
                header_row = ','.join(selected_fields)

                # Generate a CSV template
                csv_data = StringIO()
                csv_writer = csv.writer(csv_data)
                csv_writer.writerow([header_row])

                # Save the CSV template as an attachment
                attachment_data = csv_data.getvalue().encode('utf-8')
                wizard.env['ir.attachment'].create({
                    'name': 'import_template.csv',
                    'type': 'binary',
                    'datas': base64.b64encode(attachment_data),
                    'res_model': 'import.from.export.list.wizard',
                    'res_id': wizard.id,
                })

                # Close the CSV data stream
                csv_data.close()
                
    def _get_preview_data(self, csv_data):
        # Read a few lines from the CSV data to generate a preview
        preview_lines = []
        try:
            csv_reader = csv.reader(StringIO(csv_data.decode('utf-8')))
            for i, row in enumerate(csv_reader):
                if i >= 5:  # Limit the preview to the first 5 rows
                    break
                preview_lines.append(','.join(row))
        except Exception as e:
            preview_lines.append(f"Error reading CSV: {e}")
        return '\n'.join(preview_lines)
                
    def create_invoices(self):
        for wizard in self:
            csv_data = wizard.csv_file

            csv_data = wizard.csv_file
            preview_data = self._get_preview_data(csv_data)
            wizard.preview_data = preview_data
            # Process the CSV data and create invoices
            # You can use the 'csv' module for parsing as shown in previous examples
            # After processing, create the invoices using self.env['account.invoice'].create(...
            
            # Add import date and time to the note field of created invoices
            current_datetime = datetime.datetime.now()
            note = f"Imported on {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}"

            for invoice in created_invoices:
                invoice.note = note

            # Create an import log record
            log_values = {
                'user_id': self.env.user.id,
                'model': 'account.invoice',  # Replace with the actual model name
                'created_record_ids': [(6, 0, [invoice.id for invoice in created_invoices])]
            }
            self.env['import.log'].create(log_values)
            
            # Delete the attachment after processing
            attachment = self.env['ir.attachment'].search([('res_model', '=', 'import.from.export.list.wizard'), ('res_id', '=', wizard.id)])
            if attachment:
                attachment.unlink()
