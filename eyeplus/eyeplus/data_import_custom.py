import frappe
import pandas as pd 
import os
import openpyxl
import json 

@frappe.whitelist()
def sales_invoice_import(url,company):
    domain = os.getcwd() + frappe.get_site_path()[1:]
    if url.split(".")[-1].upper() == "CSV":
        data = pd.read_csv(domain+url,encoding='utf-8')
    elif url.split(".")[-1].upper() == "XLSX" or url.split(".")[-1].upper() == "XLS":
        data = pd.read_excel(domain+url)
    income_account = frappe.db.get_value("Company",{"name":company},"default_income_account")
    cost_center = frappe.db.get_value("Company",{"name":company},"cost_center")
    flag = False
    i=0
    for index,row in data.iterrows():
        date = row['Date']
        customer_item = row['Particulars']
        type = row['Voucher Type']
        invoice_id = row['Vch No.']
        qty = row['Quantity']
        rate = row['Rate']
        total_amount = row['Gross Total']
        tax = row ['GST CHARGES']
        tax_rate = tax if not pd.isna(tax) else 0
        qty_modified = qty if not pd.isna(qty) else 1
        len_data = len(data[data['Date'].notna()])  
        try:
            if not pd.isna(date):
                if flag == True:
                        doc.flags.ignore_mandatory = True
                        doc.save()
                        doc.submit()
                        # print("- -  - -- - - ",doc.name,"- - - - - -",doc.customer)
                doc = frappe.new_doc("Sales Invoice")
                doc.flags.ignore_mandatory = True
                doc.customer = customer_item
                doc.due_date = frappe.utils.nowdate()
                doc.company = company
                doc.total_qty = qty_modified
                doc.total  = total_amount
                doc.total_taxes_and_charges = tax_rate
                doc.place_of_supply = "33-Tamil Nadu"
                flag = False
                # i=i+1
                # j=0
                # print("- - - - - created -  - - - - -  - - ",i)
            else:
                    doc.flags.ignore_mandatory = True
                    doc.append("items",{
                            "item_name":customer_item,
                            "qty":qty_modified,
                            "rate":rate,
                            "income_account":income_account,
                            "cost_center":cost_center
                        })
                    flag = True
                    # j=j+1
                    # print("- - - item created  - - ",j)
            frappe.publish_realtime("progress", dict(progress=[i, len_data], title='Creating Sales Invoice'), user=frappe.session.user)		
        except Exception as e:
             print(f"{i} has {e}")

    try:
        if  pd.isna(date) and flag==True:
            doc.flags.ignore_mandatory = True
            doc.save()
            doc.submit()
            print("- -  - -- - - ", doc.name, "- - - - - -", doc.customer)
    except Exception as e:
         print({e})
        

    