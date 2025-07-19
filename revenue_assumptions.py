import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# Configure page
st.set_page_config(
    page_title="SHAED Finance Dashboard - Revenue",
    page_icon="💰",
    layout="wide"
)

# Data persistence functions
def save_data(data: dict, filename: str = "financial_model_data.json"):
    """Save data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_data(filename: str = "financial_model_data.json") -> dict:
    """Load data from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}

# Initialize session state
if 'model_data' not in st.session_state:
    st.session_state.model_data = load_data()

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
    .stButton > button {
        background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
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

# Stakeholder list (all 20 stakeholders)
stakeholders = [
    "Equipment Manufacturer", "Dealership", "Corporate", "Charging as a Service",
    "Charging Hardware", "Depot", "End User", "Infrastructure Partner",
    "Finance Partner", "Fleet Management Company", "Grants", "Logistics",
    "Non Customer", "OEM", "Service", "Technology Partner",
    "Upfitter/Distributor", "Utility/Energy Company", "Insurance Company", "Consultant"
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
                    # Format as whole number if it's a whole number, otherwise show 1 decimal
                    if value == int(value):
                        formatted_value = str(int(value))
                    else:
                        formatted_value = f"{value:.1f}"
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                    year_end_value = value  # Keep the last value of the year
                
                # Year total shows end-of-year value
                if year_end_value == int(year_end_value):
                    year_total_formatted = f"<strong>{int(year_end_value)} (EOY)</strong>"
                else:
                    year_total_formatted = f"<strong>{year_end_value:.1f} (EOY)</strong>"
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{year_total_formatted}</td>'
        else:
            for year in sorted(years_dict.keys()):
                # Get the last month of the year for end-of-year value
                last_month = years_dict[year][-1]
                year_end_value = st.session_state.model_data.get("subscription_running_totals", {}).get(stakeholder, {}).get(last_month, 0)
                if year_end_value == int(year_end_value):
                    year_total_formatted = f"<strong>{int(year_end_value)} (EOY)</strong>"
                else:
                    year_total_formatted = f"<strong>{year_end_value:.1f} (EOY)</strong>"
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

# Helper function to create editable stakeholder tables
def create_stakeholder_table_with_years(metric_name, data_key, filtered_stakeholders, default_value=0.0, format_type="number", show_monthly=True):
    # Initialize data if not exists
    if data_key not in st.session_state.model_data:
        st.session_state.model_data[data_key] = {}
    
    # Ensure all stakeholders are initialized
    for stakeholder in stakeholders:
        if stakeholder not in st.session_state.model_data[data_key]:
            st.session_state.model_data[data_key][stakeholder] = {month: default_value for month in months}
    
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
    
    # Create column config
    if show_monthly:
        column_config = {
            "Stakeholder": st.column_config.TextColumn("Stakeholder", disabled=True, width="medium", pinned=True),
        }
        for col in columns[1:]:
            if "Total" in col:
                column_config[col] = st.column_config.TextColumn(col, width=90, disabled=True)
            else:
                column_config[col] = st.column_config.NumberColumn(col, width=90)
    else:
        column_config = {
            "Stakeholder": st.column_config.TextColumn("Stakeholder", disabled=True, width="medium", pinned=True),
            **{col: st.column_config.TextColumn(col, width=70, disabled=True) for col in columns[1:]}
        }
    
    # Display editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        height=min(600, len(filtered_stakeholders) * 35 + 100),
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
    
    # Update session state
    for i, stakeholder in enumerate(filtered_stakeholders):
        if stakeholder not in st.session_state.model_data[data_key]:
            st.session_state.model_data[data_key][stakeholder] = {}
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    if month in edited_df.columns:
                        value = edited_df.iloc[i][month]
                        st.session_state.model_data[data_key][stakeholder][month] = float(value) if value != '' else default_value
    
    return edited_df

# Helper function for transactional tables
def create_transactional_table_with_years(metric_name, data_key, default_value=0.0, format_type="number", show_monthly=True):
    # Initialize data if not exists
    if data_key not in st.session_state.model_data:
        st.session_state.model_data[data_key] = {}
    
    # Ensure all categories are initialized
    for category in transactional_categories:
        if category not in st.session_state.model_data[data_key]:
            st.session_state.model_data[data_key][category] = {month: default_value for month in months}
    
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
    
    # Create column config
    if show_monthly:
        column_config = {
            "Category": st.column_config.TextColumn("Category", disabled=True, width="medium", pinned=True),
        }
        for col in columns[1:]:
            if "Total" in col:
                column_config[col] = st.column_config.TextColumn(col, width=90, disabled=True)
            else:
                column_config[col] = st.column_config.NumberColumn(col, width=90)
    else:
        column_config = {
            "Category": st.column_config.TextColumn("Category", disabled=True, width="medium", pinned=True),
            **{col: st.column_config.TextColumn(col, width=70, disabled=True) for col in columns[1:]}
        }
    
    # Display editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        height=min(400, len(transactional_categories) * 35 + 100),
        column_config=column_config,
        hide_index=True,
        column_order=["Category"] + [col for col in columns[1:]],
        key=f"transactional_table_{data_key}"
    )
    
    # Update session state
    for i, category in enumerate(transactional_categories):
        if category not in st.session_state.model_data[data_key]:
            st.session_state.model_data[data_key][category] = {}
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    if month in edited_df.columns:
                        value = edited_df.iloc[i][month]
                        st.session_state.model_data[data_key][category][month] = float(value) if value != '' else default_value
    
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

# Header
st.markdown("""
<div class="main-header">
    <h1>💵 SHAED Financial Model</h1>
    <h2>Revenue Assumptions</h2>
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

# Data management controls
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("💾 Save Data", type="primary"):
        calculate_all_revenue()
        if save_data(st.session_state.model_data):
            st.success("All revenue data saved successfully!")
        else:
            st.error("Failed to save data")

with col2:
    if st.button("📂 Load Data"):
        st.session_state.model_data = load_data()
        st.success("Data loaded successfully!")
        st.rerun()

with col3:
    view_mode = st.selectbox(
        "View Mode:",
        ["Monthly + Yearly", "Yearly Only"],
        key="view_mode_all_revenue",
        help="Switch between detailed monthly view with yearly totals or yearly summary only"
    )

show_monthly = view_mode == "Monthly + Yearly"

st.markdown("---")

# STAKEHOLDER FILTERING SECTION
st.markdown("""
<div class="filter-section">
    <div class="filter-header">🔍 Stakeholder Filters</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("**Select Stakeholders to Display:**")
    
    if 'selected_all_revenue_stakeholder_list' not in st.session_state:
        st.session_state.selected_all_revenue_stakeholder_list = stakeholders.copy()
    
    filter_option = st.selectbox(
        "Choose filtering option:",
        ["All Stakeholders", "Custom Selection"],
        key="filter_option_select_all_revenue",
        help="Choose to show all stakeholders or make a custom selection"
    )
    
    if filter_option == "Custom Selection":
        with st.expander("Select Stakeholders", expanded=True):
            checkbox_cols = st.columns(4)
            selections = {}
            
            for i, stakeholder in enumerate(stakeholders):
                col_idx = i % 4
                with checkbox_cols[col_idx]:
                    selections[stakeholder] = st.checkbox(
                        stakeholder,
                        value=stakeholder in st.session_state.selected_all_revenue_stakeholder_list,
                        key=f"all_revenue_checkbox_{stakeholder}"
                    )
            
            st.session_state.selected_all_revenue_stakeholder_list = [
                stakeholder for stakeholder, selected in selections.items() if selected
            ]
    else:
        st.session_state.selected_all_revenue_stakeholder_list = stakeholders.copy()

with col2:
    st.markdown("**Quick Actions:**")
    if st.button("Select All", key="select_all_revenue_stakeholders"):
        st.session_state.selected_all_revenue_stakeholder_list = stakeholders.copy()
        st.rerun()

with col3:
    st.markdown("**\u00A0**")
    if st.button("Clear All", key="clear_all_revenue_stakeholders"):
        st.session_state.selected_all_revenue_stakeholder_list = []
        st.rerun()

filtered_stakeholders = st.session_state.selected_all_revenue_stakeholder_list

st.markdown("---")

# Period and filter info
info_col1, info_col2 = st.columns(2)

with info_col1:
    if show_monthly:
        st.info(f"**Showing {len(months)} months from Jan 2025 to Dec 2030 with yearly subtotals**")
    else:
        st.info(f"**Showing yearly totals from 2025 to 2030**")

with info_col2:
    st.info(f"**Displaying {len(filtered_stakeholders)} of {len(stakeholders)} stakeholders**")

# Info section
st.markdown(f"""
<div style="text-align: center; padding: 1rem; background-color: white; border-radius: 8px; margin: 1rem 0;">
    <div class="revenue-badge">{len(filtered_stakeholders)} Stakeholders</div>
    <div class="revenue-badge">{len(months)} Months</div>
    <div class="revenue-badge">4 Revenue Streams</div>
</div>
""", unsafe_allow_html=True)

# TABBED INTERFACE FOR REVENUE STREAMS
tab1, tab2, tab3, tab4 = st.tabs(["📋 Subscription", "💳 Transactional", "🚀 Implementation", "🔧 Maintenance"])

with tab1:
    st.markdown('<div class="section-header">📋 Subscription Revenue (Cumulative)</div>', unsafe_allow_html=True)
    
    if len(filtered_stakeholders) > 0:
        st.markdown("**📈 New Subscription Customers Per Month:**")
        create_stakeholder_table_with_years("New Subscription Customers", "subscription_new_customers", filtered_stakeholders, default_value=0.0, format_type="number", show_monthly=show_monthly)
        
        st.markdown("---")
        
        st.markdown("**💵 Monthly Subscription Price Per Customer:**")
        create_stakeholder_table_with_years("Subscription Pricing", "subscription_pricing", filtered_stakeholders, default_value=0.0, format_type="currency", show_monthly=show_monthly)
        
        st.markdown("---")
        
        st.markdown("**📉 Monthly Churn Rates (%):**")
        create_stakeholder_table_with_years("Churn Rates", "subscription_churn_rates", filtered_stakeholders, default_value=0.0, format_type="percentage", show_monthly=show_monthly)
        
        st.markdown("---")
        
        # Calculate and display running totals (this will recalculate every time the page refreshes)
        calculate_subscription_running_totals()
        
        st.markdown("**📊 Cumulative Active Subscribers (After Churn):**")
        st.info("💡 This shows the running total of active subscribers after applying churn each month. Updates automatically as you change values above.")
        
        # Create read-only table for running totals using custom HTML format
        if "subscription_running_totals" in st.session_state.model_data:
            create_custom_cumulative_subscribers_table(filtered_stakeholders, show_monthly)
        
    else:
        st.warning("⚠️ No stakeholders selected. Please choose stakeholders from the filter above.")

with tab2:
    st.markdown('<div class="section-header">💳 Transactional Revenue (Volume × Price × Referral %)</div>', unsafe_allow_html=True)
    
    st.markdown("**📊 Transaction Volume Per Month:**")
    create_transactional_table_with_years("Transaction Volume", "transactional_volume", default_value=0.0, format_type="number", show_monthly=show_monthly)
    
    st.markdown("---")
    
    st.markdown("**💰 Average Price Per Transaction:**")
    create_transactional_table_with_years("Price Per Transaction", "transactional_price", default_value=0.0, format_type="currency", show_monthly=show_monthly)
    
    st.markdown("---")
    
    st.markdown("**🎯 Referral Fee Percentage (%):**")
    create_transactional_table_with_years("Referral Fee %", "transactional_referral_fee", default_value=0.0, format_type="percentage", show_monthly=show_monthly)

with tab3:
    st.markdown('<div class="section-header">🚀 Implementation Revenue (One-Time Fees)</div>', unsafe_allow_html=True)
    
    if len(filtered_stakeholders) > 0:
        st.markdown("**🆕 New Implementation Projects Per Month:**")
        create_stakeholder_table_with_years("New Implementations", "implementation_new_customers", filtered_stakeholders, default_value=0.0, format_type="number", show_monthly=show_monthly)
        
        st.markdown("---")
        
        st.markdown("**💵 Implementation Fee Per Project:**")
        create_stakeholder_table_with_years("Implementation Fees", "implementation_pricing", filtered_stakeholders, default_value=0.0, format_type="currency", show_monthly=show_monthly)
        
    else:
        st.warning("⚠️ No stakeholders selected. Please choose stakeholders from the filter above.")

with tab4:
    st.markdown('<div class="section-header">🔧 Maintenance Revenue (One-Time Fees)</div>', unsafe_allow_html=True)
    
    if len(filtered_stakeholders) > 0:
        st.markdown("**🔧 Total Maintenance Contracts Per Month:**")
        create_stakeholder_table_with_years("New Maintenance", "maintenance_new_customers", filtered_stakeholders, default_value=0.0, format_type="number", show_monthly=show_monthly)
        
        st.markdown("---")
        
        st.markdown("**💵 Maintenance Fee Per Contract:**")
        create_stakeholder_table_with_years("Maintenance Fees", "maintenance_pricing", filtered_stakeholders, default_value=0.0, format_type="currency", show_monthly=show_monthly)
        
    else:
        st.warning("⚠️ No stakeholders selected. Please choose stakeholders from the filter above.")

# REVENUE SUMMARY SECTION
st.markdown("---")
st.markdown('<div class="section-header">💰 Revenue Summary & Totals</div>', unsafe_allow_html=True)

# Calculate and show revenue totals
calculate_all_revenue()

# Show summary by revenue stream using custom table
revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
create_custom_table_with_years(revenue_categories, "revenue", show_monthly)

# Calculate total revenue
total_revenue = {}
for month in months:
    total_revenue[month] = sum(
        st.session_state.model_data.get("revenue", {}).get(cat, {}).get(month, 0) 
        for cat in revenue_categories
    )

st.markdown("**Total Revenue:**")
create_custom_total_row(total_revenue, "Total Revenue", show_monthly)

# Summary metrics
st.markdown("---")
st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    subscription_total = sum(st.session_state.model_data.get("revenue", {}).get("Subscription", {}).get(month, 0) for month in months)
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">📋 Subscription (6yr)</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${subscription_total:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    transactional_total = sum(st.session_state.model_data.get("revenue", {}).get("Transactional", {}).get(month, 0) for month in months)
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">💳 Transactional (6yr)</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${transactional_total:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    implementation_total = sum(st.session_state.model_data.get("revenue", {}).get("Implementation", {}).get(month, 0) for month in months)
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">🚀 Implementation (6yr)</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${implementation_total:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    maintenance_total = sum(st.session_state.model_data.get("revenue", {}).get("Maintenance", {}).get(month, 0) for month in months)
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">🔧 Maintenance (6yr)</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${maintenance_total:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

# Auto-save notification
st.info("💡 Data automatically calculates all revenue streams and updates the Income Statement when you save! Use tabs to manage different revenue types.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>SHAED Financial Model - All Revenue Streams</strong> | Powering the future of mobility
</div>
""", unsafe_allow_html=True)