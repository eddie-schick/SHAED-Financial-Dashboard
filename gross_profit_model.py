import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="SHAED Finance Dashboard - Gross Profit",
    page_icon="📊",
    layout="wide"
)

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
            "fixed_monthly_cost": 500.0,
            "cost_per_customer": 0.50,
            "go_live_month": "Jan 2025",  # Default go-live date
            "capitalize_before_go_live": True  # Toggle for capitalization
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
    """Calculate monthly hosting costs based on fixed + variable structure"""
    hosting_structure = st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]
    fixed_cost = hosting_structure["fixed_monthly_cost"]
    variable_cost = hosting_structure["cost_per_customer"]
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
    
    # Get revenue and calculate metrics
    revenue_data = st.session_state.model_data.get("revenue", {})
    gp_data = st.session_state.model_data.get("gross_profit_data", {})
    cogs_data = calculate_cogs()
    
    # Create tabs for each revenue stream
    tabs = st.tabs(revenue_streams)
    
    for idx, stream in enumerate(revenue_streams):
        with tabs[idx]:
            # Metrics for this stream
            total_revenue = sum(revenue_data.get(stream, {}).get(month, 0) for month in months)
            total_cogs = sum(cogs_data.get(stream, {}).get(month, 0) for month in months)
            total_gross_profit = total_revenue - total_cogs
            avg_gp_percentage = (total_gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>Total Revenue (6 Years)</h4>
                    <h2>${total_revenue:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>Total COGS (6 Years)</h4>
                    <h2>${total_cogs:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>Total Gross Profit (6 Years)</h4>
                    <h2>${total_gross_profit:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>Average GP Margin</h4>
                    <h2>{avg_gp_percentage:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Special handling for Subscription revenue
            if stream == "Subscription":
                st.markdown("**📊 SaaS Hosting Cost Structure**")
                st.info("💡 Hosting costs scale automatically with your customer base using a Fixed + Variable model")
                
                # Go-Live Date Configuration
                st.markdown("**🚀 Development Phase Settings:**")
                dev_col1, dev_col2, dev_col3 = st.columns(3)
                
                with dev_col1:
                    go_live_month = st.selectbox(
                        "Go-Live Month:",
                        options=months,
                        index=months.index(st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"].get("go_live_month", "Jan 2025")),
                        help="Month when platform goes live and hosting costs switch from capitalized to COGS"
                    )
                    st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["go_live_month"] = go_live_month
                
                with dev_col2:
                    capitalize_toggle = st.checkbox(
                        "Capitalize hosting costs before go-live",
                        value=st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"].get("capitalize_before_go_live", True),
                        help="When checked, hosting costs before go-live date are capitalized (COGS = $0)"
                    )
                    st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["capitalize_before_go_live"] = capitalize_toggle
                
                with dev_col3:
                    if capitalize_toggle:
                        hosting_costs, capitalized_hosting = calculate_hosting_costs()
                        total_capitalized = sum(capitalized_hosting.values())
                        st.metric("Total Capitalized Hosting", f"${total_capitalized:,.0f}")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Hosting structure inputs
                    st.markdown("**Cost Structure:**")
                    
                    # Quick templates
                    template = st.selectbox(
                        "Quick Templates:",
                        ["Custom", "Early Stage", "Growth Stage", "Scale Stage", "Enterprise"],
                        key="hosting_template"
                    )
                    
                    if template == "Early Stage":
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["fixed_monthly_cost"] = 500.0
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["cost_per_customer"] = 0.50
                    elif template == "Growth Stage":
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["fixed_monthly_cost"] = 2000.0
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["cost_per_customer"] = 0.35
                    elif template == "Scale Stage":
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["fixed_monthly_cost"] = 5000.0
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["cost_per_customer"] = 0.20
                    elif template == "Enterprise":
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["fixed_monthly_cost"] = 10000.0
                        st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["cost_per_customer"] = 0.10
                    
                    fixed_cost = st.number_input(
                        "Fixed Monthly Cost ($):",
                        value=st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["fixed_monthly_cost"],
                        min_value=0.0,
                        step=100.0,
                        format="%.2f",
                        help="Base infrastructure costs (servers, licenses, etc.)"
                    )
                    st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["fixed_monthly_cost"] = fixed_cost
                    
                    variable_cost = st.number_input(
                        "Cost Per Customer ($):",
                        value=st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["cost_per_customer"],
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        help="Variable cost per active subscriber"
                    )
                    st.session_state.model_data["gross_profit_data"]["saas_hosting_structure"]["cost_per_customer"] = variable_cost
                    
                    # Example calculation
                    example_customers = 1000
                    example_cost = fixed_cost + (variable_cost * example_customers)
                    st.markdown(f"""
                    <div class="hosting-preview">
                    <strong>📊 Example Calculation:</strong><br>
                    With {example_customers:,} customers:<br>
                    ${fixed_cost:,.2f} + (${variable_cost:.2f} × {example_customers:,}) = <strong>${example_cost:,.2f}/month</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Show projection chart
                    st.markdown("**Cost Projection:**")
                    fig = create_hosting_cost_chart()
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Show hosting costs by month
                if show_monthly:
                    st.markdown("**Monthly Hosting Costs (Calculated):**")
                    hosting_costs, capitalized_hosting = calculate_hosting_costs()
                    
                    # Create a simple table showing key months
                    sample_months = ["Jan 2025", "Jun 2025", "Dec 2025", "Jun 2026", "Dec 2026", "Jun 2027", "Dec 2027", "Jun 2028", "Dec 2028", "Jun 2029", "Dec 2029", "Jun 2030", "Dec 2030"]
                    
                    # Show capitalized vs COGS info
                    if capitalize_toggle:
                        st.info(f"📝 Hosting costs are capitalized (COGS = $0) before {go_live_month}, then become regular COGS")
                    
                    cols = st.columns(len(sample_months))
                    for i, month in enumerate(sample_months):
                        with cols[i]:
                            subscribers = get_active_subscribers(month)
                            cost = hosting_costs.get(month, 0)
                            cap_cost = capitalized_hosting.get(month, 0)
                            
                            if cap_cost > 0:
                                st.metric(
                                    month.split()[0],
                                    f"CAP ${cap_cost:,.0f}",
                                    f"{subscribers:.0f} users",
                                    label_visibility="visible"
                                )
                            else:
                                st.metric(
                                    month.split()[0],
                                    f"${cost:,.0f}",
                                    f"{subscribers:.0f} users",
                                    label_visibility="visible"
                                )
                
            else:
                # For non-subscription streams, show gross profit percentage
                st.markdown(f"**💰 Gross Profit % for {stream} Revenue**")
                
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
                    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
                    with quick_col1:
                        set_value = st.number_input(f"Set all to:", value=70.0, min_value=0.0, max_value=100.0, step=5.0, key=f"set_all_{stream}")
                    with quick_col2:
                        if st.button(f"Apply to All Months", key=f"apply_all_{stream}"):
                            for month in months:
                                st.session_state.model_data["gross_profit_data"]["gross_profit_percentages"][stream][month] = set_value
                            st.rerun()
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
            st.markdown("**📈 Gross Profit Analysis**")
            
            # Create results dataframe
            if show_monthly:
                results_data = []
                for year in sorted(years_dict.keys()):
                    for month in years_dict[year]:
                        revenue = revenue_data.get(stream, {}).get(month, 0)
                        cogs = cogs_data.get(stream, {}).get(month, 0)
                        gross_profit = revenue - cogs
                        gp_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
                        
                        results_data.append({
                            "Month": month,
                            "Revenue": revenue,
                            "COGS": cogs,
                            "Gross Profit": gross_profit,
                            "GP Margin": gp_margin
                        })
                
                results_df = pd.DataFrame(results_data)
                
                # Configure columns
                column_config = {
                    "Month": st.column_config.TextColumn("Month", width="small"),
                    "Revenue": st.column_config.NumberColumn("Revenue", format="$%.0f", width="small"),
                    "COGS": st.column_config.NumberColumn("COGS", format="$%.0f", width="small"),
                    "Gross Profit": st.column_config.NumberColumn("Gross Profit", format="$%.0f", width="small"),
                    "GP Margin": st.column_config.NumberColumn("GP Margin", format="%.1f%%", width="small")
                }
                
                st.dataframe(
                    results_df,
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
            else:
                # Yearly summary
                yearly_results = []
                for year in sorted(years_dict.keys()):
                    year_revenue = sum(revenue_data.get(stream, {}).get(month, 0) for month in years_dict[year])
                    year_cogs = sum(cogs_data.get(stream, {}).get(month, 0) for month in years_dict[year])
                    year_gp = year_revenue - year_cogs
                    year_margin = (year_gp / year_revenue * 100) if year_revenue > 0 else 0
                    
                    yearly_results.append({
                        "Year": year,
                        "Revenue": year_revenue,
                        "COGS": year_cogs,
                        "Gross Profit": year_gp,
                        "GP Margin": year_margin
                    })
                
                yearly_df = pd.DataFrame(yearly_results)
                
                column_config = {
                    "Year": st.column_config.TextColumn("Year", width="small"),
                    "Revenue": st.column_config.NumberColumn("Revenue", format="$%.0f", width="medium"),
                    "COGS": st.column_config.NumberColumn("COGS", format="$%.0f", width="medium"),
                    "Gross Profit": st.column_config.NumberColumn("Gross Profit", format="$%.0f", width="medium"),
                    "GP Margin": st.column_config.NumberColumn("GP Margin", format="%.1f%%", width="small")
                }
                
                st.dataframe(
                    yearly_df,
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=True
                )

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 SHAED Financial Model</h1>
    <h2>Gross Profit Analysis</h2>
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

# View Mode Selection
view_mode = st.selectbox(
    "View Mode:",
    ["Monthly + Yearly", "Yearly Only"],
    key="gp_view_mode"
)

show_monthly = view_mode == "Monthly + Yearly"

st.markdown("---")

# Initialize data
initialize_gross_profit_data()

# Data management controls
st.markdown('<div class="section-header">💾 Data Management</div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

with nav_col1:
    if st.button("💾 Save Data", type="primary"):
        update_income_statement_cogs()
        if save_data(st.session_state.model_data):
            st.success("Gross profit data saved and COGS updated in Income Statement!")
        else:
            st.error("Failed to save data")

with nav_col2:
    if st.button("📂 Load Data", type="secondary"):
        st.session_state.model_data = load_data()
        st.success("Data loaded successfully!")
        st.rerun()

with nav_col3:
    if st.button("🔄 Recalculate", type="secondary"):
        update_income_statement_cogs()
        st.success("COGS recalculated and updated in Income Statement!")

st.markdown("---")

# Check if revenue data exists
if "revenue" not in st.session_state.model_data or not any(
    st.session_state.model_data["revenue"].get(stream, {}) 
    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
):
    st.warning("⚠️ No revenue data found! Please generate revenue in the Revenue first.")
    st.info("The Gross Profit calculates COGS based on revenue and gross profit margins.")
else:
    # Overall summary metrics
    st.markdown('<div class="section-header">📊 Overall Gross Profit Summary</div>', unsafe_allow_html=True)
    
    # Calculate totals
    revenue_data = st.session_state.model_data.get("revenue", {})
    cogs_data = calculate_cogs()
    
    total_revenue_all = sum(
        revenue_data.get(stream, {}).get(month, 0)
        for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
        for month in months
    )
    
    total_cogs_all = sum(
        cogs_data.get(stream, {}).get(month, 0)
        for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]
        for month in months
    )
    
    total_gp_all = total_revenue_all - total_cogs_all
    overall_gp_margin = (total_gp_all / total_revenue_all * 100) if total_revenue_all > 0 else 0
    
    # Display overall metrics
    overall_col1, overall_col2, overall_col3, overall_col4 = st.columns(4)
    
    with overall_col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4>Total Revenue (All Streams)</h4>
            <h2>${total_revenue_all:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with overall_col2:
        st.markdown(f"""
        <div class="metric-container">
            <h4>Total COGS (All Streams)</h4>
            <h2>${total_cogs_all:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with overall_col3:
        st.markdown(f"""
        <div class="metric-container">
            <h4>Total Gross Profit</h4>
            <h2>${total_gp_all:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with overall_col4:
        st.markdown(f"""
        <div class="metric-container">
            <h4>Overall GP Margin</h4>
            <h2>{overall_gp_margin:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Revenue stream details
    st.markdown('<div class="section-header">💼 Gross Profit by Revenue Stream</div>', unsafe_allow_html=True)
    
    st.info("""
    💡 **How to use this dashboard:**
    - **Subscription Revenue**: Set fixed + variable hosting costs. Automatically scales with customer growth
    - **Other Revenue Streams**: Set gross profit margins by year (applies to all months in that year)
    - Changes automatically update COGS in the Income Statement when you save
    """)
    
    # Create gross profit table for each revenue stream
    revenue_streams = ["Subscription", "Transactional", "Implementation", "Maintenance"]
    create_gross_profit_table(revenue_streams, show_monthly)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <strong>SHAED Financial Model - Gross Profit Dashboard</strong> | Powering the future of mobility
</div>
""", unsafe_allow_html=True)