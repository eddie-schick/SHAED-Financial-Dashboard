import streamlit as st
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

# Password protection function
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show login form
        st.markdown("""
        <style>
            .login-container {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 70vh;
                background-color: #f8f9fa;
            }
            .login-form {
                background: white;
                padding: 3rem;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 400px;
                width: 100%;
            }
            .login-header {
                background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
                color: white;
                padding: 2rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .login-header h1 {
                margin: 0;
                font-size: 2.5rem;
                font-weight: 700;
            }
            .login-header p {
                margin: 0.5rem 0 0 0;
                font-size: 1.1rem;
                opacity: 0.9;
            }
            .stTextInput > div > div > input {
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                padding: 0.75rem;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            .stTextInput > div > div > input:focus {
                border-color: #00D084;
                box-shadow: 0 0 0 2px rgba(0, 208, 132, 0.2);
            }
            .stButton > button {
                background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.75rem 2rem;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                width: 100%;
                margin-top: 1rem;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create centered login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="login-header">
                <h1>SHAED Financial Model</h1>
                <p>Please enter password to continue</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😞 Password incorrect")
        
        return False
        
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.markdown("""
        <style>
            .login-container {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 70vh;
                background-color: #f8f9fa;
            }
            .login-form {
                background: white;
                padding: 3rem;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 400px;
                width: 100%;
            }
            .login-header {
                background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
                color: white;
                padding: 2rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .login-header h1 {
                margin: 0;
                font-size: 2.5rem;
                font-weight: 700;
            }
            .login-header p {
                margin: 0.5rem 0 0 0;
                font-size: 1.1rem;
                opacity: 0.9;
            }
            .stTextInput > div > div > input {
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                padding: 0.75rem;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            .stTextInput > div > div > input:focus {
                border-color: #00D084;
                box-shadow: 0 0 0 2px rgba(0, 208, 132, 0.2);
            }
            .stButton > button {
                background: linear-gradient(90deg, #00D084 0%, #00B574 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.75rem 2rem;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                width: 100%;
                margin-top: 1rem;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create centered login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="login-header">
                <h1>SHAED Financial Model</h1>
                <p>Please enter password to continue</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            st.error("😞 Password incorrect")
        
        return False
    else:
        # Password correct.
        return True

# Check authentication
if not check_password():
    st.stop()

# Add logout functionality to sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Logout", key="logout_button"):
        # Clear all session state variables
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

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
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Section headers */
    .section-header {
        background-color: #00D084;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 2rem 0 1.5rem 0;
        font-size: 1.3rem;
        font-weight: 600;
        text-align: center;
    }
    
    /* Navigation card styling */
    .nav-card {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        border-color: #00D084;
    }
    
    .nav-card h3 {
        color: #00D084;
        margin: 0 0 0.5rem 0;
        font-size: 1.4rem;
    }
    
    .nav-card p {
        color: #666;
        margin: 0 0 1rem 0;
        font-size: 0.95rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #00D084 0%, #00B574 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        display: block !important;
        margin: 0 auto !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        background: linear-gradient(90deg, #00B574 0%, #009A64 100%) !important;
    }
    
    /* Ensure button container takes full width */
    .stButton {
        width: 100% !important;
        display: block !important;
    }
    
    /* Force button container in columns to be full width */
    [data-testid="column"] .stButton {
        width: 100% !important;
    }
    
    [data-testid="column"] .stButton > button {
        width: 100% !important;
        min-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* Additional button width enforcement for Streamlit Cloud */
    .element-container .stButton {
        width: 100% !important;
    }
    
    .element-container .stButton > button {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 !important;
    }
    
    /* Ensure columns maintain proper spacing */
    [data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    
    [data-testid="column"]:first-child {
        padding-left: 0 !important;
    }
    
    [data-testid="column"]:last-child {
        padding-right: 0 !important;
    }
    
    /* Welcome section */
    .welcome-section {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .welcome-section h2 {
        color: #00D084;
        margin-bottom: 1rem;
    }
    
    /* Quick stats */
    .stat-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #00D084;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .stat-container h4 {
        color: #00D084;
        margin: 0;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-container h2 {
        margin: 0.5rem 0 0 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a1a;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏠 Home</h1>
    <p>Comprehensive Financial Planning & Analysis Platform</p>
</div>
""", unsafe_allow_html=True)

# Welcome message with current date
current_date = datetime.now().strftime("%B %d, %Y")
st.markdown(f"""
<div class="welcome-section">
    <h2>Welcome to Your Financial Command Center</h2>
    <p>Today is {current_date}</p>
    <p>Navigate to any dashboard below to view and manage your financial data.</p>
</div>
""", unsafe_allow_html=True)

# Navigation Section
st.markdown('<div class="section-header">🧭 Navigate to Dashboards</div>', unsafe_allow_html=True)

# Create navigation cards in a grid layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="nav-card">
        <h3>📊 KPIs Dashboard</h3>
        <p>Key performance indicators and executive summary metrics</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open KPIs Dashboard", key="kpi_btn"):
        st.switch_page("pages/1__KPIs_Dashboard.py")

with col2:
    st.markdown("""
    <div class="nav-card">
        <h3>📈 Income Statement</h3>
        <p>Complete P&L with revenue, expenses, and profitability analysis</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Income Statement", key="income_btn"):
        st.switch_page("pages/2__Income_Statement.py")

with col3:
    st.markdown("""
    <div class="nav-card">
        <h3>💰 Liquidity Forecast</h3>
        <p>Cash flow projections and liquidity management</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Liquidity Forecast", key="liquidity_btn"):
        st.switch_page("pages/3__Liquidity_Forecast.py")

# Second row of navigation cards
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class="nav-card">
        <h3>💵 Revenue Assumptions</h3>
        <p>Detailed revenue streams and growth projections</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Revenue Dashboard", key="revenue_btn"):
        st.switch_page("pages/4__Revenue_Assumptions.py")

with col5:
    st.markdown("""
    <div class="nav-card">
        <h3>👥 Headcount Planning</h3>
        <p>Employee and contractor management with payroll forecasting</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Headcount Dashboard", key="headcount_btn"):
        st.switch_page("pages/5__Headcount_Planning.py")

with col6:
    st.markdown("""
    <div class="nav-card">
        <h3>🔍 Gross Profit Analysis</h3>
        <p>Gross margin analysis and COGS management</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Gross Profit Dashboard", key="gross_profit_btn"):
        st.switch_page("pages/6__Gross_Profit_Analysis.py")

# Third row removed - hosting costs section deleted

# Features Section
st.markdown('<div class="section-header">✨ Platform Features</div>', unsafe_allow_html=True)

feat_col1, feat_col2, feat_col3 = st.columns(3)

with feat_col1:
    st.markdown("""
    #### 🔄 Integrated Data Flow
    - Automatic data synchronization between dashboards
    - Real-time updates across all modules
    - Unified data storage system
    """)

with feat_col2:
    st.markdown("""
    #### 📊 Comprehensive Analysis
    - Monthly and yearly projections
    - Visual charts and graphs
    - Detailed financial metrics
    """)

with feat_col3:
    st.markdown("""
    #### 💾 Data Management
    - Save and load functionality
    - Back end data persistence
    - Easy data export/import
    """)



# Footer
st.markdown("""
<div class="footer">
    <strong>SHAED Finance Dashboard</strong> | Powering the future of mobility<br>
    <small>© 2025 SHAED - All rights reserved</small>
</div>
""", unsafe_allow_html=True)

