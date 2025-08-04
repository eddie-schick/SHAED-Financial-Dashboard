import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go
from database import load_data, save_data, load_data_from_source, save_data_to_source, show_supabase_access_info, save_all_to_supabase_enhanced, save_income_statement_to_database, clean_up_cash_disbursement_categories, save_revenue_calculations_to_database

# Configure page
st.set_page_config(
    page_title="Income Statement",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for SHAED branding and fixed category column
st.markdown("""
<style>
    /* Main background and colors */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header h2 {
        margin: 0.5rem 0 0 0;
        font-size: 1.5rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Section headers */
    .section-header {
        background-color: #00D084;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Dashboard Navigation header - centered */
    .nav-section-header {
        background-color: #00D084;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
        text-align: center;
    }
    
    /* Button styling */
    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #00D084;
    }
    
    /* Metrics styling */
    .metric-container {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #00D084;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
    }
    
    /* Custom table container with fixed first column */
    .fixed-table-container {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        background-color: white;
        border: 1px solid #e0e0e0;
        max-height: 1125px;
        overflow-x: auto;
        overflow-y: auto;
        position: relative;
    }
    
    /* Fixed category column */
    .fixed-category-column {
        position: sticky;
        left: 0;
        width: 200px;
        min-width: 200px;
        background-color: #f8f9fa;
        border-right: 3px solid #00D084;
        z-index: 20;
        box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
        float: left;
    }
    
    .category-header {
        background-color: #00D084;
        color: white;
        padding: 0 12px;
        font-weight: 700;
        font-size: 14px;
        text-align: left;
        border-bottom: 1px solid #ddd;
        height: 44px !important;
        line-height: 44px !important;
        margin: 0;
        box-sizing: border-box;
        position: sticky;
        top: 0;
        z-index: 30;
    }
    
    .category-cell {
        padding: 0 12px;
        font-weight: 600;
        font-size: 13px;
        border-bottom: 1px solid #e0e0e0;
        background-color: #f8f9fa;
        color: #333;
        height: 44px !important;
        line-height: 44px !important;
        margin: 0;
        box-sizing: border-box;
    }
    
    .category-total {
        padding: 0 12px;
        font-weight: 700;
        font-size: 13px;
        border-top: 2px solid #00D084;
        background-color: #e8f5e8;
        color: #00D084;
        height: 44px !important;
        line-height: 44px !important;
        margin: 0;
        box-sizing: border-box;
    }
    
    .section-header-cell {
        padding: 0 12px;
        font-weight: 700;
        font-size: 13px;
        border-top: 1px solid #ccc;
        border-bottom: 1px solid #ccc;
        background-color: #f0f0f0;
        color: #333;
        height: 44px !important;
        line-height: 44px !important;
        margin: 0;
        box-sizing: border-box;
    }
    
    .section-header-row {
        border-top: 1px solid #ccc;
    }
    
    /* Comprehensive income statement table */
    .comprehensive-table {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        background-color: white;
        border: 1px solid #e0e0e0;
        max-height: 844px;
        overflow: auto;
    }
    
    .comprehensive-table table {
        border-collapse: collapse;
        width: 100%;
        table-layout: fixed;
    }
    
    .comprehensive-table th:first-child,
    .comprehensive-table td:first-child {
        position: sticky;
        left: 0;
        background-color: #f8f9fa;
        border-right: 3px solid #00D084;
        z-index: 20;
        box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
        width: 200px;
        min-width: 200px;
        padding: 0 12px;
        font-weight: 600;
        font-size: 13px;
        height: 44px !important;
        line-height: 44px !important;
        text-align: left;
        box-sizing: border-box;
    }
    
    .comprehensive-table th:first-child {
        background-color: #00D084;
        color: white;
        z-index: 30;
        font-weight: 700;
        font-size: 14px;
        position: sticky;
        top: 0;
    }
    
    .comprehensive-table th {
        background-color: #f0f0f0;
        padding: 0 4px;
        font-weight: 600;
        font-size: 13px;
        text-align: center;
        border-bottom: 1px solid #ddd;
        border-right: 1px solid #e0e0e0;
        width: 80px;
        box-sizing: border-box;
        height: 44px !important;
        line-height: 44px !important;
        position: sticky;
        top: 0;
        z-index: 15;
    }
    
    .comprehensive-table th.year-total {
        background-color: #f0f9f6;
        border-right: 2px solid #00D084;
        font-weight: 700;
        width: 100px;
    }
    
    .comprehensive-table td {
        padding: 0 4px;
        font-size: 13px;
        text-align: right;
        border-bottom: 1px solid #e0e0e0;
        border-right: 1px solid #e0e0e0;
        width: 80px;
        height: 44px !important;
        line-height: 44px !important;
        box-sizing: border-box;
    }
    
    .comprehensive-table td.year-total {
        background-color: #f0f9f6;
        font-weight: 700;
        border-right: 2px solid #00D084;
        width: 100px;
    }
    
    .comprehensive-table .section-header td:first-child {
        background-color: #f0f0f0;
        color: #333;
        border-top: 1px solid #ccc;
        border-bottom: 1px solid #ccc;
        font-weight: 700;
    }
    
    .comprehensive-table .section-header td {
        background-color: #f0f0f0;
        border-top: 1px solid #ccc;
        border-bottom: 1px solid #ccc;
    }
    
    .comprehensive-table .total-row td:first-child {
        background-color: #e8f5e8;
        color: #00D084;
        border-top: 2px solid #00D084;
        font-weight: 700;
    }
    
    .comprehensive-table .total-row td {
        border-top: 2px solid #00D084;
        background-color: #f0f9f6;
        font-weight: 700;
        color: #00D084;
    }
    
    /* Scrollable data area */
    .scrollable-data {
        margin-left: 203px;
        background-color: white;
    }
    
    /* Data table styling */
    .data-table {
        border-collapse: collapse;
        table-layout: fixed;
        width: fit-content;
        min-width: 100%;
        margin: 0;
        padding: 0;
    }
    
    .data-table thead,
    .data-table tbody,
    .data-table tr {
        margin: 0;
        padding: 0;
    }
    
    .data-table thead tr,
    .data-table tbody tr {
        height: 43px !important;
        line-height: 43px !important;
    }
    
    .data-table th,
    .data-table td {
        height: 43px !important;
        line-height: 43px !important;
        padding: 0 4px !important;
        margin: 0 !important;
        vertical-align: middle !important;
        box-sizing: border-box !important;
    }
    
    .data-header {
        background-color: #f0f0f0;
        padding: 0 4px;
        font-weight: 600;
        font-size: 13px;
        text-align: center !important;
        border-bottom: 1px solid #ddd;
        border-right: 1px solid #e0e0e0;
        width: 80px;
        box-sizing: border-box;
        height: 43px !important;
        line-height: 43px !important;
        margin: 0;
        vertical-align: middle;
        position: sticky;
        top: 0;
        z-index: 15;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .data-header.year-total {
        background-color: #f0f9f6;
        border-right: 2px solid #00D084;
        font-weight: 700;
        width: 100px;
        box-sizing: border-box;
        height: 43px !important;
        line-height: 43px !important;
        margin: 0;
        vertical-align: middle;
        text-align: center !important;
        position: sticky;
        top: 0;
        z-index: 15;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .data-cell {
        padding: 0 4px;
        font-size: 13px;
        text-align: right;
        border-bottom: 1px solid #e0e0e0;
        border-right: 1px solid #e0e0e0;
        background-color: white;
        width: 80px;
        box-sizing: border-box;
        height: 43px !important;
        line-height: 43px !important;
        margin: 0;
        vertical-align: middle;
    }
    
    .data-cell.year-total {
        background-color: #f0f9f6;
        font-weight: 700;
        border-right: 2px solid #00D084;
        width: 100px;
        box-sizing: border-box;
        height: 43px !important;
        line-height: 43px !important;
        margin: 0;
        vertical-align: middle;
    }
    
    .data-cell:nth-child(even):not(.year-total) {
        background-color: #fafafa;
    }
    
    /* Remove alternating background for proper alignment */
    .data-table tr:nth-child(even) .data-cell:not(.year-total) {
        background-color: #fafafa;
    }
    
    .data-table tr:nth-child(odd) .data-cell:not(.year-total) {
        background-color: white;
    }
    
    /* Total row styling */
    .total-row .data-cell {
        border-top: 2px solid #00D084;
        background-color: #f0f9f6;
        font-weight: 700;
        color: #00D084;
        height: 43px !important;
        line-height: 43px !important;
    }
    
    /* Force consistent row heights across all table elements */
    .fixed-table-container * {
        box-sizing: border-box !important;
    }
    
    .fixed-table-container .data-table tr {
        height: 43px !important;
    }
    
    .fixed-table-container .data-table th,
    .fixed-table-container .data-table td {
        height: 43px !important;
        line-height: 43px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Data persistence functions are now imported from database.py

if 'model_data' not in st.session_state:
    st.session_state.model_data = load_data_from_source()

# Generate months from 2025-2030
def get_months_2025_2030():
    months = []
    for year in range(2025, 2031):
        for month in range(1, 13):
            months.append(f"{date(year, month, 1).strftime('%b %Y')}")
    return months

months = get_months_2025_2030()

# Helper function to format numbers with commas
def format_number(num):
    """Format number with commas"""
    if num == 0:
        return "0"
    return f"{num:,.0f}"

# Helper function to format percentages
def format_percentage(num):
    """Format number as percentage"""
    if num == 0:
        return "0.0%"
    return f"{num:.1f}%"

# Helper function to format numbers with conditional red color for negatives
def format_number_with_color(num, apply_red_for_negative=False):
    """Format number with commas and optional red color for negatives"""
    if num == 0:
        return "0"
    
    formatted = f"{num:,.0f}"
    
    if apply_red_for_negative and num < 0:
        return f'<span style="color: #ff4444;">{formatted}</span>'
    
    return formatted

# Helper function to get year from month string
def get_year_from_month(month_str):
    """Extract year from month string like 'Jan 2025'"""
    return month_str.split(' ')[1]

# Helper function to group months by year
def group_months_by_year(months):
    """Group months by year and return dict"""
    years = {}
    for month in months:
        year = get_year_from_month(month)
        if year not in years:
            years[year] = []
        years[year].append(month)
    return years

# Auto-load COGS from Gross Profit model
def get_active_subscribers(month):
    """Get total active subscribers for a given month from revenue assumptions"""
    if "subscription_running_totals" not in st.session_state.model_data:
        return 0
    
    total_subscribers = 0
    for stakeholder, monthly_data in st.session_state.model_data["subscription_running_totals"].items():
        total_subscribers += monthly_data.get(month, 0)
    
    return total_subscribers

def calculate_hosting_costs_from_gross_profit_model():
    """Calculate hosting costs based on gross profit model monthly structure"""
    if "gross_profit_data" not in st.session_state.model_data:
        return {}, {}
    
    gp_data = st.session_state.model_data["gross_profit_data"]
    
    # Get hosting structure
    hosting_structure = gp_data.get("saas_hosting_structure", {
        "fixed_monthly_cost": 15400.0,  # Legacy fallback
        "cost_per_customer": 5.0,       # Legacy fallback
        "go_live_month": "Jan 2025",
        "capitalize_before_go_live": True
    })
    
    # Get monthly data (new structure)
    monthly_fixed_costs = hosting_structure.get("monthly_fixed_costs", {})
    monthly_variable_costs = hosting_structure.get("monthly_variable_costs", {})
    go_live_month = hosting_structure.get("go_live_month", "Jan 2025")
    capitalize_before_go_live = hosting_structure.get("capitalize_before_go_live", True)
    
    # Fallback to legacy structure if monthly data not available
    legacy_fixed = hosting_structure.get("fixed_monthly_cost", 15400.0)
    legacy_variable = hosting_structure.get("cost_per_customer", 5.0)
    
    hosting_costs = {}
    capitalized_hosting = {}
    
    # Find go-live month index
    try:
        go_live_index = months.index(go_live_month)
    except ValueError:
        go_live_index = 0  # Default to first month if invalid
    
    for i, month in enumerate(months):
        active_subscribers = get_active_subscribers(month)
        
        # Use monthly data if available, otherwise use legacy values
        fixed_cost = monthly_fixed_costs.get(month, legacy_fixed)
        variable_cost = monthly_variable_costs.get(month, legacy_variable)
        
        calculated_cost = fixed_cost + (variable_cost * active_subscribers)
        
        # Determine if costs should be capitalized or expensed
        if capitalize_before_go_live and i < go_live_index:
            hosting_costs[month] = 0  # No COGS before go-live
            capitalized_hosting[month] = calculated_cost
        else:
            hosting_costs[month] = calculated_cost
            capitalized_hosting[month] = 0
    
    return hosting_costs, capitalized_hosting

def auto_calculate_cogs_from_gross_profit_model():
    """Auto-calculate COGS from gross profit model data every time"""
    if "revenue" not in st.session_state.model_data:
        return
    
    if "gross_profit_data" not in st.session_state.model_data:
        return
    
    revenue_data = st.session_state.model_data.get("revenue", {})
    gp_data = st.session_state.model_data.get("gross_profit_data", {})
    
    # Calculate hosting costs for subscription
    hosting_costs, capitalized_hosting = calculate_hosting_costs_from_gross_profit_model()
    
    # Initialize COGS if not exists
    if "cogs" not in st.session_state.model_data:
        st.session_state.model_data["cogs"] = {}
    
    # Calculate COGS for each stream
    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
        if stream not in st.session_state.model_data["cogs"]:
            st.session_state.model_data["cogs"][stream] = {}
        
        for month in months:
            revenue = revenue_data.get(stream, {}).get(month, 0)
            
            if stream == "Subscription":
                # For subscription, COGS = hosting costs + other direct costs
                direct_costs = gp_data.get("direct_costs", {}).get(stream, {}).get(month, 0)
                st.session_state.model_data["cogs"][stream][month] = hosting_costs.get(month, 0) + direct_costs
            else:
                # For other streams, use gross profit percentage
                gp_percentage = gp_data.get("gross_profit_percentages", {}).get(stream, {}).get(month, 70.0)
                st.session_state.model_data["cogs"][stream][month] = revenue * (1 - gp_percentage / 100)
    
    # Calculate total COGS
    total_cogs = {}
    for month in months:
        total_cogs[month] = sum(
            st.session_state.model_data["cogs"][stream].get(month, 0)
            for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
        )
    st.session_state.model_data["cogs"]["Total"] = total_cogs

# Auto-calculate COGS from Gross Profit model every time the page loads
auto_calculate_cogs_from_gross_profit_model()

# Revenue calculation functions from revenue_assumptions.py
def calculate_subscription_running_totals():
    """Calculate subscription running totals (from revenue_assumptions.py)"""
    # Stakeholder list (all 20 stakeholders)
    stakeholders = [
        "Equipment Manufacturer", "Dealership", "Corporate", "Charging as a Service",
        "Charging Hardware", "Depot", "End User", "Infrastructure Partner",
        "Finance Partner", "Fleet Management Company", "Grants", "Logistics",
        "Non Customer", "OEM", "Service", "Technology Partner",
        "Upfitter/Distributor", "Utility/Energy Company", "Insurance Company", "Consultant"
    ]
    
    # Initialize running totals data
    if "subscription_running_totals" not in st.session_state.model_data:
        st.session_state.model_data["subscription_running_totals"] = {}
    
    # Ensure all stakeholders are initialized
    for stakeholder in stakeholders:
        if stakeholder not in st.session_state.model_data["subscription_running_totals"]:
            st.session_state.model_data["subscription_running_totals"][stakeholder] = {month: 0 for month in months}
    
    # Calculate running totals for subscriptions
    for stakeholder in stakeholders:
        running_total = 0
        for month in months:
            # Get new subscriptions for this month
            new_subscriptions = st.session_state.model_data.get("subscription_new_customers", {}).get(stakeholder, {}).get(month, 0)
            
            # Get churn rate for this month (as percentage, so divide by 100)
            churn_rate = st.session_state.model_data.get("subscription_churn_rates", {}).get(stakeholder, {}).get(month, 0)
            churn_decimal = churn_rate / 100.0
            
            # Apply churn to existing customers, then add new customers
            # Formula: Previous * (1 - churn_rate) + New
            running_total = running_total * (1 - churn_decimal) + new_subscriptions
            
            # Store the result (round to avoid floating point precision issues)
            st.session_state.model_data["subscription_running_totals"][stakeholder][month] = round(running_total, 2)

def calculate_all_revenue():
    """Calculate all revenue streams (from revenue_assumptions.py)"""
    # Stakeholder list and transactional categories
    stakeholders = [
        "Equipment Manufacturer", "Dealership", "Corporate", "Charging as a Service",
        "Charging Hardware", "Depot", "End User", "Infrastructure Partner",
        "Finance Partner", "Fleet Management Company", "Grants", "Logistics",
        "Non Customer", "OEM", "Service", "Technology Partner",
        "Upfitter/Distributor", "Utility/Energy Company", "Insurance Company", "Consultant"
    ]
    
    transactional_categories = ["Charging", "Vehicle", "Financing", "Other Revenue"]
    
    # Calculate subscription running totals first
    calculate_subscription_running_totals()
    
    # Initialize revenue streams
    revenue_streams = {
        "Subscription": {month: 0 for month in months},
        "Transactional": {month: 0 for month in months},
        "Implementation": {month: 0 for month in months},
        "Maintenance": {month: 0 for month in months}
    }
    
    # Subscription Revenue (cumulative customers * monthly pricing)
    for stakeholder in stakeholders:
        for month in months:
            active_customers = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(month, 0)
            monthly_price = st.session_state.model_data.get("subscription_pricing", {}).get(stakeholder, {}).get(month, 0)
            revenue = active_customers * monthly_price
            revenue_streams["Subscription"][month] += revenue
    
    # Implementation Revenue (one-time fees)
    for stakeholder in stakeholders:
        for month in months:
            new_implementations = st.session_state.model_data.get("implementation_new_customers", {}).get(stakeholder, {}).get(month, 0)
            implementation_fee = st.session_state.model_data.get("implementation_pricing", {}).get(stakeholder, {}).get(month, 0)
            revenue = new_implementations * implementation_fee
            revenue_streams["Implementation"][month] += revenue
    
    # Maintenance Revenue (one-time fees)
    for stakeholder in stakeholders:
        for month in months:
            new_maintenance = st.session_state.model_data.get("maintenance_new_customers", {}).get(stakeholder, {}).get(month, 0)
            maintenance_fee = st.session_state.model_data.get("maintenance_pricing", {}).get(stakeholder, {}).get(month, 0)
            revenue = new_maintenance * maintenance_fee
            revenue_streams["Maintenance"][month] += revenue
    
    # Transactional Revenue (volume * price * referral fee)
    for category in transactional_categories:
        for month in months:
            volume = st.session_state.model_data.get("transactional_volume", {}).get(category, {}).get(month, 0)
            price = st.session_state.model_data.get("transactional_price", {}).get(category, {}).get(month, 0)
            referral_fee = st.session_state.model_data.get("transactional_referral_fee", {}).get(category, {}).get(month, 0)
            revenue = volume * price * (referral_fee / 100)
            revenue_streams["Transactional"][month] += revenue
    
    # Update the main revenue data for Income Statement
    if "revenue" not in st.session_state.model_data:
        st.session_state.model_data["revenue"] = {}
    
    for stream, monthly_data in revenue_streams.items():
        st.session_state.model_data["revenue"][stream] = monthly_data



# Calculate revenue from assumptions (save manually via button)
calculate_all_revenue()

# SG&A sync function from liquidity model  
def update_sga_expenses_from_liquidity():
    """Update SG&A expenses from liquidity cash disbursements (from liquidity_model.py)"""
    
    # Initialize SG&A if not exists
    if "sga_expenses" not in st.session_state.model_data:
        st.session_state.model_data["sga_expenses"] = {}
    
    # Only proceed if liquidity data exists
    if "liquidity_data" not in st.session_state.model_data:
        return
        
    # Map liquidity categories to SG&A categories
    liquidity_to_sga_mapping = {
        "Payroll": "Payroll",
        "Contractors": "Contractors", 
        "License Fees": "License Fees",
        "Travel": "Travel",
        "Shows": "Shows",
        "Associations": "Associations",
        "Marketing": "Marketing",
        "Company Vehicle": "Company Vehicle",
        "Grant Writer": "Grant Writer",
        "Insurance": "Insurance",
        "Legal / Professional Fees": "Legal / Professional Fees",
        "Permitting/Fees/Licensing": "Permitting/Fees/Licensing",
        "Shared Services": "Shared Services",
        "Consultants/Audit/Tax": "Consultants/Audit/Tax",
        "Pritchard Amex": "Pritchard Amex",
        "Contingencies": "Contingencies",
    }
    
    # Get the category order from liquidity data (maintains add/remove functionality)
    ordered_categories = st.session_state.model_data["liquidity_data"].get("category_order", list(liquidity_to_sga_mapping.keys()))
    
    # Clear existing SG&A data to rebuild in correct order
    st.session_state.model_data["sga_expenses"] = {}
    
    # Copy data from liquidity cash disbursements to SG&A expenses
    for liquidity_cat in ordered_categories:
        if (liquidity_cat in liquidity_to_sga_mapping and 
            "expenses" in st.session_state.model_data["liquidity_data"] and
            liquidity_cat in st.session_state.model_data["liquidity_data"]["expenses"]):
            sga_cat = liquidity_to_sga_mapping[liquidity_cat]
            st.session_state.model_data["sga_expenses"][sga_cat] = st.session_state.model_data["liquidity_data"]["expenses"][liquidity_cat].copy()

# Auto-sync SG&A expenses from liquidity cash disbursements every time the page loads
update_sga_expenses_from_liquidity()

# Helper function to create custom tables with fixed category column
def create_custom_table_with_years(categories, data_key, show_monthly=True):
    """Create custom table with fixed category column and scrollable data"""
    
    # Initialize data if not exists
    if data_key not in st.session_state.model_data:
        st.session_state.model_data[data_key] = {}
        for category in categories:
            st.session_state.model_data[data_key][category] = {month: 0 for month in months}
    
    # Group months by year
    years_dict = group_months_by_year(months)
    
    # Create column headers
    if show_monthly:
        data_columns = []
        for year in sorted(years_dict.keys()):
            data_columns.extend(years_dict[year])
            data_columns.append(f"{year} Total")
    else:
        data_columns = [f"{year} Total" for year in sorted(years_dict.keys())]
    
    # Build HTML table
    html_content = '<div class="fixed-table-container">'
    
    # Fixed category column
    html_content += '<div class="fixed-category-column">'
    html_content += '<div class="category-header">Category</div>'
    
    for category in categories:
        html_content += f'<div class="category-cell">{category}</div>'
    
    html_content += '</div>'
    
    # Scrollable data area
    html_content += '<div class="scrollable-data">'
    html_content += '<table class="data-table"><colgroup>'
    
    # Define column groups for consistent width
    for col in data_columns:
        if "Total" in col:
            html_content += '<col style="width: 100px;">'
        else:
            html_content += '<col style="width: 80px;">'
    
    html_content += '</colgroup>'
    
    # Header row
    html_content += '<thead><tr style="height: 43px !important;">'
    for col in data_columns:
        css_class = "data-header year-total" if "Total" in col else "data-header"
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important; text-align: center !important;">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data rows
    html_content += '<tbody>'
    for category in categories:
        html_content += '<tr style="height: 43px !important;">'
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    value = st.session_state.model_data[data_key].get(category, {}).get(month, 0)
                    if data_key == "gross_margin":
                        formatted_value = format_percentage(value)
                    else:
                        formatted_value = format_number(value)
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                    yearly_total += value
                
                if data_key == "gross_margin":
                    # For gross margin, calculate correct percentage: Total Gross Profit / Total Revenue for the year
                    yearly_revenue = 0
                    yearly_gross_profit = 0
                    for month in years_dict[year]:
                        revenue = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                        gross_profit = st.session_state.model_data.get("gross_profit", {}).get(category, {}).get(month, 0)
                        yearly_revenue += revenue
                        yearly_gross_profit += gross_profit
                    
                    yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                    formatted_yearly_total = format_percentage(yearly_percentage)
                else:
                    formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
        else:
            for year in sorted(years_dict.keys()):
                if data_key == "gross_margin":
                    # For gross margin, calculate correct percentage: Total Gross Profit / Total Revenue for the year
                    yearly_revenue = sum(
                        st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                        for month in years_dict[year]
                    )
                    yearly_gross_profit = sum(
                        st.session_state.model_data.get("gross_profit", {}).get(category, {}).get(month, 0)
                        for month in years_dict[year]
                    )
                    yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                    formatted_yearly_total = format_percentage(yearly_percentage)
                else:
                    yearly_total = sum(
                        st.session_state.model_data[data_key].get(category, {}).get(month, 0)
                        for month in years_dict[year]
                    )
                    formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
        
        html_content += '</tr>'
    
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create total row with fixed category column and proper yearly percentage calculation
def create_custom_total_row_with_yearly_percentage(monthly_dict, numerator_dict, denominator_dict, row_label, show_monthly=True):
    """Create a total row with proper yearly percentage calculation for ratios"""
    years_dict = group_months_by_year(months)
    
    if show_monthly:
        data_columns = []
        for year in sorted(years_dict.keys()):
            data_columns.extend(years_dict[year])
            data_columns.append(f"{year} Total")
    else:
        data_columns = [f"{year} Total" for year in sorted(years_dict.keys())]
    
    # Build HTML table
    html_content = '<div class="fixed-table-container">'
    
    # Fixed category column
    html_content += '<div class="fixed-category-column">'
    html_content += '<div class="category-header">Category</div>'
    html_content += f'<div class="category-total">{row_label}</div>'
    html_content += '</div>'
    
    # Scrollable data area
    html_content += '<div class="scrollable-data">'
    html_content += '<table class="data-table"><colgroup>'
    
    # Define column groups for consistent width
    for col in data_columns:
        if "Total" in col:
            html_content += '<col style="width: 100px;">'
        else:
            html_content += '<col style="width: 80px;">'
    
    html_content += '</colgroup>'
    
    # Header row
    html_content += '<thead><tr style="height: 43px !important;">'
    for col in data_columns:
        css_class = "data-header year-total" if "Total" in col else "data-header"
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important; text-align: center !important;">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data row
    html_content += '<tbody><tr class="total-row" style="height: 43px !important;">'
    
    if show_monthly:
        for year in sorted(years_dict.keys()):
            # Monthly values
            for month in years_dict[year]:
                value = monthly_dict.get(month, 0)
                formatted_value = format_percentage(value)
                html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
            
            # Yearly total - calculate percentage correctly
            yearly_numerator = sum(numerator_dict.get(month, 0) for month in years_dict[year])
            yearly_denominator = sum(denominator_dict.get(month, 0) for month in years_dict[year])
            yearly_percentage = (yearly_numerator / yearly_denominator * 100) if yearly_denominator > 0 else 0
            formatted_yearly_total = format_percentage(yearly_percentage)
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
    else:
        for year in sorted(years_dict.keys()):
            # Calculate percentage correctly for yearly view
            yearly_numerator = sum(numerator_dict.get(month, 0) for month in years_dict[year])
            yearly_denominator = sum(denominator_dict.get(month, 0) for month in years_dict[year])
            yearly_percentage = (yearly_numerator / yearly_denominator * 100) if yearly_denominator > 0 else 0
            formatted_yearly_total = format_percentage(yearly_percentage)
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
    
    html_content += '</tr></tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create total row with fixed category column
def create_custom_total_row(total_dict, row_label, show_monthly=True):
    """Create a total row with fixed category column and headers"""
    years_dict = group_months_by_year(months)
    
    if show_monthly:
        data_columns = []
        for year in sorted(years_dict.keys()):
            data_columns.extend(years_dict[year])
            data_columns.append(f"{year} Total")
    else:
        data_columns = [f"{year} Total" for year in sorted(years_dict.keys())]
    
    # Build HTML table
    html_content = '<div class="fixed-table-container">'
    
    # Fixed category column
    html_content += '<div class="fixed-category-column">'
    html_content += '<div class="category-header">Category</div>'
    html_content += f'<div class="category-total">{row_label}</div>'
    html_content += '</div>'
    
    # Scrollable data area
    html_content += '<div class="scrollable-data">'
    html_content += '<table class="data-table"><colgroup>'
    
    # Define column groups for consistent width
    for col in data_columns:
        if "Total" in col:
            html_content += '<col style="width: 100px;">'
        else:
            html_content += '<col style="width: 80px;">'
    
    html_content += '</colgroup>'
    
    # Header row
    html_content += '<thead><tr style="height: 43px !important;">'
    for col in data_columns:
        css_class = "data-header year-total" if "Total" in col else "data-header"
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important; text-align: center !important;">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data row
    html_content += '<tbody><tr class="total-row" style="height: 43px !important;">'
    
    # Check if this is Net Income row to apply red formatting for negatives
    is_net_income = row_label == "Net Income"
    # Check if this is a percentage row
    is_percentage = "%" in row_label
    
    if show_monthly:
        for year in sorted(years_dict.keys()):
            yearly_total = 0
            for month in years_dict[year]:
                value = total_dict.get(month, 0)
                if is_percentage:
                    formatted_value = format_percentage(value)
                else:
                    formatted_value = format_number_with_color(value, apply_red_for_negative=is_net_income)
                html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                yearly_total += value
            
            if is_percentage:
                # For percentage rows, calculate average percentage for the year
                yearly_avg = yearly_total / len(years_dict[year])
                formatted_yearly_total = format_percentage(yearly_avg)
            else:
                formatted_yearly_total = format_number_with_color(yearly_total, apply_red_for_negative=is_net_income)
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
    else:
        for year in sorted(years_dict.keys()):
            if is_percentage:
                # For percentage rows, calculate average percentage for the year
                yearly_avg = sum(total_dict.get(month, 0) for month in years_dict[year]) / len(years_dict[year])
                formatted_yearly_total = format_percentage(yearly_avg)
            else:
                yearly_total = sum(total_dict.get(month, 0) for month in years_dict[year])
                formatted_yearly_total = format_number_with_color(yearly_total, apply_red_for_negative=is_net_income)
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
    
    html_content += '</tr></tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create comprehensive income statement table
def create_comprehensive_income_statement(show_monthly=True, include_gross_margin=False):
    """Create one unified income statement table with all sections"""
    
    # Group months by year
    years_dict = group_months_by_year(months)
    
    # Create column headers
    if show_monthly:
        data_columns = []
        for year in sorted(years_dict.keys()):
            data_columns.extend(years_dict[year])
            data_columns.append(f"{year} Total")
    else:
        data_columns = [f"{year} Total" for year in sorted(years_dict.keys())]
    
    # Define all sections and their data
    revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    cost_of_sales_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    gross_profit_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    
    # Get SG&A categories
    if ("liquidity_data" in st.session_state.model_data and 
        "category_order" in st.session_state.model_data["liquidity_data"]):
        sga_categories = st.session_state.model_data["liquidity_data"]["category_order"]
    else:
        sga_categories = [
            "Payroll", "Contractors", "License Fees", "Travel", "Shows", "Associations",
            "Marketing", "Company Vehicle", "Grant Writer", "Insurance", "Legal / Professional Fees",
            "Permitting/Fees/Licensing", "Shared Services", "Consultants/Audit/Tax", "Pritchard Amex", "Contingencies"
        ]
    
    # Calculate totals
    total_revenue = {}
    total_cost_of_sales = {}
    total_gross_profit = {}
    total_gross_margin = {}
    total_sga = {}
    net_income = {}
    
    for month in months:
        total_revenue[month] = sum(
            st.session_state.model_data.get("revenue", {}).get(cat, {}).get(month, 0) 
            for cat in revenue_categories
        )
        total_cost_of_sales[month] = sum(
            st.session_state.model_data.get("cogs", {}).get(cat, {}).get(month, 0) 
            for cat in cost_of_sales_categories
        )
        total_gross_profit[month] = total_revenue[month] - total_cost_of_sales[month]
        total_gross_margin[month] = (total_gross_profit[month] / total_revenue[month] * 100) if total_revenue[month] > 0 else 0
        total_sga[month] = sum(
            st.session_state.model_data.get("sga_expenses", {}).get(cat, {}).get(month, 0) 
            for cat in sga_categories
        )
        net_income[month] = total_gross_profit[month] - total_sga[month]
    
    # Build HTML table using new comprehensive table structure
    html_content = '<div class="comprehensive-table">'
    html_content += '<table>'
    
    # Define column groups for consistent width
    html_content += '<colgroup>'
    html_content += '<col style="width: 200px;">'  # First column (categories)
    for col in data_columns:
        if "Total" in col:
            html_content += '<col style="width: 100px;">'
        else:
            html_content += '<col style="width: 80px;">'
    html_content += '</colgroup>'
    
    # Header row
    html_content += '<thead><tr>'
    html_content += '<th>Income Statement</th>'
    for col in data_columns:
        css_class = "year-total" if "Total" in col else ""
        html_content += f'<th class="{css_class}">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data rows
    html_content += '<tbody>'
    
    # Revenue section header
    html_content += '<tr class="section-header">'
    html_content += '<td>Revenue</td>'
    for col in data_columns:
        html_content += '<td></td>'
    html_content += '</tr>'
    
    for category in revenue_categories:
        html_content += '<tr>'
        html_content += f'<td>  {category}</td>'
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    value = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                    formatted_value = format_number(value)
                    html_content += f'<td>{formatted_value}</td>'
                
                yearly_total = sum(st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        else:
            for year in sorted(years_dict.keys()):
                yearly_total = sum(st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        html_content += '</tr>'
    
    # Total Revenue row
    html_content += '<tr class="total-row">'
    html_content += '<td>Total Revenue</td>'
    if show_monthly:
        for year in sorted(years_dict.keys()):
            for month in years_dict[year]:
                value = total_revenue.get(month, 0)
                formatted_value = format_number(value)
                html_content += f'<td>{formatted_value}</td>'
            yearly_total = sum(total_revenue.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number(yearly_total)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    else:
        for year in sorted(years_dict.keys()):
            yearly_total = sum(total_revenue.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number(yearly_total)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    html_content += '</tr>'
    
    # Cost of Sales section header
    html_content += '<tr class="section-header">'
    html_content += '<td>Cost of Sales</td>'
    for col in data_columns:
        html_content += '<td></td>'
    html_content += '</tr>'
    
    for category in cost_of_sales_categories:
        html_content += '<tr>'
        html_content += f'<td>  {category}</td>'
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    value = st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0)
                    formatted_value = format_number(value)
                    html_content += f'<td>{formatted_value}</td>'
                
                yearly_total = sum(st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        else:
            for year in sorted(years_dict.keys()):
                yearly_total = sum(st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        html_content += '</tr>'
    
    # Total Cost of Sales row
    html_content += '<tr class="total-row">'
    html_content += '<td>Total Cost of Sales</td>'
    if show_monthly:
        for year in sorted(years_dict.keys()):
            for month in years_dict[year]:
                value = total_cost_of_sales.get(month, 0)
                formatted_value = format_number(value)
                html_content += f'<td>{formatted_value}</td>'
            yearly_total = sum(total_cost_of_sales.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number(yearly_total)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    else:
        for year in sorted(years_dict.keys()):
            yearly_total = sum(total_cost_of_sales.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number(yearly_total)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    html_content += '</tr>'
    
    # Gross Profit section header
    html_content += '<tr class="section-header">'
    html_content += '<td>Gross Profit</td>'
    for col in data_columns:
        html_content += '<td></td>'
    html_content += '</tr>'
    
    for category in gross_profit_categories:
        html_content += '<tr>'
        html_content += f'<td>  {category}</td>'
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    revenue = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                    cost = st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0)
                    value = revenue - cost
                    formatted_value = format_number(value)
                    html_content += f'<td>{formatted_value}</td>'
                
                yearly_revenue = sum(st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                yearly_cost = sum(st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                yearly_total = yearly_revenue - yearly_cost
                formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        else:
            for year in sorted(years_dict.keys()):
                yearly_revenue = sum(st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                yearly_cost = sum(st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                yearly_total = yearly_revenue - yearly_cost
                formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        html_content += '</tr>'
    
    # Total Gross Profit row
    html_content += '<tr class="total-row">'
    html_content += '<td>Total Gross Profit</td>'
    if show_monthly:
        for year in sorted(years_dict.keys()):
            for month in years_dict[year]:
                value = total_gross_profit.get(month, 0)
                formatted_value = format_number(value)
                html_content += f'<td>{formatted_value}</td>'
            yearly_total = sum(total_gross_profit.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number(yearly_total)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    else:
        for year in sorted(years_dict.keys()):
            yearly_total = sum(total_gross_profit.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number(yearly_total)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    html_content += '</tr>'
    
    # Gross Margin section (if enabled)
    if include_gross_margin:
        html_content += '<tr class="section-header">'
        html_content += '<td>Gross Margin %</td>'
        for col in data_columns:
            html_content += '<td></td>'
        html_content += '</tr>'
        
        for category in gross_profit_categories:
            html_content += '<tr>'
            html_content += f'<td>  {category}</td>'
            if show_monthly:
                for year in sorted(years_dict.keys()):
                    for month in years_dict[year]:
                        revenue = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                        cost = st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0)
                        gross_profit = revenue - cost
                        value = (gross_profit / revenue * 100) if revenue > 0 else 0
                        formatted_value = format_percentage(value)
                        html_content += f'<td>{formatted_value}</td>'
                    
                    yearly_revenue = sum(st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                    yearly_cost = sum(st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                    yearly_gross_profit = yearly_revenue - yearly_cost
                    yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                    formatted_yearly_total = format_percentage(yearly_percentage)
                    html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
            else:
                for year in sorted(years_dict.keys()):
                    yearly_revenue = sum(st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                    yearly_cost = sum(st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                    yearly_gross_profit = yearly_revenue - yearly_cost
                    yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                    formatted_yearly_total = format_percentage(yearly_percentage)
                    html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
            html_content += '</tr>'
        
        # Total Gross Margin row
        html_content += '<tr class="total-row">'
        html_content += '<td>Total Gross Margin %</td>'
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    value = total_gross_margin.get(month, 0)
                    formatted_value = format_percentage(value)
                    html_content += f'<td>{formatted_value}</td>'
                
                yearly_gross_profit = sum(total_gross_profit.get(month, 0) for month in years_dict[year])
                yearly_revenue = sum(total_revenue.get(month, 0) for month in years_dict[year])
                yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                formatted_yearly_total = format_percentage(yearly_percentage)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        else:
            for year in sorted(years_dict.keys()):
                yearly_gross_profit = sum(total_gross_profit.get(month, 0) for month in years_dict[year])
                yearly_revenue = sum(total_revenue.get(month, 0) for month in years_dict[year])
                yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                formatted_yearly_total = format_percentage(yearly_percentage)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        html_content += '</tr>'
    
    # SG&A section header
    html_content += '<tr class="section-header">'
    html_content += '<td>SG&A Expenses</td>'
    for col in data_columns:
        html_content += '<td></td>'
    html_content += '</tr>'
    
    for category in sga_categories:
        html_content += '<tr>'
        html_content += f'<td>  {category}</td>'
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    value = st.session_state.model_data.get("sga_expenses", {}).get(category, {}).get(month, 0)
                    formatted_value = format_number(value)
                    html_content += f'<td>{formatted_value}</td>'
                
                yearly_total = sum(st.session_state.model_data.get("sga_expenses", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        else:
            for year in sorted(years_dict.keys()):
                yearly_total = sum(st.session_state.model_data.get("sga_expenses", {}).get(category, {}).get(month, 0) for month in years_dict[year])
                formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
        html_content += '</tr>'
    
    # Total SG&A row
    html_content += '<tr class="total-row">'
    html_content += '<td>Total SG&A Expenses</td>'
    if show_monthly:
        for year in sorted(years_dict.keys()):
            for month in years_dict[year]:
                value = total_sga.get(month, 0)
                formatted_value = format_number(value)
                html_content += f'<td>{formatted_value}</td>'
            yearly_total = sum(total_sga.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number(yearly_total)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    else:
        for year in sorted(years_dict.keys()):
            yearly_total = sum(total_sga.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number(yearly_total)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    html_content += '</tr>'
    
    # Net Income row
    html_content += '<tr class="total-row">'
    html_content += '<td>Net Income</td>'
    if show_monthly:
        for year in sorted(years_dict.keys()):
            for month in years_dict[year]:
                value = net_income.get(month, 0)
                formatted_value = format_number_with_color(value, apply_red_for_negative=True)
                html_content += f'<td>{formatted_value}</td>'
            yearly_total = sum(net_income.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number_with_color(yearly_total, apply_red_for_negative=True)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    else:
        for year in sorted(years_dict.keys()):
            yearly_total = sum(net_income.get(month, 0) for month in years_dict[year])
            formatted_yearly_total = format_number_with_color(yearly_total, apply_red_for_negative=True)
            html_content += f'<td class="year-total">{formatted_yearly_total}</td>'
    html_content += '</tr>'
    
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create combined table with total row
def create_custom_table_with_total(categories, data_key, total_data, total_label, show_monthly=True):
    """Create custom table with component rows and total row combined"""
    # Initialize data if not exists
    if data_key not in st.session_state.model_data:
        st.session_state.model_data[data_key] = {}
        for category in categories:
            st.session_state.model_data[data_key][category] = {month: 0 for month in months}
    
    # Group months by year
    years_dict = group_months_by_year(months)
    
    # Create column headers
    if show_monthly:
        data_columns = []
        for year in sorted(years_dict.keys()):
            data_columns.extend(years_dict[year])
            data_columns.append(f"{year} Total")
    else:
        data_columns = [f"{year} Total" for year in sorted(years_dict.keys())]
    
    # Build HTML table
    html_content = '<div class="fixed-table-container">'
    
    # Fixed category column
    html_content += '<div class="fixed-category-column">'
    html_content += '<div class="category-header">Category</div>'
    
    for category in categories:
        html_content += f'<div class="category-cell">{category}</div>'
    
    # Add total row with special styling
    html_content += f'<div class="category-total">{total_label}</div>'
    html_content += '</div>'
    
    # Scrollable data area
    html_content += '<div class="scrollable-data">'
    html_content += '<table class="data-table"><colgroup>'
    
    # Define column groups for consistent width
    for col in data_columns:
        if "Total" in col:
            html_content += '<col style="width: 100px;">'
        else:
            html_content += '<col style="width: 80px;">'
    
    html_content += '</colgroup>'
    
    # Header row
    html_content += '<thead><tr style="height: 43px !important;">'
    for col in data_columns:
        css_class = "data-header year-total" if "Total" in col else "data-header"
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important; text-align: center !important;">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data rows
    html_content += '<tbody>'
    for category in categories:
        html_content += '<tr style="height: 43px !important;">'
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    value = st.session_state.model_data[data_key].get(category, {}).get(month, 0)
                    if data_key == "gross_margin":
                        formatted_value = format_percentage(value)
                    else:
                        formatted_value = format_number(value)
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                    yearly_total += value
                
                if data_key == "gross_margin":
                    # For gross margin, calculate correct percentage: Total Gross Profit / Total Revenue for the year
                    yearly_revenue = 0
                    yearly_gross_profit = 0
                    for month in years_dict[year]:
                        revenue = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                        gross_profit = st.session_state.model_data.get("gross_profit", {}).get(category, {}).get(month, 0)
                        yearly_revenue += revenue
                        yearly_gross_profit += gross_profit
                    
                    yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                    formatted_yearly_total = format_percentage(yearly_percentage)
                else:
                    formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
        else:
            for year in sorted(years_dict.keys()):
                if data_key == "gross_margin":
                    # For gross margin, calculate correct percentage: Total Gross Profit / Total Revenue for the year
                    yearly_revenue = sum(
                        st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                        for month in years_dict[year]
                    )
                    yearly_gross_profit = sum(
                        st.session_state.model_data.get("gross_profit", {}).get(category, {}).get(month, 0)
                        for month in years_dict[year]
                    )
                    yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                    formatted_yearly_total = format_percentage(yearly_percentage)
                else:
                    yearly_total = sum(
                        st.session_state.model_data[data_key].get(category, {}).get(month, 0)
                        for month in years_dict[year]
                    )
                    formatted_yearly_total = format_number(yearly_total)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
        
        html_content += '</tr>'
    
    # Add total row with special styling
    html_content += '<tr class="total-row" style="height: 43px !important;">'
    
    # Check if this is Net Income row to apply red formatting for negatives
    is_net_income = total_label == "Net Income"
    # Check if this is a percentage row
    is_percentage = "%" in total_label
    
    if show_monthly:
        for year in sorted(years_dict.keys()):
            yearly_total = 0
            for month in years_dict[year]:
                value = total_data.get(month, 0)
                if is_percentage:
                    formatted_value = format_percentage(value)
                else:
                    formatted_value = format_number_with_color(value, apply_red_for_negative=is_net_income)
                html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                yearly_total += value
            
            if is_percentage:
                # For percentage rows, calculate average percentage for the year
                yearly_avg = yearly_total / len(years_dict[year])
                formatted_yearly_total = format_percentage(yearly_avg)
            else:
                formatted_yearly_total = format_number_with_color(yearly_total, apply_red_for_negative=is_net_income)
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
    else:
        for year in sorted(years_dict.keys()):
            if is_percentage:
                # For percentage rows, calculate average percentage for the year
                yearly_avg = sum(total_data.get(month, 0) for month in years_dict[year]) / len(years_dict[year])
                formatted_yearly_total = format_percentage(yearly_avg)
            else:
                yearly_total = sum(total_data.get(month, 0) for month in years_dict[year])
                formatted_yearly_total = format_number_with_color(yearly_total, apply_red_for_negative=is_net_income)
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
    
    html_content += '</tr>'
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create combined percentage table with special total row calculation
def create_custom_percentage_table_with_total(categories, data_key, monthly_dict, numerator_dict, denominator_dict, total_label, show_monthly=True):
    """Create custom percentage table with component rows and special total row calculation"""
    # Initialize data if not exists
    if data_key not in st.session_state.model_data:
        st.session_state.model_data[data_key] = {}
        for category in categories:
            st.session_state.model_data[data_key][category] = {month: 0 for month in months}
    
    # Group months by year
    years_dict = group_months_by_year(months)
    
    # Create column headers
    if show_monthly:
        data_columns = []
        for year in sorted(years_dict.keys()):
            data_columns.extend(years_dict[year])
            data_columns.append(f"{year} Total")
    else:
        data_columns = [f"{year} Total" for year in sorted(years_dict.keys())]
    
    # Build HTML table
    html_content = '<div class="fixed-table-container">'
    
    # Fixed category column
    html_content += '<div class="fixed-category-column">'
    html_content += '<div class="category-header">Category</div>'
    
    for category in categories:
        html_content += f'<div class="category-cell">{category}</div>'
    
    # Add total row with special styling
    html_content += f'<div class="category-total">{total_label}</div>'
    html_content += '</div>'
    
    # Scrollable data area
    html_content += '<div class="scrollable-data">'
    html_content += '<table class="data-table"><colgroup>'
    
    # Define column groups for consistent width
    for col in data_columns:
        if "Total" in col:
            html_content += '<col style="width: 100px;">'
        else:
            html_content += '<col style="width: 80px;">'
    
    html_content += '</colgroup>'
    
    # Header row
    html_content += '<thead><tr style="height: 43px !important;">'
    for col in data_columns:
        css_class = "data-header year-total" if "Total" in col else "data-header"
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important; text-align: center !important;">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data rows
    html_content += '<tbody>'
    for category in categories:
        html_content += '<tr style="height: 43px !important;">'
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    value = st.session_state.model_data[data_key].get(category, {}).get(month, 0)
                    formatted_value = format_percentage(value)
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                    yearly_total += value
                
                # For gross margin, calculate correct percentage: Total Gross Profit / Total Revenue for the year
                yearly_revenue = 0
                yearly_gross_profit = 0
                for month in years_dict[year]:
                    revenue = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                    gross_profit = st.session_state.model_data.get("gross_profit", {}).get(category, {}).get(month, 0)
                    yearly_revenue += revenue
                    yearly_gross_profit += gross_profit
                
                yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                formatted_yearly_total = format_percentage(yearly_percentage)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
        else:
            for year in sorted(years_dict.keys()):
                # For gross margin, calculate correct percentage: Total Gross Profit / Total Revenue for the year
                yearly_revenue = sum(
                    st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
                    for month in years_dict[year]
                )
                yearly_gross_profit = sum(
                    st.session_state.model_data.get("gross_profit", {}).get(category, {}).get(month, 0)
                    for month in years_dict[year]
                )
                yearly_percentage = (yearly_gross_profit / yearly_revenue * 100) if yearly_revenue > 0 else 0
                formatted_yearly_total = format_percentage(yearly_percentage)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
        
        html_content += '</tr>'
    
    # Add total row with special yearly percentage calculation
    html_content += '<tr class="total-row" style="height: 43px !important;">'
    
    if show_monthly:
        for year in sorted(years_dict.keys()):
            # Monthly values
            for month in years_dict[year]:
                value = monthly_dict.get(month, 0)
                formatted_value = format_percentage(value)
                html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
            
            # Yearly total - calculate percentage correctly
            yearly_numerator = sum(numerator_dict.get(month, 0) for month in years_dict[year])
            yearly_denominator = sum(denominator_dict.get(month, 0) for month in years_dict[year])
            yearly_percentage = (yearly_numerator / yearly_denominator * 100) if yearly_denominator > 0 else 0
            formatted_yearly_total = format_percentage(yearly_percentage)
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
    else:
        for year in sorted(years_dict.keys()):
            # Calculate percentage correctly for yearly view
            yearly_numerator = sum(numerator_dict.get(month, 0) for month in years_dict[year])
            yearly_denominator = sum(denominator_dict.get(month, 0) for month in years_dict[year])
            yearly_percentage = (yearly_numerator / yearly_denominator * 100) if yearly_denominator > 0 else 0
            formatted_yearly_total = format_percentage(yearly_percentage)
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
    
    html_content += '</tr>'
    html_content += '</tbody></table>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Header with SHAED branding
st.markdown("""
<div class="main-header">
    <h1>📈 Income Statement</h1>
</div>
""", unsafe_allow_html=True)

# Unified Navigation Bar
st.markdown('<div class="nav-section-header">🧭 Dashboard Navigation</div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7, nav_col8 = st.columns(8)

with nav_col1:
    if st.button("🏠 Home", key="nav_home", use_container_width=True):
        st.info("Run: streamlit run home.py")

with nav_col2:
    if st.button("📊 KPIs", key="nav_kpi", use_container_width=True):
        st.info("Run: streamlit run kpi_dashboard.py")

with nav_col3:
    if st.button("📈 Income", key="nav_income", use_container_width=True):
        st.info("Run: streamlit run financial_model.py")

with nav_col4:
    if st.button("💰 Liquidity", key="nav_liquidity", use_container_width=True):
        st.info("Run: streamlit run liquidity_model.py")

with nav_col5:
    if st.button("💵 Revenue", key="nav_revenue", use_container_width=True):
        st.info("Run: streamlit run revenue_assumptions.py")

with nav_col6:
    if st.button("👥 Headcount", key="nav_headcount", use_container_width=True):
        st.info("Run: streamlit run payroll_model.py")

with nav_col7:
    if st.button("🔍 Gross Profit", key="nav_gross", use_container_width=True):
        st.info("Run: streamlit run gross_profit_model.py")

with nav_col8:
    if st.button("☁️ Hosting", key="nav_hosting", use_container_width=True):
        st.info("Run: streamlit run hosting_costs_model.py")

# Add visual separator after navigation
st.markdown("---")

# View toggle
view_col1, view_col2 = st.columns([0.75, 3.25])
with view_col1:
    view_mode = st.selectbox(
        "View Mode:",
        ["Monthly + Yearly", "Yearly Only"],
        key="view_mode"
    )

show_monthly = view_mode == "Monthly + Yearly"

# COMPREHENSIVE INCOME STATEMENT
st.markdown('<div class="section-header">📊 Income Statement</div>', unsafe_allow_html=True)
st.info("📝 Data populated from Revenue, Gross Profit, and Liquidity dashboards")

# Ensure we have the latest revenue calculations
calculate_all_revenue()

# Calculate all data for the comprehensive income statement
revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
cost_of_sales_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]

# Calculate total revenue
total_revenue = {}
for month in months:
    total_revenue[month] = sum(
        st.session_state.model_data.get("revenue", {}).get(cat, {}).get(month, 0) 
        for cat in revenue_categories
    )

# Calculate total cost of sales
total_cost_of_sales = {}
for month in months:
    total_cost_of_sales[month] = sum(
        st.session_state.model_data.get("cogs", {}).get(cat, {}).get(month, 0) 
        for cat in cost_of_sales_categories
    )

# Calculate gross profit data (Revenue - COGS)
gross_profit_data = {}
for category in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
    gross_profit_data[category] = {}
    for month in months:
        revenue = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
        cost = st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0)
        gross_profit_data[category][month] = revenue - cost

# Store gross profit data in session state
st.session_state.model_data["gross_profit"] = gross_profit_data

# Calculate total gross profit
total_gross_profit = {}
for month in months:
    total_gross_profit[month] = total_revenue[month] - total_cost_of_sales[month]

# Get SG&A categories
if ("liquidity_data" in st.session_state.model_data and 
    "category_order" in st.session_state.model_data["liquidity_data"]):
    sga_categories = st.session_state.model_data["liquidity_data"]["category_order"]
else:
            sga_categories = [
            "Payroll", "Contractors", "License Fees", "Travel", "Shows", "Associations",
            "Marketing", "Company Vehicle", "Grant Writer", "Insurance", "Legal / Professional Fees",
            "Permitting/Fees/Licensing", "Shared Services", "Consultants/Audit/Tax", "Pritchard Amex", "Contingencies"
        ]

# Calculate total SG&A expenses
total_sga = {}
for month in months:
    total_sga[month] = sum(
        st.session_state.model_data.get("sga_expenses", {}).get(cat, {}).get(month, 0) 
        for cat in sga_categories
    )

# Calculate net income
net_income = {}
for month in months:
    net_income[month] = total_gross_profit[month] - total_sga[month]

# Toggle for gross margin display
show_gross_margin = st.checkbox("Show Gross Margin %", value=False, help="Toggle to show/hide gross margin percentage in the income statement")

if show_gross_margin:
    # Calculate gross margin data
    gross_margin_data = {}
    for category in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
        gross_margin_data[category] = {}
        for month in months:
            revenue = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
            cost = st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0)
            gross_profit = revenue - cost
            gross_margin_data[category][month] = (gross_profit / revenue * 100) if revenue > 0 else 0
    
    # Store gross margin data in session state
    st.session_state.model_data["gross_margin"] = gross_margin_data

# Create the comprehensive income statement table
create_comprehensive_income_statement(show_monthly, show_gross_margin)

# Summary metrics with SHAED styling
st.markdown("---")
st.markdown('<div class="section-header">📊 Summary</div>', unsafe_allow_html=True)

# Add dropdown for time period selection
summary_col1, summary_col2 = st.columns([0.75, 3.25])
with summary_col1:
    # Calculate default index based on current year
    current_year = str(datetime.now().year)
    summary_options = ["2025", "2026", "2027", "2028", "2029", "2030", "All Years"]
    try:
        default_summary_index = summary_options.index(current_year)
    except ValueError:
        default_summary_index = 0  # Fallback to first option if current year not in list
    
    summary_period = st.selectbox(
        "Select time period for summary:",
        options=summary_options,
        index=default_summary_index,
        key="summary_period_select"
    )

# Determine which months to include based on selection
if summary_period == "All Years":
    # Use all months
    filtered_months = months
else:
    # Filter for specific year
    filtered_months = [month for month in months if summary_period in month]

# Single row of summary metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    # Calculate filtered totals based on selected period
    total_revenue_sum = sum(total_revenue.get(month, 0) for month in filtered_months)
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Revenue</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${total_revenue_sum:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_cost_of_sales_sum = sum(total_cost_of_sales.get(month, 0) for month in filtered_months)
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Cost of Sales</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${total_cost_of_sales_sum:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_gross_profit_sum = sum(total_gross_profit.get(month, 0) for month in filtered_months)
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Gross Profit</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${total_gross_profit_sum:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    gross_margin_percentage = (total_gross_profit_sum / total_revenue_sum * 100) if total_revenue_sum > 0 else 0
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Gross Margin</h4>
        <h2 style="margin: 0.5rem 0 0 0;">{gross_margin_percentage:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

with col5:
    total_sga_sum = sum(total_sga.get(month, 0) for month in filtered_months)
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total SG&A Expenses</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${total_sga_sum:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col6:
    total_net_income_sum = sum(net_income.get(month, 0) for month in filtered_months)
    color = "#00D084" if total_net_income_sum >= 0 else "#dc3545"
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Net Income</h4>
        <h2 style="margin: 0.5rem 0 0 0; color: {color};">${total_net_income_sum:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# BAR GRAPH SECTION
st.markdown("") # Small spacing

# Chart type selection dropdown
chart_type_col1, chart_type_col2 = st.columns([0.75, 3.25])
with chart_type_col1:
    # Get current index based on session state
    chart_options = ["Total Revenue", "Total Cost of Sales", "Total Gross Profit", "Gross Margin", "Total SG&A Expenses", "Total Net Income"]
    current_type = st.session_state.get("income_chart_type", "revenue")
    
    if current_type == "revenue":
        current_index = 0
    elif current_type == "cogs":
        current_index = 1
    elif current_type == "gross_profit":
        current_index = 2
    elif current_type == "gross_margin":
        current_index = 3
    elif current_type == "sga":
        current_index = 4
    else:  # net_income
        current_index = 5
    
    selected_chart = st.selectbox(
        "Select chart type:",
        options=chart_options,
        index=current_index,
        key="income_chart_type_select"
    )
    
    # Update session state based on selection
    if selected_chart == "Total Revenue":
        st.session_state.income_chart_type = "revenue"
    elif selected_chart == "Total Cost of Sales":
        st.session_state.income_chart_type = "cogs"
    elif selected_chart == "Total Gross Profit":
        st.session_state.income_chart_type = "gross_profit"
    elif selected_chart == "Gross Margin":
        st.session_state.income_chart_type = "gross_margin"
    elif selected_chart == "Total SG&A Expenses":
        st.session_state.income_chart_type = "sga"
    else:  # Total Net Income
        st.session_state.income_chart_type = "net_income"

# Get current chart type (default to revenue)
chart_type = st.session_state.get("income_chart_type", "revenue")

# Prepare chart data based on selected year
if summary_period == "All Years":
    # For All Years, show yearly totals
    chart_data = {}
    years_dict = group_months_by_year(months)
    
    for year in sorted(years_dict.keys()):
        year_months = years_dict[year]
        if chart_type == "revenue":
            chart_data[str(year)] = sum(total_revenue.get(month, 0) for month in year_months)
        elif chart_type == "cogs":
            chart_data[str(year)] = sum(total_cost_of_sales.get(month, 0) for month in year_months)
        elif chart_type == "gross_profit":
            chart_data[str(year)] = sum(total_gross_profit.get(month, 0) for month in year_months)
        elif chart_type == "gross_margin":
            # Calculate gross margin percentage for the year
            year_revenue = sum(total_revenue.get(month, 0) for month in year_months)
            year_gross_profit = sum(total_gross_profit.get(month, 0) for month in year_months)
            chart_data[str(year)] = (year_gross_profit / year_revenue * 100) if year_revenue > 0 else 0
        elif chart_type == "sga":
            chart_data[str(year)] = sum(total_sga.get(month, 0) for month in year_months)
        else:  # net_income
            chart_data[str(year)] = sum(net_income.get(month, 0) for month in year_months)
    
    # Create DataFrame for chart
    chart_df = pd.DataFrame({
        'Period': list(chart_data.keys()),
        'Value': list(chart_data.values())
    })
    chart_title = f"{selected_chart} by Year"
    
else:
    # For specific year, show monthly data
    year_months = [month for month in months if summary_period in month]
    chart_data = {}
    
    # Create month labels (Jan, Feb, etc.)
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for month_name in month_names:
        # Find matching month in our data
        matching_month = None
        for month in year_months:
            if month.startswith(month_name):
                matching_month = month
                break
        
        if matching_month:
            if chart_type == "revenue":
                chart_data[month_name] = total_revenue.get(matching_month, 0)
            elif chart_type == "cogs":
                chart_data[month_name] = total_cost_of_sales.get(matching_month, 0)
            elif chart_type == "gross_profit":
                chart_data[month_name] = total_gross_profit.get(matching_month, 0)
            elif chart_type == "gross_margin":
                # Calculate gross margin percentage for the month
                month_revenue = total_revenue.get(matching_month, 0)
                month_gross_profit = total_gross_profit.get(matching_month, 0)
                chart_data[month_name] = (month_gross_profit / month_revenue * 100) if month_revenue > 0 else 0
            elif chart_type == "sga":
                chart_data[month_name] = total_sga.get(matching_month, 0)
            else:  # net_income
                chart_data[month_name] = net_income.get(matching_month, 0)
        else:
            chart_data[month_name] = 0
    
    # Create DataFrame for chart
    chart_df = pd.DataFrame({
        'Period': list(chart_data.keys()),
        'Value': list(chart_data.values())
    })
    chart_title = f"{selected_chart} - {summary_period}"

# Display the chart
if not chart_df.empty:
    # Create Plotly figure for cleaner appearance
    fig = go.Figure()
    
    # Set color based on chart type
    if chart_type == "revenue":
        color = '#00D084'  # Green for revenue
    elif chart_type == "cogs":
        color = '#dc3545'  # Red for costs  
    elif chart_type == "gross_profit":
        color = '#00B574'  # Dark green for gross profit
    elif chart_type == "gross_margin":
        color = '#3498DB'  # Blue for margin percentage
    elif chart_type == "sga":
        color = '#F39C12'  # Orange for SG&A expenses
    else:  # net_income
        # Use conditional coloring for net income
        colors = ['#00D084' if val >= 0 else '#dc3545' for val in chart_df['Value']]
        color = colors
    
    # Add bar trace
    fig.add_trace(go.Bar(
        x=chart_df['Period'],
        y=chart_df['Value'],
        marker_color=color,
        opacity=0.7,
        hovertemplate='<b>%{x}</b><br>' + ('$%{y:,.0f}' if chart_type != "gross_margin" else '%{y:.1f}%') + '<extra></extra>',
        showlegend=False
    ))
    
    # Update layout with clean styling
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color='#262730')
        ),
        xaxis=dict(
            title='',
            showgrid=False,
            tickangle=-45 if summary_period != "All Years" else 0
        ),
        yaxis=dict(
            title=('Percentage (%)' if chart_type == "gross_margin" else 'Amount ($)'),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickformat=('%.1f%%' if chart_type == "gross_margin" else '$,.0f')
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        height=350,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

# DATA MANAGEMENT
st.markdown("---")
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Auto-save revenue data silently
    try:
        calculate_all_revenue()
        save_revenue_calculations_to_database(st.session_state.model_data)
    except Exception as e:
        pass  # Silent error handling

with col2:
    # Auto-save income statement silently
    try:
        save_income_statement_to_database(st.session_state.model_data)
    except Exception as e:
        pass  # Silent error handling

with col3:
    # Auto-save all data silently
    try:
        save_all_to_supabase_enhanced(st.session_state.model_data)
    except Exception as e:
        pass  # Silent error handling

with col4:
    if st.button("📂 Load Data", type="primary", use_container_width=True):
        try:
            st.session_state.model_data = load_data_from_source()
            st.rerun()
        except Exception as e:
            pass  # Silent error handling

with st.expander("🔧 Advanced Options"):
    st.info("Additional data management tools available here")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🧹 Fix Categories", use_container_width=True):
            try:
                # Clean up cash disbursement categories
                success = clean_up_cash_disbursement_categories(st.session_state.model_data)
                if success:
                    st.success("✅ Categories cleaned up successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to clean up categories")
            except Exception as e:
                st.error(f"Cleanup error: {str(e)}")
    
    with col_b:
        if st.button("🔍 Validate Supabase Data", use_container_width=True):
            try:
                                  # Supabase validation now integrated in consolidated database.py
                  st.info("📊 Database validation integrated in consolidated database.py")
            except Exception as e:
                st.error(f"Validation error: {str(e)}")
    
    with col_c:
        if st.button("🌐 Supabase Info", use_container_width=True):
            try:
                # Supabase info now integrated in consolidated database.py
                show_supabase_access_info()
            except Exception as e:
                st.error(f"Info error: {str(e)}")

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; margin-top: 3rem; border-top: 1px solid #e0e0e0;">
    <strong>SHAED Financial Model - Income Statement</strong> | Powering the future of mobility<br>
    <small>© 2025 SHAED - All rights reserved</small>
</div>
""", unsafe_allow_html=True)

# Auto-save all data silently - no manual buttons needed
# Save Revenue Data
try:
    from database import save_revenue_calculations_to_database
    save_revenue_calculations_to_database(st.session_state.model_data)
except Exception as e:
    pass  # Silent error handling

# Save Income Statement  
try:
    from database import save_income_statement_to_database
    save_income_statement_to_database(st.session_state.model_data)
except Exception as e:
    pass  # Silent error handling

# Save All Data
try:
    save_data_to_source(st.session_state.model_data)
except Exception as e:
    pass  # Silent error handling