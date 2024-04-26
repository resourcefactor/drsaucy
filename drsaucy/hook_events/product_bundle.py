# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from operator import itemgetter
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.selling.doctype.product_bundle.product_bundle import ProductBundle


class OverrideProductBundle(ProductBundle):
	def validate_child_items(self):
		pass


def add_sub_items_on_validate(self, method):
	update_sub_items(self, save=False)


def update_sub_items(self, save=True):
	get_sub_items(self)
	add_sub_items(self, save=save)


def get_sub_items(self):
	self.cur_sub_items = {}
	for d in self.items:
		if not d.custom_is_bom_item:
			if frappe.db.exists("Product Bundle", {"new_item_code": d.item_code}):
				get_child_sub_items(self, d.item_code, d.qty)
			elif d.item_code:
				add_to_cur_sub_items(
					self,
					frappe._dict(
						{
							"item_code": d.item_code,
							"description": d.description,
							"uom": d.uom,
							"qty": flt(d.qty),
						}
					)
				)
		else:
			if d.custom_bom:
				get_exploded_items(self, d.custom_bom, d.qty)


def add_to_cur_sub_items(self, args):
	if self.cur_sub_items.get(args.item_code):
		self.cur_sub_items[args.item_code]["qty"] += args.qty
	else:
		self.cur_sub_items[args.item_code] = args


def get_child_sub_items(self, item_code, qty):
	child_fb_items = frappe.db.sql(
		"""
		SELECT
			pbs_item.item_code,
			pbs_item.description,
			pbs_item.uom,
			pbs_item.qty
		FROM `tabProduct Bundle` as pb
		JOIN `tabProduct Bundle Sub Item` as pbs_item on pb.name = pbs_item.parent
		WHERE
			pb.new_item_code = '{0}'
	""".format(item_code), as_dict=1)

	for d in child_fb_items:
		add_to_cur_sub_items(
			self,
			frappe._dict(
				{
					"item_code": d["item_code"],
					"description": d["description"],
					"uom": d["uom"],
					"qty": d["qty"] * qty,
				}
			)
		)


def add_sub_items(self, save=True):
	"Add items to Flat BOM table"
	self.set("custom_subitems", [])

	if save:
		frappe.db.sql("""delete from `tabProduct Bundle Sub Item` where parent=%s""", self.name)

	for d in sorted(self.cur_sub_items, key=itemgetter(0)):
		ch = self.append("custom_subitems", {})
		for i in self.cur_sub_items[d].keys():
			ch.set(i, self.cur_sub_items[d][i])
		ch.docstatus = self.docstatus

		if save:
			ch.db_insert()


def get_exploded_items(self, bom, qty):
	if frappe.db.exists("BOM", {"name", bom}):
		bom_doc = frappe.get_doc("BOM", bom)
		if not bom_doc.quantity or bom_doc.quantity == 0:
			bom_doc.quantity = 1
		for d in bom_doc.exploded_items:
			add_to_cur_sub_items(
				self,
				frappe._dict(
					{
						"item_code": d.item_code,
						"description": d.description,
						"uom": d.stock_uom,
						"qty": float(d.stock_qty / bom_doc.quantity) * qty
					}
				)
			)


@frappe.whitelist()
def get_default_bom(item_code):
	bom = frappe.db.get_value("BOM", {"docstatus": 1, "item": item_code, "is_default": 1}, ["name"])
	return bom
