
import frappe

from burundi_compliance.burundi_compliance.overrides.stock_ledger_entry import send_data
from burundi_compliance.burundi_compliance.overrides.sales_invoice import submit_invoice_request
import time

def check_and_send_pending_stock_ledger_entry():
    '''
    Check and send unsend stock ledger entries
    '''
    stock_ledger_entries = frappe.get_all("Stock Ledger Entry", filters={"docstatus": 1, "custom_etracker": 0, "custom_queued":0}, fields=["name"], order_by='posting_time asc')
    
    for stock_ledger_entry in stock_ledger_entries:
        
        try:
            
            stock_ledger_entry_doc = frappe.get_doc("Stock Ledger Entry", stock_ledger_entry.name)
            if stock_ledger_entry_doc.voucher_type == "Stock Reconciliation" and stock_ledger_entry_doc.has_batch_no == 1 and stock_ledger_entry_doc.actual_qty < 0:
                continue
            check_item = frappe.get_doc("Item", stock_ledger_entry_doc.item_code)
            if check_item.custom_allow_obr_to_track_stock_movement == 0:
                continue
            # frappe.publish_realtime("msgpring",f'{stock_ledger_entry_doc}', user=frappe.session.user)
            send_data(stock_ledger_entry_doc)
            frappe.db.set_value("Stock Ledger Entry", stock_ledger_entry_doc.name, 'custom_queued', 1)
            time.sleep(2)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error in sending stock ledger entry {0}".format(stock_ledger_entry.name))
            continue
        
def check_and_send_pending_sales_invoices():
    '''
    Check and send pending sales invoices
    '''
    sales_invoices = frappe.get_all("Sales Invoice", filters={"docstatus": 1, "custom_submitted_to_obr": 0, "is_consolidated":0}, fields=["name"])
    
    for sales_invoice in sales_invoices:
        try:
            sales_invoice_doc = frappe.get_doc("Sales Invoice", sales_invoice.name)
            submit_invoice_request(sales_invoice_doc)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error in sending sales invoice {0}".format(sales_invoice.name))
            continue
        
