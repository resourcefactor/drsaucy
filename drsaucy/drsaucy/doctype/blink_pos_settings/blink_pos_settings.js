// Copyright (c) 2024, RF and contributors
// For license information, please see license.txt

frappe.ui.form.on("Blink POS Settings", {
	onload(frm) {
		frm.toggle_display("sync_orders", false);
	},
	refresh() {
		document.querySelectorAll("[data-fieldname='create_invoices']")[1].style.backgroundColor = "green";
		document.querySelectorAll("[data-fieldname='create_invoices']")[1].style.color = "white";
		document.querySelectorAll("[data-fieldname='check_connectivity']")[1].style.backgroundColor = "red";
		document.querySelectorAll("[data-fieldname='check_connectivity']")[1].style.color = "white";
		document.querySelectorAll("[data-fieldname='sync_orders']")[1].style.backgroundColor = "black";
		document.querySelectorAll("[data-fieldname='sync_orders']")[1].style.color = "white";
	},
	check_connectivity(frm) {
		frm.toggle_display("check_connectivity", false); // hide Sync Orders Button
		frappe.show_alert({ message: "Connecting to the BlinkCo POS", indicator: "orange" });
		frappe.call({
			doc: frm.doc,
			method: "check_connectivity",
			callback: function (r) {
				frm.set_value("logs", r.message.logs);
				frm.set_value("last_execution_status", r.message.status);
				frm.set_value("last_execution", frappe.datetime.now_datetime());
				frm.set_value("access_token", r.message.access_token);
				frm.save();
				if (r.message.status == "success") {
					frappe.show_alert({ message: "POS Connected", indicator: "green" });
					frm.toggle_display("sync_orders", true);
				} else {
					frappe.show_alert({ message: "Error while Connecting POS", indicator: "red" });
					frm.toggle_display("check_connectivity", true); // display Sync Orders Button
				}
			},
		});
	},
	sync_orders(frm) {
		frappe.call({
			doc: frm.doc,
			method: "sync_orders",
			// callback: function (r) {
			// 	frm.set_value("logs", r.message.logs);
			// 	frm.set_value("last_execution_status", r.message.status);
			// 	frm.set_value("last_execution", frappe.datetime.now_datetime());
			// 	frm.set_value("access_token", r.message.access_token);
			// 	frm.save();
			// 	if (r.message.status == "success") {
			// 		frappe.show_alert({ message: "POS Connected", indicator: "green" });
			// 		frm.toggle_display("sync_orders", true);
			// 	} else {
			// 		frappe.show_alert({ message: "Error while Connecting POS", indicator: "red" });
			// 		frm.toggle_display("check_connectivity", true); // display Sync Orders Button
			// 	}
			// },
		});
	},
	create_invoices(frm) {
		frappe.call({
			doc: frm.doc,
			method: "create_invoices",
		});
	}
});
