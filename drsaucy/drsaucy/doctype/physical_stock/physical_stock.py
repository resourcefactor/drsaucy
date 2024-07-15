# -*- coding: utf-8 -*-
# Copyright (c) 2021, Resource Factors DMCC and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.model.document import Document
from datetime import datetime
import datetime
from frappe.utils import today


class PhysicalStock(Document):
    def validate(self):
        self.add_totals()

    def on_submit(self):
        self.validate_doc()
        self.create_stock_entry()

    def add_totals(self):
        self.total_amount = 0
        self.total_consumption_amount = 0
        self.total_stock_difference = 0
        for d in self.items:
            self.total_amount += float(d.valuation_rate) * float(d.available_stock)
            if not d.consumption_amount:
                d.consumption_amount = 0
            self.total_consumption_amount += float(d.consumption_amount)
        self.total_stock_difference = self.total_amount - self.total_consumption_amount

    def validate_doc(self):
        for d in self.items:
            if not d.expense_account:
                frappe.throw(
                    _(
                        "<a href='#Form/Item/{0}'><b>[Item {0}:{1}]</b></a> Has No Expense Account!"
                    ).format(_(d.get("item_code")), (d.get("item_name")))
                )

    def create_stock_entry(self):
        doc = frappe.get_doc("Physical Stock", self.name)

        ste = frappe.new_doc('Stock Entry')
        ste.company = doc.company
        ste.stock_entry_type = 'Material Issue'
        ste.set_posting_time = 1
        ste.posting_date = doc.posting_date
        ste.posting_time = '23:32:1'
        ste.from_warehouse = doc.warehouse
        ste.custom_physical_stock = doc.name

        for d in doc.items:
            if d.stock_difference > 0:
                ste.append('items', {
                    'item_code': d.item_code,
                    'qty': d.stock_difference,
                    'valuation_rate': d.valuation_rate,
                    'cost_center': d.cost_center
                })
        ste.save(ignore_permissions=True)
        frappe.msgprint(_("<a href='#Form/Stock%20Entry/{0}'><b>[Stock Entry: {0}]</b></a> Created!").format(_(ste.name)))


@frappe.whitelist()
def get_items(warehouse, company, item_group=None):
    if item_group:
        lft1, rgt1 = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"])
    lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
    query = """select i.name, i.item_name, i.item_group, bin.warehouse, bin.actual_qty,
        bin.valuation_rate,	id.default_warehouse as warehouse ,id.expense_account
        from tabItem i inner join tabBin bin on i.name=bin.item_code
        and bin.warehouse in (select name from `tabWarehouse` where lft >= '{0}' and rgt <= '{1}' )
        left join `tabItem Default` id on id.parent=i.name and id.company = '{2}'
        where i.is_stock_item = 1 and i.has_serial_no = 0 and i.has_batch_no = 0 and i.has_variants = 0 and i.disabled = 0 and bin.actual_qty>0
    """.format(lft, rgt, company)

    if item_group:
        query += " and i.item_group in (select name from `tabItem Group` where lft >= '{0}' and rgt <= '{1}')".format(
            lft1, rgt1
        )
    query += " order by i.item_group, i.item_name"
    items = frappe.db.sql(query, as_dict=True)
    res = []
    for d in items:
        itm_data = {
            "item_code": d.get("name"),
            "item_name": d.get("item_name"),
            "item_group": d.get("item_group"),
            "warehouse": d.get("warehouse"),
            "available_stock": d.get("actual_qty"),
            "valuation_rate": d.get("valuation_rate"),
            "stock_difference": d.get("actual_qty"),
            "expense_account": d.get("expense_account"),
        }
        res.append(itm_data)
    if not res:
        frappe.throw("No item found on selected filters")
    return res
