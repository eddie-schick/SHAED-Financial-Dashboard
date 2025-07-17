import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="SHAED Finance Dashboard - Hosting Expenses",
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
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Data handling functions
def save_data(data: dict, filename: str = "financial_model_data.json") -> bool:
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
    hosting_data = st.session_state.model_data["hosting_costs_data"]
    go_live_month = hosting_data["go_live_settings"]["go_live_month"]
    capitalize_before = hosting_data["go_live_settings"]["capitalize_before_go_live"]
    
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
    
    # Update the gross profit model's hosting structure to match
    st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"] = {
        "fixed_monthly_cost": total_fixed_per_month,
        "cost_per_customer": total_variable_per_customer,
        "go_live_month": go_live_settings.get("go_live_month", "Jan 2025"),
        "capitalize_before_go_live": go_live_settings.get("capitalize_before_go_live", True),
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
    st.markdown("**☁️ Infrastructure Cost Components**")
    st.info("💡 Set fixed monthly costs and variable costs per customer for each service. You can add, edit, or delete services as needed.")
    
    cost_structure = st.session_state.model_data["hosting_costs_data"]["cost_structure"]
    
    # Add new category option
    st.markdown("### Add New Category")
    new_cat_col1, new_cat_col2 = st.columns([3, 1])
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
    
    st.markdown("---")
    
    # Display existing categories
    categories_to_delete = []
    
    for category, services in cost_structure.items():
        # Category header with delete option
        cat_col1, cat_col2 = st.columns([4, 1])
        with cat_col1:
            st.markdown(f"### {category}")
        with cat_col2:
            if st.button(f"🗑️ Delete", key=f"delete_cat_{category}", help=f"Delete entire {category} category"):
                categories_to_delete.append(category)
        
        # Add new service for this category
        with st.expander(f"➕ Add New Service to {category}", expanded=False):
            service_col1, service_col2, service_col3, service_col4 = st.columns([3, 2, 2, 1])
            
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
        cols = st.columns([3, 2, 2, 1])
        cols[0].markdown("**Service**")
        cols[1].markdown("**Fixed Monthly ($)**")
        cols[2].markdown("**Per Customer ($)**")
        cols[3].markdown("**Action**")
        
        services_to_delete = []
        
        for service, costs in services.items():
            cols = st.columns([3, 2, 2, 1])
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
    st.markdown("**🔧 Monthly Overrides**")
    st.info("💡 Use overrides for one-time costs, migrations, or special circumstances")
    
    if show_monthly:
        years_dict = group_months_by_year(months)
        
        for year in sorted(years_dict.keys()):
            with st.expander(f"📅 {year} Overrides", expanded=(year == "2025")):
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
    <h1>☁️ SHAED Financial Model</h1>
    <h2>☁️ Hosting Expenses</h2>
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

# Initialize data
initialize_hosting_costs_data()

# Data management controls
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("💾 Save Data", type="primary"):
        update_integrated_dashboards()
        if save_data(st.session_state.model_data):
            st.success("Hosting costs saved and integrated with other dashboards!")
        else:
            st.error("Failed to save data")

with nav_col2:
    if st.button("📂 Load Data", type="secondary"):
        st.session_state.model_data = load_data()
        st.success("Data loaded successfully!")
        st.rerun()

with nav_col3:
    if st.button("🔄 Recalculate", type="secondary"):
        update_integrated_dashboards()
        st.success("Hosting costs recalculated and integrated!")

st.markdown("---")

# View Mode Selection
view_mode = st.selectbox(
    "View Mode:",
    ["Monthly + Yearly", "Yearly Only"],
    key="hosting_view_mode"
)

show_monthly = view_mode == "Monthly + Yearly"

st.markdown("---")



# Summary Metrics
st.markdown('<div class="section-header">📊 Hosting Costs Summary</div>', unsafe_allow_html=True)

# Calculate totals
monthly_costs, _ = calculate_total_hosting_costs()
total_costs = sum(monthly_costs.values())
avg_monthly = total_costs / len(months) if len(months) > 0 else 0

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

# Display metrics
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.markdown(f"""
    <div class="metric-container">
        <h4>Total Hosting (6 Years)</h4>
        <h2>${total_costs:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with metric_col2:
    st.markdown(f"""
    <div class="metric-container">
        <h4>Average Monthly</h4>
        <h2>${avg_monthly:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with metric_col3:
    st.markdown(f"""
    <div class="metric-container">
        <h4>Fixed Costs/Month</h4>
        <h2>${total_fixed:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with metric_col4:
    st.markdown(f"""
    <div class="metric-container">
        <h4>Variable $/Customer</h4>
        <h2>${total_variable:.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Cost Structure Configuration
st.markdown('<div class="section-header">💰 Infrastructure Cost Structure</div>', unsafe_allow_html=True)

# Create cost structure table
create_cost_structure_table(show_monthly)

# Calculate and show example
example_customers = 1000
example_cost = total_fixed + (total_variable * example_customers)
st.markdown(f"""
**📊 Example Calculation:**
With {example_customers:,} customers: ${total_fixed:,.2f} + (${total_variable:.2f} × {example_customers:,}) = **${example_cost:,.2f}/month**
""")

st.markdown("---")

# Scaling Analysis
st.markdown('<div class="section-header">📈 Scaling & Efficiency Analysis</div>', unsafe_allow_html=True)

scale_col1, scale_col2 = st.columns(2)

with scale_col1:
    # Customer scaling chart
    st.plotly_chart(create_scaling_analysis(), use_container_width=True)

with scale_col2:
    # Yearly projection chart
    st.plotly_chart(create_cost_projection_chart(), use_container_width=True)

st.markdown("---")

# Monthly Overrides
st.markdown('<div class="section-header">🔧 Monthly Overrides & Adjustments</div>', unsafe_allow_html=True)
create_monthly_overrides_table(show_monthly)

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
        if selected_breakdown_year == "All Years":
            st.info("💡 Showing all 6 years of data (2025-2030)")
        else:
            st.info(f"💡 Showing {selected_breakdown_year} monthly breakdown")
    
    # Get monthly data
    monthly_costs, monthly_breakdown = calculate_total_hosting_costs()
    capitalized_costs, expensed_costs = calculate_capitalized_vs_expensed()
    
    # Filter months based on selected year
    if selected_breakdown_year == "All Years":
        filtered_months = months
    else:
        filtered_months = [month for month in months if month.endswith(selected_breakdown_year)]
    
    # Create monthly breakdown dataframe
    breakdown_data = []
    for month in filtered_months:
        subscribers = get_active_subscribers(month)
        total_cost = monthly_costs.get(month, 0)
        cap_cost = capitalized_costs.get(month, 0)
        exp_cost = expensed_costs.get(month, 0)
        
        breakdown_data.append({
            "Month": month,
            "Subscribers": subscribers,
            "Total Cost": total_cost,
            "Capitalized": cap_cost,
            "Expensed (COGS)": exp_cost,
            "Cost/Customer": total_cost / subscribers if subscribers > 0 else 0
        })
    
    breakdown_df = pd.DataFrame(breakdown_data)
    
    # Configure columns
    column_config = {
        "Month": st.column_config.TextColumn("Month", width="small"),
        "Subscribers": st.column_config.NumberColumn("Customers", format="%.0f", width="small"),
        "Total Cost": st.column_config.NumberColumn("Total Cost", format="$%.0f", width="small"),
        "Capitalized": st.column_config.NumberColumn("Capitalized", format="$%.0f", width="small"),
        "Expensed (COGS)": st.column_config.NumberColumn("COGS", format="$%.0f", width="small"),
        "Cost/Customer": st.column_config.NumberColumn("$/Customer", format="$%.2f", width="small")
    }
    
    st.dataframe(
        breakdown_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Show summary for filtered data
    if breakdown_data:
        total_filtered_cost = sum(row["Total Cost"] for row in breakdown_data)
        total_filtered_cap = sum(row["Capitalized"] for row in breakdown_data)
        total_filtered_exp = sum(row["Expensed (COGS)"] for row in breakdown_data)
        
        summary_text = f"**{selected_breakdown_year} Summary:** Total: ${total_filtered_cost:,.0f} | Capitalized: ${total_filtered_cap:,.0f} | Expensed: ${total_filtered_exp:,.0f}"
        st.markdown(summary_text)

# Integration Status
st.markdown('<div class="section-header">🔗 Integration Status</div>', unsafe_allow_html=True)

int_col1, int_col2 = st.columns(2)

with int_col1:
    st.markdown("""
    **✅ Gross Profit Integration:**
    - Hosting costs are automatically included in COGS calculations
    - Expensed costs reduce gross profit margins
    - Capitalized costs are excluded from monthly COGS
    
    **✅ Liquidity Forecast Integration:**
    - Hosting costs reduce license fees in the liquidity forecast
    - This prevents double-counting of hosting expenses
    - Cash flow projections reflect actual hosting commitments
    """)

with int_col2:
    st.markdown("""
    **✅ Liquidity Dashboard Integration:**
    - License Fees automatically reduced by expensed hosting
    - Prevents double-counting of hosting costs
    - Original license fees preserved for reference
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>SHAED Financial Model - Hosting Costs Dashboard</strong> | Powering the future of mobility
</div>
""", unsafe_allow_html=True)