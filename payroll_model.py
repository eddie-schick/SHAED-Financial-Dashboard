import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
from database import load_data, save_data

# Configure page
st.set_page_config(
    page_title="Headcount",
    page_icon="👥",
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
    
    /* Employee card styling */
    .employee-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #00D084;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
    }
    
    /* Department badges */
    .dept-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.25rem 0;
    }
    
    .dept-product {
        background-color: #e3f2fd;
        color: #1565c0;
    }
    
    .dept-sales {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    
    .dept-opex {
        background-color: #fff3e0;
        color: #ef6c00;
    }
    
    /* Pay type badges */
    .pay-salary {
        background-color: #e8f5e8;
        color: #2e7d32;
    }
    
    .pay-hourly {
        background-color: #fff8e1;
        color: #f57c00;
    }
    
    /* Employee status badges */
    .status-current {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-future {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-terminated {
        background-color: #fff3e0;
        color: #ef6c00;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* DataFrames styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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

# Data persistence functions are now imported from database.py

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

def generate_employee_id():
    """Generate unique employee ID"""
    return str(uuid.uuid4())[:8]

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

def get_employee_status(emp_data):
    """Get employee status with visual indicator"""
    try:
        today = datetime.now()
        hire_date_str = emp_data.get("hire_date")
        termination_date_str = emp_data.get("termination_date")
        
        if termination_date_str:
            termination_date = datetime.strptime(termination_date_str, "%Y-%m-%d")
            if today >= termination_date:
                return "🔴 Terminated"
        
        if hire_date_str:
            hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d")
            if today < hire_date:
                return "🔵 Future Hire"
        
        return "🟢 Current"
    except (ValueError, TypeError):
        # Fall back to active field if dates are invalid
        return "🟢 Current" if emp_data.get("active", True) else "🔴 Inactive"

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



# Calculate monthly payroll expenses
def calculate_monthly_payroll():
    """Calculate monthly payroll expenses by department"""
    
    payroll_by_dept = {
        "Product Development": {month: 0 for month in months},
        "Sales and Marketing": {month: 0 for month in months}, 
        "Opex": {month: 0 for month in months}
    }
    
    total_payroll = {month: 0 for month in months}
    
    for emp_id, emp_data in st.session_state.model_data["payroll_data"]["employees"].items():
        department = emp_data.get("department", "Opex")
        pay_type = emp_data.get("pay_type", "Salary")
        
        for month in months:
            # Check if employee is active for this specific month
            if not is_employee_active_for_month(emp_data, month):
                continue
                
            if pay_type == "Salary":
                # Salary: Annual salary / 26 pay periods * pay periods in month
                annual_salary = emp_data.get("annual_salary", 0)
                pay_periods = st.session_state.model_data["payroll_data"]["pay_periods"].get(month, 2)
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

# Calculate monthly contractor expenses
def calculate_monthly_contractor_costs():
    """Calculate monthly contractor costs by department"""
    
    total_contractor_costs = {month: 0 for month in months}
    contractor_costs_by_dept = {
        "Product Development": {month: 0 for month in months},
        "Sales and Marketing": {month: 0 for month in months}, 
        "Opex": {month: 0 for month in months}
    }
    
    for contractor_data in st.session_state.model_data["payroll_data"]["contractors"].values():
        resources = contractor_data.get("resources", 0)
        hourly_rate = contractor_data.get("hourly_rate", 0)
        department = contractor_data.get("department", "Product Development")
        
        # Calculate monthly cost: resources * hourly rate * 40 hours * 4 weeks
        monthly_cost = resources * hourly_rate * 40 * 4
        
        # Apply to months where contractor is active
        for month in months:
            if is_contractor_active_for_month(contractor_data, month):
                total_contractor_costs[month] += monthly_cost
                contractor_costs_by_dept[department][month] += monthly_cost
    
    return total_contractor_costs, contractor_costs_by_dept

# Initialize payroll configuration
def initialize_payroll_config():
    """Initialize payroll configuration data"""
    # Initialize payroll_data structure if not exists
    if "payroll_data" not in st.session_state.model_data:
        st.session_state.model_data["payroll_data"] = {}
    
    # Initialize all payroll_data sub-structures
    if "employees" not in st.session_state.model_data["payroll_data"]:
        st.session_state.model_data["payroll_data"]["employees"] = {}
    
    if "contractors" not in st.session_state.model_data["payroll_data"]:
        st.session_state.model_data["payroll_data"]["contractors"] = {}
    
    if "employee_bonuses" not in st.session_state.model_data["payroll_data"]:
        st.session_state.model_data["payroll_data"]["employee_bonuses"] = {}
    
    if "pay_periods" not in st.session_state.model_data["payroll_data"]:
        st.session_state.model_data["payroll_data"]["pay_periods"] = {month: 2 for month in months}
    
    if "payroll_config" not in st.session_state.model_data["payroll_data"]:
        st.session_state.model_data["payroll_data"]["payroll_config"] = {
            "payroll_tax_percentage": 23.0  # Default 23% for payroll taxes & benefits
        }

# Calculate total personnel costs (payroll + taxes/benefits + bonuses + contractors)
def calculate_total_personnel_costs():
    """Calculate total personnel costs including payroll, taxes/benefits, bonuses, and contractors"""
    
    payroll_by_dept, total_payroll = calculate_monthly_payroll()
    contractor_costs, contractor_costs_by_dept = calculate_monthly_contractor_costs()
    
    # Get configuration
    config = st.session_state.model_data["payroll_data"]["payroll_config"]
    payroll_tax_rate = config.get("payroll_tax_percentage", 23.0) / 100.0
    
    # Calculate bonuses from table instead of percentage
    bonuses = {month: 0 for month in months}
    employee_bonuses = st.session_state.model_data["payroll_data"]["employee_bonuses"]
    
    for bonus_data in employee_bonuses.values():
        bonus_month = bonus_data.get("month", "")
        bonus_amount = bonus_data.get("bonus_amount", 0)
        
        if bonus_month in bonuses:
            bonuses[bonus_month] += bonus_amount
    
    # Calculate payroll taxes and total payroll cost
    payroll_taxes = {}
    total_payroll_cost = {}
    
    for month in months:
        base_payroll = total_payroll[month]
        monthly_bonus = bonuses[month]
        # Apply payroll taxes to both base payroll and bonuses
        monthly_taxes = (base_payroll + monthly_bonus) * payroll_tax_rate
        
        payroll_taxes[month] = monthly_taxes
        total_payroll_cost[month] = base_payroll + monthly_bonus + monthly_taxes
    
    return total_payroll, payroll_taxes, bonuses, contractor_costs, total_payroll_cost, contractor_costs_by_dept

# Update liquidity model with separate payroll and contractor costs
def update_liquidity_payroll(effective_month=None):
    """Update liquidity model with calculated payroll and contractor costs from effective month forward"""
    
    base_payroll, payroll_taxes, bonuses, contractor_costs, total_payroll_cost, contractor_costs_by_dept = calculate_total_personnel_costs()
    
    # Initialize liquidity data if needed
    if "liquidity_data" not in st.session_state.model_data:
        st.session_state.model_data["liquidity_data"] = {}
    if "expenses" not in st.session_state.model_data["liquidity_data"]:
        st.session_state.model_data["liquidity_data"]["expenses"] = {}
    
    # Initialize payroll and contractor expense categories
    if "Payroll" not in st.session_state.model_data["liquidity_data"]["expenses"]:
        st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"] = {month: 0 for month in months}
    if "Contractors" not in st.session_state.model_data["liquidity_data"]["expenses"]:
        st.session_state.model_data["liquidity_data"]["expenses"]["Contractors"] = {month: 0 for month in months}
    
    # Remove old "Total Personnel Costs" category if it exists
    if "Total Personnel Costs" in st.session_state.model_data["liquidity_data"]["expenses"]:
        del st.session_state.model_data["liquidity_data"]["expenses"]["Total Personnel Costs"]
    
    current_payroll = st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"].copy()
    current_contractor = st.session_state.model_data["liquidity_data"]["expenses"]["Contractors"].copy()
    
    if effective_month:
        # Find the index of the effective month
        try:
            effective_index = months.index(effective_month)
        except ValueError:
            st.error(f"Invalid effective month: {effective_month}")
            return
        
        # Update only from effective month forward
        for i, month in enumerate(months):
            if i >= effective_index:
                current_payroll[month] = total_payroll_cost[month]
                current_contractor[month] = contractor_costs[month]
        
        st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"] = current_payroll
        st.session_state.model_data["liquidity_data"]["expenses"]["Contractors"] = current_contractor
    else:
        # Update all months (original behavior)
        st.session_state.model_data["liquidity_data"]["expenses"]["Payroll"] = total_payroll_cost
        st.session_state.model_data["liquidity_data"]["expenses"]["Contractors"] = contractor_costs

# Header
st.markdown("""
<div class="main-header">
    <h1>👥 Headcount Planning</h1>
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
initialize_payroll_config()



# Helper function to create employee management table
def create_employee_table():
    """Create editable employee table with hire and termination dates"""
    
    # Get all employees
    employees = st.session_state.model_data["payroll_data"]["employees"]
    
    # Create table data
    table_data = []
    employee_ids = []
    
    for emp_id, emp_data in employees.items():
        employee_ids.append(emp_id)
        
        # Format pay amount based on type
        if emp_data.get("pay_type") == "Salary":
            pay_amount = emp_data.get("annual_salary", 0)
        else:
            pay_amount = emp_data.get("hourly_rate", 0)
        
        # Format dates for display
        hire_date = emp_data.get("hire_date")
        termination_date = emp_data.get("termination_date")
        
        # Convert string dates to datetime objects for the date picker
        hire_date_obj = None
        termination_date_obj = None
        
        if hire_date:
            try:
                hire_date_obj = datetime.strptime(hire_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                hire_date_obj = date(2025, 1, 1)
        else:
            hire_date_obj = date(2025, 1, 1)
        
        if termination_date:
            try:
                termination_date_obj = datetime.strptime(termination_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                termination_date_obj = None
        
        table_data.append({
            "Employee Name": emp_data.get("name", ""),
            "Title": emp_data.get("title", ""),
            "Department": emp_data.get("department", "Opex"),
            "Pay Type": emp_data.get("pay_type", "Salary"),
            "Pay Amount": pay_amount,
            "Weekly Hours": emp_data.get("weekly_hours", 40.0),
            "Hire Date": hire_date_obj,
            "Termination Date": termination_date_obj,
            "Status": get_employee_status(emp_data)
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Column configuration
    column_config = {
        "Employee Name": st.column_config.TextColumn("Employee Name", width="medium"),
        "Title": st.column_config.TextColumn("Title", width="medium"),
        "Department": st.column_config.SelectboxColumn(
            "Department",
            options=["Product Development", "Sales and Marketing", "Opex"],
            width="medium"
        ),
        "Pay Type": st.column_config.SelectboxColumn(
            "Pay Type",
            options=["Salary", "Hourly"],
            width="small"
        ),
        "Pay Amount": st.column_config.NumberColumn(
            "Pay Amount ($)",
            help="Annual salary or hourly rate",
            format="%.2f",
            width="medium"
        ),
        "Weekly Hours": st.column_config.NumberColumn(
            "Weekly Hours",
            help="Expected weekly hours (used for hourly employees)",
            min_value=0.0,
            max_value=80.0,
            step=0.5,
            format="%.1f",
            width="small"
        ),
        "Hire Date": st.column_config.DateColumn(
            "Hire Date",
            help="Date employee started",
            width="small"
        ),
        "Termination Date": st.column_config.DateColumn(
            "Termination Date", 
            help="Date employee left (leave blank if still employed)",
            width="small"
        ),
        "Status": st.column_config.TextColumn("Status", width="small")
    }
    
    # Display editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config=column_config,
        hide_index=True,
        key="employee_management_table"
    )
    
    # Update session state with changes
    # Clear existing employees
    st.session_state.model_data["payroll_data"]["employees"] = {}
    
    # Add updated employees
    for i in range(len(edited_df)):
        row = edited_df.iloc[i]
        
        # Use existing ID if available, otherwise generate new one
        if i < len(employee_ids):
            emp_id = employee_ids[i]
        else:
            emp_id = generate_employee_id()
        
        # Skip empty rows
        employee_name = str(row["Employee Name"]) if not pd.isna(row["Employee Name"]) else ""
        if not employee_name or employee_name.strip() == "":
            continue
        
        # Format dates for storage
        hire_date_str = None
        termination_date_str = None
        
        if not pd.isna(row["Hire Date"]):
            hire_date_value = row["Hire Date"]
            if isinstance(hire_date_value, str):
                hire_date_str = hire_date_value  # Already a string
            else:
                hire_date_str = hire_date_value.strftime("%Y-%m-%d")  # Convert date to string
        
        if not pd.isna(row["Termination Date"]):
            termination_date_value = row["Termination Date"]
            if isinstance(termination_date_value, str):
                termination_date_str = termination_date_value  # Already a string
            else:
                termination_date_str = termination_date_value.strftime("%Y-%m-%d")  # Convert date to string
        
        # Create employee data
        emp_data = {
            "name": employee_name,
            "title": str(row["Title"]) if not pd.isna(row["Title"]) else "",
            "department": str(row["Department"]),
            "pay_type": str(row["Pay Type"]),
            "weekly_hours": float(row["Weekly Hours"]) if not pd.isna(row["Weekly Hours"]) else 40.0,
            "hire_date": hire_date_str,
            "termination_date": termination_date_str
        }
        
        # Set pay amount based on type
        pay_amount = float(row["Pay Amount"]) if not pd.isna(row["Pay Amount"]) else 0
        if str(row["Pay Type"]) == "Salary":
            emp_data["annual_salary"] = pay_amount
            emp_data["hourly_rate"] = 0
        else:
            emp_data["hourly_rate"] = pay_amount
            emp_data["annual_salary"] = 0
        
        st.session_state.model_data["payroll_data"]["employees"][emp_id] = emp_data
    
    return edited_df

# Helper function to create employee bonus table
def create_bonus_table():
    """Create editable employee bonus table with employee name, bonus amount, and month"""
    
    # Get all bonuses
    bonuses = st.session_state.model_data["payroll_data"]["employee_bonuses"]
    
    # Create table data
    table_data = []
    bonus_ids = []
    
    for bonus_id, bonus_data in bonuses.items():
        bonus_ids.append(bonus_id)
        table_data.append({
            "Employee Name": bonus_data.get("employee_name", ""),
            "Bonus Amount": bonus_data.get("bonus_amount", 0),
            "Month": bonus_data.get("month", "Jan 2025")
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # If no bonuses exist, create empty row
    if df.empty:
        df = pd.DataFrame({
            "Employee Name": [""],
            "Bonus Amount": [0],
            "Month": ["Jan 2025"]
        })
    
    # Column configuration
    column_config = {
        "Employee Name": st.column_config.TextColumn("Employee Name", width="medium"),
        "Bonus Amount": st.column_config.NumberColumn(
            "Bonus Amount ($)",
            help="Bonus amount in dollars",
            format="%.2f",
            width="medium"
        ),
        "Month": st.column_config.SelectboxColumn(
            "Month",
            options=months,
            width="medium"
        )
    }
    
    # Display editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config=column_config,
        hide_index=True,
        key="bonus_management_table"
    )
    
    # Update session state with changes
    # Clear existing bonuses
    st.session_state.model_data["payroll_data"]["employee_bonuses"] = {}
    
    # Add updated bonuses
    for i in range(len(edited_df)):
        row = edited_df.iloc[i]
        
        # Use existing ID if available, otherwise generate new one
        if i < len(bonus_ids):
            bonus_id = bonus_ids[i]
        else:
            bonus_id = generate_employee_id()  # Reuse the same ID generator
        
        # Skip empty rows
        employee_name = str(row["Employee Name"]) if not pd.isna(row["Employee Name"]) else ""
        if not employee_name or employee_name.strip() == "":
            continue
        
        # Create bonus data
        bonus_amount = float(row["Bonus Amount"]) if not pd.isna(row["Bonus Amount"]) else 0
        if bonus_amount <= 0:
            continue
            
        bonus_data = {
            "employee_name": employee_name,
            "bonus_amount": bonus_amount,
            "month": str(row["Month"])
        }
        
        st.session_state.model_data["payroll_data"]["employee_bonuses"][bonus_id] = bonus_data
    
    return edited_df

# Helper function to create contractor table
def create_contractor_table():
    """Create editable contractor table with vendor, role, resources, hourly rate, start/end dates, and calculated monthly rate"""
    
    # Get all contractors
    contractors = st.session_state.model_data["payroll_data"]["contractors"]
    
    # Create table data
    table_data = []
    contractor_ids = []
    
    for contractor_id, contractor_data in contractors.items():
        contractor_ids.append(contractor_id)
        
        # Calculate monthly rate (resources * hourly rate * 40 hours * 4 weeks)
        resources = contractor_data.get("resources", 0)
        hourly_rate = contractor_data.get("hourly_rate", 0)
        monthly_rate = resources * hourly_rate * 40 * 4
        
        # Format dates for display
        start_date = contractor_data.get("start_date")
        end_date = contractor_data.get("end_date")
        
        # Convert string dates to datetime objects for the date picker
        start_date_obj = None
        end_date_obj = None
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                start_date_obj = date(2025, 1, 1)
        else:
            start_date_obj = date(2025, 1, 1)
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                end_date_obj = None
        
        table_data.append({
            "Vendor": contractor_data.get("vendor", ""),
            "Role": contractor_data.get("role", ""),
            "Department": contractor_data.get("department", "Product Development"),
            "# of Resources": resources,
            "Hourly Rate": hourly_rate,
            "Start Date": start_date_obj,
            "End Date": end_date_obj,
            "Monthly Rate": monthly_rate
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # If no contractors exist, create empty row
    if df.empty:
        df = pd.DataFrame({
            "Vendor": [""],
            "Role": [""],
            "Department": ["Product Development"],
            "# of Resources": [0],
            "Hourly Rate": [0],
            "Start Date": [date(2025, 1, 1)],
            "End Date": [None],
            "Monthly Rate": [0]
        })
    
    # Column configuration
    column_config = {
        "Vendor": st.column_config.TextColumn("Vendor", width="medium"),
        "Role": st.column_config.TextColumn("Role", width="medium"),
        "Department": st.column_config.SelectboxColumn(
            "Department",
            options=["Product Development", "Sales and Marketing", "Opex"],
            width="medium"
        ),
        "# of Resources": st.column_config.NumberColumn(
            "# of Resources",
            help="Number of contractor resources",
            min_value=0,
            step=0.1,
            format="%.1f",
            width="small"
        ),
        "Hourly Rate": st.column_config.NumberColumn(
            "Hourly Rate ($)",
            help="Hourly rate per resource",
            min_value=0,
            step=0.25,
            format="%.2f",
            width="medium"
        ),
        "Start Date": st.column_config.DateColumn(
            "Start Date",
            help="Date contractor engagement started",
            width="small"
        ),
        "End Date": st.column_config.DateColumn(
            "End Date", 
            help="Date contractor engagement ended (leave blank if ongoing)",
            width="small"
        ),
        "Monthly Rate": st.column_config.NumberColumn(
            "Monthly Rate ($)",
            help="Calculated as: Resources × Hourly Rate × 40 hours × 4 weeks",
            disabled=True,
            format="%.2f",
            width="medium"
        )
    }
    
    # Display editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config=column_config,
        hide_index=True,
        key="contractor_management_table"
    )
    
    # Update session state with changes
    # Clear existing contractors
    st.session_state.model_data["payroll_data"]["contractors"] = {}
    
    # Add updated contractors
    for i in range(len(edited_df)):
        row = edited_df.iloc[i]
        
        # Use existing ID if available, otherwise generate new one
        if i < len(contractor_ids):
            contractor_id = contractor_ids[i]
        else:
            contractor_id = generate_employee_id()  # Reuse the same ID generator
        
        # Skip empty rows
        vendor = str(row["Vendor"]) if not pd.isna(row["Vendor"]) else ""
        role = str(row["Role"]) if not pd.isna(row["Role"]) else ""
        if not vendor or vendor.strip() == "" or not role or role.strip() == "":
            continue
        
        # Create contractor data
        resources = float(row["# of Resources"]) if not pd.isna(row["# of Resources"]) else 0
        hourly_rate = float(row["Hourly Rate"]) if not pd.isna(row["Hourly Rate"]) else 0
        
        if resources <= 0 or hourly_rate <= 0:
            continue
        
        # Format dates for storage
        start_date_str = None
        end_date_str = None
        
        if not pd.isna(row["Start Date"]):
            start_date_value = row["Start Date"]
            if isinstance(start_date_value, str):
                start_date_str = start_date_value  # Already a string
            else:
                start_date_str = start_date_value.strftime("%Y-%m-%d")  # Convert date to string
        
        if not pd.isna(row["End Date"]):
            end_date_value = row["End Date"]
            if isinstance(end_date_value, str):
                end_date_str = end_date_value  # Already a string
            else:
                end_date_str = end_date_value.strftime("%Y-%m-%d")  # Convert date to string
            
        # Get department
        department = str(row["Department"]) if not pd.isna(row["Department"]) else "Product Development"
        
        contractor_data = {
            "vendor": vendor,
            "role": role,
            "department": department,
            "resources": resources,
            "hourly_rate": hourly_rate,
            "start_date": start_date_str,
            "end_date": end_date_str
        }
        
        st.session_state.model_data["payroll_data"]["contractors"][contractor_id] = contractor_data
    
    return edited_df

# Helper function to create department summary table
def create_department_summary_table():
    """Create department summary table showing employee counts and totals based on current date"""
    
    # Calculate department summaries
    dept_summary = {
        "Product Development": {"count": 0, "current": 0, "future": 0, "terminated": 0, "total_salary": 0, "total_hourly": 0},
        "Sales and Marketing": {"count": 0, "current": 0, "future": 0, "terminated": 0, "total_salary": 0, "total_hourly": 0},
        "Opex": {"count": 0, "current": 0, "future": 0, "terminated": 0, "total_salary": 0, "total_hourly": 0}
    }
    
    today = datetime.now()
    
    for emp_data in st.session_state.model_data["payroll_data"]["employees"].values():
        dept = emp_data.get("department", "Opex")
        if dept in dept_summary:
            dept_summary[dept]["count"] += 1
            
            # Determine employee status
            hire_date_str = emp_data.get("hire_date")
            termination_date_str = emp_data.get("termination_date")
            
            is_current = True
            is_future = False
            is_terminated = False
            
            try:
                if termination_date_str:
                    termination_date = datetime.strptime(termination_date_str, "%Y-%m-%d")
                    if today >= termination_date:
                        is_terminated = True
                        is_current = False
                
                if hire_date_str and not is_terminated:
                    hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d")
                    if today < hire_date:
                        is_future = True
                        is_current = False
            except (ValueError, TypeError):
                pass
            
            # Update counters
            if is_current:
                dept_summary[dept]["current"] += 1
                # Add salary/hourly rates for current employees
                if emp_data.get("pay_type") == "Salary":
                    dept_summary[dept]["total_salary"] += emp_data.get("annual_salary", 0)
                else:
                    dept_summary[dept]["total_hourly"] += emp_data.get("hourly_rate", 0)
            elif is_future:
                dept_summary[dept]["future"] += 1
            elif is_terminated:
                dept_summary[dept]["terminated"] += 1
    
    # Create summary table data
    summary_data = []
    for dept, data in dept_summary.items():
        summary_data.append({
            "Department": dept,
            "Total Employees": data["count"],
            "Current": data["current"],
            "Future Hires": data["future"],
            "Terminated": data["terminated"],
            "Total Annual Salary": f"${data['total_salary']:,.0f}",
            "Total Hourly Rates": f"${data['total_hourly']:,.2f}/hr"
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Column configuration for summary
    summary_column_config = {
        "Department": st.column_config.TextColumn("Department", width="medium"),
        "Total Employees": st.column_config.NumberColumn("Total", width="small"),
        "Current": st.column_config.NumberColumn("Current", width="small"),
        "Future Hires": st.column_config.NumberColumn("Future", width="small"),
        "Terminated": st.column_config.NumberColumn("Terminated", width="small"),
        "Total Annual Salary": st.column_config.TextColumn("Annual Salary (Current)", width="medium"),
        "Total Hourly Rates": st.column_config.TextColumn("Hourly Rates (Current)", width="medium")
    }
    
    # Display summary table
    st.dataframe(
        summary_df,
        use_container_width=True,
        height=150,
        column_config=summary_column_config,
        hide_index=True
    )

# View toggle
view_col1, view_col2 = st.columns([0.75, 3.25])
with view_col1:
    view_mode = st.selectbox(
        "View Mode:",
        ["Monthly + Yearly", "Yearly Only"],
        key="payroll_view_mode"
    )

# EMPLOYEE MANAGEMENT SECTION
st.markdown('<div class="section-header">👥 Employee Management</div>', unsafe_allow_html=True)

# Employee management table
tax_col1, tax_col2 = st.columns([0.75, 3.25])
with tax_col1:
    current_tax_rate = st.session_state.model_data["payroll_data"]["payroll_config"].get("payroll_tax_percentage", 23.0)
    new_tax_rate = st.number_input(
        "Payroll Tax & Benefits (%):",
        value=current_tax_rate,
        min_value=0.0,
        max_value=50.0,
        step=0.1,
        format="%.1f",
        help="Percentage of base payroll for payroll taxes, benefits, and employer contributions"
    )
    st.session_state.model_data["payroll_data"]["payroll_config"]["payroll_tax_percentage"] = new_tax_rate

st.markdown("Employee Details:")
create_employee_table()

# Employee summary
active_employees = 0
total_monthly_rate = 0

for emp_data in st.session_state.model_data["payroll_data"]["employees"].values():
    status = get_employee_status(emp_data)
    if "Current" in status:
        active_employees += 1
        
        # Calculate monthly cost for this employee
        pay_type = emp_data.get("pay_type", "Salary")
        if pay_type == "Salary":
            annual_salary = emp_data.get("annual_salary", 0)
            # Use average of 2.17 pay periods per month (26 periods / 12 months)
            monthly_cost = (annual_salary / 26) * 2.17
        else:  # Hourly
            hourly_rate = emp_data.get("hourly_rate", 0)
            weekly_hours = emp_data.get("weekly_hours", 40.0)
            monthly_hours = weekly_hours * 4.33  # Average weeks per month
            monthly_cost = hourly_rate * monthly_hours
        
        total_monthly_rate += monthly_cost

# Employee totals removed - data will be used in key metrics section

st.markdown("Employee Bonuses:")
create_bonus_table()

st.markdown("---")

# PAY PERIOD CONFIGURATION
st.markdown('<div class="section-header">📅 Pay Period Configuration</div>', unsafe_allow_html=True)

# Display current configuration and allow editing
years_dict = group_months_by_year(months)

st.markdown("Pay Periods Per Month:")
for year in sorted(years_dict.keys()):
    with st.expander(f"📅 {year} Pay Periods", expanded=False):
        year_cols = st.columns(6)
        for i, month in enumerate(years_dict[year]):
            col_idx = i % 6
            with year_cols[col_idx]:
                current_periods = st.session_state.model_data["payroll_data"]["pay_periods"].get(month, 2)
                new_periods = st.selectbox(
                    f"{month}:",
                    options=[1, 2, 3],
                    index=[1, 2, 3].index(current_periods),
                    key=f"pay_periods_{month}"
                )
                st.session_state.model_data["payroll_data"]["pay_periods"][month] = new_periods

st.markdown("---")

# CONTRACTOR MANAGEMENT
st.markdown('<div class="section-header">🏢 Contractor Management</div>', unsafe_allow_html=True)





# Contractor table
st.markdown("Contractor Details:")
create_contractor_table()

# Contractor summary
total_resources = sum(
    contractor_data.get("resources", 0)
    for contractor_data in st.session_state.model_data["payroll_data"]["contractors"].values()
)
contractor_total = sum(
    contractor_data.get("resources", 0) * contractor_data.get("hourly_rate", 0) * 40 * 4
    for contractor_data in st.session_state.model_data["payroll_data"]["contractors"].values()
)

# Contractor totals removed - data will be used in key metrics section

st.markdown("---")

# Helper function to create custom payroll table with years
def create_custom_payroll_table(categories, payroll_data, show_monthly=True):
    """Create custom payroll table matching the format from other tabs"""
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
                    value = payroll_data.get(category, {}).get(month, 0)
                    html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{format_number(value)}</td>'
                    yearly_total += value
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
        else:
            for year in sorted(years_dict.keys()):
                yearly_total = sum(
                    payroll_data.get(category, {}).get(month, 0)
                    for month in years_dict[year]
                )
                html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
        
        html_content += '</tr>'
    
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create custom payroll table with special total row formatting
def create_custom_payroll_table_with_totals(categories, payroll_data, show_monthly=True):
    """Create custom payroll table with special formatting for Total rows"""
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
        html_content += f'<th class="{css_class}" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important; text-align: center !important;">{col}</th>'
    html_content += '</tr></thead>'
    
    # Data rows
    html_content += '<tbody>'
    for category in categories:
        # Apply total-row class to Total rows
        row_class = "total-row" if category.startswith("Total") else ""
        html_content += f'<tr class="{row_class}" style="height: 43px !important;">'
        
        # Handle empty space row
        if category.strip() == "":
            if show_monthly:
                for year in sorted(years_dict.keys()):
                    for month in years_dict[year]:
                        html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"></td>'
                    html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"></td>'
            else:
                for year in sorted(years_dict.keys()):
                    html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"></td>'
        else:
            if show_monthly:
                for year in sorted(years_dict.keys()):
                    yearly_total = 0
                    for month in years_dict[year]:
                        value = payroll_data.get(category, {}).get(month, 0)
                        html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{format_number(value)}</td>'
                        yearly_total += value
                    html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
            else:
                for year in sorted(years_dict.keys()):
                    yearly_total = sum(
                        payroll_data.get(category, {}).get(month, 0)
                        for month in years_dict[year]
                    )
                    html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{format_number(yearly_total)}</strong></td>'
        
        html_content += '</tr>'
    
    html_content += '</tbody></table>'
    html_content += '</div>'
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

# Helper function to create custom payroll total row
def create_custom_payroll_total_row(total_dict, row_label, show_monthly=True):
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

# PAYROLL TABLES
st.markdown('<div class="section-header">📊 Headcount Totals</div>', unsafe_allow_html=True)

# Calculate payroll costs for tables
base_payroll, payroll_taxes, bonuses, contractor_costs, total_payroll_cost, contractor_costs_by_dept = calculate_total_personnel_costs()
payroll_by_dept, _ = calculate_monthly_payroll()  # Still needed for department breakdown

show_monthly = view_mode == "Monthly + Yearly"

# Calculate total payroll cost (base + taxes + bonuses)
total_payroll_cost = {}
for month in months:
    total_payroll_cost[month] = base_payroll[month] + payroll_taxes[month] + bonuses[month]

# Combined payroll and contractor cost breakdown with space row
empty_row = {month: 0 for month in months}  # Empty row for spacing
combined_cost_data = {
    "Base Payroll": base_payroll,
    "Employee Bonuses": bonuses,
    "Payroll Taxes & Benefits": payroll_taxes,
    "Total Payroll Cost": total_payroll_cost,
    " ": empty_row,  # Space row
    "Total Contractor Costs": contractor_costs
}
create_custom_payroll_table_with_totals(["Base Payroll", "Employee Bonuses", "Payroll Taxes & Benefits", "Total Payroll Cost", " ", "Total Contractor Costs"], combined_cost_data, show_monthly)

st.markdown("---")

# KEY METRICS
st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)

# Time period and metrics selection
metric_col1, metric_col2, metric_col3 = st.columns([0.75, 0.75, 2.5])

with metric_col1:
    # Add dropdown for time period selection
    summary_options = ["Current", "2025", "2026", "2027", "2028", "2029", "2030", "All Years"]
    try:
        current_year = str(datetime.now().year)
        default_index = summary_options.index(current_year) if current_year in summary_options else 0
    except ValueError:
        default_index = 0
    
    selected_period = st.selectbox(
        "Select time period:",
        options=summary_options,
        index=default_index,
        key="headcount_period_select"
    )

with metric_col2:
    # Add dropdown for metrics selection
    metrics_options = ["Headcount Overview", "Department Breakdown"]
    selected_metrics = st.selectbox(
        "Select Key Metrics:",
        options=metrics_options,
        index=0,
        key="headcount_metrics_select"
    )

# Helper function to get employee status for a specific year
def get_employee_status_for_year(emp_data, year):
    """Get employee status for a specific year (as of Dec 31 of that year)"""
    try:
        if year == "Current":
            # Use current date
            reference_date = datetime.now()
        else:
            # Use Dec 31 of the selected year
            reference_date = datetime(int(year), 12, 31)
        
        hire_date_str = emp_data.get("hire_date")
        termination_date_str = emp_data.get("termination_date")
        
        if termination_date_str:
            termination_date = datetime.strptime(termination_date_str, "%Y-%m-%d")
            if reference_date >= termination_date:
                return "🔴 Terminated"
        
        if hire_date_str:
            hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d")
            if reference_date < hire_date:
                return "🔵 Future Hire"
        
        return "🟢 Current"
    except (ValueError, TypeError):
        # Fall back to active field if dates are invalid
        return "🟢 Current" if emp_data.get("active", True) else "🔴 Inactive"

# Calculate headcount metrics based on selected period
current_employees = 0
future_employees = 0
terminated_employees = 0

for emp_data in st.session_state.model_data["payroll_data"]["employees"].values():
    status = get_employee_status_for_year(emp_data, selected_period)
    if "Current" in status:
        current_employees += 1
    elif "Future" in status:
        future_employees += 1
    elif "Terminated" in status:
        terminated_employees += 1

total_employees = current_employees + future_employees + terminated_employees

# Calculate contractor metrics
total_contractors = len(st.session_state.model_data["payroll_data"]["contractors"])
active_contractors = 0
for contractor_data in st.session_state.model_data["payroll_data"]["contractors"].values():
    # Simplified active check - could be enhanced with date logic
    if contractor_data.get("resources", 0) > 0 and contractor_data.get("hourly_rate", 0) > 0:
        active_contractors += 1

# Calculate financial totals based on selected period
if selected_period == "Current":
    # Show 6-year totals for current view
    total_base_payroll = sum(base_payroll.values())
    total_payroll_taxes = sum(payroll_taxes.values())
    total_bonuses = sum(bonuses.values())
    total_contractor_costs = sum(contractor_costs.values())
    total_payroll_cost_sum = sum(total_payroll_cost.values())
    period_label = "6-Year Total"
    divisor = 6
elif selected_period == "All Years":
    # Show 6-year totals
    total_base_payroll = sum(base_payroll.values())
    total_payroll_taxes = sum(payroll_taxes.values())
    total_bonuses = sum(bonuses.values())
    total_contractor_costs = sum(contractor_costs.values())
    total_payroll_cost_sum = sum(total_payroll_cost.values())
    period_label = "6-Year Total"
    divisor = 6
else:
    # Show specific year totals
    year_months = [f"{month} {selected_period}" for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
    total_base_payroll = sum(base_payroll.get(month, 0) for month in year_months)
    total_payroll_taxes = sum(payroll_taxes.get(month, 0) for month in year_months)
    total_bonuses = sum(bonuses.get(month, 0) for month in year_months)
    total_contractor_costs = sum(contractor_costs.get(month, 0) for month in year_months)
    total_payroll_cost_sum = sum(total_payroll_cost.get(month, 0) for month in year_months)
    period_label = f"{selected_period} Total"
    divisor = 1

# Conditional KPI display based on selected metrics
if selected_metrics == "Headcount Overview":
    # Headcount Overview KPIs
    headcount_col1, headcount_col2, headcount_col3, headcount_col4, headcount_col5 = st.columns(5)

    with headcount_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">🟢 Current Employees</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{current_employees}</h2>
        </div>
        """, unsafe_allow_html=True)

    with headcount_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">🔵 Future Hires</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{future_employees}</h2>
        </div>
        """, unsafe_allow_html=True)

    with headcount_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">🔴 Terminated</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{terminated_employees}</h2>
        </div>
        """, unsafe_allow_html=True)

    with headcount_col4:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">🏢 Active Contractors</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{active_contractors}</h2>
        </div>
        """, unsafe_allow_html=True)

    with headcount_col5:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📊 Total Headcount</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{current_employees + active_contractors}</h2>
        </div>
        """, unsafe_allow_html=True)

elif selected_metrics == "Department Breakdown":
    # Department Breakdown KPIs
    dept_col1, dept_col2, dept_col3, dept_col4 = st.columns(4)

    dept_totals = {}
    for dept in ["Product Development", "Sales and Marketing", "Opex"]:
        if selected_period in ["Current", "All Years"]:
            dept_total = sum(payroll_by_dept[dept].values()) / divisor
            # Add contractor costs to each department
            dept_contractor_total = sum(contractor_costs_by_dept[dept].values()) / divisor
            dept_total += dept_contractor_total
            dept_totals[dept] = dept_total
        else:
            year_months = [f"{month} {selected_period}" for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
            dept_total = sum(payroll_by_dept[dept].get(month, 0) for month in year_months)
            # Add contractor costs for specific year
            dept_contractor_total = sum(contractor_costs_by_dept[dept].get(month, 0) for month in year_months)
            dept_total += dept_contractor_total
            dept_totals[dept] = dept_total

    with dept_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">🔧 Product Development</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${dept_totals["Product Development"]:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Annual Payroll + Contractors</p>
        </div>
        """, unsafe_allow_html=True)

    with dept_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📈 Sales and Marketing</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${dept_totals["Sales and Marketing"]:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Annual Payroll + Contractors</p>
        </div>
        """, unsafe_allow_html=True)

    with dept_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">⚙️ Operations</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${dept_totals["Opex"]:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Annual Payroll + Contractors</p>
        </div>
        """, unsafe_allow_html=True)

    with dept_col4:
        # Calculate total personnel cost across all departments
        total_dept_cost = sum(dept_totals.values())
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📊 Total Personnel Cost</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${total_dept_cost:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">All Departments</p>
        </div>
        """, unsafe_allow_html=True)

# Calculate total personnel costs for chart usage
total_personnel_costs_sum = total_payroll_cost_sum + total_contractor_costs

# Chart section
st.markdown("") # Small spacing
st.markdown("---") # Line separator

# Chart type selection dropdown
chart_type_col1, chart_type_col2 = st.columns([0.75, 3.25])
with chart_type_col1:
    chart_options = ["Total Personnel Cost", "Payroll Cost", "Contractor Cost", "Headcount", "Department Breakdown", "Personnel Cost %"]
    selected_chart = st.selectbox(
        "Select chart type:",
        options=chart_options,
        index=0,
        key="headcount_chart_type_select"
    )

# Prepare chart data based on selected period and chart type
if selected_period == "All Years":
    # For All Years, show yearly totals
    chart_data = {}
    years_dict = group_months_by_year(months)
    
    for year in sorted(years_dict.keys()):
        year_months = years_dict[year]
        if selected_chart == "Total Personnel Cost":
            payroll_total = sum(total_payroll_cost.get(month, 0) for month in year_months)
            contractor_total = sum(contractor_costs.get(month, 0) for month in year_months)
            chart_data[str(year)] = payroll_total + contractor_total
        elif selected_chart == "Payroll Cost":
            chart_data[str(year)] = sum(total_payroll_cost.get(month, 0) for month in year_months)
        elif selected_chart == "Contractor Cost":
            chart_data[str(year)] = sum(contractor_costs.get(month, 0) for month in year_months)
        elif selected_chart == "Headcount":
            # For headcount, just show current count for each year (simplified)
            chart_data[str(year)] = current_employees + active_contractors
        elif selected_chart == "Department Breakdown":
            # For department breakdown, we'll store data differently for stacking
            if str(year) not in chart_data:
                chart_data[str(year)] = {}
            
            # Calculate each department total (payroll + department-specific contractors)
            for dept in ["Product Development", "Sales and Marketing", "Opex"]:
                payroll_total = sum(payroll_by_dept[dept].get(month, 0) for month in year_months)
                contractor_total = sum(contractor_costs_by_dept[dept].get(month, 0) for month in year_months)
                # Use "Operations" as the key for display consistency with Opex
                display_key = "Operations" if dept == "Opex" else dept
                chart_data[str(year)][display_key] = payroll_total + contractor_total
        elif selected_chart == "Personnel Cost %":
            # For percentage breakdown, we'll store data differently for stacking
            if str(year) not in chart_data:
                chart_data[str(year)] = {}
            
            # Calculate department totals (payroll + department-specific contractors)
            dept_totals_year = {}
            total_personnel = 0
            
            for dept in ["Product Development", "Sales and Marketing", "Opex"]:
                payroll_total = sum(payroll_by_dept[dept].get(month, 0) for month in year_months)
                contractor_total = sum(contractor_costs_by_dept[dept].get(month, 0) for month in year_months)
                dept_total = payroll_total + contractor_total
                display_key = "Operations" if dept == "Opex" else dept
                dept_totals_year[display_key] = dept_total
                total_personnel += dept_total
            
            # Calculate percentages
            if total_personnel > 0:
                for display_key, dept_total in dept_totals_year.items():
                    chart_data[str(year)][display_key] = (dept_total / total_personnel) * 100
            else:
                chart_data[str(year)]["Product Development"] = 0
                chart_data[str(year)]["Sales and Marketing"] = 0
                chart_data[str(year)]["Operations"] = 0
    
    chart_title = f"{selected_chart} by Year"
    x_label = "Year"
    
else:
    # For specific year or current, show monthly data
    if selected_period == "Current":
        # Show all months from 2025-2030
        chart_months = months[:12]  # Show first year as sample
        chart_title = f"{selected_chart} - 2025 Sample"
    else:
        # Show specific year
        chart_months = [f"{month_name} {selected_period}" for month_name in 
                       ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
        chart_title = f"{selected_chart} - {selected_period}"
    
    chart_data = {}
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for i, month_name in enumerate(month_names):
        if i < len(chart_months):
            month = chart_months[i]
            if selected_chart == "Total Personnel Cost":
                payroll_value = total_payroll_cost.get(month, 0)
                contractor_value = contractor_costs.get(month, 0)
                chart_data[month_name] = payroll_value + contractor_value
            elif selected_chart == "Payroll Cost":
                chart_data[month_name] = total_payroll_cost.get(month, 0)
            elif selected_chart == "Contractor Cost":
                chart_data[month_name] = contractor_costs.get(month, 0)
            elif selected_chart == "Headcount":
                # Simplified headcount for chart
                chart_data[month_name] = current_employees + active_contractors
            elif selected_chart == "Department Breakdown":
                # For department breakdown, we'll store data differently for stacking
                if month_name not in chart_data:
                    chart_data[month_name] = {}
                
                # Calculate each department total (payroll + department-specific contractors)
                for dept in ["Product Development", "Sales and Marketing", "Opex"]:
                    payroll_value = payroll_by_dept[dept].get(month, 0)
                    contractor_value = contractor_costs_by_dept[dept].get(month, 0)
                    display_key = "Operations" if dept == "Opex" else dept
                    chart_data[month_name][display_key] = payroll_value + contractor_value
            elif selected_chart == "Personnel Cost %":
                # For percentage breakdown, we'll store data differently for stacking
                if month_name not in chart_data:
                    chart_data[month_name] = {}
                
                # Calculate department totals for this month (payroll + department-specific contractors)
                dept_totals_month = {}
                total_personnel = 0
                
                for dept in ["Product Development", "Sales and Marketing", "Opex"]:
                    payroll_value = payroll_by_dept[dept].get(month, 0)
                    contractor_value = contractor_costs_by_dept[dept].get(month, 0)
                    dept_total = payroll_value + contractor_value
                    display_key = "Operations" if dept == "Opex" else dept
                    dept_totals_month[display_key] = dept_total
                    total_personnel += dept_total
                
                # Calculate percentages
                if total_personnel > 0:
                    for display_key, dept_total in dept_totals_month.items():
                        chart_data[month_name][display_key] = (dept_total / total_personnel) * 100
                else:
                    chart_data[month_name]["Product Development"] = 0
                    chart_data[month_name]["Sales and Marketing"] = 0
                    chart_data[month_name]["Operations"] = 0
        else:
            if selected_chart in ["Department Breakdown", "Personnel Cost %"]:
                chart_data[month_name] = {"Product Development": 0, "Sales and Marketing": 0, "Operations": 0}
            else:
                chart_data[month_name] = 0
    
    x_label = "Month"

# Display the chart
if chart_data:
    import plotly.graph_objects as go
    
    # Create Plotly figure
    fig = go.Figure()
    
    if selected_chart in ["Department Breakdown", "Personnel Cost %"]:
        # Create stacked bar chart for departments
        departments = ["Product Development", "Sales and Marketing", "Opex"]
        colors = ['#00D084', '#7B1FA2', '#F39C12']  # Green, Purple, Orange
        
        # Set y-axis title based on chart type
        if selected_chart == "Personnel Cost %":
            y_title = 'Percentage (%)'
        else:
            y_title = 'Amount ($)'
        
        for i, dept in enumerate(departments):
            x_values = list(chart_data.keys())
            # Map display name to data key for Opex
            data_key = "Operations" if dept == "Opex" else dept
            y_values = [chart_data[x].get(data_key, 0) for x in x_values]
            
            # Create hover template for each chart type
            if selected_chart == "Personnel Cost %":
                hover_template = f'<b>%{{x}}</b><br>{dept}: %{{y:.1f}}%<extra></extra>'
            else:
                hover_template = f'<b>%{{x}}</b><br>{dept}: $%{{y:,.0f}}<extra></extra>'
            
            fig.add_trace(go.Bar(
                name=dept,
                x=x_values,
                y=y_values,
                marker_color=colors[i],
                opacity=0.8,
                hovertemplate=hover_template
            ))
        
        # Update layout for stacked bars
        fig.update_layout(barmode='stack')
        
    else:
        # Create regular single bar chart
        # Set color based on chart type
        if selected_chart == "Total Personnel Cost":
            color = '#00D084'  # Main green
        elif selected_chart == "Payroll Cost":
            color = '#00B574'  # Dark green
        elif selected_chart == "Contractor Cost":
            color = '#F39C12'  # Orange
        elif selected_chart == "Headcount":
            color = '#3498DB'  # Blue
        else:
            color = '#7B1FA2'  # Purple
        
        # Format hover template based on chart type
        if selected_chart == "Headcount":
            hover_template = '<b>%{x}</b><br>%{y} people<extra></extra>'
            y_title = 'Count'
        else:
            hover_template = '<b>%{x}</b><br>$%{y:,.0f}<extra></extra>'
            y_title = 'Amount ($)'
        
        # Add bar trace
        fig.add_trace(go.Bar(
            x=list(chart_data.keys()),
            y=list(chart_data.values()),
            marker_color=color,
            opacity=0.7,
            hovertemplate=hover_template,
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color='#262730')
        ),
        xaxis=dict(
            title=x_label,
            showgrid=False,
            tickangle=-45 if selected_period != "All Years" else 0
        ),
        yaxis=dict(
            title=y_title,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickformat='$,.0f' if selected_chart not in ["Headcount", "Personnel Cost %"] else (',' if selected_chart == "Headcount" else '.1f')
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        height=350,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ) if selected_chart in ["Department Breakdown", "Personnel Cost %"] else {}
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)



# DATA MANAGEMENT
st.markdown("---")
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

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

with col3:
    # Create Excel export for payroll data
    try:
        import tempfile
        import os
        from datetime import datetime
        
        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SHAED_Headcount_Planning_{timestamp}.xlsx"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            temp_path = tmp_file.name
        
        # Create Excel writer
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            # Export Employee Data
            employees = st.session_state.model_data["payroll_data"]["employees"]
            if employees:
                employee_data = []
                for emp_id, emp_data in employees.items():
                    employee_data.append({
                        'Employee ID': emp_id,
                        'Name': emp_data.get('name', ''),
                        'Title': emp_data.get('title', ''),
                        'Department': emp_data.get('department', ''),
                        'Pay Type': emp_data.get('pay_type', ''),
                        'Annual Salary': emp_data.get('annual_salary', 0),
                        'Hourly Rate': emp_data.get('hourly_rate', 0),
                        'Weekly Hours': emp_data.get('weekly_hours', 40),
                        'Hire Date': emp_data.get('hire_date', ''),
                        'Termination Date': emp_data.get('termination_date', ''),
                        'Status': get_employee_status(emp_data)
                    })
                
                if employee_data:
                    emp_df = pd.DataFrame(employee_data)
                    emp_df.to_excel(writer, sheet_name='Employees', index=False)
            
            # Export Contractor Data
            contractors = st.session_state.model_data["payroll_data"]["contractors"]
            if contractors:
                contractor_data = []
                for contractor_id, contractor_data_dict in contractors.items():
                                    contractor_data.append({
                    'Contractor ID': contractor_id,
                    'Vendor': contractor_data_dict.get('vendor', ''),
                    'Role': contractor_data_dict.get('role', ''),
                    'Department': contractor_data_dict.get('department', 'Product Development'),
                    'Resources': contractor_data_dict.get('resources', 0),
                    'Hourly Rate': contractor_data_dict.get('hourly_rate', 0),
                    'Start Date': contractor_data_dict.get('start_date', ''),
                    'End Date': contractor_data_dict.get('end_date', ''),
                    'Monthly Rate': contractor_data_dict.get('resources', 0) * contractor_data_dict.get('hourly_rate', 0) * 40 * 4
                })
                
                if contractor_data:
                    contractor_df = pd.DataFrame(contractor_data)
                    contractor_df.to_excel(writer, sheet_name='Contractors', index=False)
            
            # Export Payroll Summary by Month
            base_payroll, payroll_taxes, bonuses, contractor_costs, total_payroll_cost, contractor_costs_by_dept = calculate_total_personnel_costs()
            payroll_by_dept, _ = calculate_monthly_payroll()
            
            payroll_summary = []
            for month in months:
                # Calculate department totals including department-specific contractor costs
                product_dev_total = payroll_by_dept['Product Development'].get(month, 0) + contractor_costs_by_dept['Product Development'].get(month, 0)
                sales_marketing_total = payroll_by_dept['Sales and Marketing'].get(month, 0) + contractor_costs_by_dept['Sales and Marketing'].get(month, 0)
                opex_total = payroll_by_dept['Opex'].get(month, 0) + contractor_costs_by_dept['Opex'].get(month, 0)
                
                payroll_summary.append({
                    'Month': month,
                    'Base Payroll': base_payroll.get(month, 0),
                    'Payroll Taxes & Benefits': payroll_taxes.get(month, 0),
                    'Employee Bonuses': bonuses.get(month, 0),
                    'Total Payroll Cost': total_payroll_cost.get(month, 0),
                    'Contractor Costs': contractor_costs.get(month, 0),
                    'Total Personnel Costs': total_payroll_cost.get(month, 0) + contractor_costs.get(month, 0),
                    'Product Development': product_dev_total,
                    'Sales and Marketing': sales_marketing_total,
                    'Opex': opex_total
                })
            
            if payroll_summary:
                payroll_df = pd.DataFrame(payroll_summary)
                payroll_df.to_excel(writer, sheet_name='Payroll Summary', index=False)
            
            # Export Department Summary with contractor costs
            dept_summary_data = []
            years_dict = group_months_by_year(months)
            
            for year in sorted(years_dict.keys()):
                year_months = years_dict[year]
                for dept in ["Product Development", "Sales and Marketing", "Opex"]:
                    # Calculate totals for this department and year
                    payroll_total = sum(payroll_by_dept[dept].get(month, 0) for month in year_months)
                    contractor_total = sum(contractor_costs_by_dept[dept].get(month, 0) for month in year_months)
                    combined_total = payroll_total + contractor_total
                    
                    dept_summary_data.append({
                        'Year': year,
                        'Department': dept,
                        'Payroll Cost': payroll_total,
                        'Contractor Cost': contractor_total,
                        'Total Department Cost': combined_total,
                        'Average Monthly': combined_total / 12 if combined_total > 0 else 0
                    })
            
            if dept_summary_data:
                dept_summary_df = pd.DataFrame(dept_summary_data)
                dept_summary_df.to_excel(writer, sheet_name='Department Summary', index=False)
            
            # Export Contractor Costs by Department and Month
            contractor_breakdown_data = []
            for month in months:
                for dept in ["Product Development", "Sales and Marketing", "Opex"]:
                    contractor_cost = contractor_costs_by_dept[dept].get(month, 0)
                    if contractor_cost > 0:  # Only include months with contractor costs
                        contractor_breakdown_data.append({
                            'Month': month,
                            'Department': dept,
                            'Contractor Cost': contractor_cost
                        })
            
            if contractor_breakdown_data:
                contractor_breakdown_df = pd.DataFrame(contractor_breakdown_data)
                contractor_breakdown_df.to_excel(writer, sheet_name='Contractor Breakdown', index=False)
            
            # Export Employee Bonuses
            bonuses_data = st.session_state.model_data["payroll_data"]["employee_bonuses"]
            if bonuses_data:
                bonus_export_data = []
                for bonus_id, bonus_data in bonuses_data.items():
                    bonus_export_data.append({
                        'Bonus ID': bonus_id,
                        'Employee Name': bonus_data.get('employee_name', ''),
                        'Bonus Amount': bonus_data.get('bonus_amount', 0),
                        'Month': bonus_data.get('month', '')
                    })
                
                if bonus_export_data:
                    bonus_df = pd.DataFrame(bonus_export_data)
                    bonus_df.to_excel(writer, sheet_name='Employee Bonuses', index=False)
            
            # Export Annual Department Totals Summary
            annual_totals_data = []
            for dept in ["Product Development", "Sales and Marketing", "Opex"]:
                total_payroll = sum(payroll_by_dept[dept].values())
                total_contractors = sum(contractor_costs_by_dept[dept].values())
                total_combined = total_payroll + total_contractors
                
                annual_totals_data.append({
                    'Department': dept,
                    '6-Year Payroll Total': total_payroll,
                    '6-Year Contractor Total': total_contractors,
                    '6-Year Combined Total': total_combined,
                    'Annual Average': total_combined / 6,
                    'Monthly Average': total_combined / 72  # 6 years * 12 months
                })
            
            # Add overall totals row
            total_payroll_all = sum(sum(payroll_by_dept[dept].values()) for dept in ["Product Development", "Sales and Marketing", "Opex"])
            total_contractors_all = sum(sum(contractor_costs_by_dept[dept].values()) for dept in ["Product Development", "Sales and Marketing", "Opex"])
            total_combined_all = total_payroll_all + total_contractors_all
            
            annual_totals_data.append({
                'Department': 'TOTAL',
                '6-Year Payroll Total': total_payroll_all,
                '6-Year Contractor Total': total_contractors_all,
                '6-Year Combined Total': total_combined_all,
                'Annual Average': total_combined_all / 6,
                'Monthly Average': total_combined_all / 72
            })
            
            annual_totals_df = pd.DataFrame(annual_totals_data)
            annual_totals_df.to_excel(writer, sheet_name='Annual Totals', index=False)
        
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

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; margin-top: 3rem; border-top: 1px solid #e0e0e0;">
    <strong>SHAED Financial Model - Headcount Planning</strong> | Powering the future of mobility<br>
    <small>© 2025 SHAED - All rights reserved</small>
</div>
""", unsafe_allow_html=True)