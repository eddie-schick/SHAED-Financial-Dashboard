import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import plotly.graph_objects as go

# Payroll integration functions
def is_employee_active_for_month(emp_data, month_str):
    """Check if employee is active for a specific month"""
    try:
        # Convert month string (e.g., "Jan 2025") to date (first day of month)
        month_date = datetime.strptime(month_str, "%b %Y")
        
        # Check hire date
        hire_date_str = emp_data.get("hire_date")
        if hire_date_str:
            hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d")
            # Employee must be hired by the first day of the month
            if month_date < hire_date:
                return False
        
        # Check termination date
        termination_date_str = emp_data.get("termination_date")
        if termination_date_str:
            termination_date = datetime.strptime(termination_date_str, "%Y-%m-%d")
            # Employee must not be terminated before the first day of the month
            if month_date >= termination_date:
                return False
        
        return True
    except (ValueError, TypeError):
        # If there's any error parsing dates, fall back to active field
        return emp_data.get("active", True)

def is_contractor_active_for_month(contractor_data, month_str):
    """Check if contractor is active for a specific month"""
    try:
        # Convert month string (e.g., "Jan 2025") to date (first day of month)
        month_date = datetime.strptime(month_str, "%b %Y")
        
        # Check start date
        start_date_str = contractor_data.get("start_date")
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            if month_date < start_date:
                return False
        
        # Check end date
        end_date_str = contractor_data.get("end_date")
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            if month_date >= end_date:
                return False
        
        return True
    except (ValueError, TypeError):
        # If there's any error parsing dates, assume active
        return True

def get_calculated_payroll_from_headcount():
    """Get calculated payroll totals from the headcount tab"""
    if "payroll_data" not in st.session_state.model_data:
        return {}, {month: 0 for month in months}
    
    payroll_data = st.session_state.model_data["payroll_data"]
    employees = payroll_data.get("employees", {})
    
    # Calculate payroll by department and total using the same logic as payroll_model.py
    payroll_by_dept = {
        "Product Development": {month: 0 for month in months},
        "Sales and Marketing": {month: 0 for month in months}, 
        "Opex": {month: 0 for month in months}
    }
    
    total_payroll = {month: 0 for month in months}
    
    for emp_id, emp_data in employees.items():
        department = emp_data.get("department", "Opex")
        pay_type = emp_data.get("pay_type", "Salary")
        
        for month in months:
            # Check if employee is active for this specific month
            if not is_employee_active_for_month(emp_data, month):
                continue
                
            if pay_type == "Salary":
                # Salary: Annual salary / 26 pay periods * pay periods in month
                annual_salary = emp_data.get("annual_salary", 0)
                pay_periods = payroll_data.get("pay_periods", {}).get(month, 2)
                monthly_pay = (annual_salary / 26) * pay_periods
            else:  # Hourly
                # Hourly: Hourly rate * weekly hours * weeks in month (4.33 average)
                hourly_rate = emp_data.get("hourly_rate", 0)
                weekly_hours = emp_data.get("weekly_hours", 40.0)
                monthly_hours = weekly_hours * 4.33  # Average weeks per month
                monthly_pay = hourly_rate * monthly_hours
            
            payroll_by_dept[department][month] += monthly_pay
            total_payroll[month] += monthly_pay
    
    return payroll_by_dept, total_payroll

def calculate_monthly_contractor_costs():
    """Calculate monthly contractor costs from headcount data"""
    if "payroll_data" not in st.session_state.model_data:
        return {month: 0 for month in months}
    
    payroll_data = st.session_state.model_data["payroll_data"]
    contractors = payroll_data.get("contractors", {})
    
    contractor_costs = {month: 0 for month in months}
    
    for contractor_data in contractors.values():
        resources = contractor_data.get("resources", 0)
        hourly_rate = contractor_data.get("hourly_rate", 0)
        
        # Calculate monthly cost: resources * hourly rate * 40 hours * 4 weeks
        monthly_cost = resources * hourly_rate * 40 * 4
        
        for month in months:
            # Check if contractor is active for this specific month
            if not is_contractor_active_for_month(contractor_data, month):
                continue
                
            contractor_costs[month] += monthly_cost
    
    return contractor_costs

def calculate_total_personnel_costs():
    """Calculate total personnel costs using the same logic as the payroll model"""
    
    # Use the same calculation logic as the payroll model
    payroll_by_dept, base_payroll = get_calculated_payroll_from_headcount()
    contractor_costs = calculate_monthly_contractor_costs()
    
    # Get configuration for payroll tax rate
    payroll_tax_rate = 0.23  # Default 23%
    if "payroll_data" in st.session_state.model_data:
        config = st.session_state.model_data["payroll_data"].get("payroll_config", {})
        payroll_tax_rate = config.get("payroll_tax_percentage", 23.0) / 100.0
    
    # Calculate bonuses from employee bonus data (same as payroll model)
    bonuses = {month: 0 for month in months}
    if "payroll_data" in st.session_state.model_data:
        employee_bonuses = st.session_state.model_data["payroll_data"].get("employee_bonuses", {})
        
        for bonus_data in employee_bonuses.values():
            bonus_month = bonus_data.get("month", "")
            bonus_amount = bonus_data.get("bonus_amount", 0)
            
            if bonus_month in bonuses:
                bonuses[bonus_month] += bonus_amount
    
    # Calculate payroll taxes and total payroll cost (same as payroll model)
    payroll_taxes = {}
    total_payroll_cost = {}
    
    for month in months:
        monthly_base = base_payroll[month]
        monthly_bonus = bonuses[month]
        # Apply payroll taxes to both base payroll and bonuses
        monthly_taxes = (monthly_base + monthly_bonus) * payroll_tax_rate
        
        payroll_taxes[month] = monthly_taxes
        total_payroll_cost[month] = monthly_base + monthly_bonus + monthly_taxes
    
    return base_payroll, payroll_taxes, bonuses, contractor_costs, total_payroll_cost

def update_liquidity_with_payroll(effective_month=None):
    """Update liquidity model with calculated payroll and contractor costs from headcount tab"""
    
    # Calculate costs using the same logic as the payroll model
    base_payroll, payroll_taxes, bonuses, contractor_costs, total_payroll_cost = calculate_total_personnel_costs()
    
    # Initialize liquidity data if needed
    if "liquidity_data" not in st.session_state.model_data:
        st.session_state.model_data["liquidity_data"] = {}
    if "expenses" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["expenses"] = {}
    
    # Initialize payroll and contractor categories if they don't exist
    if "Payroll" not in st.session_state.model_data["liquidity_data"]["expenses"]:
        st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"] = {month: 0 for month in months}
    if "Contractors" not in st.session_state.model_data["liquidity_data"]["expenses"]:
        st.session_state.model_data["liquidity_data"]["expenses"]["Contractors"] = {month: 0 for month in months}
    
    if effective_month:
        # Find the index of the effective month
        try:
            effective_index = months.index(effective_month)
        except ValueError:
            st.error(f"Invalid effective month: {effective_month}")
            return
        
        # Update only from effective month forward
        current_payroll = st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"].copy()
        current_contractors = st.session_state.model_data["liquidity_data"]["expenses"]["Contractors"].copy()
        
        for i, month in enumerate(months):
            if i >= effective_index:
                # Use total_payroll_cost which includes base + taxes + bonuses
                current_payroll[month] = total_payroll_cost[month]
                current_contractors[month] = contractor_costs[month]
        
        st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"] = current_payroll
        st.session_state.model_data["liquidity_data"]["expenses"]["Contractors"] = current_contractors
    else:
        # Update all months - use total_payroll_cost which includes base + taxes + bonuses
        st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"] = total_payroll_cost
        st.session_state.model_data["liquidity_data"]["expenses"]["Contractors"] = contractor_costs
    
    # Remove old categories if they exist
    old_categories = ["Total Personnel Costs", "Payroll Taxes & Benefits", "Employee Bonuses", "Payroll Expense", "Contractor Expense"]
    for old_cat in old_categories:
        if old_cat in st.session_state.model_data["liquidity_data"]["expenses"]:
            del st.session_state.model_data["liquidity_data"]["expenses"][old_cat]

# Configure page
st.set_page_config(
    page_title="Liquidity",
    page_icon="💰",
    layout="wide"
)

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
    
    /* Secondary button styling to match primary exactly */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(90deg, #00D084 0%, #00B574 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(90deg, #00D084 0%, #00B574 100%) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        border: none !important;
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
    
    /* DataFrames styling */
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
        font-size: 13px !important;
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
        font-size: 13px !important;
        border-bottom: 1px solid #e0e0e0 !important;
        border-right: 1px solid #e0e0e0 !important;
        vertical-align: middle !important;
        text-align: right !important;
    }
    
    /* First column (Category) styling */
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
        font-size: 13px !important;
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
        font-size: 13px !important;
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
        font-size: 13px !important;
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
        font-size: 13px !important;
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
    
    /* Force consistent table styling */
    .stDataFrame table {
        table-layout: fixed !important;
        width: 100% !important;
    }
    
    .stDataFrame th, .stDataFrame td {
        text-align: center !important;
        padding: 4px !important;
        font-size: 12px !important;
    }
    
    /* Category column */
    .stDataFrame th:first-child, .stDataFrame td:first-child {
        width: 200px !important;
        text-align: left !important;
    }
    
    /* Month columns */
    .stDataFrame th:not(:first-child), .stDataFrame td:not(:first-child) {
        width: 115px !important;
        min-width: 115px !important;
        max-width: 115px !important;
    }
    
    /* Year total columns styling */
    .year-total {
        background-color: #f0f9f6 !important;
        font-weight: bold !important;
    }
    
    /* Expense category styling */
    .expense-category {
        background-color: #fff3cd;
        font-weight: bold;
        color: #856404;
    }
    
    /* Cash flow positive/negative styling */
    .cash-positive {
        background-color: #d4edda !important;
        color: #155724 !important;
    }
    
    .cash-negative {
        background-color: #f8d7da !important;
        color: #721c24 !important;
    }

    /* New styles for fixed table */
    .fixed-table-container {
        display: flex;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        background-color: white;
        border: 1px solid #e0e0e0;
    }

    .fixed-category-column {
        width: 200px;
        min-width: 200px;
        background-color: #f8f9fa;
        border-right: 3px solid #00D084;
        flex-shrink: 0;
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

    .category-header {
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
        color: #00D084;
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

def load_data_from_month(effective_month=None, filename: str = "financial_model_data.json") -> dict:
    """Load data from JSON file, preserving historical expenses before effective month"""
    try:
        if not os.path.exists(filename):
            return {}
        
        with open(filename, 'r') as f:
            new_data = json.load(f)
        
        # If no effective month specified, load everything
        if not effective_month:
            return new_data
        
        # Find the index of the effective month
        try:
            effective_index = months.index(effective_month)
        except ValueError:
            st.error(f"Invalid effective month: {effective_month}")
            return {}
        
        # Get current data to preserve historical expenses
        current_data = st.session_state.model_data.copy()
        
        # Update only expense data from effective month forward
        if "liquidity_data" in new_data and "expenses" in new_data["liquidity_data"]:
            if "liquidity_data" not in current_data:
                current_data["liquidity_data"] = {}
            if "expenses" not in current_data["liquidity_data"]:
                current_data["liquidity_data"]["expenses"] = {}
            
            # For each expense category, preserve historical data and update from effective month
            for category, monthly_data in new_data["liquidity_data"]["expenses"].items():
                if category not in current_data["liquidity_data"]["expenses"]:
                    current_data["liquidity_data"]["expenses"][category] = {month: 0 for month in months}
                
                # Update only from effective month forward
                for i, month in enumerate(months):
                    if i >= effective_index:
                        current_data["liquidity_data"]["expenses"][category][month] = monthly_data.get(month, 0)
        
        # Update all other data (revenue, cash flow, etc.) completely
        for key, value in new_data.items():
            if key != "liquidity_data":
                current_data[key] = value
            elif key == "liquidity_data":
                # For liquidity_data, update everything except expenses (which we handled above)
                for subkey, subvalue in value.items():
                    if subkey != "expenses":
                        if key not in current_data:
                            current_data[key] = {}
                        current_data[key][subkey] = subvalue
        
        return current_data
        
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
    """Format number with commas and handle negatives properly"""
    if num == 0:
        return "0"
    if num < 0:
        return f"({abs(num):,.0f})"
    return f"{num:,.0f}"

# Helper function to format numbers with color
def format_number_with_color(num):
    """Format number with commas and color: red for negative, green for positive"""
    if num == 0:
        return "0"
    elif num < 0:
        return f'<span style="color: #ff4444; font-weight: bold;">({abs(num):,.0f})</span>'
    else:
        return f'<span style="color: #00B574; font-weight: bold;">{num:,.0f}</span>'

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

# Initialize liquidity data structure
def initialize_liquidity_data():
    """Initialize the liquidity data structure with default expense categories"""
    
    # Default expense categories based on the template (in correct order)
    default_categories = {
        # Personnel (combined into one line item)
        "Payroll": {"classification": "Personnel", "editable": False},
        "Contractors": {"classification": "Personnel", "editable": True},
        
        # License Fees (from Product Development tab - placeholder for now)
        "License Fees": {"classification": "Product Development", "editable": False},
        
        # Travel and Shows (right after License Fees)
        "Travel": {"classification": "Sales and Marketing", "editable": True},
        "Shows": {"classification": "Sales and Marketing", "editable": True},
        
        # Sales and Marketing (continued)
        "Associations": {"classification": "Sales and Marketing", "editable": True},
        "Marketing": {"classification": "Sales and Marketing", "editable": True},
        
        # Operations
        "Company Vehicle": {"classification": "Opex", "editable": True},
        "Grant Writer": {"classification": "Opex", "editable": True},
        "Insurance": {"classification": "Opex", "editable": True},
        "Legal / Professional Fees": {"classification": "Opex", "editable": True},
        "Permitting/Fees/Licensing": {"classification": "Opex", "editable": True},
        "Shared Services": {"classification": "Opex", "editable": True},
        "Consultants/Audit/Tax": {"classification": "Opex", "editable": True},
        "Pritchard AMEX": {"classification": "Opex", "editable": True},
        "Contingencies": {"classification": "Opex", "editable": True},
    }
    
    # Initialize liquidity data if not exists
    if "liquidity_data" not in st.session_state.model_data:
        st.session_state.model_data["liquidity_data"] = {}
    
    # Initialize revenue (will come from revenue)
    if "revenue" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["revenue"] = {month: 0 for month in months}
    
    # Initialize investment
    if "investment" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["investment"] = {month: 0 for month in months}
    
    # Initialize other cash receipts
    if "other_cash_receipts" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["other_cash_receipts"] = {month: 0 for month in months}
    
    # Migration: Convert existing "cash_receipts" to "revenue"
    if "cash_receipts" in st.session_state.model_data["liquidity_data"]:
        # Move existing cash_receipts data to revenue
        if "revenue" not in st.session_state.model_data["liquidity_data"]:
            st.session_state.model_data["liquidity_data"]["revenue"] = st.session_state.model_data["liquidity_data"]["cash_receipts"]
        # Remove the old cash_receipts key
        del st.session_state.model_data["liquidity_data"]["cash_receipts"]
    
    # Initialize expense categories
    if "expense_categories" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["expense_categories"] = default_categories
    
    # Initialize category order (for display order in both liquidity and financial models)
    if "category_order" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["category_order"] = list(default_categories.keys())
    
    # Initialize expense data for each category
    if "expenses" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["expenses"] = {}
    
    # Ensure all categories have data
    for category in default_categories:
        if category not in st.session_state.model_data["liquidity_data"]["expenses"]:
            st.session_state.model_data["liquidity_data"]["expenses"][category] = {month: 0 for month in months}
    
    # Initialize starting balance
    if "starting_balance" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["starting_balance"] = 1773162  # From template
    

    
    # Migration: Split "Travel Shows" into "Travel" and "Shows" if it exists
    if "Travel Shows" in st.session_state.model_data["liquidity_data"]["expense_categories"]:
        # Get existing Travel Shows data
        travel_shows_data = st.session_state.model_data["liquidity_data"]["expenses"].get("Travel Shows", {})
        
        # Split the data equally between Travel and Shows
        travel_data = {}
        shows_data = {}
        for month, value in travel_shows_data.items():
            # Split 50/50 for migration
            travel_data[month] = value / 2
            shows_data[month] = value / 2
        
        # Add new categories
        st.session_state.model_data["liquidity_data"]["expense_categories"]["Travel"] = {
            "classification": "Sales and Marketing", 
            "editable": True
        }
        st.session_state.model_data["liquidity_data"]["expense_categories"]["Shows"] = {
            "classification": "Sales and Marketing", 
            "editable": True
        }
        
        # Add data
        st.session_state.model_data["liquidity_data"]["expenses"]["Travel"] = travel_data
        st.session_state.model_data["liquidity_data"]["expenses"]["Shows"] = shows_data
        
        # Remove old category
        del st.session_state.model_data["liquidity_data"]["expense_categories"]["Travel Shows"]
        if "Travel Shows" in st.session_state.model_data["liquidity_data"]["expenses"]:
            del st.session_state.model_data["liquidity_data"]["expenses"]["Travel Shows"]
    
    # Migration: Rename "Travel Slush" to "Pritchard AMEX" if it exists
    if "Travel Slush" in st.session_state.model_data["liquidity_data"]["expense_categories"]:
        # Get existing Travel Slush data
        travel_slush_category = st.session_state.model_data["liquidity_data"]["expense_categories"]["Travel Slush"]
        travel_slush_data = st.session_state.model_data["liquidity_data"]["expenses"].get("Travel Slush", {})
        
        # Add new category with same data
        st.session_state.model_data["liquidity_data"]["expense_categories"]["Pritchard AMEX"] = travel_slush_category
        st.session_state.model_data["liquidity_data"]["expenses"]["Pritchard AMEX"] = travel_slush_data
        
        # Remove old category
        del st.session_state.model_data["liquidity_data"]["expense_categories"]["Travel Slush"]
        if "Travel Slush" in st.session_state.model_data["liquidity_data"]["expenses"]:
            del st.session_state.model_data["liquidity_data"]["expenses"]["Travel Slush"]
    
    # Migration: Update Contractors classification from "Product Development" to "Personnel"
    if ("Contractors" in st.session_state.model_data["liquidity_data"]["expense_categories"] and 
        st.session_state.model_data["liquidity_data"]["expense_categories"]["Contractors"].get("classification") == "Product Development"):
        st.session_state.model_data["liquidity_data"]["expense_categories"]["Contractors"]["classification"] = "Personnel"
        st.session_state.model_data["liquidity_data"]["expense_categories"]["Contractors"]["editable"] = True

    # Migration: Remove old separate personnel categories
    old_personnel_categories = ["Personnel Expenses", "Payroll Taxes & Benefits", "Employee Bonuses"]
    
    # Check if old categories exist and remove them
    for old_cat in old_personnel_categories:
        if old_cat in st.session_state.model_data["liquidity_data"]["expense_categories"]:
            del st.session_state.model_data["liquidity_data"]["expense_categories"][old_cat]
        
        if old_cat in st.session_state.model_data["liquidity_data"]["expenses"]:
            del st.session_state.model_data["liquidity_data"]["expenses"][old_cat]
    
    # Update category order to remove old categories
    if "category_order" in st.session_state.model_data["liquidity_data"]:
        category_order = st.session_state.model_data["liquidity_data"]["category_order"]
        # Remove old categories from order
        category_order = [cat for cat in category_order if cat not in old_personnel_categories]
        st.session_state.model_data["liquidity_data"]["category_order"] = category_order
    
    # Migration: Rename "Total Personnel Costs" to "Payroll" if it exists
    if "Total Personnel Costs" in st.session_state.model_data["liquidity_data"]["expense_categories"]:
        # Move the category definition
        st.session_state.model_data["liquidity_data"]["expense_categories"]["Payroll"] = st.session_state.model_data["liquidity_data"]["expense_categories"]["Total Personnel Costs"]
        del st.session_state.model_data["liquidity_data"]["expense_categories"]["Total Personnel Costs"]
        
        # Move the expense data
        if "Total Personnel Costs" in st.session_state.model_data["liquidity_data"]["expenses"]:
            st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"] = st.session_state.model_data["liquidity_data"]["expenses"]["Total Personnel Costs"]
            del st.session_state.model_data["liquidity_data"]["expenses"]["Total Personnel Costs"]
        
        # Update category order
        if "category_order" in st.session_state.model_data["liquidity_data"]:
            category_order = st.session_state.model_data["liquidity_data"]["category_order"]
            if "Total Personnel Costs" in category_order:
                index = category_order.index("Total Personnel Costs")
                category_order[index] = "Payroll"
                st.session_state.model_data["liquidity_data"]["category_order"] = category_order

    # Ensure Payroll category exists (in case it was removed by migration)
    if "Payroll" not in st.session_state.model_data["liquidity_data"]["expense_categories"]:
        st.session_state.model_data["liquidity_data"]["expense_categories"]["Payroll"] = {
            "classification": "Personnel", 
            "editable": False
        }
    
    if "Payroll" not in st.session_state.model_data["liquidity_data"]["expenses"]:
        st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"] = {month: 0 for month in months}
    
    # Ensure Payroll is at the beginning of category order
    if "category_order" in st.session_state.model_data["liquidity_data"]:
        category_order = st.session_state.model_data["liquidity_data"]["category_order"]
        if "Payroll" not in category_order:
            category_order.insert(0, "Payroll")
            st.session_state.model_data["liquidity_data"]["category_order"] = category_order
        elif category_order.index("Payroll") != 0:
            # Move Payroll to the beginning if it's not already there
            category_order.remove("Payroll")
            category_order.insert(0, "Payroll")
            st.session_state.model_data["liquidity_data"]["category_order"] = category_order

# Note: Payroll taxes are now calculated in the payroll model and included in Payroll

# Function to create editable expense table with yearly subtotals
def create_expense_table_with_years(categories, show_monthly=True):
    """Create editable expense table with yearly subtotals"""
    
    # Group months by year
    years_dict = group_months_by_year(months)
    
    # Create columns list based on view preference
    if show_monthly:
        columns = ["Expense Category"]
        for year in sorted(years_dict.keys()):
            columns.extend(years_dict[year])
            columns.append(f"{year} Total")
        columns.append("Classification")
    else:
        columns = ["Expense Category"] + [f"{year} Total" for year in sorted(years_dict.keys())] + ["Classification"]
    
    # Create data for display
    table_data = []
    for category in categories:
        row = {"Expense Category": category}
        
        if show_monthly:
            # Add monthly data and yearly totals
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    value = st.session_state.model_data["liquidity_data"]["expenses"].get(category, {}).get(month, 0)
                    # Display negative values in parentheses
                    row[month] = -abs(value) if value != 0 else 0  # Expenses are negative
                    yearly_total += value
                row[f"{year} Total"] = f"**({abs(yearly_total):,.0f})**" if yearly_total != 0 else "**0**"
        else:
            # Add only yearly totals
            for year in sorted(years_dict.keys()):
                yearly_total = sum(
                    st.session_state.model_data["liquidity_data"]["expenses"].get(category, {}).get(month, 0)
                    for month in years_dict[year]
                )
                row[f"{year} Total"] = f"**({abs(yearly_total):,.0f})**" if yearly_total != 0 else "**0**"
        
        # Add classification
        classification = st.session_state.model_data["liquidity_data"]["expense_categories"].get(category, {}).get("classification", "Opex")
        is_auto_calc = st.session_state.model_data["liquidity_data"]["expense_categories"].get(category, {}).get("auto_calc", False)
        if is_auto_calc:
            row["Classification"] = f"{classification} (Auto)"
        else:
            row["Classification"] = classification
        
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Create column config exactly matching cash receipts table configuration
    if show_monthly:
        column_config = {
            "Expense Category": st.column_config.TextColumn("Expense Category", disabled=True, width="medium", pinned=True),
            "Classification": st.column_config.TextColumn("Classification", disabled=True, width="medium"),
        }
        for col in columns[1:-1]:  # Skip first and last columns
            if "Total" in col:
                column_config[col] = st.column_config.TextColumn(col, disabled=True)
            else:
                column_config[col] = st.column_config.NumberColumn(col, format="%.0f")
    else:
        column_config = {
            "Expense Category": st.column_config.TextColumn("Expense Category", disabled=True, width="medium", pinned=True),
            "Classification": st.column_config.TextColumn("Classification", disabled=True, width="medium"),
            **{col: st.column_config.TextColumn(col, disabled=True) for col in columns[1:-1]}
        }
    
    # Display editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        height=min(650, len(categories) * 40 + 120),
        column_config=column_config,
        hide_index=True,
        column_order=["Expense Category"] + [col for col in columns[1:]],
        key="expense_table_editor"
    )
    
    # Update session state with edited values (only for editable categories)
    for i, category in enumerate(categories):
        # Skip auto-calculated categories
        is_auto_calc = st.session_state.model_data["liquidity_data"]["expense_categories"].get(category, {}).get("auto_calc", False)
        if is_auto_calc:
            continue
            
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    if month in edited_df.columns:
                        value = edited_df.iloc[i][month]
                        # Convert to positive for storage (expenses are stored as positive, displayed as negative)
                        st.session_state.model_data["liquidity_data"]["expenses"][category][month] = abs(float(value)) if value != 0 else 0
    
    return edited_df

# Function to calculate departmental breakdown for charts
def calculate_departmental_breakdown():
    """Calculate spending by department using actual cash disbursements allocated by department percentages from headcount data"""
    
    # Initialize department totals
    department_totals = {
        "Product Development": {month: 0 for month in months},
        "Sales and Marketing": {month: 0 for month in months},
        "Operations": {month: 0 for month in months}  # Renamed from "Opex" for display
    }
    
    # Get actual cash disbursements from liquidity expenses
    expenses = st.session_state.model_data["liquidity_data"].get("expenses", {})
    actual_payroll_disbursements = expenses.get("Payroll", {month: 0 for month in months})
    actual_contractor_disbursements = expenses.get("Contractors", {month: 0 for month in months})
    
    # Calculate departmental allocation percentages from headcount data
    if "payroll_data" in st.session_state.model_data:
        # Get theoretical departmental payroll breakdown to calculate percentages
        payroll_by_dept, total_theoretical_payroll = get_calculated_payroll_from_headcount()
        
        # Get theoretical departmental contractor breakdown to calculate percentages
        payroll_data = st.session_state.model_data["payroll_data"]
        contractors = payroll_data.get("contractors", {})
        
        contractor_costs_by_dept = {
            "Product Development": {month: 0 for month in months},
            "Sales and Marketing": {month: 0 for month in months},
            "Opex": {month: 0 for month in months}
        }
        total_theoretical_contractors = {month: 0 for month in months}
        
        for contractor_data in contractors.values():
            resources = contractor_data.get("resources", 0)
            hourly_rate = contractor_data.get("hourly_rate", 0)
            department = contractor_data.get("department", "Product Development")
            monthly_cost = resources * hourly_rate * 40 * 4
            
            for month in months:
                if is_contractor_active_for_month(contractor_data, month):
                    contractor_costs_by_dept[department][month] += monthly_cost
                    total_theoretical_contractors[month] += monthly_cost
        
        # Apply departmental percentages to actual cash disbursements
        for month in months:
            # Allocate payroll disbursements by department percentage
            total_payroll = total_theoretical_payroll.get(month, 0)
            actual_payroll = actual_payroll_disbursements.get(month, 0)
            
            if total_payroll > 0:
                # Calculate department percentages and apply to actual disbursements
                pd_payroll_pct = payroll_by_dept["Product Development"].get(month, 0) / total_payroll
                sm_payroll_pct = payroll_by_dept["Sales and Marketing"].get(month, 0) / total_payroll
                ops_payroll_pct = payroll_by_dept["Opex"].get(month, 0) / total_payroll
                
                department_totals["Product Development"][month] += actual_payroll * pd_payroll_pct
                department_totals["Sales and Marketing"][month] += actual_payroll * sm_payroll_pct
                department_totals["Operations"][month] += actual_payroll * ops_payroll_pct
            
            # Allocate contractor disbursements by department percentage
            total_contractors = total_theoretical_contractors.get(month, 0)
            actual_contractors = actual_contractor_disbursements.get(month, 0)
            
            if total_contractors > 0:
                # Calculate department percentages and apply to actual disbursements
                pd_contractor_pct = contractor_costs_by_dept["Product Development"].get(month, 0) / total_contractors
                sm_contractor_pct = contractor_costs_by_dept["Sales and Marketing"].get(month, 0) / total_contractors
                ops_contractor_pct = contractor_costs_by_dept["Opex"].get(month, 0) / total_contractors
                
                department_totals["Product Development"][month] += actual_contractors * pd_contractor_pct
                department_totals["Sales and Marketing"][month] += actual_contractors * sm_contractor_pct
                department_totals["Operations"][month] += actual_contractors * ops_contractor_pct
    
    # Add other expense categories based on their classification
    expense_categories = st.session_state.model_data["liquidity_data"].get("expense_categories", {})
    
    # Classification to department mapping
    classification_to_dept = {
        "Product Development": "Product Development",
        "Sales and Marketing": "Sales and Marketing", 
        "Opex": "Operations"
    }
    
    for category, category_info in expense_categories.items():
        # Skip Payroll and Contractors as they're already handled above
        if category in ["Payroll", "Contractors"]:
            continue
            
        classification = category_info.get("classification", "Operations")
        department = classification_to_dept.get(classification, "Operations")
        
        if category in expenses:
            for month in months:
                expense_amount = expenses[category].get(month, 0)
                department_totals[department][month] += expense_amount
    
    return department_totals

def calculate_departmental_percentages(department_totals):
    """Calculate percentage breakdown by department for each month"""
    department_percentages = {
        "Product Development": {month: 0 for month in months},
        "Sales and Marketing": {month: 0 for month in months},
        "Operations": {month: 0 for month in months}
    }
    
    for month in months:
        total_spend = sum(dept_data[month] for dept_data in department_totals.values())
        
        if total_spend > 0:
            for dept in department_percentages:
                department_percentages[dept][month] = (department_totals[dept][month] / total_spend) * 100
    
    return department_percentages

# Function to calculate and update SG&A expenses in main model
def update_sga_expenses():
    """Update SG&A expenses in the main financial model from liquidity data"""
    
    # Initialize SG&A if not exists
    if "sga_expenses" not in st.session_state.model_data:
        st.session_state.model_data["sga_expenses"] = {}
    
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
        "Pritchard AMEX": "Pritchard AMEX",
        "Contingencies": "Contingencies",
    }
    
    # Update each SG&A category in the correct order
    ordered_categories = st.session_state.model_data["liquidity_data"].get("category_order", list(liquidity_to_sga_mapping.keys()))
    
    # Clear existing SG&A data to rebuild in correct order
    st.session_state.model_data["sga_expenses"] = {}
    
    for liquidity_cat in ordered_categories:
        if liquidity_cat in liquidity_to_sga_mapping and liquidity_cat in st.session_state.model_data["liquidity_data"]["expenses"]:
            sga_cat = liquidity_to_sga_mapping[liquidity_cat]
            st.session_state.model_data["sga_expenses"][sga_cat] = st.session_state.model_data["liquidity_data"]["expenses"][liquidity_cat].copy()

# Function to calculate cash flow and cumulative balance
def calculate_cash_flow():
    """Calculate monthly cash flow and cumulative balance"""
    
    cash_flow = {}
    cumulative_balance = {}
    starting_balance = st.session_state.model_data["liquidity_data"]["starting_balance"]
    running_balance = starting_balance
    
    for month in months:
        # Cash inflows
        revenue = st.session_state.model_data["liquidity_data"]["revenue"].get(month, 0)
        other_cash_receipts = st.session_state.model_data["liquidity_data"]["other_cash_receipts"].get(month, 0)
        investment = st.session_state.model_data["liquidity_data"]["investment"].get(month, 0)
        
        # Cash outflows (sum of all expenses)
        total_expenses = sum(
            st.session_state.model_data["liquidity_data"]["expenses"].get(category, {}).get(month, 0)
            for category in st.session_state.model_data["liquidity_data"]["expense_categories"].keys()
        )
        
        # Monthly cash flow
        monthly_flow = revenue + other_cash_receipts + investment - total_expenses
        cash_flow[month] = monthly_flow
        
        # Cumulative balance
        running_balance += monthly_flow
        cumulative_balance[month] = running_balance
    
    return cash_flow, cumulative_balance

# Function to create summary tables
def create_summary_table_with_years(data_dict, row_label, show_monthly=True, is_balance=False, use_color=False):
    """Create a summary row with fixed category column matching financial model format"""
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
    html_content += '<div class="category-header"></div>'
    html_content += f'<div class="category-cell">{row_label}</div>'
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
    html_content += '<tbody>'
    html_content += '<tr style="height: 43px !important;">'
    
    if show_monthly:
        for year in sorted(years_dict.keys()):
            yearly_total = 0
            for month in years_dict[year]:
                value = data_dict.get(month, 0)
                formatted_value = format_number_with_color(value) if use_color else format_number(value)
                html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                yearly_total += value
            
            if is_balance:
                # For balance, show end-of-year value
                last_month = years_dict[year][-1]
                eoy_value = data_dict.get(last_month, 0)
                formatted_eoy = format_number_with_color(eoy_value) if use_color else format_number(eoy_value)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_eoy}</strong></td>'
            else:
                # For flows, show total
                formatted_total = format_number_with_color(yearly_total) if use_color else format_number(yearly_total)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_total}</strong></td>'
    else:
        for year in sorted(years_dict.keys()):
            if is_balance:
                # For balance, show end-of-year value
                last_month = years_dict[year][-1]
                eoy_value = data_dict.get(last_month, 0)
                formatted_eoy = format_number_with_color(eoy_value) if use_color else format_number(eoy_value)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_eoy}</strong></td>'
            else:
                # For flows, show total
                yearly_total = sum(data_dict.get(month, 0) for month in years_dict[year])
                formatted_total = format_number_with_color(yearly_total) if use_color else format_number(yearly_total)
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_total}</strong></td>'
    
    html_content += '</tr>'
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Function to create combined cash flow summary table
def create_combined_cash_flow_summary(data_list, show_monthly=True):
    """Create combined cash flow summary table with multiple rows"""
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
    for data_config in data_list:
        html_content += f'<div class="category-cell">{data_config["label"]}</div>'
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
    for data_config in data_list:
        html_content += '<tr style="height: 43px !important;">'
        
        data_dict = data_config["data"]
        is_balance = data_config.get("is_balance", False)
        use_color = data_config.get("use_color", False)
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    value = data_dict.get(month, 0)
                    formatted_value = format_number_with_color(value) if use_color else format_number(value)
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                    yearly_total += value
                
                if is_balance:
                    # For balance, show end-of-year value
                    last_month = years_dict[year][-1]
                    eoy_value = data_dict.get(last_month, 0)
                    formatted_eoy = format_number_with_color(eoy_value) if use_color else format_number(eoy_value)
                    html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_eoy}</strong></td>'
                else:
                    # For flows, show total
                    formatted_total = format_number_with_color(yearly_total) if use_color else format_number(yearly_total)
                    html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_total}</strong></td>'
        else:
            for year in sorted(years_dict.keys()):
                if is_balance:
                    # For balance, show end-of-year value
                    last_month = years_dict[year][-1]
                    eoy_value = data_dict.get(last_month, 0)
                    formatted_eoy = format_number_with_color(eoy_value) if use_color else format_number(eoy_value)
                    html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_eoy}</strong></td>'
                else:
                    # For flows, show total
                    yearly_total = sum(data_dict.get(month, 0) for month in years_dict[year])
                    formatted_total = format_number_with_color(yearly_total) if use_color else format_number(yearly_total)
                    html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_total}</strong></td>'
        
        html_content += '</tr>'
    
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Header with SHAED branding
st.markdown("""
<div class="main-header">
    <h1>💰 Liquidity Forecast</h1>
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

# Initialize data
initialize_liquidity_data()

# Auto-sync revenue from Income Statement
def auto_sync_revenue_from_income_statement():
    """Automatically sync revenue with total revenue from Income Statement"""
    if "revenue" in st.session_state.model_data:
        total_revenue = {}
        revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
        for month in months:
            total_revenue[month] = sum(
                st.session_state.model_data.get("revenue", {}).get(cat, {}).get(month, 0) 
                for cat in revenue_categories
            )
        st.session_state.model_data["liquidity_data"]["revenue"] = total_revenue

# Auto-sync revenue automatically when page loads
auto_sync_revenue_from_income_statement()

# Auto-populate payroll and contractor data from headcount tab
# update_liquidity_with_payroll()

# View toggle
view_col1, view_col2 = st.columns([0.75, 3.25])
with view_col1:
    view_mode = st.selectbox(
        "View Mode:",
        ["Monthly + Yearly", "Yearly Only"],
        key="view_mode_liquidity"
    )

show_monthly = view_mode == "Monthly + Yearly"

# LIQUIDITY ASSUMPTIONS SECTION
st.markdown('<div class="section-header">💡 Liquidity Assumptions</div>', unsafe_allow_html=True)

# CASH RECEIPTS SECTION - COLLAPSIBLE
with st.expander("💵 Cash Receipts", expanded=False):
    # Starting Cash Balance input
    balance_col1, balance_col2 = st.columns([0.75, 3.25])
    with balance_col1:
        starting_balance = st.number_input(
            "Starting Cash Balance (12/31/24):",
            value=st.session_state.model_data["liquidity_data"]["starting_balance"],
            step=1000,
            format="%d",
            key="starting_balance_input"
        )
        st.session_state.model_data["liquidity_data"]["starting_balance"] = starting_balance

    st.info("✅ Revenue automatically syncs with revenue from the Income Statement when page loads")

    # Create editable table for revenue, investment, and other cash receipts
    cash_categories = ["Revenue", "Investment", "Other"]
    cash_data_keys = ["revenue", "investment", "other_cash_receipts"]

    years_dict = group_months_by_year(months)

    if show_monthly:
        columns = ["Cash Flow Item"]
        for year in sorted(years_dict.keys()):
            columns.extend(years_dict[year])
            columns.append(f"{year} Total")
        columns.append("Type")  # Add dummy column to match disbursements structure
    else:
        columns = ["Cash Flow Item"] + [f"{year} Total" for year in sorted(years_dict.keys())] + ["Type"]

    # Create cash flow table data
    cash_table_data = []
    for i, category in enumerate(cash_categories):
        data_key = cash_data_keys[i]
        row = {"Cash Flow Item": category}
        
        if show_monthly:
            for year in sorted(years_dict.keys()):
                yearly_total = 0
                for month in years_dict[year]:
                    value = st.session_state.model_data["liquidity_data"][data_key].get(month, 0)
                    row[month] = value
                    yearly_total += value
                row[f"{year} Total"] = f"**{format_number(yearly_total)}**"
        else:
            for year in sorted(years_dict.keys()):
                yearly_total = sum(
                    st.session_state.model_data["liquidity_data"][data_key].get(month, 0)
                    for month in years_dict[year]
                )
                row[f"{year} Total"] = f"**{format_number(yearly_total)}**"
        
        # Add type column
        row["Type"] = "Cash Inflow"
        cash_table_data.append(row)

    cash_df = pd.DataFrame(cash_table_data)

    # Create column config exactly matching disbursements table configuration  
    if show_monthly:
        cash_column_config = {
            "Cash Flow Item": st.column_config.TextColumn("Cash Flow Item", disabled=True, width="medium", pinned=True),
            "Type": st.column_config.TextColumn("Type", disabled=True, width="medium"),
        }
        for col in columns[1:-1]:  # Skip first and last columns (like disbursements)
            if "Total" in col:
                cash_column_config[col] = st.column_config.TextColumn(col, disabled=True)
            else:
                cash_column_config[col] = st.column_config.NumberColumn(col, format="%.0f")
    else:
        cash_column_config = {
            "Cash Flow Item": st.column_config.TextColumn("Cash Flow Item", disabled=True, width="medium", pinned=True),
            "Type": st.column_config.TextColumn("Type", disabled=True, width="medium"),
            **{col: st.column_config.TextColumn(col, disabled=True) for col in columns[1:-1]}
        }

    # Display editable cash flow table
    edited_cash_df = st.data_editor(
        cash_df,
        use_container_width=True,
        num_rows="fixed",
        height=150,
        column_config=cash_column_config,
        hide_index=True,
        column_order=["Cash Flow Item"] + [col for col in columns[1:]],
        key="cash_flow_editor"
    )

    # Update session state with cash flow edits
    for i, data_key in enumerate(cash_data_keys):
        if show_monthly:
            for year in sorted(years_dict.keys()):
                for month in years_dict[year]:
                    if month in edited_cash_df.columns:
                        value = edited_cash_df.iloc[i][month]
                        st.session_state.model_data["liquidity_data"][data_key][month] = float(value) if value != '' else 0

# CASH DISBURSEMENTS SECTION - COLLAPSIBLE
with st.expander("💸 Cash Disbursements", expanded=False):
    # Expense Management Dropdown
    mgmt_col1, mgmt_col2, mgmt_col3, mgmt_col4 = st.columns([0.75, 1.083, 1.083, 1.083])

    with mgmt_col1:
        management_action = st.selectbox(
            "Expense Management:",
            ["Add New Expense Category", "Delete Expense Category", "Reorder Expense Categories"],
            key="expense_management_action"
        )

    # Display relevant section based on selection
    if management_action == "Add New Expense Category":
        exp_col1, exp_col2, exp_col3, exp_col4 = st.columns([0.75, 0.75, 1.25, 1.25])

        with exp_col1:
            new_category = st.text_input("Category Name:", key="new_category_input", placeholder="e.g., Office Supplies")

        with exp_col2:
            classification = st.selectbox("Classification:", 
                                        ["Personnel", "Product Development", "Sales and Marketing", "Opex"], 
                                        key="new_category_classification")

        with exp_col3:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            if st.button("➕ Add Category", type="primary"):
                if not new_category or new_category.strip() == "":
                    st.error("Please enter a category name!")
                elif new_category in st.session_state.model_data["liquidity_data"]["expense_categories"]:
                    st.error(f"Category '{new_category}' already exists!")
                else:
                    # Add new category
                    st.session_state.model_data["liquidity_data"]["expense_categories"][new_category] = {
                        "classification": classification, 
                        "editable": True
                    }
                    # Initialize data for new category
                    st.session_state.model_data["liquidity_data"]["expenses"][new_category] = {month: 0 for month in months}
                    
                    # Add to category_order list so it shows up in the table
                    if "category_order" not in st.session_state.model_data["liquidity_data"]:
                        st.session_state.model_data["liquidity_data"]["category_order"] = []
                    st.session_state.model_data["liquidity_data"]["category_order"].append(new_category)
                    
                    st.success(f"Added '{new_category}' to {classification}")
                    st.rerun()

    elif management_action == "Delete Expense Category":
        delete_col1, delete_col2, delete_col3, delete_col4 = st.columns([0.75, 1.083, 1.083, 1.083])

        with delete_col1:
            # Get editable categories only
            editable_categories = [cat for cat, info in st.session_state.model_data["liquidity_data"]["expense_categories"].items() 
                                  if info.get("editable", True)]
            
            if editable_categories:
                category_to_delete = st.selectbox("Select Category to Delete:", 
                                                [""] + editable_categories, 
                                                key="delete_category_select")
            else:
                st.info("No editable categories available to delete")
                category_to_delete = ""

        with delete_col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            if st.button("🗑️ Delete Category", type="secondary") and category_to_delete:
                # Show confirmation dialog
                if st.session_state.get("confirm_delete") != category_to_delete:
                    st.session_state.confirm_delete = category_to_delete
                    st.warning(f"⚠️ Are you sure you want to delete '{category_to_delete}'? This will remove all data for this category.")
                else:
                    # Delete the category
                    if category_to_delete in st.session_state.model_data["liquidity_data"]["expense_categories"]:
                        del st.session_state.model_data["liquidity_data"]["expense_categories"][category_to_delete]
                    if category_to_delete in st.session_state.model_data["liquidity_data"]["expenses"]:
                        del st.session_state.model_data["liquidity_data"]["expenses"][category_to_delete]
                    # Remove from category_order list
                    if "category_order" in st.session_state.model_data["liquidity_data"] and category_to_delete in st.session_state.model_data["liquidity_data"]["category_order"]:
                        st.session_state.model_data["liquidity_data"]["category_order"].remove(category_to_delete)
                    st.success(f"Deleted '{category_to_delete}' successfully!")
                    st.session_state.confirm_delete = None
                    st.rerun()

        # Confirm delete button
        if st.session_state.get("confirm_delete"):
            confirm_col1, confirm_col2, confirm_col3, confirm_col4 = st.columns([1, 1, 1, 1])
            with confirm_col2:
                if st.button(f"✅ Confirm Delete '{st.session_state.confirm_delete}'", type="secondary"):
                    category_to_delete = st.session_state.confirm_delete
                    # Delete the category
                    if category_to_delete in st.session_state.model_data["liquidity_data"]["expense_categories"]:
                        del st.session_state.model_data["liquidity_data"]["expense_categories"][category_to_delete]
                    if category_to_delete in st.session_state.model_data["liquidity_data"]["expenses"]:
                        del st.session_state.model_data["liquidity_data"]["expenses"][category_to_delete]
                    # Remove from category_order list
                    if "category_order" in st.session_state.model_data["liquidity_data"] and category_to_delete in st.session_state.model_data["liquidity_data"]["category_order"]:
                        st.session_state.model_data["liquidity_data"]["category_order"].remove(category_to_delete)
                    st.success(f"Deleted '{category_to_delete}' successfully!")
                    st.session_state.confirm_delete = None
                    st.rerun()

    elif management_action == "Reorder Expense Categories":
        # Initialize category order if not exists
        if "category_order" not in st.session_state.model_data["liquidity_data"]:
            st.session_state.model_data["liquidity_data"]["category_order"] = list(st.session_state.model_data["liquidity_data"]["expense_categories"].keys())

        # Get current ordered categories
        current_order = st.session_state.model_data["liquidity_data"]["category_order"]

        # Ensure all categories are in the order list (for new categories)
        all_categories = list(st.session_state.model_data["liquidity_data"]["expense_categories"].keys())
        for cat in all_categories:
            if cat not in current_order:
                current_order.append(cat)

        # Remove categories that no longer exist
        current_order = [cat for cat in current_order if cat in all_categories]
        st.session_state.model_data["liquidity_data"]["category_order"] = current_order

        # Initialize selected category in session state if not exists
        if "selected_reorder_category" not in st.session_state:
            st.session_state.selected_reorder_category = current_order[0] if current_order else None

        # Ensure selected category is still valid
        if st.session_state.selected_reorder_category not in current_order:
            st.session_state.selected_reorder_category = current_order[0] if current_order else None

        # Create interface with grouped buttons
        reorder_col1, reorder_col2, reorder_col3, reorder_col4 = st.columns([0.75, 1.083, 1.083, 1.083])

        with reorder_col1:
            if current_order:
                # Use index to maintain selection
                try:
                    current_index = current_order.index(st.session_state.selected_reorder_category)
                except (ValueError, AttributeError):
                    current_index = 0
                    
                selected_index = st.selectbox(
                    "Select Category to Move:", 
                    range(len(current_order)),
                    format_func=lambda x: current_order[x],
                    index=current_index,
                    key="reorder_category_select"
                )
                st.session_state.selected_reorder_category = current_order[selected_index]
            else:
                st.info("No categories available to reorder")

        with reorder_col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            # Create sub-columns for move buttons to be side by side
            move_col1, move_col2 = st.columns([1, 1])
            
            with move_col1:
                if st.button("⬆️ Move Up", type="secondary", use_container_width=True) and current_order:
                    current_index = current_order.index(st.session_state.selected_reorder_category)
                    if current_index > 0:
                        # Swap with previous item
                        current_order[current_index], current_order[current_index - 1] = current_order[current_index - 1], current_order[current_index]
                        st.session_state.model_data["liquidity_data"]["category_order"] = current_order
                        st.success(f"Moved '{st.session_state.selected_reorder_category}' up!")
                        st.rerun()
                    else:
                        st.warning(f"'{st.session_state.selected_reorder_category}' is already at the top!")
            
            with move_col2:
                if st.button("⬇️ Move Down", type="secondary", use_container_width=True) and current_order:
                    current_index = current_order.index(st.session_state.selected_reorder_category)
                    if current_index < len(current_order) - 1:
                        # Swap with next item
                        current_order[current_index], current_order[current_index + 1] = current_order[current_index + 1], current_order[current_index]
                        st.session_state.model_data["liquidity_data"]["category_order"] = current_order
                        st.success(f"Moved '{st.session_state.selected_reorder_category}' down!")
                        st.rerun()
                    else:
                        st.warning(f"'{st.session_state.selected_reorder_category}' is already at the bottom!")

    # Get current expense categories in the specified order
    expense_categories = st.session_state.model_data["liquidity_data"]["category_order"]

    st.info("💡 Payroll & Contractors will populate from the Headcount dashboard once synched. Expense data automatically flows to SG&A section of Income Statement")

    # Create expense table
    if expense_categories:
        create_expense_table_with_years(expense_categories, show_monthly)
    else:
        st.warning("No expense categories found.")

st.markdown("---")

# SENSITIVITY ANALYSIS
st.markdown('<div class="section-header">🔍 Sensitivity Analysis</div>', unsafe_allow_html=True)
st.info("🎯 Adjust revenue and expenses starting from a specific month to see how changes impact your cash flow and key metrics")

# Sensitivity controls
sens_col1, sens_col2, sens_col3 = st.columns([1.125, 1.125, 0.75])

# Initialize reset counter
if "sensitivity_reset_counter" not in st.session_state:
    st.session_state.sensitivity_reset_counter = 0

# Reset button (placed before widgets)
reset_col1, reset_col2 = st.columns([0.75, 3.25])
with reset_col1:
    if st.button("🔄 Reset Sensitivity", help="Reset sliders to 0% and effective date to start", use_container_width=True, type="secondary"):
        # Increment reset counter to force widget recreation
        st.session_state.sensitivity_reset_counter += 1
        st.rerun()

# Use reset counter in widget keys to force recreation
reset_suffix = f"_{st.session_state.sensitivity_reset_counter}"

with sens_col1:
    st.markdown("Revenue Adjustment")
    revenue_adjustment = st.slider(
        "Revenue Change (%)",
        min_value=-100,
        max_value=100,
        value=0,
        step=5,
        help="Adjust total revenue by this percentage",
        key=f"revenue_sensitivity{reset_suffix}"
    )
    
with sens_col2:
    st.markdown("Expense Adjustment")
    expense_adjustment = st.slider(
        "Expense Change (%)",
        min_value=-100,
        max_value=100,
        value=0,
        step=5,
        help="Adjust total expenses by this percentage",
        key=f"expense_sensitivity{reset_suffix}"
    )

with sens_col3:
    st.markdown("Effective Date")
    # Calculate current month as default
    current_date = datetime.now()
    current_month_str = current_date.strftime('%b %Y')
    try:
        current_month_index = months.index(current_month_str)
    except ValueError:
        current_month_index = 0  # Fallback to first month if current month not in list
    
    effective_month = st.selectbox(
        "Start adjustments from:",
        options=months,
        index=current_month_index,
        help="Adjustments will only apply starting from this month",
        key=f"sensitivity_effective_month{reset_suffix}"
    )

# Apply adjustments
revenue_multiplier = 1 + (revenue_adjustment / 100)
expense_multiplier = 1 + (expense_adjustment / 100)

# Get effective month index
effective_month_index = months.index(effective_month)



# CASH FLOW SUMMARY
st.markdown('<div class="section-header">📊 Cash Flow Summary</div>', unsafe_allow_html=True)

# Calculate cash flow and cumulative balance with adjustments
monthly_cash_flow, cumulative_balance = calculate_cash_flow()

# Create adjusted summary tables
total_inflows = {}
for i, month in enumerate(months):
    base_inflows = (st.session_state.model_data["liquidity_data"]["revenue"].get(month, 0) + 
                   st.session_state.model_data["liquidity_data"]["other_cash_receipts"].get(month, 0) +
                   st.session_state.model_data["liquidity_data"]["investment"].get(month, 0))
    
    # Apply adjustment only from effective month forward
    if i >= effective_month_index:
        total_inflows[month] = base_inflows * revenue_multiplier
    else:
        total_inflows[month] = base_inflows

# Calculate all cash flow components
total_outflows = {}
for i, month in enumerate(months):
    base_outflows = -sum(  # Negative because outflows
        st.session_state.model_data["liquidity_data"]["expenses"].get(category, {}).get(month, 0)
        for category in expense_categories
    )
    
    # Apply adjustment only from effective month forward
    if i >= effective_month_index:
        total_outflows[month] = base_outflows * expense_multiplier
    else:
        total_outflows[month] = base_outflows

# Calculate adjusted monthly cash flow
adjusted_monthly_cash_flow = {}
for month in months:
    adjusted_monthly_cash_flow[month] = total_inflows[month] + total_outflows[month]  # outflows are already negative

# Calculate adjusted cumulative balance
adjusted_cumulative_balance = {}
starting_balance = st.session_state.model_data["liquidity_data"]["starting_balance"]
running_balance = starting_balance
for month in months:
    running_balance += adjusted_monthly_cash_flow[month]
    adjusted_cumulative_balance[month] = running_balance

# Create combined cash flow summary table
cash_flow_summary_data = [
    {"label": "Total Cash Inflows", "data": total_inflows},
    {"label": "Total Cash Outflows", "data": total_outflows},
    {"label": "Net Cash Flow", "data": adjusted_monthly_cash_flow, "use_color": True},
    {"label": "Cumulative Cash Balance", "data": adjusted_cumulative_balance, "is_balance": True, "use_color": True}
]

create_combined_cash_flow_summary(cash_flow_summary_data, show_monthly)

st.markdown("---")

# KEY METRICS
st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)

# Add dropdown for time period selection
metrics_col1, metrics_col2 = st.columns([0.75, 3.25])
with metrics_col1:
    # Calculate default index based on current year
    current_year = str(datetime.now().year)
    metrics_options = ["2025", "2026", "2027", "2028", "2029", "2030", "All Years"]
    try:
        default_metrics_index = metrics_options.index(current_year)
    except ValueError:
        default_metrics_index = 0  # Fallback to first option if current year not in list
    
    metrics_period = st.selectbox(
        "Select time period for metrics:",
        options=metrics_options,
        index=default_metrics_index,
        key="metrics_period_select"
    )

# Determine which months to include based on selection
if metrics_period == "All Years":
    # Use all months
    filtered_months = months
else:
    # Filter for specific year
    filtered_months = [month for month in months if metrics_period in month]

# Calculate summary metrics using adjusted values for selected period
total_inflows_period = sum(total_inflows.get(month, 0) for month in filtered_months)
total_outflows_period = sum(total_outflows.get(month, 0) for month in filtered_months)
net_cash_flow_period = sum(adjusted_monthly_cash_flow.get(month, 0) for month in filtered_months)
ending_balance = adjusted_cumulative_balance[filtered_months[-1]]

# Find when we run out of money (cash balance goes negative) using adjusted values
cash_out_month = None
for month in months:
    if adjusted_cumulative_balance[month] < 0:
        cash_out_month = month
        break

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Inflows</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${total_inflows_period:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Total Outflows</h4>
        <h2 style="margin: 0.5rem 0 0 0;">${abs(total_outflows_period):,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    color = "#00D084" if net_cash_flow_period >= 0 else "#dc3545"
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Net Cash Flow</h4>
        <h2 style="margin: 0.5rem 0 0 0; color: {color};">${net_cash_flow_period:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    color = "#00D084" if ending_balance >= 0 else "#dc3545"
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Ending Balance</h4>
        <h2 style="margin: 0.5rem 0 0 0; color: {color};">${ending_balance:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col5:
    if cash_out_month:
        color = "#dc3545"
        cash_out_text = cash_out_month
    else:
        color = "#00D084"
        cash_out_text = "Sufficient"
    
    st.markdown(f"""
    <div class="metric-container">
        <h4 style="color: #00D084; margin: 0;">Cash Runway</h4>
        <h2 style="margin: 0.5rem 0 0 0; color: {color};">{cash_out_text}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# BAR GRAPH SECTION
st.markdown("") # Small spacing

# Chart type selection dropdown
chart_type_col1, chart_type_col2 = st.columns([0.75, 3.25])
with chart_type_col1:
    # Get current index based on session state
    chart_options = ["Total Inflows", "Total Outflows", "Net Cash Flow", "Ending Balance", "Gross Spend by Department", "% Spend by Department"]
    current_type = st.session_state.get("chart_type", "inflows")
    
    if current_type == "inflows":
        current_index = 0
    elif current_type == "outflows":
        current_index = 1
    elif current_type == "net":
        current_index = 2
    elif current_type == "ending_balance":
        current_index = 3
    elif current_type == "dept_gross":
        current_index = 4
    elif current_type == "dept_percent":
        current_index = 5
    else:
        current_index = 0
    
    selected_chart = st.selectbox(
        "Select chart type:",
        options=chart_options,
        index=current_index,
        key="chart_type_select"
    )
    
    # Update session state based on selection
    if selected_chart == "Total Inflows":
        st.session_state.chart_type = "inflows"
    elif selected_chart == "Total Outflows":
        st.session_state.chart_type = "outflows"
    elif selected_chart == "Net Cash Flow":
        st.session_state.chart_type = "net"
    elif selected_chart == "Ending Balance":
        st.session_state.chart_type = "ending_balance"
    elif selected_chart == "Gross Spend by Department":
        st.session_state.chart_type = "dept_gross"
    elif selected_chart == "% Spend by Department":
        st.session_state.chart_type = "dept_percent"

# Get current chart type (default to inflows)
chart_type = st.session_state.get("chart_type", "inflows")

# Calculate departmental data if needed
if chart_type in ["dept_gross", "dept_percent"]:
    department_totals = calculate_departmental_breakdown()
    department_percentages = calculate_departmental_percentages(department_totals)

# Prepare chart data based on selected year and chart type
if chart_type in ["dept_gross", "dept_percent"]:
    # Handle departmental charts differently (stacked bars)
    chart_data = None  # Will be handled in the chart creation section
    chart_df = None
    if chart_type == "dept_gross":
        chart_title = f"Gross Spend by Department"
    else:
        chart_title = f"% Spend by Department"
    
    if metrics_period != "All Years":
        chart_title += f" - {metrics_period}"
    else:
        chart_title += f" (All Years)"
        
elif metrics_period == "All Years":
    # For All Years, show yearly totals
    chart_data = {}
    years_dict = group_months_by_year(months)
    
    for year in sorted(years_dict.keys()):
        year_months = years_dict[year]
        if chart_type == "inflows":
            chart_data[str(year)] = sum(total_inflows.get(month, 0) for month in year_months)
        elif chart_type == "outflows":
            chart_data[str(year)] = abs(sum(total_outflows.get(month, 0) for month in year_months))
        elif chart_type == "net":
            chart_data[str(year)] = sum(adjusted_monthly_cash_flow.get(month, 0) for month in year_months)
        else:  # ending_balance
            # For ending balance, show the balance at the end of the year (last month)
            last_month_of_year = year_months[-1]
            chart_data[str(year)] = adjusted_cumulative_balance.get(last_month_of_year, 0)
    
    # Create DataFrame for chart
    chart_df = pd.DataFrame({
        'Period': list(chart_data.keys()),
        'Value': list(chart_data.values())
    })
    chart_title = f"{chart_type.title().replace('_', ' ')} by Year"
    
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
            if chart_type == "inflows":
                chart_data[month_name] = total_inflows.get(matching_month, 0)
            elif chart_type == "outflows":
                chart_data[month_name] = abs(total_outflows.get(matching_month, 0))
            elif chart_type == "net":
                chart_data[month_name] = adjusted_monthly_cash_flow.get(matching_month, 0)
            else:  # ending_balance
                chart_data[month_name] = adjusted_cumulative_balance.get(matching_month, 0)
        else:
            chart_data[month_name] = 0
    
    # Create DataFrame for chart
    chart_df = pd.DataFrame({
        'Period': list(chart_data.keys()),
        'Value': list(chart_data.values())
    })
    chart_title = f"{chart_type.title().replace('_', ' ')} - {metrics_period}"

# Display the chart
if chart_type in ["dept_gross", "dept_percent"]:
    # Handle departmental charts with stacked bars
    fig = go.Figure()
    
    # SHAED color palette for departments
    colors = {
        'Product Development': '#00D084',  # Primary SHAED green
        'Sales and Marketing': '#00B574',  # Darker SHAED green  
        'Operations': '#17a2b8'  # Blue for operations
    }
    
    if metrics_period == "All Years":
        # For All Years, show yearly totals by department
        years_dict = group_months_by_year(months)
        year_labels = []
        dept_chart_data = {dept: [] for dept in department_totals.keys()}
        
        for year in sorted(years_dict.keys()):
            year_labels.append(str(year))
            year_months = years_dict[year]
            
            if chart_type == "dept_gross":
                # Calculate yearly totals for each department
                for dept in department_totals.keys():
                    yearly_total = sum(department_totals[dept].get(month, 0) for month in year_months)
                    dept_chart_data[dept].append(yearly_total)
            else:  # dept_percent
                # Calculate yearly percentages for each department
                yearly_totals = {}
                total_yearly_spend = 0
                for dept in department_totals.keys():
                    yearly_total = sum(department_totals[dept].get(month, 0) for month in year_months)
                    yearly_totals[dept] = yearly_total
                    total_yearly_spend += yearly_total
                
                for dept in department_percentages.keys():
                    if total_yearly_spend > 0:
                        dept_chart_data[dept].append((yearly_totals[dept] / total_yearly_spend) * 100)
                    else:
                        dept_chart_data[dept].append(0)
        
        x_labels = year_labels
        
    else:
        # For specific year, show monthly data by department
        year_months = [month for month in months if metrics_period in month]
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_labels = []
        dept_chart_data = {dept: [] for dept in department_totals.keys()}
        
        for month_name in month_names:
            matching_month = None
            for month in year_months:
                if month.startswith(month_name):
                    matching_month = month
                    break
            
            month_labels.append(month_name)
            
            if chart_type == "dept_gross":
                for dept in department_totals.keys():
                    if matching_month:
                        dept_chart_data[dept].append(department_totals[dept].get(matching_month, 0))
                    else:
                        dept_chart_data[dept].append(0)
            else:  # dept_percent
                for dept in department_percentages.keys():
                    if matching_month:
                        dept_chart_data[dept].append(department_percentages[dept].get(matching_month, 0))
                    else:
                        dept_chart_data[dept].append(0)
        
        x_labels = month_labels
    
    # Add traces for each department
    for dept in department_totals.keys():
        if chart_type == "dept_gross":
            hovertemplate = f'<b>{dept}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>'
        else:  # dept_percent
            hovertemplate = f'<b>{dept}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>'
            
        fig.add_trace(go.Bar(
            name=dept,
            x=x_labels,
            y=dept_chart_data[dept],
            marker_color=colors[dept],
            hovertemplate=hovertemplate,
            opacity=0.8
        ))
    
    # Update layout
    if chart_type == "dept_gross":
        yaxis_format = '$,.0f'
        yaxis_title = 'Amount ($)'
        yaxis_range = None
    else:  # dept_percent
        yaxis_format = '.0f'
        yaxis_title = 'Percentage (%)'
        yaxis_range = [0, 100]
    
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color='#262730')
        ),
        barmode='stack',
        xaxis=dict(
            title='',
            showgrid=False,
            tickangle=-45 if metrics_period != "All Years" else 0
        ),
        yaxis=dict(
            title=yaxis_title,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickformat=yaxis_format,
            range=yaxis_range
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
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

elif not chart_df.empty:
    # Handle regular single-value charts
    fig = go.Figure()
    
    # Set color based on chart type
    if chart_type == "inflows":
        color = '#00D084'  # Green for inflows
    elif chart_type == "outflows":
        color = '#dc3545'  # Red for outflows  
    elif chart_type == "net":
        # Use conditional coloring for net cash flow
        colors = ['#00D084' if val >= 0 else '#dc3545' for val in chart_df['Value']]
        color = colors
    else:  # ending_balance
        # Use conditional coloring for ending balance
        colors = ['#00D084' if val >= 0 else '#dc3545' for val in chart_df['Value']]
        color = colors
    
    # Add bar trace
    fig.add_trace(go.Bar(
        x=chart_df['Period'],
        y=chart_df['Value'],
        marker_color=color,
        opacity=0.7,
        hovertemplate='<b>%{x}</b><br>$%{y:,.0f}<extra></extra>',
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
            title='Amount ($)',
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickformat='$,.0f'
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

# DATA MANAGEMENT SECTION
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

# Effective date selection for loading data - shorter list
current_year = datetime.now().year
load_effective_options = ["All Data (Replace Everything)"]

# Add only current year and next 2 years to keep dropdown manageable
for year in range(current_year, current_year + 3):
    for month_num in range(1, 13):
        month_str = f"{date(year, month_num, 1).strftime('%b %Y')}"
        if month_str in months:  # Only include months that exist in our data
            load_effective_options.append(month_str)

data_col1, data_col2, data_col3, data_col4, data_col5, data_col6 = st.columns([1, 1, 1, 1, 0.75, 1.25])

with data_col1:
    if st.button("💾 Save Data", type="primary", use_container_width=True):
        update_sga_expenses()  # Update SG&A before saving
        if save_data(st.session_state.model_data):
            st.success("Liquidity data saved and SG&A updated!")
        else:
            st.error("Failed to save data")

with data_col2:
    if st.button("📂 Load Data", type="secondary", use_container_width=True):
        load_effective_month = st.session_state.get("load_effective_month", "All Data (Replace Everything)")
        if load_effective_month == "All Data (Replace Everything)":
            st.session_state.model_data = load_data()
            load_message = "All data loaded successfully!"
            initialize_liquidity_data()
        else:
            st.session_state.model_data = load_data_from_month(load_effective_month)
            load_message = f"Data loaded from {load_effective_month} forward, historical expenses preserved!"
            initialize_liquidity_data()
        
        st.success(load_message)
        st.rerun()

with data_col3:
    # Create Excel export data
    try:
        import tempfile
        import os
        from datetime import datetime
        
        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SHAED_Liquidity_Model_{timestamp}.xlsx"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            temp_path = tmp_file.name
        
        # Create Excel writer
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            # Export Cash Receipts Data
            liquidity_data = st.session_state.model_data.get("liquidity_data", {})
            
            # Export all cash inflow components
            cash_inflows_data = {}
            if "revenue" in liquidity_data:
                cash_inflows_data['Revenue'] = liquidity_data['revenue']
            if "other_cash_receipts" in liquidity_data:
                cash_inflows_data['Other Cash Receipts'] = liquidity_data['other_cash_receipts']
            if "investment" in liquidity_data:
                cash_inflows_data['Investment'] = liquidity_data['investment']
            
            if cash_inflows_data:
                cash_inflows_df = pd.DataFrame(cash_inflows_data)
                cash_inflows_df.index.name = 'Month'
                cash_inflows_df.to_excel(writer, sheet_name='Cash Inflows')
            
            # Export Expense Categories (Cash Outflows)
            if "expenses" in liquidity_data and liquidity_data["expenses"]:
                expenses_df = pd.DataFrame(liquidity_data["expenses"])
                expenses_df.index.name = 'Month'
                expenses_df.to_excel(writer, sheet_name='Cash Outflows')
            
            # Export Cash Flow Summary with calculated values
            cash_flow_summary = []
            cumulative_balance = liquidity_data.get("starting_balance", 0)
            
            for month in months:
                # Cash inflows
                revenue = liquidity_data.get("revenue", {}).get(month, 0)
                other_receipts = liquidity_data.get("other_cash_receipts", {}).get(month, 0)
                investment = liquidity_data.get("investment", {}).get(month, 0)
                total_inflows = revenue + other_receipts + investment
                
                # Cash outflows
                total_outflows = 0
                expense_categories = liquidity_data.get("category_order", [])
                for category in expense_categories:
                    total_outflows += liquidity_data.get("expenses", {}).get(category, {}).get(month, 0)
                
                # Net cash flow and cumulative balance
                net_cash_flow = total_inflows - total_outflows
                cumulative_balance += net_cash_flow
                
                cash_flow_summary.append({
                    'Month': month,
                    'Revenue': revenue,
                    'Other Cash Receipts': other_receipts,
                    'Investment': investment,
                    'Total Cash Inflows': total_inflows,
                    'Total Cash Outflows': total_outflows,
                    'Net Cash Flow': net_cash_flow,
                    'Cumulative Cash Balance': cumulative_balance
                })
            
            if cash_flow_summary:
                cash_flow_df = pd.DataFrame(cash_flow_summary)
                cash_flow_df.to_excel(writer, sheet_name='Cash Flow Summary', index=False)
            
            # Export Departmental Breakdown Data
            department_totals = calculate_departmental_breakdown()
            department_percentages = calculate_departmental_percentages(department_totals)
            
            # Gross spend by department
            if department_totals:
                dept_gross_df = pd.DataFrame(department_totals)
                dept_gross_df.index.name = 'Month'
                dept_gross_df.to_excel(writer, sheet_name='Gross Spend by Department')
            
            # Percentage spend by department
            if department_percentages:
                dept_percent_df = pd.DataFrame(department_percentages)
                dept_percent_df.index.name = 'Month'
                dept_percent_df.to_excel(writer, sheet_name='% Spend by Department')
            
            # Export Key Metrics for different time periods
            years_dict = group_months_by_year(months)
            metrics_summary = []
            
            # Calculate metrics for each year and overall
            for year in sorted(years_dict.keys()):
                year_months = years_dict[year]
                
                year_inflows = sum(
                    liquidity_data.get("revenue", {}).get(month, 0) +
                    liquidity_data.get("other_cash_receipts", {}).get(month, 0) +
                    liquidity_data.get("investment", {}).get(month, 0)
                    for month in year_months
                )
                
                year_outflows = sum(
                    sum(liquidity_data.get("expenses", {}).get(category, {}).get(month, 0)
                        for category in expense_categories)
                    for month in year_months
                )
                
                year_net_flow = year_inflows - year_outflows
                year_end_balance = cash_flow_summary[months.index(year_months[-1])]['Cumulative Cash Balance'] if cash_flow_summary else 0
                
                metrics_summary.append({
                    'Period': year,
                    'Total Inflows': year_inflows,
                    'Total Outflows': year_outflows,
                    'Net Cash Flow': year_net_flow,
                    'Ending Balance': year_end_balance
                })
            
            # Add overall totals
            total_inflows = sum(row['Total Inflows'] for row in metrics_summary)
            total_outflows = sum(row['Total Outflows'] for row in metrics_summary)
            total_net_flow = total_inflows - total_outflows
            final_balance = metrics_summary[-1]['Ending Balance'] if metrics_summary else 0
            
            metrics_summary.append({
                'Period': 'All Years',
                'Total Inflows': total_inflows,
                'Total Outflows': total_outflows,
                'Net Cash Flow': total_net_flow,
                'Ending Balance': final_balance
            })
            
            if metrics_summary:
                metrics_df = pd.DataFrame(metrics_summary)
                metrics_df.to_excel(writer, sheet_name='Key Metrics by Period', index=False)
            
            # Export Configuration Data
            config_data = []
            config_data.append(['Starting Cash Balance', liquidity_data.get("starting_balance", 0)])
            
            # Find cash out month
            cash_out_month = None
            for row in cash_flow_summary:
                if row['Cumulative Cash Balance'] < 0:
                    cash_out_month = row['Month']
                    break
            
            config_data.append(['Cash Runway', cash_out_month if cash_out_month else 'Sufficient'])
            
            config_df = pd.DataFrame(config_data, columns=['Setting', 'Value'])
            config_df.to_excel(writer, sheet_name='Configuration', index=False)
            
            # Export Expense Categories with Classifications
            if "expense_categories" in liquidity_data:
                category_info = []
                for category, info in liquidity_data["expense_categories"].items():
                    category_info.append({
                        'Expense Category': category,
                        'Classification': info.get('classification', 'Opex'),
                        'Editable': info.get('editable', True),
                        'Auto Calculated': info.get('auto_calc', False)
                    })
                
                if category_info:
                    category_df = pd.DataFrame(category_info)
                    category_df.to_excel(writer, sheet_name='Expense Categories', index=False)
            
            # Export Yearly Totals Summary
            yearly_summary = []
            for year in sorted(years_dict.keys()):
                year_months = years_dict[year]
                
                # Calculate yearly totals for each major category
                yearly_data = {'Year': year}
                
                # Cash inflows breakdown
                yearly_data['Revenue'] = sum(liquidity_data.get("revenue", {}).get(month, 0) for month in year_months)
                yearly_data['Other Cash Receipts'] = sum(liquidity_data.get("other_cash_receipts", {}).get(month, 0) for month in year_months)
                yearly_data['Investment'] = sum(liquidity_data.get("investment", {}).get(month, 0) for month in year_months)
                yearly_data['Total Inflows'] = yearly_data['Revenue'] + yearly_data['Other Cash Receipts'] + yearly_data['Investment']
                
                # Cash outflows by department
                dept_totals_year = {dept: sum(department_totals[dept].get(month, 0) for month in year_months) for dept in department_totals.keys()}
                yearly_data['Product Development'] = dept_totals_year.get('Product Development', 0)
                yearly_data['Sales and Marketing'] = dept_totals_year.get('Sales and Marketing', 0)
                yearly_data['Operations'] = dept_totals_year.get('Operations', 0)
                yearly_data['Total Outflows'] = sum(dept_totals_year.values())
                
                # Net and ending balance
                yearly_data['Net Cash Flow'] = yearly_data['Total Inflows'] - yearly_data['Total Outflows']
                yearly_data['Ending Balance'] = cash_flow_summary[months.index(year_months[-1])]['Cumulative Cash Balance'] if cash_flow_summary else 0
                
                yearly_summary.append(yearly_data)
            
            if yearly_summary:
                yearly_df = pd.DataFrame(yearly_summary)
                yearly_df.to_excel(writer, sheet_name='Yearly Summary', index=False)
        
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

with data_col4:
    if st.button("🔄 Sync Headcount", type="secondary", use_container_width=True):
        load_effective_month = st.session_state.get("load_effective_month", "All Data (Replace Everything)")
        effective_month_for_sync = None if load_effective_month == "All Data (Replace Everything)" else load_effective_month
        update_liquidity_with_payroll(effective_month_for_sync)
        
        if effective_month_for_sync:
            st.success(f"Payroll and contractor data synced from {effective_month_for_sync} forward, historical data preserved!")
        else:
            st.success("Payroll and contractor data synced for all months!")
        
        st.rerun()

with data_col5:
    # Calculate default index for current month
    current_month_str = datetime.now().strftime('%b %Y')
    try:
        default_index = load_effective_options.index(current_month_str)
    except ValueError:
        # If current month not found, default to first option
        default_index = 0
    
    load_effective_month = st.selectbox(
        "Load Headcount Data From:",
        options=load_effective_options,
        index=default_index,
        key="load_effective_month_select",
        help="Choose when to start loading expense data. 'All Data' replaces everything, or select a specific month to preserve historical expenses."
    )
    
    # Store in session state for access by Load Data button
    st.session_state.load_effective_month = load_effective_month

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; margin-top: 3rem; border-top: 1px solid #e0e0e0;">
    <strong>SHAED Finance Dashboard - Liquidity</strong> | Powering the future of mobility<br>
    <small>© 2025 SHAED - All rights reserved</small>
</div>
""", unsafe_allow_html=True)