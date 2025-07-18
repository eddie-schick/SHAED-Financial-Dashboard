import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# Configure page
st.set_page_config(
    page_title="SHAED Financial Model",
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
</style>
""", unsafe_allow_html=True)

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
    """Calculate hosting costs based on gross profit model structure"""
    if "gross_profit_data" not in st.session_state.model_data:
        return {}, {}
    
    gp_data = st.session_state.model_data["gross_profit_data"]
    
    # Get hosting structure
    hosting_structure = gp_data.get("saas_hosting_structure", {
        "fixed_monthly_cost": 500.0,
        "cost_per_customer": 0.50,
        "go_live_month": "Jan 2025",
        "capitalize_before_go_live": True
    })
    
    fixed_cost = hosting_structure.get("fixed_monthly_cost", 500.0)
    variable_cost = hosting_structure.get("cost_per_customer", 0.50)
    go_live_month = hosting_structure.get("go_live_month", "Jan 2025")
    capitalize_before_go_live = hosting_structure.get("capitalize_before_go_live", True)
    
    hosting_costs = {}
    capitalized_hosting = {}
    
    # Find go-live month index
    try:
        go_live_index = months.index(go_live_month)
    except ValueError:
        go_live_index = 0  # Default to first month if invalid
    
    for i, month in enumerate(months):
        active_subscribers = get_active_subscribers(month)
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

# Header with SHAED branding
st.markdown("""
<div class="main-header">
    <h1>📈 SHAED Financial Model</h1>
    <h2>Income Statement</h2>
</div>
""", unsafe_allow_html=True)

# Unified Navigation Bar
st.markdown('<div class="section-header">🧭 Dashboard Navigation</div>', unsafe_allow_html=True)

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
    if st.button("📊 Gross Profit", key="nav_gross", use_container_width=True):
        st.info("Run: streamlit run gross_profit_model.py")

with nav_col8:
    if st.button("☁️ Hosting", key="nav_hosting", use_container_width=True):
        st.info("Run: streamlit run hosting_costs_model.py")

# Add visual separator after navigation
st.markdown("---")

# View toggle
view_col1, view_col2 = st.columns([1, 3])
with view_col1:
    view_mode = st.selectbox(
        "View Mode:",
        ["Monthly + Yearly", "Yearly Only"],
        key="view_mode"
    )

show_monthly = view_mode == "Monthly + Yearly"

# REVENUE SECTION
st.markdown('<div class="section-header">💰 Revenue</div>', unsafe_allow_html=True)
st.info("📝 Revenue will be populated from the Revenue Assumptions dashboard")

# Updated revenue categories in new order
revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
create_custom_table_with_years(revenue_categories, "revenue", show_monthly)

# Calculate total revenue
total_revenue = {}
for month in months:
    total_revenue[month] = sum(
        st.session_state.model_data.get("revenue", {}).get(cat, {}).get(month, 0) 
        for cat in revenue_categories
    )


create_custom_total_row(total_revenue, "Total Revenue", show_monthly)

st.markdown("---")

# COST OF SALES SECTION
st.markdown('<div class="section-header">📦 Cost of Sales</div>', unsafe_allow_html=True)
st.info("📝 Cost of Sales will be populated from Gross Profit dashboard")

# Updated cost of sales categories to match revenue
cost_of_sales_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
create_custom_table_with_years(cost_of_sales_categories, "cogs", show_monthly)

# Calculate total cost of sales
total_cost_of_sales = {}
for month in months:
    total_cost_of_sales[month] = sum(
        st.session_state.model_data.get("cogs", {}).get(cat, {}).get(month, 0) 
        for cat in cost_of_sales_categories
    )


create_custom_total_row(total_cost_of_sales, "Total Cost of Sales", show_monthly)

st.markdown("---")

# GROSS PROFIT SECTION
st.markdown('<div class="section-header">📈 Gross Profit</div>', unsafe_allow_html=True)

# Calculate gross profit data (Revenue - COGS)
gross_profit_data = {}
for category in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
    gross_profit_data[category] = {}
    for month in months:
        revenue = st.session_state.model_data.get("revenue", {}).get(category, {}).get(month, 0)
        cost = st.session_state.model_data.get("cogs", {}).get(category, {}).get(month, 0)
        gross_profit_data[category][month] = revenue - cost

# Store gross profit data in session state for the custom table function
st.session_state.model_data["gross_profit"] = gross_profit_data

create_custom_table_with_years(["Subscription", "Transactional", "Implementation", "Maintenance"], "gross_profit", show_monthly)

# Calculate total gross profit
total_gross_profit = {}
for month in months:
    total_gross_profit[month] = total_revenue[month] - total_cost_of_sales[month]


create_custom_total_row(total_gross_profit, "Total Gross Profit", show_monthly)

# Toggle for gross margin display
show_gross_margin = st.checkbox("Show Gross Margin %", value=False, help="Toggle to show/hide gross margin percentage tables")

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

    # Store gross margin data in session state for the custom table function
    st.session_state.model_data["gross_margin"] = gross_margin_data


    create_custom_table_with_years(["Subscription", "Transactional", "Implementation", "Maintenance"], "gross_margin", show_monthly)

    # Calculate total gross margin
    total_gross_margin = {}
    for month in months:
        total_gross_margin[month] = (total_gross_profit[month] / total_revenue[month] * 100) if total_revenue[month] > 0 else 0


    create_custom_total_row_with_yearly_percentage(total_gross_margin, total_gross_profit, total_revenue, "Total Gross Margin %", show_monthly)

st.markdown("---")

# SELLING, GENERAL AND ADMINISTRATIVE EXPENSES
st.markdown('<div class="section-header">🏢 Selling, General and Administrative Expenses</div>', unsafe_allow_html=True)
st.info("📝 SG&A Expenses will be populated from Liquidity Forecast dashboard")

# Get SG&A categories from liquidity model order (if available)
if ("liquidity_data" in st.session_state.model_data and 
    "category_order" in st.session_state.model_data["liquidity_data"]):
    sga_categories = st.session_state.model_data["liquidity_data"]["category_order"]
else:
    # Fallback to default order if liquidity data not available
    sga_categories = [
        "Payroll",
        "Contractors",
        "License Fees",
        "Travel",
        "Shows",
        "Associations",
        "Marketing",
        "Company Vehicle",
        "Grant Writer",
        "Insurance",
        "Legal / Professional Fees",
        "Permitting/Fees/Licensing",
        "Shared Services",
        "Consultants/Audit/Tax",
        "Pritchard AMEX",
        "Contingencies"
    ]

create_custom_table_with_years(sga_categories, "sga_expenses", show_monthly)

# Calculate total SG&A expenses
total_sga = {}
for month in months:
    total_sga[month] = sum(
        st.session_state.model_data.get("sga_expenses", {}).get(cat, {}).get(month, 0) 
        for cat in sga_categories
    )


create_custom_total_row(total_sga, "Total SG&A Expenses", show_monthly)

st.markdown("---")

# NET INCOME
st.markdown('<div class="section-header">💵 Net Income</div>', unsafe_allow_html=True)

# Calculate net income
net_income = {}
for month in months:
    net_income[month] = total_gross_profit[month] - total_sga[month]

create_custom_total_row(net_income, "Net Income", show_monthly)

# Summary metrics with SHAED styling
st.markdown("---")
st.markdown('<div class="section-header">📊 Summary</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    total_revenue_sum = sum(total_revenue.values())
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Revenue (6 years)</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${total_revenue_sum:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_expenses_sum = sum(total_cost_of_sales.values()) + sum(total_sga.values())
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Expenses (6 years)</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${total_expenses_sum:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_net_income_sum = sum(net_income.values())
    color = "#00D084" if total_net_income_sum >= 0 else "#dc3545"
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Net Income (6 years)</h4>
        <h2 style="margin: 0.5rem 0 0 0; color: {color};">${total_net_income_sum:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

# Yearly breakdown
st.markdown("### Yearly Breakdown")
years_dict = group_months_by_year(months)
yearly_cols = st.columns(len(years_dict))

for i, year in enumerate(sorted(years_dict.keys())):
    with yearly_cols[i]:
        year_revenue = sum(total_revenue.get(month, 0) for month in years_dict[year])
        year_expenses = sum(total_cost_of_sales.get(month, 0) + total_sga.get(month, 0) for month in years_dict[year])
        year_net = sum(net_income.get(month, 0) for month in years_dict[year])
        year_color = "#00D084" if year_net >= 0 else "#dc3545"
        
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">{year}</h4>
            <p style="margin: 0.2rem 0; font-size: 0.9rem;">Revenue: ${year_revenue:,.0f}</p>
            <p style="margin: 0.2rem 0; font-size: 0.9rem;">Expenses: ${year_expenses:,.0f}</p>
            <p style="margin: 0.2rem 0; font-weight: bold; color: {year_color};">Net: ${year_net:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)

# DATA MANAGEMENT
st.markdown("---")
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    if st.button("💾 Save Data", type="primary", use_container_width=True):
        if save_data(st.session_state.model_data):
            st.success("✅ Data saved successfully!")
        else:
            st.error("❌ Failed to save data")

with col2:
    if st.button("📂 Load Data", type="primary", use_container_width=True):
        st.session_state.model_data = load_data()
        st.success("✅ Data loaded successfully!")
        st.rerun()

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; margin-top: 3rem; border-top: 1px solid #e0e0e0;">
    <strong>SHAED Financial Model - Income Statement</strong> | Powering the future of mobility<br>
    <small>© 2025 SHAED - All rights reserved</small>
</div>
""", unsafe_allow_html=True)