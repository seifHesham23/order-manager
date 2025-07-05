import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os
import streamlit as st
# === Google Sheets Setup ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
service_account_info = {
    "type": st.secrets["gcp_service_account"]["type"],
    "project_id": st.secrets["gcp_service_account"]["project_id"],
    "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
    "private_key": st.secrets["gcp_service_account"]["private_key"],
    "client_email": st.secrets["gcp_service_account"]["client_email"],
    "client_id": st.secrets["gcp_service_account"]["client_id"],
    "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
    "token_uri": st.secrets["gcp_service_account"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
    "universe_domain": st.secrets["gcp_service_account"]["universe_domain"]
}
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# Open your Google Sheet
sheet = client.open("order_data").worksheet("Orders")

# === Define Headers ===
HEADERS = [
    "Order ID", "Client", "Item Name", "Cost Price", "Sell Price", "Quantity", "Representative",
    "Amount Paid", "Total Order Price", "Total Order Cost", "Order Profit", "Remaining Balance",
    "Issue Date", "Submission Date", "Status", "Notes"
]

# === Ensure Headers Exist ===
def ensure_headers():
    current = sheet.row_values(1)
    if current != HEADERS:
        sheet.clear()
        sheet.append_row(HEADERS)

# === Save Order to Sheet ===
def save_order(order):
    ensure_headers()

    for item in order.items:
        row = [
            order.order_id,
            order.client,
            item.name,
            item.cost_price,
            item.sell_price,
            item.quantity,
            item.representative,
            order.amount_paid,
            order.total_price(),
            order.total_cost(),
            order.profit(),
            order.remaining_balance(),
            order.issue_date,
            order.submission_date,
            order.status,
            order.notes
        ]
        sheet.append_row(row)

def get_all_orders():
    ensure_headers()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def get_orders_grouped():
    df = get_all_orders()
    grouped = df.groupby("Order ID")
    orders = []

    for order_id, group in grouped:
        order_info = group.iloc[0].to_dict()
        items = group[["Item Name", "Cost Price", "Sell Price", "Quantity", "Representative"]].to_dict(orient="records")
        order_info["Items"] = items
        orders.append(order_info)

    return orders

def update_order(order):
    ensure_headers()
    records = sheet.get_all_values()

    # Find all row indices (1-based) with this Order ID
    matching_indices = []
    for i in range(1, len(records)):
        row = records[i]
        if row and row[0] == order.order_id:
            matching_indices.append(i + 1)  # gspread uses 1-based indexing

    items = order.items
    num_existing = len(matching_indices)
    num_new = len(items)

    # 1. Update existing rows
    for i in range(min(num_existing, num_new)):
        item = items[i]
        new_row = [
            order.order_id,
            order.client,
            item.name,
            item.cost_price,
            item.sell_price,
            item.quantity,
            item.representative,
            order.amount_paid,
            order.total_price(),
            order.total_cost(),
            order.profit(),
            order.remaining_balance(),
            order.issue_date,
            order.submission_date,
            order.status,
            order.notes
        ]
        sheet.update(f"A{matching_indices[i]}:P{matching_indices[i]}", [new_row])

    # 2. Append new items if the order has more items than existing rows
    for i in range(num_existing, num_new):
        item = items[i]
        new_row = [
            order.order_id,
            order.client,
            item.name,
            item.cost_price,
            item.sell_price,
            item.quantity,
            item.representative,
            order.amount_paid,
            order.total_price(),
            order.total_cost(),
            order.profit(),
            order.remaining_balance(),
            order.issue_date,
            order.submission_date,
            order.status,
            order.notes
        ]
        sheet.append_row(new_row)

    # 3. Delete extra rows if the order has fewer items than before
    if num_existing > num_new:
        rows_to_delete = matching_indices[num_new:]
        for row_num in reversed(rows_to_delete):  # Delete bottom-up
            sheet.delete_rows(row_num)

def delete_order_by_id(order_id):
    ensure_headers()
    records = sheet.get_all_values()
    rows_to_delete = []

    for i in range(1, len(records)):
        row = records[i]
        if row and row[0] == order_id:
            rows_to_delete.append(i + 1)  # 1-based indexing

    for row_index in reversed(rows_to_delete):  # Delete from bottom up
        sheet.delete_rows(row_index)
