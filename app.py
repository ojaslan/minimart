import streamlit as st
import os
from dotenv import load_dotenv
from payman_sdk.client import PaymanClient
from payman_sdk.types import PaymanConfig

# --- Load Environment Variables ---
load_dotenv()

# --- Payman Setup ---
config: PaymanConfig = {
    'client_id': os.getenv("PAYMAN_CLIENT_ID"),
    'client_secret': os.getenv("PAYMAN_CLIENT_SECRET")
}
client = PaymanClient.with_credentials(config)

# --- Sample Products ---
products = [
    {"id": 1, "name": "creatine", "price": 49},
    {"id": 2, "name": "whey", "price": 99},
    {"id": 3, "name": "museli", "price": 89},
    {"id": 4, "name": "oats", "price": 93},
    {"id": 5, "name": "almond butter", "price": 120},
    {"id": 6, "name": "peanut butter", "price": 85},
    {"id": 7, "name": "protein bar", "price": 45},
    {"id": 8, "name": "multivitamin", "price": 75},
    {"id": 9, "name": "electrolyte powder", "price": 65},
    {"id": 10, "name": "chia seeds", "price": 55}
]


# --- Session Cart Setup ---
if "cart" not in st.session_state:
    st.session_state.cart = []

# --- UI Starts ---
st.set_page_config(page_title="Bill Buddy", page_icon="🛒")
st.title("🛍️ minimart - Smart E-Commerce with Payman AI")

# --- Product Listing ---
st.header("📦 Products")
for product in products:
    st.write(f"**{product['name']}** - ₹{product['price']}")
    if st.button(f"🛒 Add to Cart - {product['id']}", key=f"add_{product['id']}"):
        st.session_state.cart.append(product)
        st.success(f"{product['name']} added to cart!")

# --- Cart Display ---
st.subheader("🧾 Your Cart")

if st.session_state.cart:
    total = sum(p["price"] for p in st.session_state.cart)
    item_names = ", ".join(p["name"] for p in st.session_state.cart)

    for i, item in enumerate(st.session_state.cart):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"- {item['name']} - ₹{item['price']}")
        with col2:
            if st.button("❌ Remove", key=f"remove_{i}"):
                st.session_state.cart.pop(i)
                st.experimental_rerun()

    st.markdown(f"**Total: ₹{total}**")

    # --- Smart Checkout via Payman AI ---
    st.subheader("💳 Payman AI Checkout")
    payee = "ojas"
    wallet = "brainshopwallet"

    default_prompt = f"Send {total} TSD to {payee} from {wallet} for items: {item_names}"
    user_prompt = st.text_area("AI Prompt for Payment", value=default_prompt)

    response = client.ask(user_prompt)

    # Show raw response
    st.subheader("📨 Response from Payman AI")
    st.json(response)

    # Extract & create task if intent is valid
    if "intent" in response:
        task_data = response.get("task", {})

        # Required: Ensure payee is added properly
        if "payee" not in task_data:
            task_data["payee"] = {"name": payee}

        try:
            task_response = client.submit_task(task_data)
            st.success("✅ Task successfully created in Payman AI!")
            st.json(task_response)
        except Exception as e:
            st.error("❌ Failed to create task on Payman AI")
            st.exception(e)

    elif "summary" in response:
        st.success("✅ " + response["summary"])
    else:
        st.warning("⚠️ No valid intent found. AI may not have understood your prompt.")

    if st.button("🧠 Ask Payman AI to Pay"):
        with st.spinner("Processing via Payman AI..."):
            try:
                response = client.ask(user_prompt)

                st.subheader("📨 Response from Payman AI")
                st.json(response)

                if "summary" in response:
                    st.success("✅ " + response["summary"])
                elif "task" in response and "summary" in response["task"]:
                    st.success("🧾 " + response["task"]["summary"])
                else:
                    st.info("ℹ️ No summary provided.")

            except Exception as e:
                st.error("❌ Payment Failed")
                st.exception(e)
else:
    st.warning("🛒 Your cart is empty. Please add items to checkout.")





