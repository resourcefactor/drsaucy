# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import cint
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class OverrideSalesInvoice(SalesInvoice):
	def update_packing_list(self):
		if cint(self.update_stock) == 1:
			from drsaucy.hook_events.utils import make_packing_list

			make_packing_list(self)
		else:
			self.set("packed_items", [])
