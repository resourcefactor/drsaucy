# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from erpnext.manufacturing.doctype.blanket_order.blanket_order import (
	validate_against_blanket_order,
)
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	validate_inter_company_party,
)
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder


class OverrideSalesOrder(SalesOrder):
	def validate(self):
		super().validate()
		self.validate_delivery_date()
		self.validate_proj_cust()
		self.validate_po()
		self.validate_uom_is_integer("stock_uom", "stock_qty")
		self.validate_uom_is_integer("uom", "qty")
		self.validate_for_items()
		self.validate_warehouse()
		self.validate_drop_ship()
		self.validate_reserved_stock()
		self.validate_serial_no_based_delivery()
		validate_against_blanket_order(self)
		validate_inter_company_party(
			self.doctype, self.customer, self.company, self.inter_company_order_reference
		)

		if self.coupon_code:
			from erpnext.accounts.doctype.pricing_rule.utils import validate_coupon_code

			validate_coupon_code(self.coupon_code)

		from drsaucy.hook_events.utils import make_packing_list

		make_packing_list(self)

		self.validate_with_previous_doc()
		self.set_status()

		if not self.billing_status:
			self.billing_status = "Not Billed"
		if not self.delivery_status:
			self.delivery_status = "Not Delivered"

		self.reset_default_field_value("set_warehouse", "items", "warehouse")
