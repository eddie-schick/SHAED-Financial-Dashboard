import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go
from database import load_data, save_data, load_data_from_source, save_data_to_source, save_gross_profit_data_to_database, save_revenue_and_cogs_to_database
# load_gross_profit_data_from_database removed - using load_data instead

# Configure page
st.set_page_config(
    page_title="Gross Profit",
    page_icon="🔍",
    layout="wide"
)

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

# Custom CSS for SHAED branding (matching other dashboards)
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
    }
    
    /* Section headers */
    .section-header {
        background-color: #00D084;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 5px;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    

    
    /* Metric containers */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
        height: 100%;
    }
    
    .metric-container h4 {
        color: #00D084;
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-container h2 {
        margin: 0;
        font-size: 2rem;
        color: #1a1a1a;
    }
    
    /* Custom table styling */
    .custom-table-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        overflow-x: auto;
    }
    
    .table-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #00D084;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
    }
    
    /* Streamlit native element styling */
    .stButton > button {
        background-color: #00D084;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #00B574;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    /* Hosting cost preview */
    .hosting-preview {
        background: #f0f9ff;
        border: 2px solid #00D084;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
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

# Data handling functions are now imported from database.py

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

# Helper functions
def format_number(num):
    """Format number with commas and handle negatives properly"""
    if num == 0:
        return "0"
    if num < 0:
        return f"({abs(num):,.0f})"
    return f"{num:,.0f}"

def format_percentage(num):
    """Format number as percentage"""
    return f"{num:.1f}%"

def get_year_from_month(month_str):
    """Extract year from month string like 'Jan 2025'"""
    return month_str.split(' ')[1]

def group_months_by_year(months):
    """Group months by year and return dict"""
    years = {}
    for month in months:
        year = get_year_from_month(month)
        if year not in years:
            years[year] = []
        years[year].append(month)
    return years

# Initialize gross profit data structure
def initialize_gross_profit_data():
    """Initialize the gross profit data structure"""
    if "gross_profit_data" not in st.session_state.model_data:
        # Load data from model_settings via load_data instead of dedicated function
        try:
            full_data = load_data()
            if "gross_profit_data" in full_data:
                st.session_state.model_data["gross_profit_data"] = full_data["gross_profit_data"]
            else:
                st.session_state.model_data["gross_profit_data"] = {}
        except:
            st.session_state.model_data["gross_profit_data"] = {}
    
    # Revenue streams to track
    revenue_streams = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    
    # Initialize gross profit percentages for each stream
    if "gross_profit_percentages" not in st.session_state.model_data["gross_profit_data"]:
        st.session_state.model_data["gross_profit_data"]["gross_profit_percentages"] = {
            stream: {month: 70.0 for month in months}  # Default 70% gross profit
            for stream in revenue_streams
        }
    
    # Initialize SaaS hosting cost structure
    if "saas_hosting_structure" not in st.session_state.model_data["gross_profit_data"]:
        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"] = {
            "fixed_monthly_cost": 500.0,  # Legacy - kept for backward compatibility
            "cost_per_customer": 0.50,    # Legacy - kept for backward compatibility
            "go_live_month": "Jan 2025",  # Default go-live date
            "capitalize_before_go_live": True  # Toggle for capitalization
        }
    
    # Initialize monthly hosting costs (new structure)
    if "monthly_fixed_costs" not in st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]:
        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_fixed_costs"] = {
            month: 15400.0 for month in months  # Default $15,400/month
        }
    
    if "monthly_variable_costs" not in st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]:
        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_variable_costs"] = {
            month: 5.0 for month in months  # Default $5.00/customer
        }
    
    # Initialize other direct costs
    if "direct_costs" not in st.session_state.model_data["gross_profit_data"]:
        st.session_state.model_data["gross_profit_data"]["direct_costs"] = {
            stream: {month: 0 for month in months}
            for stream in revenue_streams
        }

# Get active subscribers from revenue assumptions
def get_active_subscribers(month):
    """Get total active subscribers for a given month"""
    if "subscription_running_totals" not in st.session_state.model_data:
        return 0
    
    total_subscribers = 0
    for stakeholder, monthly_data in st.session_state.model_data["subscription_running_totals"].items():
        total_subscribers += monthly_data.get(month, 0)
    
    return total_subscribers

# Calculate hosting costs based on structure
def calculate_hosting_costs():
    """Calculate monthly hosting costs based on monthly fixed + variable structure"""
    hosting_structure = st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]
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

# Calculate COGS and update income statement
def calculate_cogs():
    """Calculate COGS based on revenue and gross profit percentages"""
    if "revenue" not in st.session_state.model_data:
        return {stream: {month: 0 for month in months} for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]}
    
    cogs_by_stream = {}
    revenue_data = st.session_state.model_data.get("revenue", {})
    gp_data = st.session_state.model_data.get("gross_profit_data", {})
    
    # Calculate hosting costs for subscription
    hosting_costs, capitalized_hosting = calculate_hosting_costs()
    
    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
        cogs_by_stream[stream] = {}
        
        for month in months:
            revenue = revenue_data.get(stream, {}).get(month, 0)
            
            if stream == "Subscription":
                # For subscription, COGS = hosting costs + other direct costs
                cogs_by_stream[stream][month] = hosting_costs.get(month, 0) + gp_data.get("direct_costs", {}).get(stream, {}).get(month, 0)
            else:
                # For other streams, use gross profit percentage
                gp_percentage = gp_data.get("gross_profit_percentages", {}).get(stream, {}).get(month, 70.0)
                cogs_by_stream[stream][month] = revenue * (1 - gp_percentage / 100)
    
    return cogs_by_stream

def update_income_statement_cogs():
    """Update COGS in the income statement"""
    cogs_by_stream = calculate_cogs()
    
    # Initialize COGS in model data if not exists
    if "cogs" not in st.session_state.model_data:
        st.session_state.model_data["cogs"] = {}
    
    # Update COGS for each stream
    for stream, monthly_cogs in cogs_by_stream.items():
        st.session_state.model_data["cogs"][stream] = monthly_cogs
    
    # Calculate total COGS
    total_cogs = {}
    for month in months:
        total_cogs[month] = sum(
            cogs_by_stream[stream].get(month, 0) 
            for stream in cogs_by_stream
        )
    st.session_state.model_data["cogs"]["Total"] = total_cogs

# Create hosting cost preview chart
def create_hosting_cost_chart():
    """Create a visual chart showing hosting costs at different customer levels"""
    hosting_structure = st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]
    fixed_cost = hosting_structure["fixed_monthly_cost"]
    variable_cost = hosting_structure["cost_per_customer"]
    
    # Generate data points
    customer_counts = [0, 100, 500, 1000, 2500, 5000, 10000]
    hosting_costs = [fixed_cost + (variable_cost * count) for count in customer_counts]
    
    # Create plotly chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=customer_counts,
        y=hosting_costs,
        mode='lines+markers',
        name='Hosting Cost',
        line=dict(color='#00D084', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Hosting Cost Projection",
        xaxis_title="Number of Active Customers",
        yaxis_title="Monthly Hosting Cost ($)",
        height=300,
        showlegend=False,
        plot_bgcolor='white',
        yaxis=dict(tickformat='$,.0f'),
        xaxis=dict(tickformat=',')
    )
    
    return fig

# Custom table display function
def create_gross_profit_table(revenue_streams, show_monthly=True):
    """Create a custom table for gross profit metrics"""
    years_dict = group_months_by_year(months)
    
    # Create mapping from display names to data keys
    stream_mapping = {
        "📋 Subscription": "Subscription",
        "💳 Transactional": "Transactional", 
        "🚀 Implementation": "Implementation",
        "🔧 Maintenance": "Maintenance"
    }
    
    # Get revenue and calculate metrics
    revenue_data = st.session_state.model_data.get("revenue", {})
    gp_data = st.session_state.model_data.get("gross_profit_data", {})
    cogs_data = calculate_cogs()
    
    # Create tabs for each revenue stream
    tabs = st.tabs(revenue_streams)
    
    for idx, stream_display in enumerate(revenue_streams):
        stream = stream_mapping.get(stream_display, stream_display)
        with tabs[idx]:
            
            # Special handling for Subscription revenue
            if stream == "Subscription":
                
                # Go-Live Date Configuration
                st.markdown("Development Phase Settings:")
                dev_col1, dev_col2, dev_col3, dev_col4 = st.columns([0.75, 0.75, 0.75, 1.75])
                
                with dev_col1:
                    current_go_live = st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"].get("go_live_month", "Jan 2025")
                    go_live_month = st.selectbox(
                        "Go-Live Month:",
                        options=months,
                        index=months.index(current_go_live),
                        help="Month when platform goes live and hosting costs switch from capitalized to COGS",
                        key="go_live_month_select"
                    )
                    
                    # Auto-save when go-live month changes
                    if go_live_month != current_go_live:
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["go_live_month"] = go_live_month
                        try:
                            if save_gross_profit_data_to_database(st.session_state.model_data):
                                st.success(f"✅ Go-live month updated to {go_live_month}")
                            else:
                                st.warning("⚠️ Go-live month changed but not saved to database")
                        except Exception as e:
                            st.error(f"❌ Error saving go-live month: {str(e)}")
                    else:
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["go_live_month"] = go_live_month
                
                with dev_col2:
                    current_capitalize = st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"].get("capitalize_before_go_live", True)
                    capitalize_toggle = st.checkbox(
                        "Capitalize hosting costs before go-live",
                        value=current_capitalize,
                        help="When checked, hosting costs before go-live date are capitalized (COGS = $0)",
                        key="capitalize_toggle_check"
                    )
                    
                    # Auto-save when capitalize setting changes
                    if capitalize_toggle != current_capitalize:
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["capitalize_before_go_live"] = capitalize_toggle
                        try:
                            if save_gross_profit_data_to_database(st.session_state.model_data):
                                st.success(f"✅ Capitalization setting updated")
                            else:
                                st.warning("⚠️ Capitalization setting changed but not saved to database")
                        except Exception as e:
                            st.error(f"❌ Error saving capitalization setting: {str(e)}")
                    else:
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["capitalize_before_go_live"] = capitalize_toggle
                
                with dev_col3:
                    pass
                
                # Monthly Fixed Costs Grid
                st.markdown("💰 Monthly Fixed Hosting Costs ($)")
                
                if show_monthly:
                    # Monthly input grid for fixed costs
                    fixed_cols = st.columns(13)
                    fixed_cols[0].markdown("**Month**")
                    for i in range(1, 13):
                        fixed_cols[i].markdown(f"**{i}**")
                    
                    for year in sorted(years_dict.keys()):
                        year_months = years_dict[year]
                        cols = st.columns(13)
                        cols[0].markdown(f"**{year}**")
                        
                        for i, month in enumerate(year_months):
                            current_fixed = st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_fixed_costs"].get(month, 15400.0)
                            new_fixed = cols[i + 1].number_input(
                                f"Fixed Cost",
                                value=float(current_fixed),
                                min_value=0.0,
                                step=100.0,
                                format="%.0f",
                                key=f"fixed_{month}",
                                label_visibility="collapsed"
                            )
                            # Only update session state if value actually changed
                            if new_fixed != current_fixed:
                                st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_fixed_costs"][month] = new_fixed
                    
                    # Calculate defaults from hosting costs tab
                    def get_hosting_costs_defaults():
                        """Get total fixed and variable costs from hosting costs tab structure"""
                        if "hosting_costs_data" not in st.session_state.model_data:
                            return 15400.0, 5.0  # Fallback defaults
                        
                        hosting_data = st.session_state.model_data["hosting_costs_data"]
                        cost_structure = hosting_data.get("cost_structure", {})
                        
                        total_fixed = sum(
                            costs.get("fixed", 0)
                            for category in cost_structure.values()
                            for costs in category.values()
                        )
                        total_variable = sum(
                            costs.get("variable", 0)
                            for category in cost_structure.values()
                            for costs in category.values()
                        )
                        
                        return total_fixed or 15400.0, total_variable or 5.0
                    
                    default_fixed, default_variable = get_hosting_costs_defaults()
                    
                    # Store calculated defaults in session state to force widget refresh
                    if "calculated_hosting_defaults" not in st.session_state:
                        st.session_state.calculated_hosting_defaults = {"fixed": default_fixed, "variable": default_variable}
                    else:
                        # Update session state with fresh calculations
                        st.session_state.calculated_hosting_defaults["fixed"] = default_fixed
                        st.session_state.calculated_hosting_defaults["variable"] = default_variable
                    
                    # Quick set buttons for fixed costs
                    fixed_quick_col1, fixed_quick_col2, fixed_quick_col3, fixed_quick_col4 = st.columns([0.75, 0.75, 0.75, 1.75])
                    with fixed_quick_col1:
                        # Use static key but store default in session state to track changes
                        if "hosting_defaults_cache" not in st.session_state:
                            st.session_state.hosting_defaults_cache = {"fixed": default_fixed, "variable": 0}
                        
                        # Update cache when hosting costs change
                        if st.session_state.hosting_defaults_cache["fixed"] != default_fixed:
                            st.session_state.hosting_defaults_cache["fixed"] = default_fixed
                            # Clear the widget value by forcing rerun
                            if "set_all_fixed" in st.session_state:
                                del st.session_state.set_all_fixed
                        
                        fixed_set_value = st.number_input("Set fixed costs to:", value=0.0, min_value=0.0, step=1000.0, key="set_all_fixed")
                    
                    with fixed_quick_col2:
                        fixed_start_month = st.selectbox(
                            "From month:",
                            options=months,
                            index=0,
                            key="fixed_start_month"
                        )
                    
                    with fixed_quick_col3:
                        fixed_end_month = st.selectbox(
                            "To month:",
                            options=months,
                            index=len(months)-1,
                            key="fixed_end_month"
                        )
                    
                    with fixed_quick_col4:
                        if st.button("Apply to Selected Range", key="apply_range_fixed"):
                            start_idx = months.index(fixed_start_month)
                            end_idx = months.index(fixed_end_month)
                            
                            if start_idx <= end_idx:
                                for i in range(start_idx, end_idx + 1):
                                    month = months[i]
                                    st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_fixed_costs"][month] = fixed_set_value
                                st.success(f"✅ Applied ${fixed_set_value:,.0f} to {end_idx - start_idx + 1} months")
                                st.rerun()
                            else:
                                st.error("❌ Start month must be before or equal to end month")
                
                st.markdown("---")
                
                # Monthly Variable Costs Grid  
                st.markdown("👥 Monthly Variable Costs per Customer ($)")
                
                if show_monthly:
                    # Monthly input grid for variable costs
                    var_cols = st.columns(13)
                    var_cols[0].markdown("**Month**")
                    for i in range(1, 13):
                        var_cols[i].markdown(f"**{i}**")
                    
                    for year in sorted(years_dict.keys()):
                        year_months = years_dict[year]
                        cols = st.columns(13)
                        cols[0].markdown(f"**{year}**")
                        
                        for i, month in enumerate(year_months):
                            current_variable = st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_variable_costs"].get(month, 5.0)
                            new_variable = cols[i + 1].number_input(
                                f"Variable Cost",
                                value=float(current_variable),
                                min_value=0.0,
                                step=0.25,
                                format="%.2f",
                                key=f"variable_{month}",
                                label_visibility="collapsed"
                            )
                            # Only update session state if value actually changed
                            if new_variable != current_variable:
                                st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_variable_costs"][month] = new_variable
                    
                    # Quick set buttons for variable costs
                    var_quick_col1, var_quick_col2, var_quick_col3, var_quick_col4 = st.columns([0.75, 0.75, 0.75, 1.75])
                    with var_quick_col1:
                        # Update cache when hosting costs change
                        if st.session_state.hosting_defaults_cache["variable"] != default_variable:
                            st.session_state.hosting_defaults_cache["variable"] = default_variable
                            # Clear the widget value by forcing rerun
                            if "set_all_variable" in st.session_state:
                                del st.session_state.set_all_variable
                        
                        var_set_value = st.number_input("Set variable costs to:", value=0.0, min_value=0.0, step=0.50, key="set_all_variable")
                    
                    with var_quick_col2:
                        var_start_month = st.selectbox(
                            "From month:",
                            options=months,
                            index=0,
                            key="var_start_month"
                        )
                    
                    with var_quick_col3:
                        var_end_month = st.selectbox(
                            "To month:",
                            options=months,
                            index=len(months)-1,
                            key="var_end_month"
                        )
                    
                    with var_quick_col4:
                        if st.button("Apply to Selected Range", key="apply_range_variable"):
                            start_idx = months.index(var_start_month)
                            end_idx = months.index(var_end_month)
                            
                            if start_idx <= end_idx:
                                for i in range(start_idx, end_idx + 1):
                                    month = months[i]
                                    st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_variable_costs"][month] = var_set_value
                                st.success(f"✅ Applied ${var_set_value:.2f} to {end_idx - start_idx + 1} months")
                                st.rerun()
                            else:
                                st.error("❌ Start month must be before or equal to end month")
                else:
                    # Yearly view - show averages for hosting costs
                    fixed_yearly_data = []
                    variable_yearly_data = []
                    for year in sorted(years_dict.keys()):
                        year_months = years_dict[year]
                        avg_fixed = sum(st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_fixed_costs"].get(month, 15400.0) 
                                      for month in year_months) / len(year_months)
                        avg_variable = sum(st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["monthly_variable_costs"].get(month, 5.0) 
                                         for month in year_months) / len(year_months)
                        fixed_yearly_data.append({"Year": year, "Average Fixed Cost": f"${avg_fixed:,.0f}"})
                        variable_yearly_data.append({"Year": year, "Average Variable Cost": f"${avg_variable:.2f}"})
                    
                    st.markdown("💰 **Fixed Costs by Year**")
                    fixed_df = pd.DataFrame(fixed_yearly_data)
                    st.dataframe(fixed_df, use_container_width=True, hide_index=True)
                    
                    st.markdown("👥 **Variable Costs by Year**")
                    variable_df = pd.DataFrame(variable_yearly_data)
                    st.dataframe(variable_df, use_container_width=True, hide_index=True)
                
            else:
                # For non-subscription streams, show gross profit percentage
                st.markdown(f"Gross Profit % for {stream_display} Revenue")
                
                if show_monthly:
                    # Monthly input grid
                    gp_cols = st.columns(13)
                    gp_cols[0].markdown("**Month**")
                    for i in range(1, 13):
                        gp_cols[i].markdown(f"**{i}**")
                    
                    for year in sorted(years_dict.keys()):
                        year_months = years_dict[year]
                        cols = st.columns(13)
                        cols[0].markdown(f"**{year}**")
                        
                        for i, month in enumerate(year_months):
                            current_gp = gp_data.get("gross_profit_percentages", {}).get(stream, {}).get(month, 70.0)
                            new_gp = cols[i + 1].number_input(
                                f"GP%",
                                value=float(current_gp),
                                min_value=0.0,
                                max_value=100.0,
                                step=1.0,
                                format="%.1f",
                                key=f"gp_{stream}_{month}",
                                label_visibility="collapsed"
                            )
                            st.session_state.model_data["gross_profit_data"]["gross_profit_percentages"][stream][month] = new_gp
                    
                    # Quick set buttons
                    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns([0.75, 0.75, 0.75, 1.75])
                    with quick_col1:
                        set_value = st.number_input(f"Set GP% to:", value=70.0, min_value=0.0, max_value=100.0, step=5.0, key=f"set_all_{stream}")
                    
                    with quick_col2:
                        gp_start_month = st.selectbox(
                            "From month:",
                            options=months,
                            index=0,
                            key=f"gp_start_month_{stream}"
                        )
                    
                    with quick_col3:
                        gp_end_month = st.selectbox(
                            "To month:",
                            options=months,
                            index=len(months)-1,
                            key=f"gp_end_month_{stream}"
                        )
                    
                    with quick_col4:
                        if st.button(f"Apply to Selected Range", key=f"apply_range_{stream}"):
                            start_idx = months.index(gp_start_month)
                            end_idx = months.index(gp_end_month)
                            
                            if start_idx <= end_idx:
                                for i in range(start_idx, end_idx + 1):
                                    month = months[i]
                                    st.session_state.model_data["gross_profit_data"]["gross_profit_percentages"][stream][month] = set_value
                                st.success(f"✅ Applied {set_value:.1f}% to {end_idx - start_idx + 1} months")
                                st.rerun()
                            else:
                                st.error("❌ Start month must be before or equal to end month")
                else:
                    # Yearly view - show averages
                    yearly_data = []
                    for year in sorted(years_dict.keys()):
                        year_months = years_dict[year]
                        avg_gp = sum(gp_data.get("gross_profit_percentages", {}).get(stream, {}).get(month, 70.0) 
                                   for month in year_months) / len(year_months)
                        yearly_data.append({
                            "Year": year,
                            "Average GP%": f"{avg_gp:.1f}%"
                        })
                    
                    yearly_df = pd.DataFrame(yearly_data)
                    st.dataframe(yearly_df, use_container_width=True, hide_index=True)
            
            # Results table
            st.markdown("---")
            st.markdown("Gross Profit Analysis")
            
            # Create custom HTML table with fixed category column (matching financial model format)
            def create_gross_profit_analysis_table(stream, show_monthly=True):
                """Create custom gross profit table with fixed category column"""
                categories = ["Revenue", "COGS", "Gross Profit", "GP Margin"]
                
                # Group months by year
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
                    if category == "GP Margin":
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
                    row_class = "total-row" if category == "GP Margin" else ""
                    html_content += f'<tr class="{row_class}" style="height: 43px !important;">'
                    
                    if show_monthly:
                        for year in sorted(years_dict.keys()):
                            yearly_total = 0
                            yearly_revenue = 0
                            yearly_cogs = 0
                            
                            for month in years_dict[year]:
                                revenue = revenue_data.get(stream, {}).get(month, 0)
                                cogs = cogs_data.get(stream, {}).get(month, 0)
                                gross_profit = revenue - cogs
                                gp_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
                                
                                if category == "Revenue":
                                    value = revenue
                                elif category == "COGS":
                                    value = cogs
                                elif category == "Gross Profit":
                                    value = gross_profit
                                else:  # GP Margin
                                    value = gp_margin
                                
                                # Format value based on category
                                if category == "GP Margin":
                                    formatted_value = f"{value:.1f}%"
                                else:
                                    formatted_value = format_number(value)
                                
                                html_content += f'<td class="data-cell" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;">{formatted_value}</td>'
                                
                                # Accumulate for yearly totals
                                if category == "Revenue":
                                    yearly_total += value
                                    yearly_revenue += value
                                elif category == "COGS":
                                    yearly_total += value
                                    yearly_cogs += value
                                elif category == "Gross Profit":
                                    yearly_total += value
                                else:  # GP Margin - calculate based on yearly totals
                                    yearly_revenue += revenue
                                    yearly_cogs += cogs
                            
                            # Calculate yearly total
                            if category == "GP Margin":
                                yearly_gp = yearly_revenue - yearly_cogs
                                yearly_margin = (yearly_gp / yearly_revenue * 100) if yearly_revenue > 0 else 0
                                formatted_yearly_total = f"{yearly_margin:.1f}%"
                            else:
                                formatted_yearly_total = format_number(yearly_total)
                            
                            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_yearly_total}</strong></td>'
                    else:
                        # Yearly only view
                        for year in sorted(years_dict.keys()):
                            year_revenue = sum(revenue_data.get(stream, {}).get(month, 0) for month in years_dict[year])
                            year_cogs = sum(cogs_data.get(stream, {}).get(month, 0) for month in years_dict[year])
                            year_gp = year_revenue - year_cogs
                            year_margin = (year_gp / year_revenue * 100) if year_revenue > 0 else 0
                            
                            if category == "Revenue":
                                value = year_revenue
                            elif category == "COGS":
                                value = year_cogs
                            elif category == "Gross Profit":
                                value = year_gp
                            else:  # GP Margin
                                value = year_margin
                            
                            # Format value based on category
                            if category == "GP Margin":
                                formatted_value = f"{value:.1f}%"
                            else:
                                formatted_value = format_number(value)
                            
                            html_content += f'<td class="data-cell year-total" style="height: 43px !important; line-height: 43px !important; padding: 0 4px !important;"><strong>{formatted_value}</strong></td>'
                    
                    html_content += '</tr>'
                
                html_content += '</tbody></table>'
                html_content += '</div>'
                html_content += '</div>'
                
                st.markdown(html_content, unsafe_allow_html=True)
            
            # Display the custom table
            create_gross_profit_analysis_table(stream, show_monthly)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 Gross Profit Analysis</h1>
</div>
""", unsafe_allow_html=True)



# View toggle
view_col1, view_col2 = st.columns([0.75, 3.25])
with view_col1:
    view_mode = st.selectbox(
        "View Mode:",
        ["Monthly + Yearly", "Yearly Only"],
        key="gp_view_mode"
    )

show_monthly = view_mode == "Monthly + Yearly"

# Initialize data
initialize_gross_profit_data()



# Check if revenue data exists
if "revenue" not in st.session_state.model_data or not any(
    st.session_state.model_data["revenue"].get(stream, {}) 
    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
):
    st.warning("⚠️ No revenue data found! Please generate revenue in the Revenue first.")
    st.info("The Gross Profit calculates COGS based on revenue and gross profit margins.")
else:
    # Revenue stream details
    st.markdown('<div class="section-header">💼 Gross Profit by Revenue Stream</div>', unsafe_allow_html=True)
    

    
    # Create gross profit table for each revenue stream
    revenue_streams = ["📋 Subscription", "💳 Transactional", "🚀 Implementation", "🔧 Maintenance"]
    create_gross_profit_table(revenue_streams, show_monthly)

# KEY METRICS
st.markdown("---")
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
        key="gp_period_select"
    )

with metric_col2:
    # Add dropdown for metrics selection
    metrics_options = ["Total Summary", "Revenue Overview", "Margin Analysis", "Hosting Costs"]
    selected_metrics = st.selectbox(
        "Select Key Metrics:",
        options=metrics_options,
        index=0,
        key="gp_metrics_select"
    )

# Calculate totals based on selected period
def calculate_period_totals(selected_period):
    """Calculate gross profit totals for the selected period"""
    revenue_data = st.session_state.model_data.get("revenue", {})
    cogs_data = calculate_cogs()
    
    stream_mapping = {
        "Subscription": "Subscription",
        "Transactional": "Transactional", 
        "Implementation": "Implementation",
        "Maintenance": "Maintenance"
    }
    
    period_data = {}
    
    for stream_key in stream_mapping.keys():
        if selected_period == "Current" or selected_period == "All Years":
            # Show 6-year totals
            stream_revenue = sum(revenue_data.get(stream_key, {}).get(month, 0) for month in months)
            stream_cogs = sum(cogs_data.get(stream_key, {}).get(month, 0) for month in months)
        else:
            # Show specific year totals
            year_months = [f"{month_name} {selected_period}" for month_name in 
                          ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
            stream_revenue = sum(revenue_data.get(stream_key, {}).get(month, 0) for month in year_months)
            stream_cogs = sum(cogs_data.get(stream_key, {}).get(month, 0) for month in year_months)
        
        stream_gross_profit = stream_revenue - stream_cogs
        stream_gp_margin = (stream_gross_profit / stream_revenue * 100) if stream_revenue > 0 else 0
        
        period_data[stream_key] = {
            'revenue': stream_revenue,
            'cogs': stream_cogs,
            'gross_profit': stream_gross_profit,
            'gp_margin': stream_gp_margin
        }
    
    return period_data

# Get period data
period_data = calculate_period_totals(selected_period)

# Calculate overall totals
total_revenue = sum(period_data[stream]['revenue'] for stream in period_data)
total_cogs = sum(period_data[stream]['cogs'] for stream in period_data)
total_gross_profit = total_revenue - total_cogs
overall_gp_margin = (total_gross_profit / total_revenue * 100) if total_revenue > 0 else 0

# Get hosting costs data
hosting_costs, capitalized_hosting = calculate_hosting_costs()
if selected_period == "Current" or selected_period == "All Years":
    total_hosting = sum(hosting_costs.values())
    total_capitalized = sum(capitalized_hosting.values())
else:
    year_months = [f"{month_name} {selected_period}" for month_name in 
                  ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
    total_hosting = sum(hosting_costs.get(month, 0) for month in year_months)
    total_capitalized = sum(capitalized_hosting.get(month, 0) for month in year_months)

# Period label for display
period_label = "6-Year Total" if selected_period in ["Current", "All Years"] else f"{selected_period} Total"

# Conditional KPI display based on selected metrics
if selected_metrics == "Total Summary":
    # Total Summary KPIs
    overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

    with overview_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📈 Total Revenue</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${total_revenue:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">{period_label}</p>
        </div>
        """, unsafe_allow_html=True)

    with overview_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💸 Total COGS</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${total_cogs:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">{period_label}</p>
        </div>
        """, unsafe_allow_html=True)

    with overview_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💰 Gross Profit</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${total_gross_profit:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">{period_label}</p>
        </div>
        """, unsafe_allow_html=True)

    with overview_col4:
        # Color code the margin
        margin_color = "#00D084" if overall_gp_margin >= 70 else "#F39C12" if overall_gp_margin >= 50 else "#dc3545"
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📊 GP Margin</h4>
            <h2 style="margin: 0.5rem 0 0 0; color: {margin_color};">{overall_gp_margin:.1f}%</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Average</p>
        </div>
        """, unsafe_allow_html=True)

elif selected_metrics == "Revenue Overview":
    # Revenue Overview KPIs
    stream_col1, stream_col2, stream_col3, stream_col4 = st.columns(4)

    streams = ["📋 Subscription", "💳 Transactional", "🚀 Implementation", "🔧 Maintenance"]
    stream_keys = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    
    for i, (stream_display, stream_key) in enumerate(zip(streams, stream_keys)):
        col = [stream_col1, stream_col2, stream_col3, stream_col4][i]
        stream_data = period_data[stream_key]
        
        with col:
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="color: #00D084; margin: 0;">{stream_display}</h4>
                <h2 style="margin: 0.5rem 0 0 0;">${stream_data['revenue']:,.0f}</h2>
                <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Revenue • {stream_data['gp_margin']:.1f}% GP</p>
            </div>
            """, unsafe_allow_html=True)

elif selected_metrics == "Margin Analysis":
    # Margin Analysis KPIs - show GP margins for each stream
    margin_col1, margin_col2, margin_col3, margin_col4 = st.columns(4)

    streams = ["📋 Subscription", "💳 Transactional", "🚀 Implementation", "🔧 Maintenance"]
    stream_keys = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    
    for i, (stream_display, stream_key) in enumerate(zip(streams, stream_keys)):
        col = [margin_col1, margin_col2, margin_col3, margin_col4][i]
        stream_data = period_data[stream_key]
        
        # Color code the margin
        margin = stream_data['gp_margin']
        margin_color = "#00D084" if margin >= 70 else "#F39C12" if margin >= 50 else "#dc3545"
        
        with col:
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="color: #00D084; margin: 0;">{stream_display}</h4>
                <h2 style="margin: 0.5rem 0 0 0; color: {margin_color};">{margin:.1f}%</h2>
                <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Gross Profit Margin</p>
            </div>
            """, unsafe_allow_html=True)

elif selected_metrics == "Hosting Costs":
    # Hosting Costs KPIs
    hosting_col1, hosting_col2, hosting_col3, hosting_col4 = st.columns(4)
    
    # Get hosting structure for calculations
    hosting_structure = st.session_state.model_data.get("gross_profit_data", {}).get("saas_hosting_structure", {})
    fixed_cost = hosting_structure.get("fixed_monthly_cost", 0)
    variable_cost = hosting_structure.get("cost_per_customer", 0)
    
    # Get average subscribers for the period
    if selected_period == "Current" or selected_period == "All Years":
        # Average across all months
        total_subscribers = sum(get_active_subscribers(month) for month in months)
        avg_subscribers = total_subscribers / len(months) if months else 0
    else:
        year_months = [f"{month_name} {selected_period}" for month_name in 
                      ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
        total_subscribers = sum(get_active_subscribers(month) for month in year_months)
        avg_subscribers = total_subscribers / len(year_months) if year_months else 0

    with hosting_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💻 Fixed Monthly Cost</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${fixed_cost:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Base Infrastructure</p>
        </div>
        """, unsafe_allow_html=True)

    with hosting_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">👥 Cost Per Customer</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${variable_cost:.2f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Variable Rate</p>
        </div>
        """, unsafe_allow_html=True)

    with hosting_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">☁️ Total Hosting Cost</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${total_hosting:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">{period_label}</p>
        </div>
        """, unsafe_allow_html=True)

    with hosting_col4:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📊 Avg Subscribers</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{avg_subscribers:,.0f}</h2>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #666;">Active Users</p>
        </div>
        """, unsafe_allow_html=True)

# Chart section
st.markdown("") # Small spacing
st.markdown("---") # Line separator

# Chart type selection dropdown
chart_type_col1, chart_type_col2 = st.columns([0.75, 3.25])
with chart_type_col1:
    chart_options = ["Total Revenue", "Total COGS", "Gross Profit", "GP Margin", "Stream Breakdown", "Hosting Costs", "GP Margin by Year"]
    selected_chart = st.selectbox(
        "Select chart type:",
        options=chart_options,
        index=0,
        key="gp_chart_type_select"
    )

# Prepare chart data based on selected period and chart type
revenue_data = st.session_state.model_data.get("revenue", {})
cogs_data = calculate_cogs()

if selected_period == "All Years" or selected_chart == "GP Margin by Year":
    # For All Years or GP Margin by Year (always show all years), show yearly totals
    chart_data = {}
    years_dict = group_months_by_year(months)
    
    for year in sorted(years_dict.keys()):
        year_months = years_dict[year]
        if selected_chart == "Total Revenue":
            chart_data[str(year)] = sum(
                revenue_data.get(stream, {}).get(month, 0)
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                for month in year_months
            )
        elif selected_chart == "Total COGS":
            chart_data[str(year)] = sum(
                cogs_data.get(stream, {}).get(month, 0)
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                for month in year_months
            )
        elif selected_chart == "Gross Profit":
            year_revenue = sum(
                revenue_data.get(stream, {}).get(month, 0)
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                for month in year_months
            )
            year_cogs = sum(
                cogs_data.get(stream, {}).get(month, 0)
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                for month in year_months
            )
            chart_data[str(year)] = year_revenue - year_cogs
        elif selected_chart == "GP Margin":
            year_revenue = sum(
                revenue_data.get(stream, {}).get(month, 0)
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                for month in year_months
            )
            year_cogs = sum(
                cogs_data.get(stream, {}).get(month, 0)
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                for month in year_months
            )
            year_gp = year_revenue - year_cogs
            chart_data[str(year)] = (year_gp / year_revenue * 100) if year_revenue > 0 else 0
        elif selected_chart == "Stream Breakdown":
            if str(year) not in chart_data:
                chart_data[str(year)] = {}
            for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
                year_revenue = sum(revenue_data.get(stream, {}).get(month, 0) for month in year_months)
                chart_data[str(year)][stream] = year_revenue
        elif selected_chart == "Hosting Costs":
            chart_data[str(year)] = sum(hosting_costs.get(month, 0) for month in year_months)
        elif selected_chart == "GP Margin by Year":
            year_revenue = sum(
                revenue_data.get(stream, {}).get(month, 0)
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                for month in year_months
            )
            year_cogs = sum(
                cogs_data.get(stream, {}).get(month, 0)
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                for month in year_months
            )
            year_gp = year_revenue - year_cogs
            chart_data[str(year)] = (year_gp / year_revenue * 100) if year_revenue > 0 else 0
    
    if selected_chart == "GP Margin by Year":
        chart_title = "Gross Profit Margin by Year (2025-2030)"
    else:
        chart_title = f"{selected_chart} by Year"
    x_label = "Year"
    
else:
    # For specific year or current, show monthly data
    if selected_period == "Current":
        # Show first year as sample
        chart_months = months[:12]
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
            if selected_chart == "Total Revenue":
                chart_data[month_name] = sum(
                    revenue_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                )
            elif selected_chart == "Total COGS":
                chart_data[month_name] = sum(
                    cogs_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                )
            elif selected_chart == "Gross Profit":
                month_revenue = sum(
                    revenue_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                )
                month_cogs = sum(
                    cogs_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                )
                chart_data[month_name] = month_revenue - month_cogs
            elif selected_chart == "GP Margin":
                month_revenue = sum(
                    revenue_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                )
                month_cogs = sum(
                    cogs_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                )
                month_gp = month_revenue - month_cogs
                chart_data[month_name] = (month_gp / month_revenue * 100) if month_revenue > 0 else 0
            elif selected_chart == "Stream Breakdown":
                if month_name not in chart_data:
                    chart_data[month_name] = {}
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
                    chart_data[month_name][stream] = revenue_data.get(stream, {}).get(month, 0)
            elif selected_chart == "Hosting Costs":
                chart_data[month_name] = hosting_costs.get(month, 0)
            elif selected_chart == "GP Margin by Year":
                # For GP Margin by Year, we'll show the same data as GP Margin when viewing specific periods
                month_revenue = sum(
                    revenue_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                )
                month_cogs = sum(
                    cogs_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                )
                month_gp = month_revenue - month_cogs
                chart_data[month_name] = (month_gp / month_revenue * 100) if month_revenue > 0 else 0
        else:
            if selected_chart == "Stream Breakdown":
                chart_data[month_name] = {"Subscription": 0, "Transactional": 0, "Implementation": 0, "Maintenance": 0}
            else:
                chart_data[month_name] = 0
    
    x_label = "Month"

# Display the chart
if chart_data:
    fig = go.Figure()
    
    if selected_chart == "Stream Breakdown":
        # Create stacked bar chart for revenue streams
        streams = ["Subscription", "Transactional", "Implementation", "Maintenance"]
        colors = ['#00D084', '#00B574', '#7B1FA2', '#F39C12']  # Green variations, Purple, Orange
        
        for i, stream in enumerate(streams):
            x_values = list(chart_data.keys())
            y_values = [chart_data[x].get(stream, 0) for x in x_values]
            
            hover_template = f'<b>%{{x}}</b><br>{stream}: $%{{y:,.0f}}<extra></extra>'
            
            fig.add_trace(go.Bar(
                name=stream,
                x=x_values,
                y=y_values,
                marker_color=colors[i],
                opacity=0.8,
                hovertemplate=hover_template
            ))
        
        # Update layout for stacked bars
        fig.update_layout(barmode='stack')
        y_title = 'Revenue ($)'
        
    else:
        # Create regular single bar chart
        # Set color based on chart type
        if selected_chart == "Total Revenue":
            color = '#00D084'  # Main green
        elif selected_chart == "Total COGS":
            color = '#dc3545'  # Red
        elif selected_chart == "Gross Profit":
            color = '#00B574'  # Dark green
        elif selected_chart == "GP Margin":
            color = '#3498DB'  # Blue
        elif selected_chart == "GP Margin by Year":
            color = '#3498DB'  # Blue (same as GP Margin)
        elif selected_chart == "Hosting Costs":
            color = '#F39C12'  # Orange
        else:
            color = '#7B1FA2'  # Purple
        
        # Format hover template based on chart type
        if selected_chart in ["GP Margin", "GP Margin by Year"]:
            hover_template = '<b>%{x}</b><br>%{y:.1f}%<extra></extra>'
            y_title = 'Percentage (%)'
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
            tickformat='$,.0f' if selected_chart not in ["GP Margin", "GP Margin by Year"] else '.1f'
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
        ) if selected_chart == "Stream Breakdown" else {}
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

# DATA MANAGEMENT
st.markdown("---")
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

data_col1, data_col2, data_col3, data_col4, data_col5, data_col6 = st.columns([1, 1, 1, 1, 0.75, 1.25])

with data_col1:
    if st.button("💾 Save Data", type="primary", use_container_width=True):
        try:
            update_income_statement_cogs()  # KEEP THIS - updates COGS in Income Statement
            
            # Save gross profit data specifically
            if save_gross_profit_data_to_database(st.session_state.model_data):
                # Save revenue and COGS data
                save_revenue_and_cogs_to_database(st.session_state.model_data)
                # Save comprehensive data
                save_data_to_source(st.session_state.model_data)
                st.success("✅ Gross profit data saved successfully to database!")
            else:
                # Fallback to general save
                save_data_to_source(st.session_state.model_data) 
                st.success("✅ Data saved successfully!")
        except Exception as e:
            st.error(f"❌ Error saving data: {str(e)}")

with data_col2:
    if st.button("📂 Load Data", type="secondary", use_container_width=True):
        st.session_state.model_data = load_data_from_source()
        st.success("✅ Data loaded successfully!")
        st.rerun()

with data_col3:
    # Create Excel export data
    try:
        import tempfile
        import os
        from datetime import datetime
        
        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SHAED_Gross_Profit_Analysis_{timestamp}.xlsx"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            temp_path = tmp_file.name
        
        # Create Excel writer
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            # === REVENUE DATA ===
            if "revenue" in st.session_state.model_data:
                revenue_data = st.session_state.model_data["revenue"]
                revenue_streams = ["Subscription", "Transactional", "Implementation", "Maintenance"]
                filtered_revenue_data = {stream: revenue_data[stream] for stream in revenue_streams if stream in revenue_data}
                
                if filtered_revenue_data:
                    revenue_df = pd.DataFrame(filtered_revenue_data)
                    revenue_df = revenue_df.T
                    revenue_df.index.name = 'Month'
                    
                    # Add total revenue row
                    total_row = {}
                    for month in months:
                        total_row[month] = sum(filtered_revenue_data[stream].get(month, 0) for stream in filtered_revenue_data.keys())
                    
                    revenue_df.loc['TOTAL REVENUE'] = pd.Series(total_row)
                    revenue_df.to_excel(writer, sheet_name='Revenue by Stream')
            
            # === COGS DATA ===
            cogs_data = calculate_cogs()
            if cogs_data:
                cogs_df = pd.DataFrame(cogs_data)
                cogs_df = cogs_df.T
                cogs_df.index.name = 'Month'
                
                # Add total COGS row
                total_cogs_row = {}
                for month in months:
                    total_cogs_row[month] = sum(cogs_data[stream].get(month, 0) for stream in cogs_data.keys())
                
                cogs_df.loc['TOTAL COGS'] = pd.Series(total_cogs_row)
                cogs_df.to_excel(writer, sheet_name='COGS by Stream')
            
            # === GROSS PROFIT DATA ===
            gp_data = {}
            for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
                gp_data[stream] = {}
                for month in months:
                    revenue = st.session_state.model_data.get("revenue", {}).get(stream, {}).get(month, 0)
                    cogs = cogs_data.get(stream, {}).get(month, 0)
                    gp_data[stream][month] = revenue - cogs
            
            if gp_data:
                gp_df = pd.DataFrame(gp_data)
                gp_df = gp_df.T
                gp_df.index.name = 'Month'
                
                # Add total gross profit row
                total_gp_row = {}
                for month in months:
                    total_gp_row[month] = sum(gp_data[stream].get(month, 0) for stream in gp_data.keys())
                
                gp_df.loc['TOTAL GROSS PROFIT'] = pd.Series(total_gp_row)
                gp_df.to_excel(writer, sheet_name='Gross Profit by Stream')
            
            # === GROSS PROFIT MARGINS ===
            gp_margins = {}
            for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
                gp_margins[stream] = {}
                for month in months:
                    revenue = st.session_state.model_data.get("revenue", {}).get(stream, {}).get(month, 0)
                    cogs = cogs_data.get(stream, {}).get(month, 0)
                    gross_profit = revenue - cogs
                    gp_margins[stream][month] = (gross_profit / revenue * 100) if revenue > 0 else 0
            
            if gp_margins:
                margins_df = pd.DataFrame(gp_margins)
                margins_df = margins_df.T
                margins_df.index.name = 'Month'
                
                # Add overall margin row
                overall_margin_row = {}
                for month in months:
                    total_rev = sum(st.session_state.model_data.get("revenue", {}).get(stream, {}).get(month, 0) for stream in gp_margins.keys())
                    total_cogs = sum(cogs_data.get(stream, {}).get(month, 0) for stream in gp_margins.keys())
                    total_gp = total_rev - total_cogs
                    overall_margin_row[month] = (total_gp / total_rev * 100) if total_rev > 0 else 0
                
                margins_df.loc['OVERALL MARGIN'] = pd.Series(overall_margin_row)
                margins_df.to_excel(writer, sheet_name='GP Margins by Stream (%)')
            
            # === HOSTING COSTS DATA ===
            hosting_costs, capitalized_hosting = calculate_hosting_costs()
            if hosting_costs:
                hosting_df = pd.DataFrame({
                    'Hosting Costs': hosting_costs,
                    'Capitalized Hosting': capitalized_hosting
                })
                hosting_df = hosting_df.T
                hosting_df.index.name = 'Month'
                hosting_df.to_excel(writer, sheet_name='Hosting Costs')
            
            # === GROSS PROFIT PERCENTAGES (INPUT DATA) ===
            if "gross_profit_data" in st.session_state.model_data and "gross_profit_percentages" in st.session_state.model_data["gross_profit_data"]:
                gp_percentages = st.session_state.model_data["gross_profit_data"]["gross_profit_percentages"]
                
                for stream in ["Transactional", "Implementation", "Maintenance"]:  # Subscription uses hosting cost model
                    if stream in gp_percentages:
                        stream_df = pd.DataFrame({stream: gp_percentages[stream]})
                        stream_df = stream_df.T
                        stream_df.index.name = 'Month'
                        stream_df.to_excel(writer, sheet_name=f'{stream} GP Settings (%)')
            
            # === HOSTING STRUCTURE SETTINGS ===
            if "gross_profit_data" in st.session_state.model_data and "saas_hosting_structure" in st.session_state.model_data["gross_profit_data"]:
                hosting_structure = st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]
                
                # Export go-live settings
                settings_df = pd.DataFrame([{
                    'Setting': 'Go-Live Month',
                    'Value': hosting_structure.get('go_live_month', 'Jan 2025')
                }, {
                    'Setting': 'Capitalize Before Go-Live',
                    'Value': hosting_structure.get('capitalize_before_go_live', True)
                }])
                
                settings_df.to_excel(writer, sheet_name='Hosting Structure Settings', index=False)
                
                # Export monthly fixed costs
                monthly_fixed_costs = hosting_structure.get('monthly_fixed_costs', {})
                if monthly_fixed_costs:
                    fixed_df = pd.DataFrame([monthly_fixed_costs])
                    fixed_df = fixed_df.T
                    fixed_df.columns = ['Fixed Cost ($)']
                    fixed_df.index.name = 'Month'
                    fixed_df.to_excel(writer, sheet_name='Monthly Fixed Costs')
                
                # Export monthly variable costs
                monthly_variable_costs = hosting_structure.get('monthly_variable_costs', {})
                if monthly_variable_costs:
                    variable_df = pd.DataFrame([monthly_variable_costs])
                    variable_df = variable_df.T
                    variable_df.columns = ['Variable Cost per Customer ($)']
                    variable_df.index.name = 'Month'
                    variable_df.to_excel(writer, sheet_name='Monthly Variable Costs')
            
            # === ANNUAL SUMMARY ===
            years_dict = group_months_by_year(months)
            annual_summary = []
            
            for year in sorted(years_dict.keys()):
                year_months = years_dict[year]
                
                year_revenue = {}
                year_cogs = {}
                year_gp = {}
                year_margin = {}
                
                for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
                    stream_revenue = sum(st.session_state.model_data.get("revenue", {}).get(stream, {}).get(month, 0) for month in year_months)
                    stream_cogs = sum(cogs_data.get(stream, {}).get(month, 0) for month in year_months)
                    stream_gp = stream_revenue - stream_cogs
                    stream_margin = (stream_gp / stream_revenue * 100) if stream_revenue > 0 else 0
                    
                    year_revenue[stream] = stream_revenue
                    year_cogs[stream] = stream_cogs
                    year_gp[stream] = stream_gp
                    year_margin[stream] = stream_margin
                
                # Overall totals
                total_revenue = sum(year_revenue.values())
                total_cogs = sum(year_cogs.values())
                total_gp = total_revenue - total_cogs
                overall_margin = (total_gp / total_revenue * 100) if total_revenue > 0 else 0
                
                # Hosting costs
                year_hosting = sum(hosting_costs.get(month, 0) for month in year_months)
                year_capitalized = sum(capitalized_hosting.get(month, 0) for month in year_months)
                
                annual_summary.append({
                    'Year': year,
                    'Total Revenue': total_revenue,
                    'Total COGS': total_cogs,
                    'Total Gross Profit': total_gp,
                    'Overall GP Margin (%)': overall_margin,
                    'Subscription Revenue': year_revenue.get('Subscription', 0),
                    'Subscription COGS': year_cogs.get('Subscription', 0),
                    'Subscription GP': year_gp.get('Subscription', 0),
                    'Subscription GP (%)': year_margin.get('Subscription', 0),
                    'Transactional Revenue': year_revenue.get('Transactional', 0),
                    'Transactional COGS': year_cogs.get('Transactional', 0),
                    'Transactional GP': year_gp.get('Transactional', 0),
                    'Transactional GP (%)': year_margin.get('Transactional', 0),
                    'Implementation Revenue': year_revenue.get('Implementation', 0),
                    'Implementation COGS': year_cogs.get('Implementation', 0),
                    'Implementation GP': year_gp.get('Implementation', 0),
                    'Implementation GP (%)': year_margin.get('Implementation', 0),
                    'Maintenance Revenue': year_revenue.get('Maintenance', 0),
                    'Maintenance COGS': year_cogs.get('Maintenance', 0),
                    'Maintenance GP': year_gp.get('Maintenance', 0),
                    'Maintenance GP (%)': year_margin.get('Maintenance', 0),
                    'Total Hosting Costs': year_hosting,
                    'Capitalized Hosting': year_capitalized
                })
            
            if annual_summary:
                summary_df = pd.DataFrame(annual_summary)
                summary_df.to_excel(writer, sheet_name='Annual Summary', index=False)
            
            # === CHART DATA (GP MARGIN BY YEAR) ===
            chart_data_yearly = {}
            for year in sorted(years_dict.keys()):
                year_months = years_dict[year]
                year_revenue = sum(
                    st.session_state.model_data.get("revenue", {}).get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                    for month in year_months
                )
                year_cogs = sum(
                    cogs_data.get(stream, {}).get(month, 0)
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
                    for month in year_months
                )
                year_gp = year_revenue - year_cogs
                chart_data_yearly[year] = (year_gp / year_revenue * 100) if year_revenue > 0 else 0
            
            if chart_data_yearly:
                chart_df = pd.DataFrame([chart_data_yearly])
                chart_df.index = ['GP Margin (%)']
                chart_df.to_excel(writer, sheet_name='GP Margin by Year Chart')
        
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
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>SHAED Financial Model - Gross Profit Analysis</strong> | Powering the future of mobility<br>
    © 2025 SHAED - All rights reserved
</div>
""", unsafe_allow_html=True)

# Update integrated dashboards
def update_integrated_dashboards():
    """Update integrated dashboards with current gross profit data"""
    try:
        # Save current gross profit data to database
        if save_gross_profit_data_to_database(st.session_state.model_data):
            # Also save the calculated COGS data
            save_revenue_and_cogs_to_database(st.session_state.model_data)
            return True
        return False
    except Exception as e:
        st.error(f"❌ Error updating integrated dashboards: {str(e)}")
        return False

update_integrated_dashboards()  # KEEP THIS - updates integrated dashboards