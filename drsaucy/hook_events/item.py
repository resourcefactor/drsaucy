import frappe
from frappe import _


def validate_store_uom(self, method):
	uoms = [d.uom for d in self.uoms]
	if self.store_uom and self.stock_uom != self.store_uom and self.store_uom not in uoms:
		frappe.throw(_("Store UOM: <b>{0}</b> should be same as Default UOM or include in UOM Table.").format(self.store_uom))
