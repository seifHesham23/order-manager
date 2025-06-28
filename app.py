import streamlit as st
import pandas as pd
from datetime import date
from order import Item, Order
from db import get_all_orders, save_order

st.set_page_config(page_title="Order Manager", layout="centered")
st.title("📦 Order Management App")

# Initialize item storage
if "items" not in st.session_state:
    st.session_state["items"] = []

# 📝 Create New Order Section
with st.expander("📝 Create New Order", expanded=False):
    st.subheader("➕ Add Item to Order")
    with st.form("item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name")
        cost_price = st.number_input("Cost Price", min_value=0.0)
        sell_price = st.number_input("Sell Price", min_value=0.0)
        quantity = st.number_input("Quantity", min_value=1, step=1)
        representative = st.text_input("Representative")
        item_submit = st.form_submit_button("Add Item")

    if item_submit:
        item = Item(item_name, cost_price, sell_price, quantity, representative)
        st.session_state["items"].append(item)
        st.success(f"✅ Added {item_name} by {representative} ({quantity})")

    if st.session_state["items"]:
        st.subheader("🧾 Current Items")
        item_data = [{
            "Name": item.name,
            "Cost": item.cost_price,
            "Sell": item.sell_price,
            "Qty": item.quantity,
            "Rep": item.representative,
            "Total Cost": item.total_cost(),
            "Total Price": item.total_price(),
            "Profit": item.profit()
        } for item in st.session_state["items"]]
        st.dataframe(pd.DataFrame(item_data))

    st.subheader("📄 Finalize Order")
    client = st.text_input("Client Name")
    amount_paid = st.number_input("Amount Paid", min_value=0.0)
    submission_date = st.date_input("Expected Delivery Date", value=date.today())
    status = st.selectbox("Order Status", ["in_progress", "completed", "delivered", "paid"])
    notes = st.text_area("Notes (optional)", placeholder="Write any special instructions or remarks here...")
    submit_order = st.button("Create Order")

    if submit_order:
        if not client:
            st.warning("⚠️ Please enter the client's name.")
        elif not st.session_state["items"]:
            st.warning("⚠️ Add at least one item to the order.")
        else:
            order = Order(
                client=client,
                items=st.session_state["items"],
                amount_paid=amount_paid,
                submission_date=submission_date.strftime("%Y-%m-%d"),
                status=status,
                notes=notes
            )
            save_order(order)
            st.success("📤 Order saved to Google Sheets.")
            st.session_state["items"] = []

# 📦 Filter & View Orders
st.header("📦 Filter Orders")
orders_df = get_all_orders()
orders_df["Issue Date"] = pd.to_datetime(orders_df["Issue Date"])

clients = sorted(orders_df["Client"].unique().tolist())
selected_client = st.selectbox("👤 Filter by Client", ["All"] + clients)

min_date = orders_df["Issue Date"].min().date()
max_date = orders_df["Issue Date"].max().date()
start_date, end_date = st.date_input("📅 Filter by Issue Date Range", [min_date, max_date])

filtered_df = orders_df.copy()
if selected_client != "All":
    filtered_df = filtered_df[filtered_df["Client"] == selected_client]
filtered_df = filtered_df[
    (filtered_df["Issue Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Issue Date"] <= pd.to_datetime(end_date))
]

if st.button("🔄 Show Orders"):
    try:
        grouped = filtered_df.groupby("Order ID")
        for order_id, group in grouped:
            order_info = group.iloc[0].to_dict()
            with st.expander(f"🧾 Order {order_info['Order ID']} | {order_info['Client']} | {order_info['Status']}"):
                st.markdown(f"**Client:** {order_info['Client']}")
                st.markdown(f"**Amount Paid:** {order_info['Amount Paid']}")
                st.markdown(f"**Status:** `{order_info['Status']}`")
                st.markdown(f"**Issue Date:** {order_info['Issue Date']}")
                st.markdown(f"**Submission Date:** {order_info['Submission Date']}")
                st.markdown(f"**Remaining Balance:** {order_info['Remaining Balance']}")
                st.markdown(f"**Notes:** {order_info.get('Notes', '')}")

                st.markdown("**Items:**")
                item_df = group[["Item Name", "Cost Price", "Sell Price", "Quantity", "Representative"]]
                item_df.columns = ["Name", "Cost", "Sell", "Qty", "Rep"]
                st.table(item_df.reset_index(drop=True))

    except Exception as e:
        st.error(f"❌ Error loading orders: {e}")
