# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote


class OverrideDeliveryNote(DeliveryNote):
	def validate(self):
		self.validate_posting_time()
		super().validate()
		self.validate_references()
		self.set_status()
		self.so_required()
		self.validate_proj_cust()
		self.check_sales_order_on_hold_or_close("against_sales_order")
		self.validate_warehouse()
		self.validate_uom_is_integer("stock_uom", "stock_qty")
		self.validate_uom_is_integer("uom", "qty")
		self.validate_with_previous_doc()
		self.set_serial_and_batch_bundle_from_pick_list()

		from drsaucy.hook_events.utils import make_packing_list

		make_packing_list(self)
		self.update_current_stock()

		if not self.installation_status:
			self.installation_status = "Not Installed"

		self.validate_against_stock_reservation_entries()
		self.reset_default_field_value("set_warehouse", "items", "warehouse")
