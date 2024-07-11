import frappe
from frappe import _
from erpnext.stock.doctype.packed_item.packed_item import (
	get_indexed_packed_items_table,
	reset_packing_list,
	is_product_bundle,
	add_packed_item_row,
	get_packed_item_details,
	update_packed_item_basic_data,
	update_packed_item_stock_data,
	update_packed_item_price_data,
	update_packed_item_from_cancelled_doc,
	update_product_bundle_rate,
	set_product_bundle_rate_amount,
)


def make_packing_list(doc):
	"Make/Update packing list for Product Bundle Item."
	if doc.get("_action") and doc._action == "update_after_submit":
		return

	parent_items_price, reset = {}, False
	set_price_from_children = frappe.db.get_single_value("Selling Settings", "editable_bundle_item_rates")

	stale_packed_items_table = get_indexed_packed_items_table(doc)

	reset = reset_packing_list(doc)

	for item_row in doc.get("items"):
		if is_product_bundle(item_row.item_code):
			for bundle_item in get_product_bundle_items(item_row.item_code):
				pi_row = add_packed_item_row(
					doc=doc,
					packing_item=bundle_item,
					main_item_row=item_row,
					packed_items_table=stale_packed_items_table,
					reset=reset,
				)
				item_data = get_packed_item_details(bundle_item.item_code, doc.company)
				update_packed_item_basic_data(item_row, pi_row, bundle_item, item_data)
				update_packed_item_stock_data(item_row, pi_row, bundle_item, item_data, doc)
				update_packed_item_price_data(pi_row, item_data, doc)
				update_packed_item_from_cancelled_doc(item_row, bundle_item, pi_row, doc)

				if set_price_from_children:  # create/update bundle item wise price dict
					update_product_bundle_rate(parent_items_price, pi_row, item_row)

	if parent_items_price:
		set_product_bundle_rate_amount(doc, parent_items_price)  # set price in bundle item


def get_product_bundle_items(item_code):
	product_bundle = frappe.qb.DocType("Product Bundle")
	product_bundle_item = frappe.qb.DocType("Product Bundle Sub Item")

	query = (
		frappe.qb.from_(product_bundle_item)
		.join(product_bundle)
		.on(product_bundle_item.parent == product_bundle.name)
		.select(
			product_bundle_item.item_code,
			product_bundle_item.qty,
			product_bundle_item.uom,
			product_bundle_item.description,
		)
		.where((product_bundle.new_item_code == item_code) & (product_bundle.disabled == 0))
		.orderby(product_bundle_item.idx)
	)
	return query.run(as_dict=True)


def validate_store_uom(self, method):
	for item in self.items:
		if not item.item_code:
			continue

		store_uom = frappe.db.get_value("Item", item.item_code, "store_uom")
		if not store_uom:
			frappe.throw(f"Please set Store UOM in Item <a href='/app/item/{item.item_code}'><b>{item.item_code}</b></a>")


def validate_uom(doc, method):
	for res in doc.items:
		if res.item_code and res.uom:
			# Check if the UOM conversion exists for the given item
			if not frappe.db.exists("UOM Conversion Detail", {"parent": res.item_code, "uom": res.uom}):
				frappe.throw(f"<b>Row#{res.idx}:</b> UOM <b>{res.uom}</b> conversion rate not found in Item <a href='/app/item/{res.item_code}'><b>{res.item_code}</b></a>.")
