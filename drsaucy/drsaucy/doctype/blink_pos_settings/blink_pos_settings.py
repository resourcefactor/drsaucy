# Copyright (c) 2024, RF and contributors
# For license information, please see license.txt


import frappe
from datetime import datetime
import requests
import json
import re
from time import sleep
from frappe.utils import (
    getdate,
    get_datetime,
    validate_email_address,
    validate_phone_number,
)
from frappe.utils.password import get_decrypted_password
from frappe.model.document import Document


class BlinkPOSSettings(Document):
    @frappe.whitelist()
    def check_connectivity(self):
        """Tries to connect with BlinkCo POS server to be synced"""
        self._validate_mandatory()
        password = get_decrypted_password(
            self.doctype, "Blink POS Settings", fieldname="password"
        )
        response = requests.post(f"{self.api_url}/login?email={self.email}&password={password}&type={self.type}")
        result = json.loads(response.content)
        formatted_logs = json.dumps(result, indent=4)
        return {
            "logs": formatted_logs,  # response.content.decode("utf-8"),
            "status": result.get("status"),
            "access_token": result.get("access_token")
            if result.get("access_token")
            else "",
        }

    def update_last_connectivity_check(self):
        self.db_set("last_execution", get_datetime())

    def get_end_point_url(self, end_point):
        # API URL Sanitization
        return f"{self.api_url}/{end_point}"

    def make_get_request(self, end_point, params, headers):
        self.update_last_connectivity_check()
        url = self.get_end_point_url(end_point)
        r = requests.get(url, params=params, headers=headers)
        return r.json()

    @frappe.whitelist()
    def sync_orders(self):
        frappe.msgprint("Sync Job Created")
        frappe.enqueue(sync_orders, self=self, timeout=30000000, is_async=True)
        # sync_orders(self)

    @frappe.whitelist()
    def create_invoices(self):
        frappe.enqueue(create_invoices, self=self, timeout=30000000, is_async=True)
        # create_invoices(self)

    @frappe.whitelist()
    def sync_customers(self):
        """Syncs Customers from BlinkCo to Customer in ERPNext"""
        self._validate_mandatory()
        if not self.last_customer_updated_at:
            updated_at = "2022-11-01T22:43:50.000000Z"
        else:
            updated_at = self.last_customer_updated_at
        params = {"page": 1, "updated_at": updated_at}
        headers = {"Authorization": f"Bearer {self.access_token}"}

        last_page = False
        total_customers = 0
        processed_customers = 0
        while not last_page:
            result = self.make_get_request("get-customer", params, headers)
            total_customers = result["customer"]["total"]

            if not total_customers:
                return

            frappe.publish_progress(
                percent=(processed_customers * 100) / total_customers,
                title="Syncing Customers",
                description=f"{processed_customers}/{total_customers} Customers",
            )

            for row in result["customer"]["data"]:
                original_format = "%Y-%m-%dT%H:%M:%S.%fZ"
                formatted_datetime = datetime.strptime(row["updated_at"], original_format)

                phone = ""
                if row.get("phone") and len(row.get("phone")) <= 12:
                    check = validate_phone_number(phone)
                    if not check:
                        phone = row["phone"] if re.match(r"^\d+$", row["phone"]) else None

                if not frappe.db.exists(
                    "Customer", {"custom_blinkco_customer_id": row["id"]}
                ):
                    customer = frappe.get_doc(
                        {
                            "doctype": "Customer",
                            "customer_name": row["full_name"],
                            "custom_blinkco_customer_id": row["id"],
                            "custom_last_updated": formatted_datetime,
                            "email_id": row["email"] if validate_email_address(row["email"]) else None,
                            "mobile_no": phone,
                        }
                    )
                    customer.save()
                    frappe.db.commit()
                    frappe.db.set_single_value("Blink POS Settings", "last_customer_updated_at", row["updated_at"])

                else:
                    customer = frappe.get_doc("Customer", {"custom_blinkco_customer_id": row["id"]})
                    if customer.custom_last_updated != formatted_datetime:
                        customer.customer_name = row["full_name"]
                        customer.custom_blinkco_customer_id = row["id"]
                        customer.custom_last_updated = formatted_datetime
                        customer.email_id = row["email"] if validate_email_address(row["email"]) else None
                        customer.mobile_no = phone
                        customer.save()
                        frappe.db.commit()
                        frappe.db.set_single_value("Blink POS Settings", "last_customer_updated_at", row["updated_at"])

                processed_customers += 1

                frappe.publish_progress(
                    percent=(processed_customers * 100) / total_customers,
                    title="Syncing Customers",
                    description=f"{processed_customers}/{total_customers} Customers",
                )

            if result["customer"]["current_page"] == result["customer"]["last_page"]:
                last_page = True
            else:
                params["page"] += 1

        return total_customers or "Zero"

    @frappe.whitelist()
    def sync_items(self):
        """Syncs Items from BlinkCo to Item in ERPNext"""
        self._validate_mandatory()
        if not self.last_item_updated_at:
            updated_at = "2022-11-01T22:43:50.000000Z"
        else:
            updated_at = self.last_item_updated_at
        params = {"page": 1, "updated_at": updated_at}
        headers = {"Authorization": f"Bearer {self.access_token}"}

        last_page = False
        total_items = 0
        while not last_page:
            result = self.make_get_request("item-listing", params, headers)
            total_items = result["items"]["total"]
            for row in result["items"]["data"]:
                if not frappe.db.exists(
                    "Item", {"custom_blinkco_item_id": row["id"]}
                ):
                    original_format = "%Y-%m-%dT%H:%M:%S.%fZ"
                    formatted_datetime = datetime.strptime(
                        row["updated_at"], original_format
                    )

                    item = frappe.get_doc(
                        {
                            "doctype": "Item",
                            "item_name": row["item_name"],
                            "custom_blinkco_item_id": row["id"],
                            "custom_last_updated": formatted_datetime,
                            "email_id": row["email"],
                            "mobile_no": row["phone"]
                            if re.match(r"^\d+$", row["phone"])
                            else None,
                        }
                    )
                    item.save()
                    frappe.db.commit()
                else:
                    item = frappe.db.get_doc(
                        "Item", {"custom_blinkco_item_id": row["id"]}
                    )
                    if item.custom_last_updated != formatted_datetime:
                        item.item_name = row["item_name"]
                        item.custom_blinkco_item_id = row["id"]
                        item.custom_last_updated = formatted_datetime
                        item.email_id = row["email"]
                        item.mobile_no = row["phone"]
                        item.save()
                        frappe.db.commit()

            if result["item"]["current_page"] == result["item"]["last_page"]:
                last_page = True
            else:
                params["page"] += 1

        return total_items or "Zero"


def sync_orders(self):
    frappe.publish_realtime(
        "eval_js",
        'frappe.show_alert({message: "Syncing Customer", indicator: "orange"})',
    )
    total_customers = self.sync_customers()
    frappe.publish_realtime(
        "eval_js",
        f'frappe.show_alert({{message: "{total_customers} customers synced", indicator: "green"}})',
    )

    # sleep(2)
    # frappe.publish_realtime(
    #     "eval_js",
    #     'frappe.show_alert({message: "Syncing Items", indicator: "orange"})',
    # )
    # total_items = self.sync_items()
    # frappe.publish_realtime(
    #     "eval_js",
    #     f'frappe.show_alert({{message: "{total_items} products synced", indicator: "green"}})',
    # )

    sleep(2)
    # Syncing Orders
    frappe.publish_realtime(
        "eval_js", 'frappe.show_alert({message: "Syncing Orders", indicator: "orange"})'
    )
    if not self.last_order_updated_at:
        updated_at = "2022-11-01T22:43:50.000000Z"
    else:
        updated_at = self.last_order_updated_at

    params = {"page": 1, "updated_at": updated_at}
    headers = {"Authorization": f"Bearer {self.access_token}"}

    last_page = False
    processed_invoices = 0
    total_invoices = 0
    while not last_page:
        result = self.make_get_request("order-listing", params, headers)
        total_invoices = result["data"]["total"]

        if not total_invoices:
            break
        frappe.publish_progress(
            percent=(processed_invoices * 100) / total_invoices,
            title="Syncing Invoices",
            description=f"{processed_invoices}/{total_invoices} Invoices",
        )

        for blinkco_order in result["data"]["data"]:
            if float(blinkco_order["grand_total"]) > 0 and not frappe.db.exists("BlinkCo Orders", {"name": blinkco_order["id"]}):
                order_detail = self.make_get_request("order-detail", {"id": blinkco_order["id"]}, headers)
                doc = order_detail["data"]
                new_order = frappe.new_doc("BlinkCo Orders")
                new_order.customer_id = doc["customer_id"]
                new_order.order_id = doc["id"]
                new_order.branch_id = doc["branch_id"]
                new_order.payment_type = doc["payment_type"] if doc.get("payment_type") else None

                for ch in doc.get("charge"):
                    new_order.delivery_charges = float(ch.get("amount"))

                new_order.tax = float(doc["tax"])
                new_order.discount = float(doc["discount"])
                new_order.total = float(doc["sub_total"])
                new_order.grand_total = float(doc["grand_total"])
                new_order.created_at = get_datetime(doc["created_at"].replace("Z", ""))
                new_order.updated_at = doc["updated_at"]

                for inv in doc["invoice"]:
                    d = inv["item"]
                    qty = float(d["qty"]) if d.get("qty") else float(inv["qty"]) if inv.get("qty") else 1

                    new_order.append("items", {
                        "item_id": d["id"],
                        "category_id": d["category_id"],
                        "price": float(d["price"]) if d.get("price") else inv.get("actual_total") / qty if inv.get("actual_total") else 0,
                        "qty": qty,
                        "amount": float(inv["total"]) if inv.get("total") else 0,
                        "discount": float(d["discount"]) if d.get("discount") else 0,
                    })

                new_order.save()
                frappe.db.commit()

                frappe.db.set_single_value("Blink POS Settings", "last_order_updated_at", doc["updated_at"])

                processed_invoices += 1

                frappe.publish_progress(
                    percent=(processed_invoices * 100) / total_invoices,
                    title="Syncing Invoices",
                    description=f"{processed_invoices}/{total_invoices} Invoices",
                )

        if result["data"]["current_page"] == result["data"]["last_page"]:
            last_page = True
        else:
            params["page"] += 1

    frappe.publish_realtime(
        "eval_js",
        f'frappe.show_alert({{message: "{processed_invoices}/{total_invoices} orders synced",indicator: "green"}})',
    )


def create_invoices(self):
    self._validate_mandatory()

    branch_list = frappe.db.sql(
        """
        select
            branch_id
        from `tabBlinkCo Orders` bo
        where bo.created_at >= '{0}' and bo.created_at <= '{1}'
        and bo.status = "Non-Billed"
        group by branch_id
    """.format(self.from_date, self.to_date),
        as_dict=True,
    )

    for branch in branch_list:
        order_list = frappe.db.sql(
            """
            select
                boi.item_id, bo.payment_type, boi.price,
                sum(bo.delivery_charges) as delivery_charges,
                sum(boi.qty) as qty, sum(boi.amount) as amount
            from `tabBlinkCo Orders` bo
            left join `tabBlinkCo Orders Item` as boi on boi.parent = bo.name
            where bo.created_at >= '{0}' and bo.created_at <= '{1}'
            and bo.branch_id = '{2}' and bo.status = "Non-Billed"
            group by boi.item_id
        """.format(self.from_date, self.to_date, branch.branch_id),
            as_dict=True,
        )
        for order in order_list:
            item = frappe.get_doc("Item", {"custom_blinkco_item_id": order.item_id})
            new_si = frappe.new_doc("Sales Invoice")
            new_si.customer = self.customer
            new_si.is_pos = 1
            new_si.cost_center = frappe.db.get_value("Cost Center", {"blinkco_branch_id": branch.branch_id}, "name")

            new_si.append("items", {
                "item_code": item.name,
                "qty": order.qty,
                "rate": order.price,
                "amount": order.amount,
            })

            if not new_si.taxes:
                new_si.append(
                    "taxes",
                    {
                        "charge_type": "Actual",
                        "account_head": self.delivery_charges_account,
                        "description": "Delivery Charges",
                        "tax_amount": order.delivery_charges,
                    },
                )

        payment_type_list = frappe.db.sql(
            """
            select
                bo.payment_type, sum(boi.amount) as amount
            from `tabBlinkCo Orders` bo
            left join `tabBlinkCo Orders Item` as boi on boi.parent = bo.name
            where bo.created_at >= '{0}' and bo.created_at <= '{1}'
            and bo.branch_id = '{2}' and bo.status = "Non-Billed"
            group by bo.payment_type
        """.format(self.from_date, self.to_date, branch.branch_id),
            as_dict=True,
        )

        for payment_type in payment_type_list:
            new_si.append(
                "payments",
                {
                    "mode_of_payment": "Credit Card" if payment_type.payment_type == "card" else "Cash",
                    "amount": payment_type.amount,
                },
            )

        new_si.set_missing_values()
        new_si.calculate_taxes_and_totals()
        new_si.save(ignore_permissions=True)

        order_id_list = frappe.db.sql(
            """
            select
                bo.name
            from `tabBlinkCo Orders` bo
            left join `tabBlinkCo Orders Item` as boi on boi.parent = bo.name
            where bo.created_at >= '{0}' and bo.created_at <= '{1}'
            and bo.branch_id = '{2}' and bo.status = "Non-Billed"
        """.format(self.from_date, self.to_date, branch.branch_id),
            as_dict=True,
        )

        for d in order_id_list:
            order = frappe.get_doc("BlinkCo Orders", d.name)
            order.status = "Billed"
            order.db_update()

        frappe.db.commit()
