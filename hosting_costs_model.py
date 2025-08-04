import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go
from database import load_data, save_data, load_data_from_source, save_data_to_source

# Configure page
st.set_page_config(
    page_title="Hosting",
    page_icon="☁️",
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
    
    /* Dashboard Navigation header - centered */
    .nav-section-header {
        background-color: #00D084;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 5px;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
        text-align: center;
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
    
    /* Cost breakdown styling */
    .cost-category {
        background: #f8f9fa;
        border-left: 4px solid #00D084;
        padding: 0.5rem 0.3rem;
        margin: 0.2rem 0;
        border-radius: 5px;
        font-size: 13px;
        width: 100%;
        box-sizing: border-box;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    /* Green table styling */
    .green-table-container {
        background: white;
        border-radius: 10px;
        padding: 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        overflow-x: auto;
        border: 1px solid #e0e0e0;
    }
    
    .green-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0;
    }
    
    .green-table th {
        background-color: #00D084;
        color: white;
        padding: 12px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 14px;
        border-bottom: 1px solid #00B574;
    }
    
    .green-table th:first-child {
        border-top-left-radius: 10px;
    }
    
    .green-table th:last-child {
        border-top-right-radius: 10px;
    }
    
    .green-table td {
        padding: 10px 8px;
        text-align: center;
        font-size: 13px;
        border-bottom: 1px solid #e0e0e0;
        background-color: white;
    }
    
    .green-table tr:nth-child(even) td {
        background-color: #f8f9fa;
    }
    
    .green-table tr:hover td {
        background-color: #e8f5e8;
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

# Initialize hosting costs data structure
def initialize_hosting_costs_data():
    """Initialize the hosting costs data structure"""
    if "hosting_costs_data" not in st.session_state.model_data:
        st.session_state.model_data["hosting_costs_data"] = {}
    
    # Initialize go-live settings
    if "go_live_settings" not in st.session_state.model_data["hosting_costs_data"]:
        st.session_state.model_data["hosting_costs_data"]["go_live_settings"] = {
            "go_live_month": "Jan 2025",
            "capitalize_before_go_live": True
        }
    
    # Initialize cost categories with defaults
    default_categories = {
        "Cloud Infrastructure": {
            "Base Servers & Compute": {"fixed": 2000.0, "variable": 0.20},
            "Database Hosting": {"fixed": 500.0, "variable": 0.10},
            "Storage": {"fixed": 200.0, "variable": 0.05},
            "CDN & Content Delivery": {"fixed": 300.0, "variable": 0.03},
            "Load Balancers": {"fixed": 150.0, "variable": 0.02}
        },
        "Supporting Services": {
            "Monitoring & Analytics": {"fixed": 200.0, "variable": 0.02},
            "Security & Compliance": {"fixed": 500.0, "variable": 0.05},
            "Backup & Disaster Recovery": {"fixed": 300.0, "variable": 0.03},
            "Development/Testing Environments": {"fixed": 1000.0, "variable": 0.0}
        },
        "Third-Party Services": {
            "Email Services": {"fixed": 100.0, "variable": 0.01},
            "SMS/Notifications": {"fixed": 50.0, "variable": 0.02},
            "Payment Processing Infrastructure": {"fixed": 100.0, "variable": 0.0},
            "Other API Services": {"fixed": 200.0, "variable": 0.05}
        }
    }
    
    # Initialize cost structure if not exists
    if "cost_structure" not in st.session_state.model_data["hosting_costs_data"]:
        st.session_state.model_data["hosting_costs_data"]["cost_structure"] = default_categories
    
    # Initialize monthly overrides (for special circumstances)
    if "monthly_overrides" not in st.session_state.model_data["hosting_costs_data"]:
        st.session_state.model_data["hosting_costs_data"]["monthly_overrides"] = {month: 0 for month in months}
    
    # Initialize scaling scenarios
    if "scaling_scenarios" not in st.session_state.model_data["hosting_costs_data"]:
        st.session_state.model_data["hosting_costs_data"]["scaling_scenarios"] = {
            "conservative": 1.0,
            "moderate": 1.2,
            "aggressive": 1.5
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

# Calculate total hosting costs
def calculate_total_hosting_costs():
    """Calculate total hosting costs based on all categories"""
    hosting_data = st.session_state.model_data["hosting_costs_data"]
    cost_structure = hosting_data["cost_structure"]
    monthly_overrides = hosting_data.get("monthly_overrides", {})
    
    monthly_costs = {}
    monthly_breakdown = {}
    
    for month in months:
        active_subscribers = get_active_subscribers(month)
        total_fixed = 0
        total_variable = 0
        breakdown = {}
        
        # Calculate costs for each category
        for category, services in cost_structure.items():
            category_fixed = 0
            category_variable = 0
            
            for service, costs in services.items():
                fixed = costs.get("fixed", 0)
                variable = costs.get("variable", 0)
                
                category_fixed += fixed
                category_variable += variable * active_subscribers
            
            breakdown[category] = category_fixed + category_variable
            total_fixed += category_fixed
            total_variable += category_variable
        
        # Apply monthly override if exists
        monthly_total = total_fixed + total_variable
        override = monthly_overrides.get(month, 0)
        
        if override > 0:
            monthly_costs[month] = override
            breakdown["Override Applied"] = override
        else:
            monthly_costs[month] = monthly_total
        
        monthly_breakdown[month] = breakdown
    
    return monthly_costs, monthly_breakdown

# Calculate capitalized vs expensed costs
def calculate_capitalized_vs_expensed():
    """Determine which costs are capitalized vs expensed based on go-live date"""
    # Read go-live settings from gross profit model (primary source)
    gross_profit_data = st.session_state.model_data.get("gross_profit_data", {})
    hosting_structure = gross_profit_data.get("saas_hosting_structure", {})
    
    go_live_month = hosting_structure.get("go_live_month", "Jan 2025")
    capitalize_before = hosting_structure.get("capitalize_before_go_live", True)
    
    monthly_costs, _ = calculate_total_hosting_costs()
    
    capitalized_costs = {}
    expensed_costs = {}
    
    try:
        go_live_index = months.index(go_live_month)
    except ValueError:
        go_live_index = 0
    
    for i, month in enumerate(months):
        cost = monthly_costs.get(month, 0)
        
        if capitalize_before and i < go_live_index:
            capitalized_costs[month] = cost
            expensed_costs[month] = 0
        else:
            capitalized_costs[month] = 0
            expensed_costs[month] = cost
    
    return capitalized_costs, expensed_costs

# Update other dashboards with hosting costs
def update_integrated_dashboards():
    """Update Gross Profit and Liquidity with hosting costs"""
    
    _, expensed_costs = calculate_capitalized_vs_expensed()
    
    # Update gross profit data for COGS calculation
    if "gross_profit_data" not in st.session_state.model_data:
        st.session_state.model_data["gross_profit_data"] = {}
    
    # Store calculated hosting costs for gross profit dashboard
    st.session_state.model_data["gross_profit_data"]["calculated_hosting_costs"] = expensed_costs
    
    # Update the simple hosting structure in gross profit data to match detailed model
    hosting_data = st.session_state.model_data["hosting_costs_data"]
    cost_structure = hosting_data.get("cost_structure", {})
    go_live_settings = hosting_data.get("go_live_settings", {})
    
    # Calculate equivalent simple structure values
    total_fixed_per_month = sum(
        costs.get("fixed", 0)
        for category in cost_structure.values()
        for costs in category.values()
    )
    total_variable_per_customer = sum(
        costs.get("variable", 0)
        for category in cost_structure.values()
        for costs in category.values()
    )
    
    # Update the gross profit model's hosting structure costs (preserve go-live settings)
    existing_structure = st.session_state.model_data["gross_profit_data"].get("saas_hosting_structure", {})
    st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"] = {
        "fixed_monthly_cost": total_fixed_per_month,
        "cost_per_customer": total_variable_per_customer,
        "go_live_month": existing_structure.get("go_live_month", "Jan 2025"),  # Preserve existing setting
        "capitalize_before_go_live": existing_structure.get("capitalize_before_go_live", True),  # Preserve existing setting
        "source": "hosting_costs_model",  # Mark as sourced from detailed model
        "last_updated": str(datetime.now())
    }
    
    # Update liquidity dashboard license fees (reduce by hosting amount)
    if "liquidity_data" in st.session_state.model_data:
        if "expenses" in st.session_state.model_data["liquidity_data"]:
            if "License Fees" in st.session_state.model_data["liquidity_data"]["expenses"]:
                # Store original license fees if not already stored
                if "original_license_fees" not in st.session_state.model_data["hosting_costs_data"]:
                    st.session_state.model_data["hosting_costs_data"]["original_license_fees"] = \
                        st.session_state.model_data["liquidity_data"]["expenses"]["License Fees"].copy()
                
                # Reduce license fees by expensed hosting costs
                original_fees = st.session_state.model_data["hosting_costs_data"]["original_license_fees"]
                for month in months:
                    hosting_cost = expensed_costs.get(month, 0)
                    original_fee = original_fees.get(month, 0)
                    st.session_state.model_data["liquidity_data"]["expenses"]["License Fees"][month] = \
                        max(0, original_fee - hosting_cost)

# Create cost structure table
def create_cost_structure_table(show_monthly=True):
    """Create editable table for hosting cost structure"""
    st.markdown("☁️ Infrastructure Cost Components")
    
    cost_structure = st.session_state.model_data["hosting_costs_data"]["cost_structure"]
    
    # Add new category option
    new_cat_col1, new_cat_col2 = st.columns([0.75, 3.25])
    with new_cat_col1:
        new_category_name = st.text_input("New Category Name:", key="new_category_name")
    with new_cat_col2:
        if st.button("➕ Add Category", type="primary"):
            if new_category_name and new_category_name not in cost_structure:
                cost_structure[new_category_name] = {}
                st.success(f"Added category: {new_category_name}")
                st.rerun()
            elif new_category_name in cost_structure:
                st.error("Category already exists!")
            else:
                st.error("Please enter a category name")
    
    # Display existing categories
    categories_to_delete = []
    
    for category, services in cost_structure.items():
        # Add space above category
        st.markdown("")
        
        # Category header with delete option
        cat_col1, cat_col2 = st.columns([0.75, 3.25])
        with cat_col1:
            st.markdown(f"**{category}**")
        with cat_col2:
            if st.button(f"🗑️ Delete", key=f"delete_cat_{category}", help=f"Delete entire {category} category"):
                categories_to_delete.append(category)
        
        # Add new service for this category
        expander_cols = st.columns([3.25, 0.75])
        with expander_cols[0]:
            with st.expander(f"➕ Add New Service to {category}", expanded=False):
                service_col1, service_col2, service_col3, service_col4 = st.columns([0.75, 0.75, 0.75, 1.75])
                
                with service_col1:
                    new_service_name = st.text_input("Service Name:", key=f"new_service_{category}")
                with service_col2:
                    new_service_fixed = st.number_input("Fixed Cost:", min_value=0.0, value=0.0, step=50.0, key=f"new_fixed_{category}")
                with service_col3:
                    new_service_variable = st.number_input("Per Customer:", min_value=0.0, value=0.0, step=0.01, key=f"new_variable_{category}")
                with service_col4:
                    if st.button("Add", key=f"add_service_{category}"):
                        if new_service_name and new_service_name not in services:
                            cost_structure[category][new_service_name] = {
                                "fixed": new_service_fixed,
                                "variable": new_service_variable
                            }
                            st.success(f"Added service: {new_service_name}")
                            st.rerun()
                        elif new_service_name in services:
                            st.error("Service already exists in this category!")
                        else:
                            st.error("Please enter a service name")
        
        # Service headers
        cols = st.columns([0.75, 0.75, 0.75, 1.75])
        cols[0].markdown("Service")
        cols[1].markdown("Fixed Monthly ($)")
        cols[2].markdown("Per Customer ($)")
        cols[3].markdown("Action")
        
        services_to_delete = []
        
        for service, costs in services.items():
            cols = st.columns([0.75, 0.75, 0.75, 1.75])
            cols[0].markdown(f"<div class='cost-category'>{service}</div>", unsafe_allow_html=True)
            
            # Fixed cost input
            new_fixed = cols[1].number_input(
                f"Fixed",
                value=costs.get("fixed", 0.0),
                min_value=0.0,
                step=50.0,
                format="%.2f",
                key=f"fixed_{category}_{service}",
                label_visibility="collapsed"
            )
            
            # Variable cost input
            new_variable = cols[2].number_input(
                f"Variable",
                value=costs.get("variable", 0.0),
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key=f"variable_{category}_{service}",
                label_visibility="collapsed"
            )
            
            # Delete button
            if cols[3].button("🗑️", key=f"delete_{category}_{service}", help=f"Delete {service}"):
                services_to_delete.append(service)
            
            # Update values
            st.session_state.model_data["hosting_costs_data"]["cost_structure"][category][service]["fixed"] = new_fixed
            st.session_state.model_data["hosting_costs_data"]["cost_structure"][category][service]["variable"] = new_variable
        
        # Delete services marked for deletion
        for service in services_to_delete:
            del cost_structure[category][service]
            st.rerun()
    
    # Delete categories marked for deletion
    for category in categories_to_delete:
        del cost_structure[category]
        st.rerun()

# Create monthly overrides table
def create_monthly_overrides_table(show_monthly=True):
    """Create table for monthly override amounts"""
    st.markdown("🔧 Monthly Overrides")
    
    if show_monthly:
        years_dict = group_months_by_year(months)
        
        for year in sorted(years_dict.keys()):
            with st.expander(f"📅 {year} Overrides", expanded=False):
                cols = st.columns(4)
                year_months = years_dict[year]
                
                for i, month in enumerate(year_months):
                    col_idx = i % 4
                    current_override = st.session_state.model_data["hosting_costs_data"]["monthly_overrides"].get(month, 0)
                    
                    new_override = cols[col_idx].number_input(
                        f"{month}:",
                        value=float(current_override),
                        min_value=0.0,
                        step=100.0,
                        format="%.0f",
                        key=f"override_{month}"
                    )
                    
                    st.session_state.model_data["hosting_costs_data"]["monthly_overrides"][month] = new_override
    else:
        st.info("Switch to monthly view to set override amounts")

# Create cost projection chart
def create_cost_projection_chart():
    """Create a chart showing hosting cost projections"""
    monthly_costs, _ = calculate_total_hosting_costs()
    capitalized_costs, expensed_costs = calculate_capitalized_vs_expensed()
    
    years_dict = group_months_by_year(months)
    
    # Create yearly aggregates
    yearly_data = []
    for year in sorted(years_dict.keys()):
        year_total = sum(monthly_costs.get(month, 0) for month in years_dict[year])
        year_cap = sum(capitalized_costs.get(month, 0) for month in years_dict[year])
        year_exp = sum(expensed_costs.get(month, 0) for month in years_dict[year])
        
        yearly_data.append({
            "Year": year,
            "Total": year_total,
            "Capitalized": year_cap,
            "Expensed": year_exp
        })
    
    # Create plotly chart
    fig = go.Figure()
    
    years = [d["Year"] for d in yearly_data]
    
    fig.add_trace(go.Bar(
        name='Capitalized',
        x=years,
        y=[d["Capitalized"] for d in yearly_data],
        marker_color='#00B574'
    ))
    
    fig.add_trace(go.Bar(
        name='Expensed (COGS)',
        x=years,
        y=[d["Expensed"] for d in yearly_data],
        marker_color='#00D084'
    ))
    
    fig.update_layout(
        title="Annual Hosting Costs: Capitalized vs Expensed",
        xaxis_title="Year",
        yaxis_title="Cost ($)",
        barmode='stack',
        height=400,
        showlegend=True,
        plot_bgcolor='white',
        yaxis=dict(tickformat='$,.0f')
    )
    
    return fig

# Create customer scaling chart
def create_scaling_analysis():
    """Create analysis showing cost per customer at different scales"""
    cost_structure = st.session_state.model_data["hosting_costs_data"]["cost_structure"]
    
    # Calculate total fixed and variable
    total_fixed = 0
    total_variable = 0
    
    for category, services in cost_structure.items():
        for service, costs in services.items():
            total_fixed += costs.get("fixed", 0)
            total_variable += costs.get("variable", 0)
    
    # Create scaling analysis
    customer_levels = [0, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
    costs_per_customer = []
    
    for customers in customer_levels:
        if customers == 0:
            costs_per_customer.append(0)
        else:
            total_cost = total_fixed + (total_variable * customers)
            costs_per_customer.append(total_cost / customers)
    
    # Create chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=customer_levels[1:],  # Skip 0 customers
        y=costs_per_customer[1:],
        mode='lines+markers',
        name='Cost per Customer',
        line=dict(color='#00D084', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Cost per Customer at Different Scales",
        xaxis_title="Number of Customers",
        yaxis_title="Cost per Customer ($)",
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        xaxis=dict(type='log', tickformat=','),
        yaxis=dict(tickformat='$,.2f')
    )
    
    return fig

# Header
st.markdown("""
<div class="main-header">
    <h1>☁️ Hosting Costs</h1>
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
initialize_hosting_costs_data()

# View Mode Selection
view_col1, view_col2 = st.columns([0.75, 3.25])
with view_col1:
    view_mode = st.selectbox(
        "View Mode:",
        ["Monthly + Yearly", "Yearly Only"],
        key="hosting_view_mode"
    )

show_monthly = view_mode == "Monthly + Yearly"

# Cost Structure Configuration
st.markdown('<div class="section-header">💰 Infrastructure Cost Structure</div>', unsafe_allow_html=True)

# Create cost structure table
create_cost_structure_table(show_monthly)

st.markdown("---")

# Monthly Breakdown Table
if show_monthly:
    st.markdown('<div class="section-header">📅 Monthly Cost Breakdown</div>', unsafe_allow_html=True)
    
    # Year filter for monthly breakdown
    breakdown_filter_col1, breakdown_filter_col2 = st.columns([1, 3])
    
    with breakdown_filter_col1:
        available_years = ["All Years"] + [str(year) for year in range(2025, 2031)]
        selected_breakdown_year = st.selectbox(
            "Filter by Year:",
            options=available_years,
            index=1,  # Default to 2025
            key="breakdown_year_filter"
        )
    
    with breakdown_filter_col2:
        pass
    
    # Get monthly data
    monthly_costs, monthly_breakdown = calculate_total_hosting_costs()
    capitalized_costs, expensed_costs = calculate_capitalized_vs_expensed()
    
    # Filter months based on selected year
    if selected_breakdown_year == "All Years":
        filtered_months = months
    else:
        filtered_months = [month for month in months if month.endswith(selected_breakdown_year)]
    
    # Get cost structure for detailed breakdown
    cost_structure = st.session_state.model_data["hosting_costs_data"]["cost_structure"]
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
    
    # Create monthly breakdown dataframe
    breakdown_data = []
    for month in filtered_months:
        subscribers = get_active_subscribers(month)
        total_cost = monthly_costs.get(month, 0)
        cap_cost = capitalized_costs.get(month, 0)
        exp_cost = expensed_costs.get(month, 0)
        
        # Calculate fixed and per customer costs
        fixed_cost = total_fixed
        per_customer_cost = total_variable * subscribers
        
        breakdown_data.append({
            "Month": month,
            "Subscribers": subscribers,
            "Fixed Cost": fixed_cost,
            "Per Customer Cost": per_customer_cost,
            "Total Cost": total_cost,
            "Capitalized": cap_cost,
            "Expensed (COGS)": exp_cost,
            "Cost/Customer": total_cost / subscribers if subscribers > 0 else 0
        })
    
    # Create custom HTML table with green styling
    html_table = '<div class="green-table-container">'
    html_table += '<table class="green-table">'
    
    # Table header
    html_table += '<thead><tr>'
    headers = ["Month", "Customers", "🏗️ Fixed Cost", "👥 Per Customer", "💰 Total Cost", "📈 Capitalized", "💸 COGS", "💳 $/Customer"]
    for header in headers:
        html_table += f'<th>{header}</th>'
    html_table += '</tr></thead>'
    
    # Table body
    html_table += '<tbody>'
    for row in breakdown_data:
        html_table += '<tr>'
        html_table += f'<td style="text-align: left; font-weight: 600;">{row["Month"]}</td>'
        html_table += f'<td>{row["Subscribers"]:,.0f}</td>'
        html_table += f'<td>${row["Fixed Cost"]:,.0f}</td>'
        html_table += f'<td>${row["Per Customer Cost"]:,.0f}</td>'
        html_table += f'<td>${row["Total Cost"]:,.0f}</td>'
        html_table += f'<td>${row["Capitalized"]:,.0f}</td>'
        html_table += f'<td>${row["Expensed (COGS)"]:,.0f}</td>'
        html_table += f'<td>${row["Cost/Customer"]:,.2f}</td>'
        html_table += '</tr>'
    html_table += '</tbody>'
    html_table += '</table>'
    html_table += '</div>'
    
    st.markdown(html_table, unsafe_allow_html=True)
    
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
        key="hosting_period_select"
    )

with metric_col2:
    # Add dropdown for metrics selection
    metrics_options = ["Cost Overview", "Infrastructure Breakdown"]
    selected_metrics = st.selectbox(
        "Select Key Metrics:",
        options=metrics_options,
        index=0,
        key="hosting_metrics_select"
    )

# Calculate hosting metrics based on selected period
monthly_costs, monthly_breakdown = calculate_total_hosting_costs()
capitalized_costs, expensed_costs = calculate_capitalized_vs_expensed()

# Calculate cost structure totals
cost_structure = st.session_state.model_data["hosting_costs_data"]["cost_structure"]
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

# Calculate financial totals based on selected period
if selected_period == "Current":
    # Show 6-year totals for current view
    total_hosting_costs = sum(monthly_costs.values())
    total_capitalized = sum(capitalized_costs.values())
    total_expensed = sum(expensed_costs.values())
    period_label = "6-Year Total"
    period_months_count = 72  # 6 years * 12 months
elif selected_period == "All Years":
    # Show 6-year totals
    total_hosting_costs = sum(monthly_costs.values())
    total_capitalized = sum(capitalized_costs.values())
    total_expensed = sum(expensed_costs.values())
    period_label = "6-Year Total"
    period_months_count = 72  # 6 years * 12 months
else:
    # Show specific year totals
    year_months = [f"{month} {selected_period}" for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
    total_hosting_costs = sum(monthly_costs.get(month, 0) for month in year_months)
    total_capitalized = sum(capitalized_costs.get(month, 0) for month in year_months)
    total_expensed = sum(expensed_costs.get(month, 0) for month in year_months)
    period_label = f"{selected_period} Total"
    period_months_count = 12

# Calculate average monthly
avg_monthly = total_hosting_costs / period_months_count if period_months_count > 0 else 0

# Calculate average customers for the period
if selected_period == "Current" or selected_period == "All Years":
    period_months_list = months
else:
    period_months_list = [f"{month} {selected_period}" for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]

total_customers = 0
customer_months = 0
for month in period_months_list:
    customers = get_active_subscribers(month)
    total_customers += customers
    customer_months += 1
avg_customers = total_customers / customer_months if customer_months > 0 else 0

# Conditional KPI display based on selected metrics
if selected_metrics == "Cost Overview":
    # Cost Overview KPIs
    cost_col1, cost_col2, cost_col3, cost_col4, cost_col5 = st.columns(5)

    with cost_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💰 Total Hosting</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${total_hosting_costs:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with cost_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">📅 Average Monthly</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${avg_monthly:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with cost_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">🏗️ Fixed Costs/Month</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${total_fixed:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with cost_col4:
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">👥 Variable $/Customer</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${total_variable:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with cost_col5:
        cost_per_customer = avg_monthly / avg_customers if avg_customers > 0 else 0
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: #00D084; margin: 0;">💳 Avg Cost/Customer</h4>
            <h2 style="margin: 0.5rem 0 0 0;">${cost_per_customer:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

elif selected_metrics == "Infrastructure Breakdown":
    # Infrastructure Breakdown KPIs
    # Calculate costs by category
    category_costs = {}
    for category, services in cost_structure.items():
        cat_fixed = sum(costs.get("fixed", 0) for costs in services.values())
        cat_variable = sum(costs.get("variable", 0) for costs in services.values())
        category_costs[category] = {"fixed": cat_fixed, "variable": cat_variable, "total": cat_fixed + (cat_variable * avg_customers)}
    
    # Display top 4 categories
    sorted_categories = sorted(category_costs.items(), key=lambda x: x[1]["total"], reverse=True)
    
    infra_col1, infra_col2, infra_col3, infra_col4 = st.columns(4)
    
    for i, (category, costs) in enumerate(sorted_categories[:4]):
        # Determine icon based on category name
        if "Cloud" in category:
            icon = "☁️"
        elif "Support" in category:
            icon = "🔧"
        elif "Third" in category or "Party" in category:
            icon = "🔗"
        else:
            icon = "📡"
        
        monthly_cost = costs["fixed"] + (costs["variable"] * avg_customers)
        
        cols = [infra_col1, infra_col2, infra_col3, infra_col4]
        with cols[i]:
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="color: #00D084; margin: 0;">{icon} {category}</h4>
                <h2 style="margin: 0.5rem 0 0 0;">${monthly_cost:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)

# Charts
scale_col1, scale_col2 = st.columns(2)

with scale_col1:
    # Customer scaling chart
    st.plotly_chart(create_scaling_analysis(), use_container_width=True)

with scale_col2:
    # Yearly projection chart
    st.plotly_chart(create_cost_projection_chart(), use_container_width=True)

# DATA MANAGEMENT
st.markdown("---")
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

with col1:
    # Auto-save data silently - no manual button needed
    try:
        save_data_to_source(st.session_state.model_data)
    except Exception as e:
        pass  # Silent error handling

with col2:
    if st.button("📂 Load Data", type="primary", use_container_width=True):
        st.session_state.model_data = load_data_from_source()
        st.success("✅ Data loaded successfully!")
        st.rerun()

with col3:
    # Create Excel export data
    try:
        import tempfile
        import os
        from datetime import datetime
        
        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SHAED_Hosting_Costs_Analysis_{timestamp}.xlsx"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            temp_path = tmp_file.name
        
        # Create Excel writer
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            # === COST STRUCTURE DATA ===
            cost_structure = st.session_state.model_data["hosting_costs_data"]["cost_structure"]
            
            # Flatten cost structure for Excel export
            cost_structure_data = []
            for category, services in cost_structure.items():
                for service, costs in services.items():
                    cost_structure_data.append({
                        'Category': category,
                        'Service': service,
                        'Fixed Monthly Cost ($)': costs.get('fixed', 0),
                        'Variable Cost per Customer ($)': costs.get('variable', 0)
                    })
            
            if cost_structure_data:
                structure_df = pd.DataFrame(cost_structure_data)
                structure_df.to_excel(writer, sheet_name='Cost Structure', index=False)
            
            # === MONTHLY COST BREAKDOWN ===
            monthly_costs, monthly_breakdown = calculate_total_hosting_costs()
            capitalized_costs, expensed_costs = calculate_capitalized_vs_expensed()
            
            breakdown_data = []
            for month in months:
                subscribers = get_active_subscribers(month)
                total_cost = monthly_costs.get(month, 0)
                cap_cost = capitalized_costs.get(month, 0)
                exp_cost = expensed_costs.get(month, 0)
                
                # Calculate fixed and per customer costs
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
                
                fixed_cost = total_fixed
                per_customer_cost = total_variable * subscribers
                
                breakdown_data.append({
                    'Month': month,
                    'Active Customers': subscribers,
                    'Fixed Cost ($)': fixed_cost,
                    'Per Customer Cost ($)': per_customer_cost,
                    'Total Cost ($)': total_cost,
                    'Capitalized ($)': cap_cost,
                    'Expensed COGS ($)': exp_cost,
                    'Cost per Customer ($)': total_cost / subscribers if subscribers > 0 else 0
                })
            
            if breakdown_data:
                breakdown_df = pd.DataFrame(breakdown_data)
                breakdown_df.to_excel(writer, sheet_name='Monthly Cost Breakdown', index=False)
            
            # === COST BY CATEGORY BREAKDOWN ===
            category_breakdown_data = []
            for month in months:
                subscribers = get_active_subscribers(month)
                row = {'Month': month, 'Active Customers': subscribers}
                
                for category, services in cost_structure.items():
                    category_fixed = sum(costs.get("fixed", 0) for costs in services.values())
                    category_variable = sum(costs.get("variable", 0) for costs in services.values())
                    category_total = category_fixed + (category_variable * subscribers)
                    row[f'{category} ($)'] = category_total
                
                category_breakdown_data.append(row)
            
            if category_breakdown_data:
                category_df = pd.DataFrame(category_breakdown_data)
                category_df.to_excel(writer, sheet_name='Cost by Category', index=False)
            
            # === MONTHLY OVERRIDES ===
            monthly_overrides = st.session_state.model_data["hosting_costs_data"]["monthly_overrides"]
            if any(override > 0 for override in monthly_overrides.values()):
                overrides_data = [{'Month': month, 'Override Amount ($)': amount} 
                                 for month, amount in monthly_overrides.items() if amount > 0]
                if overrides_data:
                    overrides_df = pd.DataFrame(overrides_data)
                    overrides_df.to_excel(writer, sheet_name='Monthly Overrides', index=False)
            
            # === ANNUAL SUMMARY ===
            years_dict = group_months_by_year(months)
            annual_summary = []
            
            for year in sorted(years_dict.keys()):
                year_months = years_dict[year]
                
                year_total = sum(monthly_costs.get(month, 0) for month in year_months)
                year_cap = sum(capitalized_costs.get(month, 0) for month in year_months)
                year_exp = sum(expensed_costs.get(month, 0) for month in year_months)
                
                # Average customers
                avg_customers = sum(get_active_subscribers(month) for month in year_months) / len(year_months)
                
                annual_summary.append({
                    'Year': year,
                    'Total Hosting Cost ($)': year_total,
                    'Capitalized ($)': year_cap,
                    'Expensed COGS ($)': year_exp,
                    'Average Customers': avg_customers,
                    'Average Monthly Cost ($)': year_total / 12,
                    'Average Cost per Customer ($)': year_total / (avg_customers * 12) if avg_customers > 0 else 0
                })
            
            if annual_summary:
                summary_df = pd.DataFrame(annual_summary)
                summary_df.to_excel(writer, sheet_name='Annual Summary', index=False)
            
            # === SCALING ANALYSIS DATA ===
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
            
            customer_levels = [0, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
            scaling_data = []
            
            for customers in customer_levels:
                total_cost = total_fixed + (total_variable * customers)
                cost_per_customer = total_cost / customers if customers > 0 else 0
                
                scaling_data.append({
                    'Customer Count': customers,
                    'Total Monthly Cost ($)': total_cost,
                    'Cost per Customer ($)': cost_per_customer,
                    'Fixed Component ($)': total_fixed,
                    'Variable Component ($)': total_variable * customers
                })
            
            if scaling_data:
                scaling_df = pd.DataFrame(scaling_data)
                scaling_df.to_excel(writer, sheet_name='Customer Scaling Analysis', index=False)
            
            # === GO-LIVE SETTINGS ===
            go_live_settings = st.session_state.model_data["hosting_costs_data"]["go_live_settings"]
            settings_data = [{
                'Setting': 'Go-Live Month',
                'Value': go_live_settings.get('go_live_month', 'Jan 2025')
            }, {
                'Setting': 'Capitalize Before Go-Live',
                'Value': go_live_settings.get('capitalize_before_go_live', True)
            }]
            
            settings_df = pd.DataFrame(settings_data)
            settings_df.to_excel(writer, sheet_name='Go-Live Settings', index=False)
            
            # === CHART DATA ===
            # Yearly cost projection data
            yearly_data = []
            for year in sorted(years_dict.keys()):
                year_total = sum(monthly_costs.get(month, 0) for month in years_dict[year])
                year_cap = sum(capitalized_costs.get(month, 0) for month in years_dict[year])
                year_exp = sum(expensed_costs.get(month, 0) for month in years_dict[year])
                
                yearly_data.append({
                    'Year': year,
                    'Total Cost ($)': year_total,
                    'Capitalized ($)': year_cap,
                    'Expensed ($)': year_exp
                })
            
            if yearly_data:
                chart_df = pd.DataFrame(yearly_data)
                chart_df.to_excel(writer, sheet_name='Cost Projection Chart Data', index=False)
        
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
    <strong>SHAED Financial Model - Hosting Costs</strong> | Powering the future of mobility<br/>
    © 2025 SHAED - All rights reserved
</div>
""", unsafe_allow_html=True)