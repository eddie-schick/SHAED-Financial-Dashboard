import streamlit as st
import pandas as pd
from datetime import datetime, date
import time
import plotly.graph_objects as go
from database import (
    load_data,
    save_data,
    load_data_from_source,
    save_data_to_source,
    save_comprehensive_revenue_assumptions_to_database,
    load_revenue_assumptions_from_database,
    load_comprehensive_revenue_data_from_database,
    get_supabase_connection_info,
)

# Configure page
st.set_page_config(
    page_title="Revenue Assumptions",
    page_icon="💵",
    layout="wide"
)

# Data persistence functions are now imported from database.py

# Check authentication
if "password_correct" not in st.session_state or not st.session_state.get("password_correct", False):
    st.error("🔒 Please login from the Home page first.")
    st.stop()

# Add logout functionality to sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Logout", key="logout_button"):
        # Clear all session state variables
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Show Supabase connection status
    try:
        conn_info = get_supabase_connection_info()
    except Exception:
        conn_info = {"mode": "unknown"}
    status_text = f"DB: {'Configured' if conn_info.get('url_configured') else 'Not Configured'} | Mode: {conn_info.get('mode','').upper()}"
    st.caption(status_text)

if 'model_data' not in st.session_state:
    st.session_state.model_data = load_data_from_source()

# Ensure revenue assumptions are loaded from Supabase on first visit to this tab
if not st.session_state.get("revenue_data_initialized", False):
    try:
        db_revenue = load_revenue_assumptions_from_database()
        if isinstance(db_revenue, dict) and db_revenue:
            keys_to_merge = [
                'subscription_new_customers', 'subscription_pricing', 'subscription_churn_rates',
                'implementation_new_customers', 'implementation_pricing',
                'maintenance_new_customers', 'maintenance_pricing',
                'transactional_volume', 'transactional_price', 'transactional_referral_fee'
            ]
            for k in keys_to_merge:
                if k in db_revenue:
                    st.session_state.model_data[k] = db_revenue[k]
    except Exception:
        pass
    finally:
        st.session_state["revenue_data_initialized"] = True


# Custom CSS for SHAED branding
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
    
    /* Revenue badges */
    .revenue-badge {
        background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    /* Filter section */
    .filter-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #00D084;
        margin: 1rem 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    .filter-header {
        color: #00D084;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Custom table container with fixed first column */
    .fixed-table-container {
        display: flex;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        background-color: white;
        border: 1px solid #e0e0e0;
    }
    
    /* Fixed category column */
    .fixed-category-column {
        width: 200px;
        min-width: 200px;
        background-color: #f8f9fa;
        border-right: 3px solid #00D084;
        flex-shrink: 0;
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
    
    /* Scrollable data area */
    .scrollable-data {
        flex: 1;
        overflow-x: auto;
        overflow-y: hidden;
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
    
    /* Streamlit data_editor styling to match custom tables */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        background-color: white;
        border: 1px solid #e0e0e0;
    }
    
    /* Style the data editor table headers */
    .stDataFrame thead th {
        background-color: #f0f0f0 !important;
        color: #000 !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        text-align: center !important;
        border-bottom: 1px solid #ddd !important;
        border-right: 1px solid #e0e0e0 !important;
        height: 43px !important;
        line-height: 43px !important;
        padding: 0 4px !important;
        vertical-align: middle !important;
    }
    
    /* Special styling for year total columns in data editor */
    .stDataFrame thead th:contains("Total") {
        background-color: #f0f9f6 !important;
        border-right: 2px solid #00D084 !important;
        font-weight: 700 !important;
    }
    
    /* Style the data editor table cells */
    .stDataFrame tbody td {
        height: 43px !important;
        line-height: 43px !important;
        padding: 0 4px !important;
        font-size: 11px !important;
        border-bottom: 1px solid #e0e0e0 !important;
        border-right: 1px solid #e0e0e0 !important;
        vertical-align: middle !important;
    }
    
    /* First column (Stakeholder/Category) styling */
    .stDataFrame tbody td:first-child {
        background-color: #f8f9fa !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #000 !important;
        border-right: 3px solid #00D084 !important;
        width: 200px !important;
        min-width: 200px !important;
        text-align: left !important;
    }
    
    /* Numeric input cells */
    .stDataFrame tbody td:not(:first-child) {
        text-align: right !important;
        background-color: white !important;
    }
    
    /* Year total columns in data editor */
    .stDataFrame tbody td[data-column*="Total"] {
        background-color: #f0f9f6 !important;
        font-weight: 700 !important;
        border-right: 2px solid #00D084 !important;
        color: #00D084 !important;
    }
    
    /* Alternating row colors for data editor */
    .stDataFrame tbody tr:nth-child(even) td:not(:first-child):not([data-column*="Total"]) {
        background-color: #fafafa !important;
    }
    
    .stDataFrame tbody tr:nth-child(odd) td:not(:first-child):not([data-column*="Total"]) {
        background-color: white !important;
    }
    
    /* Input field styling within data editor */
    .stDataFrame input[type="number"] {
        width: 100% !important;
        height: 35px !important;
        border: none !important;
        background: transparent !important;
        font-size: 11px !important;
        text-align: right !important;
        padding: 0 4px !important;
        color: #000 !important;
    }
    
    .stDataFrame input[type="number"]:focus {
        outline: 2px solid #00D084 !important;
        background-color: #f0f9f6 !important;
        border-radius: 4px !important;
    }
    
    /* Remove default Streamlit table styling */
    .stDataFrame table {
        border-collapse: collapse !important;
        border-spacing: 0 !important;
    }
    
    /* Header row styling */
    .stDataFrame thead tr {
        height: 43px !important;
        line-height: 43px !important;
    }
    
    /* Data row styling */
    .stDataFrame tbody tr {
        height: 43px !important;
        line-height: 43px !important;
    }
    
    /* Override any default padding/margins */
    .stDataFrame * {
        box-sizing: border-box !important;
    }
    
    /* More specific Streamlit data_editor styling */
    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        background-color: white;
        border: 1px solid #e0e0e0;
    }
    
    /* Data editor table styling */
    div[data-testid="stDataFrame"] table {
        border-collapse: collapse !important;
        border-spacing: 0 !important;
        width: 100% !important;
    }
    
    /* Header cells in data editor */
    div[data-testid="stDataFrame"] th {
        background-color: #f0f0f0 !important;
        color: #000 !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        text-align: center !important;
        border-bottom: 1px solid #ddd !important;
        border-right: 1px solid #e0e0e0 !important;
        height: 43px !important;
        line-height: 43px !important;
        padding: 0 4px !important;
        vertical-align: middle !important;
    }
    
    /* Data cells in data editor */
    div[data-testid="stDataFrame"] td {
        height: 43px !important;
        line-height: 43px !important;
        padding: 0 4px !important;
        font-size: 11px !important;
        border-bottom: 1px solid #e0e0e0 !important;
        border-right: 1px solid #e0e0e0 !important;
        vertical-align: middle !important;
        text-align: right !important;
    }
    
    /* First column styling */
    div[data-testid="stDataFrame"] td:first-child {
        background-color: #f8f9fa !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #000 !important;
        border-right: 3px solid #00D084 !important;
        text-align: left !important;
    }
    
    /* Input fields in data editor */
    div[data-testid="stDataFrame"] input {
        width: 100% !important;
        height: 35px !important;
        border: none !important;
        background: transparent !important;
        font-size: 11px !important;
        text-align: right !important;
        padding: 0 4px !important;
        color: #000 !important;
    }
    
    div[data-testid="stDataFrame"] input:focus {
        outline: 2px solid #00D084 !important;
        background-color: #f0f9f6 !important;
        border-radius: 4px !important;
    }
    
    /* Alternating row colors */
    div[data-testid="stDataFrame"] tr:nth-child(even) td:not(:first-child) {
        background-color: #fafafa !important;
    }
    
    div[data-testid="stDataFrame"] tr:nth-child(odd) td:not(:first-child) {
        background-color: white !important;
    }

</style>
""", unsafe_allow_html=True)

# Generate months from 2025-2030
def get_months_2025_2030():
    months = []
    for year in range(2025, 2031):
        for month in range(1, 13):
            months.append(f"{date(year, month, 1).strftime('%b %Y')}")
    return months

months = get_months_2025_2030()

# Helper functions
def get_year_from_month(month_str):
    return month_str.split(' ')[1]

def group_months_by_year(months):
    years = {}
    for month in months:
        year = get_year_from_month(month)
        if year not in years:
            years[year] = []
        years[year].append(month)
    return years

def format_number(num):
    if num == 0:
        return "0"
    return f"{num:,.0f}"

# Stakeholder list (first 21 business segments from Supabase)
stakeholders = [
    "Dealership", "End User", "Equipment Manufacturer", "Upfitter",
    "Depot", "Fleet Management Company", "Logistics", "OEM",
    "Traditional Finance Provider", "Channel Partner", "Charging OEM", "Insurance Provider",
    "Maintenance Provider", "Charging as a Service", "EPC", "Government Agency",
    "Grant Administrator", "Operating and Maintenance Provider", "Remarketing Specialists", "Technology Solutions",
    "Utility Provider"
]

# Transactional revenue categories
transactional_categories = ["Charging", "Vehicle", "Financing", "Other Revenue"]

# Helper function to create custom cumulative subscribers table with fixed category column
def create_custom_cumulative_subscribers_table(stakeholders, show_monthly=True):
    """Create custom table for cumulative subscribers with fixed category column"""
    
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
    html_content += '<div class="category-header">Stakeholder</div>'
    
    for stakeholder in stakeholders:
        html_content += f'<div class="category-cell">{stakeholder}</div>'
    
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
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data rows
    html_content += '<tbody>'
    for stakeholder in stakeholders:
        html_content += '<tr style="height: 43px !important;">'
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                year_end_value = 0
                for month in years_dict[year]:
                    value = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(month, 0)
                    # Format as whole number without decimals
                    formatted_value = str(int(round(value)))
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                    year_end_value = value  # Keep the last value of the year
                
                # Year total shows end-of-year value
                year_total_formatted = f"<strong>{int(round(year_end_value))} (EOY)</strong>"
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{year_total_formatted}</td>'
        else:
            for year in sorted(years_dict.keys()):
                # Get the last month of the year for end-of-year value
                last_month = years_dict[year][-1]
                year_end_value = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(last_month, 0)
                year_total_formatted = f"<strong>{int(round(year_end_value))} (EOY)</strong>"
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{year_total_formatted}</td>'
        
        html_content += '</tr>'
    
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create custom tables with fixed category column (matching financial_model.py)
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
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{col}</th>'
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
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{format_number(value)}</td>'
                    yearly_total += value
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
        else:
            for year in sorted(years_dict.keys()):
                yearly_total = sum(
                    st.session_state.model_data[data_key].get(category, {}).get(month, 0)
                    for month in years_dict[year]
                )
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
        
        html_content += '</tr>'
    
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create total row with fixed category column
def create_custom_total_row(total_dict, row_label, show_monthly=True):
    """Create a total row with fixed category column"""
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
            yearly_total = 0
            for month in years_dict[year]:
                value = total_dict.get(month, 0)
                html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{format_number(value)}</td>'
                yearly_total += value
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
    else:
        for year in sorted(years_dict.keys()):
            yearly_total = sum(total_dict.get(month, 0) for month in years_dict[year])
            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
    
    html_content += '</tr></tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create custom table with special total row formatting
def create_custom_table_with_totals(categories, data_key, show_monthly=True):
    """Create custom table with special formatting for Total rows"""
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
    for category in categories:
        # Apply special styling to Total rows
        if category.startswith("Total"):
            html_content += f'<div class="category-total">{category}</div>'
        else:
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
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data rows
    html_content += '<tbody>'
    for category in categories:
        # Apply total-row class to Total rows
        row_class = "total-row" if category.startswith("Total") else ""
        html_content += f'<tr class="{row_class}" style="height: 43px !important;">'
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    # Handle special case for "Total Revenue" calculation
                    if category == "Total Revenue":
                        # Calculate total revenue for this month
                        revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
                        value = sum(
                            st.session_state.model_data.get(data_key, {}).get(cat, {}).get(month, 0) 
                            for cat in revenue_categories
                        )
                    else:
                        value = st.session_state.model_data.get(data_key, {}).get(category, {}).get(month, 0)
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{format_number(value)}</td>'
                    yearly_total += value
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
        else:
            for year in sorted(years_dict.keys()):
                if category == "Total Revenue":
                    # Calculate total revenue for this year
                    revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
                    yearly_total = sum(
                        st.session_state.model_data.get(data_key, {}).get(cat, {}).get(month, 0)
                        for cat in revenue_categories
                        for month in years_dict[year]
                    )
                else:
                    yearly_total = sum(
                        st.session_state.model_data.get(data_key, {}).get(category, {}).get(month, 0)
                        for month in years_dict[year]
                    )
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
        
        html_content += '</tr>'
    
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create editable stakeholder tables
def create_stakeholder_table_with_years(metric_name, data_key, filtered_stakeholders, default_value=0.0, format_type="number", show_monthly=True):
    # Initialize data if not exists
    if data_key not in st.session_state.model_data:
        st.session_state.model_data[data_key] = {}
    
    # Ensure all stakeholders are initialized (preserve existing data)
    for stakeholder in filtered_stakeholders:
        if stakeholder not in st.session_state.model_data[data_key]:
            st.session_state.model_data[data_key][stakeholder] = {}
        
        # Only add missing months, don't overwrite existing data
        for month in months:
            if month not in st.session_state.model_data[data_key][stakeholder]:
                st.session_state.model_data[data_key][stakeholder][month] = default_value
    
    # Group months by year
    years_dict = group_months_by_year(months)
    
    # Create columns list based on view preference
    if show_monthly:
        columns = ["Stakeholder"]
        for year in sorted(years_dict.keys()):
            columns.extend(years_dict[year])
            columns.append(f"{year} Total")
    else:
        columns = ["Stakeholder"] + [f"{year} Total" for year in sorted(years_dict.keys())]
    
    # Create data for display
    table_data = []
    for stakeholder in filtered_stakeholders:
        row = {"Stakeholder": stakeholder}
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    value = st.session_state.model_data[data_key].get(stakeholder, {}).get(month, default_value)
                    row[month] = value
                    yearly_total += value
                # Format yearly total - use average for pricing and percentages
                if format_type == "currency":
                    yearly_avg = yearly_total / len(years_dict[year])
                    row[f"{year} Total"] = f"**${yearly_avg:,.0f} (Avg)**"
                elif format_type == "percentage":
                    yearly_avg = yearly_total / len(years_dict[year])
                    row[f"{year} Total"] = f"**{yearly_avg:.1f}% (Avg)**"
                else:
                    row[f"{year} Total"] = f"**{yearly_total:,.0f}**"
        else:
            for year in sorted(years_dict.keys()):
                yearly_total = sum(
                    st.session_state.model_data[data_key].get(stakeholder, {}).get(month, default_value)
                    for month in years_dict[year]
                )
                # Format yearly total - use average for pricing and percentages
                if format_type == "currency":
                    yearly_avg = yearly_total / len(years_dict[year])
                    row[f"{year} Total"] = f"**${yearly_avg:,.0f} (Avg)**"
                elif format_type == "percentage":
                    yearly_avg = yearly_total / len(years_dict[year])
                    row[f"{year} Total"] = f"**{yearly_avg:.1f}% (Avg)**"
                else:
                    row[f"{year} Total"] = f"**{yearly_total:,.0f}**"
        
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Create column config matching liquidity model configuration
    if show_monthly:
        column_config = {
            "Stakeholder": st.column_config.TextColumn("Stakeholder", disabled=True, width="medium", pinned=True),
        }
        for col in columns[1:]:
            if "Total" in col:
                column_config[col] = st.column_config.TextColumn(col, disabled=True)
            else:
                column_config[col] = st.column_config.NumberColumn(col)
    else:
        column_config = {
            "Stakeholder": st.column_config.TextColumn("Stakeholder", disabled=True, width="medium", pinned=True),
            **{col: st.column_config.TextColumn(col, disabled=True) for col in columns[1:]}
        }
    
    # Display editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        height=len(filtered_stakeholders) * 35 + 50,
        column_config=column_config,
        hide_index=True,
        column_order=["Stakeholder"] + [col for col in columns[1:]],
        key=f"stakeholder_table_{data_key}"
    )
    
    # Force black text with JavaScript
    st.markdown("""
    <script>
    setTimeout(function() {
        const dataFrames = document.querySelectorAll('[data-testid="stDataFrame"]');
        dataFrames.forEach(function(df) {
            const allElements = df.querySelectorAll('*');
            allElements.forEach(function(el) {
                el.style.color = '#000000 !important';
            });
        });
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    
    # Update session state and check for changes
    changes_made = False
    for i, stakeholder in enumerate(filtered_stakeholders):
        if stakeholder not in st.session_state.model_data[data_key]:
            st.session_state.model_data[data_key][stakeholder] = {}
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    if month in edited_df.columns:
                        value = edited_df.iloc[i][month]
                        new_value = float(value) if value != '' else default_value
                        old_value = st.session_state.model_data[data_key][stakeholder].get(month, default_value)
                        
                        if old_value != new_value:
                            changes_made = True
                            st.session_state.model_data[data_key][stakeholder][month] = new_value
    
    # Save to database immediately if changes were made
    if changes_made:
        try:
            # Recalculate revenue if this affects revenue calculations
            if data_key in ['subscription_new_customers', 'subscription_pricing', 'subscription_churn_rates',
                           'implementation_new_customers', 'implementation_pricing',
                           'maintenance_new_customers', 'maintenance_pricing']:
                calculate_all_revenue()
            
            # Auto-save all revenue assumptions and calculations to database
            success = save_comprehensive_revenue_assumptions_to_database(st.session_state.model_data)
            if success:
                # Clear cache to ensure fresh data on next load
                load_revenue_assumptions_from_database.clear()
                load_comprehensive_revenue_data_from_database.clear()
            else:
                st.error("⚠️ Failed to save data. Please try again or refresh the page.")
        except Exception as e:
            st.error(f"❌ Error saving data: {str(e)}")
    
    return edited_df

# Helper function for transactional tables
def create_transactional_table_with_years(metric_name, data_key, default_value=0.0, format_type="number", show_monthly=True):
    # Initialize data if not exists
    if data_key not in st.session_state.model_data:
        st.session_state.model_data[data_key] = {}
    
    # Ensure all categories are initialized (preserve existing data)
    for category in transactional_categories:
        if category not in st.session_state.model_data[data_key]:
            st.session_state.model_data[data_key][category] = {}
        
        # Only add missing months, don't overwrite existing data
        for month in months:
            if month not in st.session_state.model_data[data_key][category]:
                st.session_state.model_data[data_key][category][month] = default_value
    
    # Group months by year
    years_dict = group_months_by_year(months)
    
    # Create columns list
    if show_monthly:
        columns = ["Category"]
        for year in sorted(years_dict.keys()):
            columns.extend(years_dict[year])
            columns.append(f"{year} Total")
    else:
        columns = ["Category"] + [f"{year} Total" for year in sorted(years_dict.keys())]
    
    # Create data for display
    table_data = []
    for category in transactional_categories:
        row = {"Category": category}
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    value = st.session_state.model_data[data_key].get(category, {}).get(month, default_value)
                    row[month] = value
                    yearly_total += value
                # Format yearly total - use average for pricing and percentages
                if format_type == "currency":
                    yearly_avg = yearly_total / len(years_dict[year])
                    row[f"{year} Total"] = f"**${yearly_avg:,.0f} (Avg)**"
                elif format_type == "percentage":
                    yearly_avg = yearly_total / len(years_dict[year])
                    row[f"{year} Total"] = f"**{yearly_avg:.1f}% (Avg)**"
                else:
                    row[f"{year} Total"] = f"**{yearly_total:,.0f}**"
        else:
            for year in sorted(years_dict.keys()):
                yearly_total = sum(
                    st.session_state.model_data[data_key].get(category, {}).get(month, default_value)
                    for month in years_dict[year]
                )
                # Format yearly total - use average for pricing and percentages
                if format_type == "currency":
                    yearly_avg = yearly_total / len(years_dict[year])
                    row[f"{year} Total"] = f"**${yearly_avg:,.0f} (Avg)**"
                elif format_type == "percentage":
                    yearly_avg = yearly_total / len(years_dict[year])
                    row[f"{year} Total"] = f"**{yearly_avg:.1f}% (Avg)**"
                else:
                    row[f"{year} Total"] = f"**{yearly_total:,.0f}**"
        
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Create column config matching liquidity model configuration
    if show_monthly:
        column_config = {
            "Category": st.column_config.TextColumn("Category", disabled=True, width="medium", pinned=True),
        }
        for col in columns[1:]:
            if "Total" in col:
                column_config[col] = st.column_config.TextColumn(col, disabled=True)
            else:
                column_config[col] = st.column_config.NumberColumn(col)
    else:
        column_config = {
            "Category": st.column_config.TextColumn("Category", disabled=True, width="medium", pinned=True),
            **{col: st.column_config.TextColumn(col, disabled=True) for col in columns[1:]}
        }
    
    # Display editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        height=len(transactional_categories) * 35 + 50,
        column_config=column_config,
        hide_index=True,
        column_order=["Category"] + [col for col in columns[1:]],
        key=f"transactional_table_{data_key}"
    )
    
    # Update session state and check for changes
    changes_made = False
    for i, category in enumerate(transactional_categories):
        if category not in st.session_state.model_data[data_key]:
            st.session_state.model_data[data_key][category] = {}
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    if month in edited_df.columns:
                        value = edited_df.iloc[i][month]
                        new_value = float(value) if value != '' else default_value
                        old_value = st.session_state.model_data[data_key][category].get(month, default_value)
                        
                        if old_value != new_value:
                            changes_made = True
                            st.session_state.model_data[data_key][category][month] = new_value
    
    # Save to database immediately if changes were made
    if changes_made:
        try:
            # Recalculate revenue if this affects revenue calculations
            if data_key in ['transactional_volume', 'transactional_price', 'transactional_referral_fee']:
                calculate_all_revenue()
            
            # Save all revenue assumptions and calculations to database
            try:
                from database import save_revenue_assumptions_to_database, save_revenue_calculations_to_database
                
                revenue_assumptions_success = save_revenue_assumptions_to_database(st.session_state.model_data)
                revenue_calculations_success = save_revenue_calculations_to_database(st.session_state.model_data)
                
                if revenue_assumptions_success or revenue_calculations_success:
                    # Clear cache to ensure fresh data on next load
                    load_revenue_assumptions_from_database.clear()
                    load_comprehensive_revenue_data_from_database.clear()
                
                # For transaction volume, the key data (customer assumptions) is saved successfully
                # Revenue calculations are secondary and shouldn't fail the entire save
                if data_key == 'transactional_volume':
                    success = revenue_assumptions_success  # Only require assumptions to succeed
                    if success:
                        st.success(f"✅ {metric_name} data successfully saved to database!")
                    else:
                        st.error(f"❌ Failed to save {metric_name} data to database")
                else:
                    success = revenue_assumptions_success and revenue_calculations_success
                    if success:
                        st.success(f"✅ {metric_name} data successfully saved to database!")
                    else:
                        st.error(f"❌ Failed to save {metric_name} data to database")
                        st.error(f"Revenue assumptions: {revenue_assumptions_success}, Revenue calculations: {revenue_calculations_success}")
                    
            except Exception as save_e:
                st.error(f"Error during save process: {str(save_e)}")
                success = False
        except Exception as e:
            st.error(f"❌ Error saving {metric_name} data: {str(e)}")
    
    return edited_df

# Calculate subscription running totals
def calculate_subscription_running_totals():
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

# Calculate all revenue streams
def calculate_all_revenue():
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

# Header with SHAED branding
st.markdown("""
<div class="main-header">
    <h1>💵 Revenue Assumptions</h1>
</div>
""", unsafe_allow_html=True)

# View mode and stakeholder filter controls
view_col1, view_col2, view_col3, view_col4 = st.columns([0.75, 0.05, 0.75, 2.45])
with view_col1:
    view_mode = st.selectbox(
        "View Mode:",
        ["Monthly + Yearly", "Yearly Only"],
        key="view_mode_all_revenue"
    )

with view_col3:
    stakeholder_options = ["All Stakeholders"] + stakeholders
    selected_stakeholder = st.selectbox(
        "Stakeholder:",
        stakeholder_options,
        key="stakeholder_filter_all_revenue"
    )

show_monthly = view_mode == "Monthly + Yearly"

# Determine filtered stakeholders based on selection
if selected_stakeholder == "All Stakeholders":
    filtered_stakeholders = stakeholders.copy()
else:
    filtered_stakeholders = [selected_stakeholder]

# REVENUE ASSUMPTIONS TABS
st.markdown('<div class="section-header">💼 Revenue Assumptions</div>', unsafe_allow_html=True)

# Create tabs for different revenue streams
tab1, tab2, tab3, tab4 = st.tabs(["📋 Subscription", "🔄 Transactional", "🚀 Implementation", "🔧 Maintenance"])

with tab1:
    if len(filtered_stakeholders) > 0:
        with st.expander("📈 New Customers", expanded=False):
            create_stakeholder_table_with_years("New Subscription Customers", "subscription_new_customers", filtered_stakeholders, default_value=0.0, format_type="number", show_monthly=show_monthly)
        
        with st.expander("💵 Monthly Subscription Price", expanded=False):
            create_stakeholder_table_with_years("Subscription Pricing", "subscription_pricing", filtered_stakeholders, default_value=0.0, format_type="currency", show_monthly=show_monthly)
        
        with st.expander("📉 Monthly Churn Rates (%)", expanded=False):
            create_stakeholder_table_with_years("Churn Rates", "subscription_churn_rates", filtered_stakeholders, default_value=0.0, format_type="percentage", show_monthly=show_monthly)
        
        # Calculate and display running totals (this will recalculate every time the page refreshes)
        calculate_subscription_running_totals()
        
        with st.expander("📊 Cumulative Active Subscribers", expanded=False):
            st.info("💡 This shows the running total of active subscribers after applying churn each month. Updates automatically as you change values above.")
            
            # Create read-only table for running totals using custom HTML format
            if "subscription_running_totals" in st.session_state.model_data:
                create_custom_cumulative_subscribers_table(filtered_stakeholders, show_monthly)
        
    else:
        st.warning("⚠️ No stakeholders selected. Please choose stakeholders from the filter above.")

with tab2:
    with st.expander("📊 Transaction Volume", expanded=False):
        create_transactional_table_with_years("Transaction Volume", "transactional_volume", default_value=0.0, format_type="number", show_monthly=show_monthly)
    
    with st.expander("💰 Average Price Per Transaction", expanded=False):
        create_transactional_table_with_years("Price Per Transaction", "transactional_price", default_value=0.0, format_type="currency", show_monthly=show_monthly)
    
    with st.expander("🎯 Referral Fee (%)", expanded=False):
        create_transactional_table_with_years("Referral Fee %", "transactional_referral_fee", default_value=0.0, format_type="percentage", show_monthly=show_monthly)

with tab3:
    if len(filtered_stakeholders) > 0:
        with st.expander("🆕 Implementation Engagements", expanded=False):
            create_stakeholder_table_with_years("New Implementations", "implementation_new_customers", filtered_stakeholders, default_value=0.0, format_type="number", show_monthly=show_monthly)
        
        with st.expander("💵 Implementation Fee", expanded=False):
            create_stakeholder_table_with_years("Implementation Fees", "implementation_pricing", filtered_stakeholders, default_value=0.0, format_type="currency", show_monthly=show_monthly)
        
    else:
        st.warning("⚠️ No stakeholders selected. Please choose stakeholders from the filter above.")

with tab4:
    if len(filtered_stakeholders) > 0:
        with st.expander("🔧 Total Maintenance Contracts Per Month", expanded=False):
            create_stakeholder_table_with_years("New Maintenance", "maintenance_new_customers", filtered_stakeholders, default_value=0.0, format_type="number", show_monthly=show_monthly)
        
        with st.expander("💵 Maintenance Fee Per Contract", expanded=False):
            create_stakeholder_table_with_years("Maintenance Fees", "maintenance_pricing", filtered_stakeholders, default_value=0.0, format_type="currency", show_monthly=show_monthly)
        
    else:
        st.warning("⚠️ No stakeholders selected. Please choose stakeholders from the filter above.")

# BULK EDIT SECTION
st.markdown("---")
st.markdown('<div class="section-header">✏️ Bulk Edit</div>', unsafe_allow_html=True)

with st.expander("✏️ Bulk Edit Revenue Assumptions", expanded=False):
    # Revenue stream selection
    bulk_edit_col1, bulk_edit_col2 = st.columns(2)

    with bulk_edit_col1:
        selected_revenue_streams = st.multiselect(
            "Select Revenue Streams:",
            options=["Subscription", "Transactional", "Implementation", "Maintenance"],
            default=[],
            key="bulk_edit_streams"
        )

    with bulk_edit_col2:
        # Dynamic assumption types based on selected streams
        assumption_options = []
        if "Subscription" in selected_revenue_streams:
            assumption_options.extend(["New Customers", "Monthly Pricing", "Churn Rates"])
        if "Transactional" in selected_revenue_streams:
            assumption_options.extend(["Transaction Volume", "Price per Transaction", "Referral Fee %"])
        if "Implementation" in selected_revenue_streams:
            assumption_options.extend(["Implementation Engagements", "Implementation Fees"])
        if "Maintenance" in selected_revenue_streams:
            assumption_options.extend(["Maintenance Contracts", "Maintenance Fees"])
        
        selected_assumptions = st.multiselect(
            "Select Assumption Types:",
            options=assumption_options,
            key="bulk_edit_assumptions"
        )

    # Stakeholder/Category selection
    bulk_stakeholder_col1, bulk_stakeholder_col2 = st.columns(2)

    with bulk_stakeholder_col1:
        # For transactional, show categories; for others, show stakeholders
        if "Transactional" in selected_revenue_streams:
            entity_options = ["Charging", "Vehicle", "Financing", "Other Revenue"]
            entity_label = "Category"
        else:
            entity_options = stakeholders
            entity_label = "Category"
        
        selected_entities = st.multiselect(
            f"Select {entity_label}:",
            options=entity_options,
            default=[],  # Default to blank
            key="bulk_edit_entities"
        )

    with bulk_stakeholder_col2:
        # Month range selection
        bulk_start_month = st.selectbox(
            "Start Month:",
            options=months,
            index=0,
            key="bulk_edit_start_month"
        )
        
        bulk_end_month = st.selectbox(
            "End Month:",
            options=months,
            index=min(11, len(months)-1),
            key="bulk_edit_end_month"
        )

    # Filter months for the selected range
    bulk_start_idx = months.index(bulk_start_month)
    bulk_end_idx = months.index(bulk_end_month)
    if bulk_start_idx <= bulk_end_idx:
        bulk_selected_months = months[bulk_start_idx:bulk_end_idx+1]
    else:
        st.error("❌ End month must be after start month")
        bulk_selected_months = []

    if bulk_selected_months and selected_assumptions and selected_entities:
        
        # Value input and operation selection
        bulk_value_col1, bulk_value_col2, bulk_value_col3 = st.columns(3)
        
        with bulk_value_col1:
            bulk_operation = st.selectbox(
                "Operation:",
                options=["Set Value", "Add to Existing", "Multiply by Factor", "Percentage Change"],
                key="bulk_operation"
            )
        
        with bulk_value_col2:
            bulk_value = st.number_input(
                "Value:" if bulk_operation == "Set Value" else
                "Amount to Add:" if bulk_operation == "Add to Existing" else
                "Multiplication Factor:" if bulk_operation == "Multiply by Factor" else
                "Percentage Change (%):",
                value=0.0,
                key="bulk_edit_value"
            )
        
        with bulk_value_col3:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if st.button("🔄 Preview Changes", use_container_width=True):
                st.session_state.show_bulk_preview = True
            
        # Preview changes
        if st.session_state.get('show_bulk_preview', False):
            st.markdown("### 👁️ Preview Changes")
            
            preview_data = []
            for assumption in selected_assumptions:
                # Map assumption to data key
                data_key = None
                if assumption == "New Customers":
                    data_key = "subscription_new_customers"
                elif assumption == "Monthly Pricing":
                    data_key = "subscription_pricing"
                elif assumption == "Churn Rates":
                    data_key = "subscription_churn_rates"
                elif assumption == "Transaction Volume":
                    data_key = "transactional_volume"
                elif assumption == "Price per Transaction":
                    data_key = "transactional_price"
                elif assumption == "Referral Fee %":
                    data_key = "transactional_referral_fee"
                elif assumption == "Implementation Engagements":
                    data_key = "implementation_new_customers"
                elif assumption == "Implementation Fees":
                    data_key = "implementation_pricing"
                elif assumption == "Maintenance Contracts":
                    data_key = "maintenance_new_customers"
                elif assumption == "Maintenance Fees":
                    data_key = "maintenance_pricing"
                
                if data_key:
                    for entity in selected_entities:
                        for month in bulk_selected_months[:6]:  # Show first 6 months only for preview
                            current_value = st.session_state.model_data.get(data_key, {}).get(entity, {}).get(month, 0)
                            
                            if bulk_operation == "Set Value":
                                new_value = bulk_value
                            elif bulk_operation == "Add to Existing":
                                new_value = current_value + bulk_value
                            elif bulk_operation == "Multiply by Factor":
                                new_value = current_value * bulk_value
                            elif bulk_operation == "Percentage Change":
                                new_value = current_value * (1 + bulk_value / 100)
                            
                            preview_data.append({
                                "Assumption": assumption,
                                "Entity": entity,
                                "Month": month,
                                "Current Value": f"{current_value:,.2f}",
                                "New Value": f"{new_value:,.2f}",
                                "Change": f"{new_value - current_value:+,.2f}"
                            })
            
            if preview_data:
                preview_df = pd.DataFrame(preview_data)
                st.dataframe(preview_df, use_container_width=True, height=300)
                
                if len(bulk_selected_months) > 6:
                    st.info(f"📝 Preview shows first 6 months. Changes will be applied to all {len(bulk_selected_months)} selected months.")
                
                # Apply changes button
                bulk_apply_col1, bulk_apply_col2 = st.columns([1, 1])
                with bulk_apply_col1:
                    if st.button("✅ Apply Changes", type="primary", use_container_width=True):
                        try:
                            changes_made = 0
                            
                            for assumption in selected_assumptions:
                                # Map assumption to data key
                                data_key = None
                                if assumption == "New Customers":
                                    data_key = "subscription_new_customers"
                                elif assumption == "Monthly Pricing":
                                    data_key = "subscription_pricing"
                                elif assumption == "Churn Rates":
                                    data_key = "subscription_churn_rates"
                                elif assumption == "Transaction Volume":
                                    data_key = "transactional_volume"
                                elif assumption == "Price per Transaction":
                                    data_key = "transactional_price"
                                elif assumption == "Referral Fee %":
                                    data_key = "transactional_referral_fee"
                                elif assumption == "Implementation Engagements":
                                    data_key = "implementation_new_customers"
                                elif assumption == "Implementation Fees":
                                    data_key = "implementation_pricing"
                                elif assumption == "Maintenance Contracts":
                                    data_key = "maintenance_new_customers"
                                elif assumption == "Maintenance Fees":
                                    data_key = "maintenance_pricing"
                                
                                if data_key:
                                    # Initialize data structure if needed
                                    if data_key not in st.session_state.model_data:
                                        st.session_state.model_data[data_key] = {}
                                    
                                    for entity in selected_entities:
                                        if entity not in st.session_state.model_data[data_key]:
                                            st.session_state.model_data[data_key][entity] = {}
                                        
                                        for month in bulk_selected_months:
                                            current_value = st.session_state.model_data[data_key][entity].get(month, 0)
                                            
                                            if bulk_operation == "Set Value":
                                                new_value = bulk_value
                                            elif bulk_operation == "Add to Existing":
                                                new_value = current_value + bulk_value
                                            elif bulk_operation == "Multiply by Factor":
                                                new_value = current_value * bulk_value
                                            elif bulk_operation == "Percentage Change":
                                                new_value = current_value * (1 + bulk_value / 100)
                                            
                                            st.session_state.model_data[data_key][entity][month] = new_value
                                            changes_made += 1
                            
                            # Recalculate revenue
                            calculate_all_revenue()
                            
                            # Save to database
                            success = save_comprehensive_revenue_assumptions_to_database(st.session_state.model_data)
                            
                            if success:
                                # Clear cache to ensure fresh data on next load
                                load_revenue_assumptions_from_database.clear()
                                load_comprehensive_revenue_data_from_database.clear()
                                st.success(f"✅ Successfully applied {changes_made} changes!")
                            else:
                                st.error("⚠️ Failed to save changes. Please try again.")
                            st.session_state.show_bulk_preview = False
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error applying bulk changes: {str(e)}")
                
                with bulk_apply_col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_bulk_preview = False
                        st.rerun()

# REVENUE SUMMARY SECTION
st.markdown("---")
st.markdown('<div class="section-header">💰 Revenue Summary & Totals</div>', unsafe_allow_html=True)

# Ensure we have the latest revenue calculations
calculate_all_revenue()

# Show summary by revenue stream using combined table with special total formatting
revenue_categories_with_total = ["Subscription", "Transactional", "Implementation", "Maintenance", "Total Revenue"]
create_custom_table_with_totals(revenue_categories_with_total, "revenue", show_monthly)

# MONTHLY SUMMARY SECTION
st.markdown("---")
st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)

# Time period and revenue stream selector for summary metrics
years_dict = group_months_by_year(months)
metrics_options = ["All Years"] + sorted(years_dict.keys())

# Get current year for default selection (default to first model year)
if len(years_dict) > 0:
    # Use the first year in the model (2025)
    first_model_year = sorted(years_dict.keys())[0]
    try:
        default_metrics_index = metrics_options.index(first_model_year)
    except ValueError:
        # If first model year not found, fallback to first year option (skip "All Years")
        default_metrics_index = 1 if len(metrics_options) > 1 else 0
else:
    # Fallback if no years defined
    default_metrics_index = 0

# Revenue stream filter options
stream_options = [
    "Subscription",
    "Transactional", 
    "Implementation",
    "Maintenance"
]

metrics_col1, metrics_col2, metrics_col3 = st.columns([0.75, 0.75, 2.5])
with metrics_col1:
    metrics_period = st.selectbox(
        "Select time period for metrics:",
        options=metrics_options,
        index=default_metrics_index,
        key="revenue_metrics_period_select"
    )

with metrics_col2:
    stream_options = ["All Streams", "Subscription", "Transactional", "Implementation", "Maintenance"]
    selected_stream = st.selectbox(
        "Select revenue stream:",
        options=stream_options,
        index=0,
        key="revenue_stream_filter_select_metrics"
    )

# Determine which months to include based on selection
if metrics_period == "All Years":
    filtered_months = months
else:
    filtered_months = [month for month in months if metrics_period in month]

# Calculate summary metrics for selected period
subscription_revenue_period = sum(st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0) for month in filtered_months)
transactional_revenue_period = sum(st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0) for month in filtered_months)
implementation_revenue_period = sum(st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0) for month in filtered_months)
maintenance_revenue_period = sum(st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0) for month in filtered_months)
total_revenue_period = subscription_revenue_period + transactional_revenue_period + implementation_revenue_period + maintenance_revenue_period

# Add KPI cards for All Streams view
if selected_stream == "All Streams":
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display KPI cards in a row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 4px; height: 20px; background-color: #00D084; margin-right: 8px; border-radius: 2px;"></div>
                    <span style="color: #00D084; font-weight: 600; font-size: 0.9rem;">💳 Subscription</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #262730;">${subscription_revenue_period:,.0f}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with kpi_col2:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 4px; height: 20px; background-color: #3498DB; margin-right: 8px; border-radius: 2px;"></div>
                    <span style="color: #3498DB; font-weight: 600; font-size: 0.9rem;">🚀 Implementation</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #262730;">${implementation_revenue_period:,.0f}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with kpi_col3:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 4px; height: 20px; background-color: #F39C12; margin-right: 8px; border-radius: 2px;"></div>
                    <span style="color: #F39C12; font-weight: 600; font-size: 0.9rem;">💰 Transactional</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #262730;">${transactional_revenue_period:,.0f}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with kpi_col4:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 4px; height: 20px; background-color: #9B59B6; margin-right: 8px; border-radius: 2px;"></div>
                    <span style="color: #9B59B6; font-weight: 600; font-size: 0.9rem;">🔧 Maintenance</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #262730;">${maintenance_revenue_period:,.0f}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)

# Calculate customer metrics
total_new_subscribers_period = 0
total_implementation_engagements_period = 0
total_maintenance_engagements_period = 0

for stakeholder in stakeholders:
    total_new_subscribers_period += sum(st.session_state.model_data.get("subscription_new_customers", {}).get(stakeholder, {}).get(month, 0) for month in filtered_months)
    total_implementation_engagements_period += sum(st.session_state.model_data.get("implementation_new_customers", {}).get(stakeholder, {}).get(month, 0) for month in filtered_months)
    total_maintenance_engagements_period += sum(st.session_state.model_data.get("maintenance_new_customers", {}).get(stakeholder, {}).get(month, 0) for month in filtered_months)

# Get ending cumulative subscribers for the period
if filtered_months:
    ending_cumulative_subscribers = 0
    for stakeholder in stakeholders:
        ending_cumulative_subscribers += st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(filtered_months[-1], 0)
else:
    ending_cumulative_subscribers = 0

# Calculate total transaction volume for the period
total_transaction_volume_period = 0
for category in transactional_categories:
    total_transaction_volume_period += sum(st.session_state.model_data.get("transactional_volume", {}).get(category, {}).get(month, 0) for month in filtered_months)

# Calculate average prices for the period (only if there's volume/customers)
if total_new_subscribers_period > 0:
    avg_subscription_price = subscription_revenue_period / sum(
        st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(month, 0) 
        for stakeholder in stakeholders 
        for month in filtered_months
    ) if sum(st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(month, 0) for stakeholder in stakeholders for month in filtered_months) > 0 else 0
else:
    avg_subscription_price = 0

if total_implementation_engagements_period > 0:
    avg_implementation_price = implementation_revenue_period / total_implementation_engagements_period
else:
    avg_implementation_price = 0

if total_maintenance_engagements_period > 0:
    avg_maintenance_price = maintenance_revenue_period / total_maintenance_engagements_period
else:
    avg_maintenance_price = 0

if total_transaction_volume_period > 0:
    avg_transactional_revenue_per_transaction = transactional_revenue_period / total_transaction_volume_period
else:
    avg_transactional_revenue_per_transaction = 0

# Calculate average churn rate for stakeholders with active subscribers (following KPI dashboard logic)
total_churn_rates = 0
total_months = 0

for stakeholder in stakeholders:
    # Check if this stakeholder has active subscribers in the selected period
    customers = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {})
    has_active_subscribers = any(customers.get(month, 0) > 0 for month in filtered_months)
    
    # Only include stakeholders with active subscribers in churn calculation
    if has_active_subscribers:
        churns = st.session_state.model_data.get("subscription_churn_rates", {}).get(stakeholder, {})
        
        for month in filtered_months:
            churn_rate = churns.get(month, 0)
            total_churn_rates += churn_rate
            total_months += 1

# Calculate average churn rate
if total_months > 0:
    avg_churn_rate = total_churn_rates / total_months
else:
    avg_churn_rate = 0.0

# Format churn rate with color coding (following KPI dashboard logic)
if avg_churn_rate == 0:
    churn_color = "#666"  # Gray for no data
elif avg_churn_rate < 3:
    churn_color = "#00D084"  # Green
elif avg_churn_rate < 5:
    churn_color = "#FFA500"  # Orange
else:
    churn_color = "#dc3545"  # Red

# SUBSCRIPTION REVENUE STREAM
if selected_stream == "Subscription":
    sub_col1, sub_col2, sub_col3, sub_col4, sub_col5 = st.columns(5)

    with sub_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💵 Revenue</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${subscription_revenue_period:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with sub_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">👥 New Subscribers</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{total_new_subscribers_period:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with sub_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📉 Avg Churn Rate</h4>
            <h2 style="margin: 0.5rem 0 0 0; color: {churn_color};">{avg_churn_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)

    with sub_col4:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📈 Cumulative Subs</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{ending_cumulative_subscribers:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with sub_col5:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💰 Avg Monthly Price</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${avg_subscription_price:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

# IMPLEMENTATION REVENUE STREAM
if selected_stream == "Implementation":
    impl_col1, impl_col2, impl_col3 = st.columns(3)

    with impl_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💵 Revenue</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${implementation_revenue_period:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with impl_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📊 Projects</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{total_implementation_engagements_period:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with impl_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💰 Avg Fee</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${avg_implementation_price:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

# MAINTENANCE REVENUE STREAM
if selected_stream == "Maintenance":
    maint_col1, maint_col2, maint_col3 = st.columns(3)

    with maint_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💵 Revenue</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${maintenance_revenue_period:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with maint_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📋 Contracts</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{total_maintenance_engagements_period:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with maint_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💰 Avg Fee</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${avg_maintenance_price:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

# TRANSACTIONAL REVENUE STREAM
if selected_stream == "Transactional":
    trans_col1, trans_col2, trans_col3 = st.columns(3)

    with trans_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💵 Revenue</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${transactional_revenue_period:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with trans_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📊 Transactions</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{total_transaction_volume_period:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with trans_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💰 Avg Revenue/Trans</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${avg_transactional_revenue_per_transaction:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# BAR GRAPH SECTION
st.markdown("") # Small spacing

# Chart type selection dropdown
chart_type_col1, chart_type_col2 = st.columns([0.75, 3.25])
with chart_type_col1:
    # Chart options based on selected revenue stream
    if selected_stream == "All Streams":
        chart_options = ["Revenue"]
        chart_keys = ["revenue"]
    elif selected_stream == "Subscription":
        chart_options = ["Revenue", "New Subscribers", "Cumulative Subscribers", "Average Churn Rate", "Average Monthly Price"]
        chart_keys = ["revenue", "new_subscribers", "cumulative_subscribers", "churn_rate", "avg_price"]
    elif selected_stream == "Transactional":
        chart_options = ["Revenue", "Total Transactions", "Avg Revenue per Transaction"]
        chart_keys = ["revenue", "transactions", "avg_revenue_per_transaction"]
    elif selected_stream == "Implementation":
        chart_options = ["Revenue", "Implementation Projects", "Average Fee"]
        chart_keys = ["revenue", "projects", "avg_fee"]
    elif selected_stream == "Maintenance":
        chart_options = ["Revenue", "Maintenance Contracts", "Average Fee"]
        chart_keys = ["revenue", "contracts", "avg_fee"]
    
    if selected_stream == "All Streams":
        # For All Streams, only show Revenue and don't show dropdown
        selected_chart = "Revenue"
        st.session_state.revenue_chart_type = "revenue"

    else:
        # Get current index based on session state
        current_type = st.session_state.get("revenue_chart_type", chart_keys[0])
        try:
            current_index = chart_keys.index(current_type)
        except ValueError:
            current_index = 0
        
        selected_chart = st.selectbox(
            "Select chart type:",
            options=chart_options,
            index=current_index,
            key="revenue_chart_type_select"
        )
    
    # Update session state based on selection
    if selected_stream != "All Streams":
        selected_index = chart_options.index(selected_chart)
        st.session_state.revenue_chart_type = chart_keys[selected_index]

# Get current chart type
chart_type = st.session_state.get("revenue_chart_type", chart_keys[0])

# Prepare chart data based on selected year
if metrics_period == "All Years":
    # For All Years, show yearly totals
    chart_data = {}
    years_dict = group_months_by_year(months)
    
    for year in sorted(years_dict.keys()):
        year_months = years_dict[year]
        
        if selected_stream == "All Streams":
            # For stacked chart, we need all stream data
            chart_data[str(year)] = {
                'Subscription': sum(st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0) for month in year_months),
                'Implementation': sum(st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0) for month in year_months),
                'Transactional': sum(st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0) for month in year_months),
                'Maintenance': sum(st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0) for month in year_months)
            }
        elif selected_stream == "Subscription":
            if chart_type == "revenue":
                chart_data[str(year)] = sum(st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0) for month in year_months)
            elif chart_type == "new_subscribers":
                year_total = 0
                for stakeholder in stakeholders:
                    year_total += sum(st.session_state.model_data.get("subscription_new_customers", {}).get(stakeholder, {}).get(month, 0) for month in year_months)
                chart_data[str(year)] = year_total
            elif chart_type == "cumulative_subscribers":
                # Get end-of-year cumulative subscribers
                end_year_total = 0
                for stakeholder in stakeholders:
                    end_year_total += st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(year_months[-1], 0)
                chart_data[str(year)] = end_year_total
            elif chart_type == "churn_rate":
                # Calculate average churn rate for the year (only for stakeholders with active subscribers)
                total_churn_rates = 0
                total_months = 0
                for stakeholder in stakeholders:
                    customers = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {})
                    has_active_subscribers = any(customers.get(month, 0) > 0 for month in year_months)
                    if has_active_subscribers:
                        churns = st.session_state.model_data.get("subscription_churn_rates", {}).get(stakeholder, {})
                        for month in year_months:
                            churn_rate = churns.get(month, 0)
                            total_churn_rates += churn_rate
                            total_months += 1
                chart_data[str(year)] = (total_churn_rates / total_months) if total_months > 0 else 0
            elif chart_type == "avg_price":
                # Calculate average subscription price
                year_revenue = sum(st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0) for month in year_months)
                year_subscriber_months = 0
                for stakeholder in stakeholders:
                    year_subscriber_months += sum(st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(month, 0) for month in year_months)
                chart_data[str(year)] = (year_revenue / year_subscriber_months) if year_subscriber_months > 0 else 0
                
        elif selected_stream == "Transactional":
            if chart_type == "revenue":
                chart_data[str(year)] = sum(st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0) for month in year_months)
            elif chart_type == "transactions":
                year_total = 0
                for category in transactional_categories:
                    year_total += sum(st.session_state.model_data.get("transactional_volume", {}).get(category, {}).get(month, 0) for month in year_months)
                chart_data[str(year)] = year_total
            elif chart_type == "avg_revenue_per_transaction":
                year_revenue = sum(st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0) for month in year_months)
                year_transactions = 0
                for category in transactional_categories:
                    year_transactions += sum(st.session_state.model_data.get("transactional_volume", {}).get(category, {}).get(month, 0) for month in year_months)
                chart_data[str(year)] = (year_revenue / year_transactions) if year_transactions > 0 else 0
                
        elif selected_stream == "Implementation":
            if chart_type == "revenue":
                chart_data[str(year)] = sum(st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0) for month in year_months)
            elif chart_type == "projects":
                year_total = 0
                for stakeholder in stakeholders:
                    year_total += sum(st.session_state.model_data.get("implementation_new_customers", {}).get(stakeholder, {}).get(month, 0) for month in year_months)
                chart_data[str(year)] = year_total
            elif chart_type == "avg_fee":
                year_revenue = sum(st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0) for month in year_months)
                year_projects = 0
                for stakeholder in stakeholders:
                    year_projects += sum(st.session_state.model_data.get("implementation_new_customers", {}).get(stakeholder, {}).get(month, 0) for month in year_months)
                chart_data[str(year)] = (year_revenue / year_projects) if year_projects > 0 else 0
                
        elif selected_stream == "Maintenance":
            if chart_type == "revenue":
                chart_data[str(year)] = sum(st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0) for month in year_months)
            elif chart_type == "contracts":
                year_total = 0
                for stakeholder in stakeholders:
                    year_total += sum(st.session_state.model_data.get("maintenance_new_customers", {}).get(stakeholder, {}).get(month, 0) for month in year_months)
                chart_data[str(year)] = year_total
            elif chart_type == "avg_fee":
                year_revenue = sum(st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0) for month in year_months)
                year_contracts = 0
                for stakeholder in stakeholders:
                    year_contracts += sum(st.session_state.model_data.get("maintenance_new_customers", {}).get(stakeholder, {}).get(month, 0) for month in year_months)
                chart_data[str(year)] = (year_revenue / year_contracts) if year_contracts > 0 else 0
    
    # Create DataFrame for chart
    if selected_stream == "All Streams" and selected_chart == "Revenue":
        # For stacked revenue chart, create separate data structure
        periods = list(chart_data.keys())
        chart_df = pd.DataFrame({
            'Period': periods,
            'Subscription': [chart_data[period]['Subscription'] for period in periods],
            'Implementation': [chart_data[period]['Implementation'] for period in periods],
            'Transactional': [chart_data[period]['Transactional'] for period in periods],
            'Maintenance': [chart_data[period]['Maintenance'] for period in periods]
        })
        chart_title = "Total Revenue by Stream - All Years"
    else:
        chart_df = pd.DataFrame({
            'Period': list(chart_data.keys()),
            'Value': list(chart_data.values())
        })
        chart_title = f"{selected_chart} by Year"
    
else:
    # For specific year, show monthly data
    year_months = [month for month in months if metrics_period in month]
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
            if selected_stream == "All Streams":
                # For stacked chart, we need all stream data
                chart_data[month_name] = {
                    'Subscription': st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(matching_month, 0),
                    'Implementation': st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(matching_month, 0),
                    'Transactional': st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(matching_month, 0),
                    'Maintenance': st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(matching_month, 0)
                }
            elif selected_stream == "Subscription":
                if chart_type == "revenue":
                    chart_data[month_name] = st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(matching_month, 0)
                elif chart_type == "new_subscribers":
                    month_total = 0
                    for stakeholder in stakeholders:
                        month_total += st.session_state.model_data.get("subscription_new_customers", {}).get(stakeholder, {}).get(matching_month, 0)
                    chart_data[month_name] = month_total
                elif chart_type == "cumulative_subscribers":
                    month_total = 0
                    for stakeholder in stakeholders:
                        month_total += st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(matching_month, 0)
                    chart_data[month_name] = month_total
                elif chart_type == "churn_rate":
                    # Calculate average churn rate for the month
                    total_churn_rates = 0
                    total_stakeholders = 0
                    for stakeholder in stakeholders:
                        customers = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {})
                        has_active_subscribers = customers.get(matching_month, 0) > 0
                        if has_active_subscribers:
                            churns = st.session_state.model_data.get("subscription_churn_rates", {}).get(stakeholder, {})
                            churn_rate = churns.get(matching_month, 0)
                            total_churn_rates += churn_rate
                            total_stakeholders += 1
                    chart_data[month_name] = (total_churn_rates / total_stakeholders) if total_stakeholders > 0 else 0
                elif chart_type == "avg_price":
                    month_revenue = st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(matching_month, 0)
                    month_subscribers = 0
                    for stakeholder in stakeholders:
                        month_subscribers += st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(matching_month, 0)
                    chart_data[month_name] = (month_revenue / month_subscribers) if month_subscribers > 0 else 0
                    
            elif selected_stream == "Transactional":
                if chart_type == "revenue":
                    chart_data[month_name] = st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(matching_month, 0)
                elif chart_type == "transactions":
                    month_total = 0
                    for category in transactional_categories:
                        month_total += st.session_state.model_data.get("transactional_volume", {}).get(category, {}).get(matching_month, 0)
                    chart_data[month_name] = month_total
                elif chart_type == "avg_revenue_per_transaction":
                    month_revenue = st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(matching_month, 0)
                    month_transactions = 0
                    for category in transactional_categories:
                        month_transactions += st.session_state.model_data.get("transactional_volume", {}).get(category, {}).get(matching_month, 0)
                    chart_data[month_name] = (month_revenue / month_transactions) if month_transactions > 0 else 0
                    
            elif selected_stream == "Implementation":
                if chart_type == "revenue":
                    chart_data[month_name] = st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(matching_month, 0)
                elif chart_type == "projects":
                    month_total = 0
                    for stakeholder in stakeholders:
                        month_total += st.session_state.model_data.get("implementation_new_customers", {}).get(stakeholder, {}).get(matching_month, 0)
                    chart_data[month_name] = month_total
                elif chart_type == "avg_fee":
                    month_revenue = st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(matching_month, 0)
                    month_projects = 0
                    for stakeholder in stakeholders:
                        month_projects += st.session_state.model_data.get("implementation_new_customers", {}).get(stakeholder, {}).get(matching_month, 0)
                    chart_data[month_name] = (month_revenue / month_projects) if month_projects > 0 else 0
                    
            elif selected_stream == "Maintenance":
                if chart_type == "revenue":
                    chart_data[month_name] = st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(matching_month, 0)
                elif chart_type == "contracts":
                    month_total = 0
                    for stakeholder in stakeholders:
                        month_total += st.session_state.model_data.get("maintenance_new_customers", {}).get(stakeholder, {}).get(matching_month, 0)
                    chart_data[month_name] = month_total
                elif chart_type == "avg_fee":
                    month_revenue = st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(matching_month, 0)
                    month_contracts = 0
                    for stakeholder in stakeholders:
                        month_contracts += st.session_state.model_data.get("maintenance_new_customers", {}).get(stakeholder, {}).get(matching_month, 0)
                    chart_data[month_name] = (month_revenue / month_contracts) if month_contracts > 0 else 0
        else:
            chart_data[month_name] = 0
    
    # Create DataFrame for chart
    if selected_stream == "All Streams" and selected_chart == "Revenue":
        # For stacked revenue chart, create separate data structure
        periods = list(chart_data.keys())
        chart_df = pd.DataFrame({
            'Period': periods,
            'Subscription': [chart_data[period]['Subscription'] for period in periods],
            'Implementation': [chart_data[period]['Implementation'] for period in periods],
            'Transactional': [chart_data[period]['Transactional'] for period in periods],
            'Maintenance': [chart_data[period]['Maintenance'] for period in periods]
        })
        chart_title = f"Total Revenue by Stream - {metrics_period}"
    else:
        chart_df = pd.DataFrame({
            'Period': list(chart_data.keys()),
            'Value': list(chart_data.values())
        })
        chart_title = f"{selected_chart} - {metrics_period}"

# Display the chart
if not chart_df.empty:
    # Create Plotly figure for cleaner appearance
    fig = go.Figure()
    
    # Set color based on chart type and values
    if chart_type in ["revenue", "new_subscribers", "cumulative_subscribers", "transactions", "projects", "contracts"]:
        color = '#00D084'  # Green for positive metrics
    elif chart_type == "churn_rate":
        # Use conditional coloring for churn rate
        colors = []
        for val in chart_df['Value']:
            if val == 0:
                colors.append('#666')  # Gray for no data
            elif val < 3:
                colors.append('#00D084')  # Green
            elif val < 5:
                colors.append('#FFA500')  # Orange
            else:
                colors.append('#dc3545')  # Red
        color = colors
    else:  # avg_price, avg_fee, avg_revenue_per_transaction
        color = '#00B574'  # Slightly different green for averages
    
    if selected_stream == "All Streams" and chart_type == "revenue":
        # Create stacked bar chart for all revenue streams
        revenue_streams = ['Subscription', 'Implementation', 'Transactional', 'Maintenance']
        colors = ['#00D084', '#3498DB', '#F39C12', '#9B59B6']  # SHAED colors
        
        for i, stream in enumerate(revenue_streams):
            fig.add_trace(go.Bar(
                name=stream,
                x=chart_df['Period'],
                y=chart_df[stream],
                marker_color=colors[i],
                hovertemplate=f'<b>{stream}</b><br>%{{x}}<br>${{y:,.0f}}<extra></extra>',
                opacity=0.8
            ))
        
        # Update layout for stacked bars
        fig.update_layout(barmode='stack')
        
    else:
        # Add bar trace
        fig.add_trace(go.Bar(
            x=chart_df['Period'],
            y=chart_df['Value'],
            marker_color=color,
            opacity=0.7,
            hovertemplate='<b>%{x}</b><br>' + 
                         ('$%{y:,.0f}' if chart_type in ["revenue", "avg_price", "avg_fee", "avg_revenue_per_transaction"] else
                          '%{y:.1f}%' if chart_type == "churn_rate" else
                          '%{y:,.0f}') + '<extra></extra>',
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
            tickangle=-45 if metrics_period != "All Years" else 0
        ),
        yaxis=dict(
            title=('Percentage (%)' if chart_type == "churn_rate" else
                   'Amount ($)' if chart_type in ["revenue", "avg_price", "avg_fee", "avg_revenue_per_transaction"] else
                   'Count'),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickformat=('%.1f%%' if chart_type == "churn_rate" else
                       '$,.0f' if chart_type in ["revenue", "avg_price", "avg_fee", "avg_revenue_per_transaction"] else
                       ',.0f')
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

st.markdown("---")

# DATA MANAGEMENT
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

data_col1, data_col2, data_col3, data_col4, data_col5, data_col6 = st.columns([1, 1, 1, 1, 0.75, 1.25])

# Auto-save is triggered when data changes in the edit handlers, not on page load
# This prevents overwriting database on page refresh

with data_col1:
    if st.button("💾 Save Data", type="primary", use_container_width=True):
        st.write("💾 Saving data to database...")
        try:
            # Clear all caches before saving to ensure fresh connections
            from database import get_supabase_client
            get_supabase_client.clear()
            
            save_data_to_source(st.session_state.model_data)
            
            # Clear data caches after save
            load_revenue_assumptions_from_database.clear()
            load_comprehensive_revenue_data_from_database.clear()
            
            st.success("✅ Data saved successfully to database!")
            st.info("💡 Refresh the page to see the latest saved data.")
        except Exception as e:
            st.error(f"❌ Error saving data: {str(e)}")

with data_col2:
    if st.button("📂 Load Data", type="secondary", use_container_width=True):
        st.write("🔄 Loading data from database...")
        # Clear caches to ensure fresh data
        load_revenue_assumptions_from_database.clear()
        load_comprehensive_revenue_data_from_database.clear()
        get_supabase_client.clear()
        
        loaded_data = load_data_from_source()
        st.session_state.model_data = loaded_data
            
        st.rerun()

with data_col3:
    # Create Excel export data
    try:
        import tempfile
        import os
        from datetime import datetime
        
        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SHAED_Revenue_Assumptions_{timestamp}.xlsx"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            temp_path = tmp_file.name
        
        # Create Excel writer
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            # === SUBSCRIPTION REVENUE STREAM ===
            
            # New Subscription Customers
            if "subscription_new_customers" in st.session_state.model_data:
                new_customers_df = pd.DataFrame(st.session_state.model_data["subscription_new_customers"])
                if not new_customers_df.empty:
                    new_customers_df = new_customers_df.T
                    new_customers_df.index.name = 'Month'
                    new_customers_df.to_excel(writer, sheet_name='Sub - New Customers')
            
            # Subscription Pricing
            if "subscription_pricing" in st.session_state.model_data:
                pricing_df = pd.DataFrame(st.session_state.model_data["subscription_pricing"])
                if not pricing_df.empty:
                    pricing_df = pricing_df.T
                    pricing_df.index.name = 'Month'
                    pricing_df.to_excel(writer, sheet_name='Sub - Pricing')
            
            # Churn Rates
            if "subscription_churn_rates" in st.session_state.model_data:
                churn_df = pd.DataFrame(st.session_state.model_data["subscription_churn_rates"])
                if not churn_df.empty:
                    churn_df = churn_df.T
                    churn_df.index.name = 'Month'
                    churn_df.to_excel(writer, sheet_name='Sub - Churn Rates')
            
            # Cumulative Active Subscribers
            if "subscription_running_totals" in st.session_state.model_data:
                cumulative_df = pd.DataFrame(st.session_state.model_data["subscription_running_totals"])
                if not cumulative_df.empty:
                    cumulative_df = cumulative_df.T
                    cumulative_df.index.name = 'Month'
                    cumulative_df.to_excel(writer, sheet_name='Sub - Cumulative Subscribers')
            
            # === TRANSACTIONAL REVENUE STREAM ===
            
            # Transaction Volume
            if "transactional_volume" in st.session_state.model_data:
                volume_df = pd.DataFrame(st.session_state.model_data["transactional_volume"])
                if not volume_df.empty:
                    volume_df = volume_df.T
                    volume_df.index.name = 'Month'
                    volume_df.to_excel(writer, sheet_name='Trans - Volume')
            
            # Transaction Price
            if "transactional_price" in st.session_state.model_data:
                trans_price_df = pd.DataFrame(st.session_state.model_data["transactional_price"])
                if not trans_price_df.empty:
                    trans_price_df = trans_price_df.T
                    trans_price_df.index.name = 'Month'
                    trans_price_df.to_excel(writer, sheet_name='Trans - Price per Transaction')
            
            # Referral Fee Percentage
            if "transactional_referral_fee" in st.session_state.model_data:
                referral_df = pd.DataFrame(st.session_state.model_data["transactional_referral_fee"])
                if not referral_df.empty:
                    referral_df = referral_df.T
                    referral_df.index.name = 'Month'
                    referral_df.to_excel(writer, sheet_name='Trans - Referral Fee %')
            
            # === IMPLEMENTATION REVENUE STREAM ===
            
            # Implementation Engagements
            if "implementation_new_customers" in st.session_state.model_data:
                impl_customers_df = pd.DataFrame(st.session_state.model_data["implementation_new_customers"])
                if not impl_customers_df.empty:
                    impl_customers_df = impl_customers_df.T
                    impl_customers_df.index.name = 'Month'
                    impl_customers_df.to_excel(writer, sheet_name='Impl - Engagements')
            
            # Implementation Pricing
            if "implementation_pricing" in st.session_state.model_data:
                impl_pricing_df = pd.DataFrame(st.session_state.model_data["implementation_pricing"])
                if not impl_pricing_df.empty:
                    impl_pricing_df = impl_pricing_df.T
                    impl_pricing_df.index.name = 'Month'
                    impl_pricing_df.to_excel(writer, sheet_name='Impl - Fees')
            
            # === MAINTENANCE REVENUE STREAM ===
            
            # Maintenance Contracts
            if "maintenance_new_customers" in st.session_state.model_data:
                maint_customers_df = pd.DataFrame(st.session_state.model_data["maintenance_new_customers"])
                if not maint_customers_df.empty:
                    maint_customers_df = maint_customers_df.T
                    maint_customers_df.index.name = 'Month'
                    maint_customers_df.to_excel(writer, sheet_name='Maint - Contracts')
            
            # Maintenance Pricing
            if "maintenance_pricing" in st.session_state.model_data:
                maint_pricing_df = pd.DataFrame(st.session_state.model_data["maintenance_pricing"])
                if not maint_pricing_df.empty:
                    maint_pricing_df = maint_pricing_df.T
                    maint_pricing_df.index.name = 'Month'
                    maint_pricing_df.to_excel(writer, sheet_name='Maint - Fees')
            
            # === REVENUE TOTALS ===
            
            # Revenue by Stream (Monthly)
            if "revenue" in st.session_state.model_data:
                revenue_data = st.session_state.model_data["revenue"]
                revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
                filtered_revenue_data = {cat: revenue_data[cat] for cat in revenue_categories if cat in revenue_data}
                
                if filtered_revenue_data:
                    revenue_df = pd.DataFrame(filtered_revenue_data)
                    revenue_df = revenue_df.T
                    revenue_df.index.name = 'Month'
                    
                    # Add total revenue row
                    total_row = {}
                    for month in months:
                        total_row[month] = sum(filtered_revenue_data[cat].get(month, 0) for cat in filtered_revenue_data.keys())
                    
                    # Add total row to dataframe
                    revenue_df.loc['TOTAL REVENUE'] = pd.Series(total_row)
                    revenue_df.to_excel(writer, sheet_name='Revenue by Stream')
            
            # === REVENUE SUMMARY BY YEAR ===
            years_dict = group_months_by_year(months)
            revenue_summary = []
            
            for year in sorted(years_dict.keys()):
                year_months = years_dict[year]
                
                # Calculate yearly totals
                year_subscription = sum(
                    st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0)
                    for month in year_months
                )
                year_transactional = sum(
                    st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0)
                    for month in year_months
                )
                year_implementation = sum(
                    st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0)
                    for month in year_months
                )
                year_maintenance = sum(
                    st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0)
                    for month in year_months
                )
                year_total = year_subscription + year_transactional + year_implementation + year_maintenance
                
                # Calculate key metrics for the year
                total_new_subscribers = sum(
                    st.session_state.model_data.get("subscription_new_customers", {}).get(stakeholder, {}).get(month, 0)
                    for stakeholder in stakeholders
                    for month in year_months
                )
                
                total_implementations = sum(
                    st.session_state.model_data.get("implementation_new_customers", {}).get(stakeholder, {}).get(month, 0)
                    for stakeholder in stakeholders
                    for month in year_months
                )
                
                total_maintenance = sum(
                    st.session_state.model_data.get("maintenance_new_customers", {}).get(stakeholder, {}).get(month, 0)
                    for stakeholder in stakeholders
                    for month in year_months
                )
                
                # Get end-of-year cumulative subscribers
                end_year_subscribers = sum(
                    st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(year_months[-1], 0)
                    for stakeholder in stakeholders
                )
                
                # Calculate transaction volume
                total_transactions = sum(
                    st.session_state.model_data.get("transactional_volume", {}).get(category, {}).get(month, 0)
                    for category in transactional_categories
                    for month in year_months
                )
                
                revenue_summary.append({
                    'Year': year,
                    'Subscription Revenue': year_subscription,
                    'Transactional Revenue': year_transactional,
                    'Implementation Revenue': year_implementation,
                    'Maintenance Revenue': year_maintenance,
                    'Total Revenue': year_total,
                    'New Subscribers': total_new_subscribers,
                    'End-of-Year Cumulative Subscribers': end_year_subscribers,
                    'Implementation Projects': total_implementations,
                    'Maintenance Contracts': total_maintenance,
                    'Total Transactions': total_transactions
                })
            
            if revenue_summary:
                summary_df = pd.DataFrame(revenue_summary)
                summary_df.to_excel(writer, sheet_name='Annual Summary', index=False)
            
            # === KEY METRICS BY MONTH ===
            monthly_metrics = []
            
            for month in months:
                # Revenue by stream
                sub_revenue = st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0)
                trans_revenue = st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0)
                impl_revenue = st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0)
                maint_revenue = st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0)
                total_rev = sub_revenue + trans_revenue + impl_revenue + maint_revenue
                
                # Customer metrics
                new_subs = sum(
                    st.session_state.model_data.get("subscription_new_customers", {}).get(stakeholder, {}).get(month, 0)
                    for stakeholder in stakeholders
                )
                
                cumulative_subs = sum(
                    st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(month, 0)
                    for stakeholder in stakeholders
                )
                
                # Transaction metrics
                total_trans = sum(
                    st.session_state.model_data.get("transactional_volume", {}).get(category, {}).get(month, 0)
                    for category in transactional_categories
                )
                
                # Implementation and maintenance
                impl_projects = sum(
                    st.session_state.model_data.get("implementation_new_customers", {}).get(stakeholder, {}).get(month, 0)
                    for stakeholder in stakeholders
                )
                
                maint_contracts = sum(
                    st.session_state.model_data.get("maintenance_new_customers", {}).get(stakeholder, {}).get(month, 0)
                    for stakeholder in stakeholders
                )
                
                monthly_metrics.append({
                    'Month': month,
                    'Total Revenue': total_rev,
                    'Subscription Revenue': sub_revenue,
                    'Transactional Revenue': trans_revenue,
                    'Implementation Revenue': impl_revenue,
                    'Maintenance Revenue': maint_revenue,
                    'New Subscribers': new_subs,
                    'Cumulative Subscribers': cumulative_subs,
                    'Total Transactions': total_trans,
                    'Implementation Projects': impl_projects,
                    'Maintenance Contracts': maint_contracts
                })
            
            if monthly_metrics:
                monthly_df = pd.DataFrame(monthly_metrics)
                monthly_df.to_excel(writer, sheet_name='Monthly Metrics', index=False)
        
        # Read the file data for download
        with open(temp_path, 'rb') as f:
            excel_data = f.read()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Direct download button that triggers immediately
        st.download_button(
            label="📊 Export Excel",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
        
    except ImportError:
        # Fallback button if openpyxl not available
        if st.button("📊 Export Excel", type="primary", use_container_width=True):
            st.error("❌ Excel export requires openpyxl. Please install: pip install openpyxl")
    except Exception as e:
        # Fallback button if there's an error
        if st.button("📊 Export Excel", type="primary", use_container_width=True):
            st.error(f"❌ Error creating Excel file: {str(e)}")

# Add utility buttons in data_col4 and data_col5
with data_col4:
    pass

with data_col5:
    pass

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; margin-top: 3rem; border-top: 1px solid #e0e0e0;">
    <strong>SHAED Financial Model - Revenue Assumptions</strong> | Powering the future of mobility<br>
    <small>© 2025 SHAED - All rights reserved</small>
</div>
""", unsafe_allow_html=True)

# Calculate initial revenue totals on page load
calculate_all_revenue()

# Note: Auto-save is triggered when data changes in the edit handlers
# This prevents overwriting database with empty data on page refresh