import frappe
from frappe import _


def validate_store_uom(self, method):
	uoms = [d.uom for d in self.uoms]
	if self.custom_store_uom and self.stock_uom != self.custom_store_uom and self.custom_store_uom not in uoms:
		frappe.throw(_("Store UOM: <b>{0}</b> should be same as Default UOM or include in UOM Table.").format(self.custom_store_uom))
