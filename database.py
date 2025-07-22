import os
from supabase import create_client, Client
import streamlit as st
from typing import Dict, Any, List
import json
from datetime import datetime

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client with caching"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        supabase = create_client(url, key)
        return supabase
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        # Fallback to hardcoded values for testing
        url = "https://gdltscxgbhgybppbngeo.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdkbHRzY3hnYmhneWJwcGJuZ2VvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTQ5NzAsImV4cCI6MjA2ODY3MDk3MH0.0wmAJx0zTrHuTvk1ihIdltEN-7sQBbR5BpVQKDvYPlQ"
        return create_client(url, key)

# Generic save/load functions for backward compatibility
def save_to_supabase(data: Dict[str, Any]) -> bool:
    """Save data to Supabase - maintains compatibility with existing code"""
    try:
        supabase = init_supabase()
        
        # Process different data types
        for data_type, type_data in data.items():
            if data_type == "revenue_assumptions":
                save_revenue_assumptions(type_data)
            elif data_type == "headcount":
                save_headcount_data(type_data)
            elif data_type == "liquidity":
                save_liquidity_data(type_data)
            elif data_type == "kpis":
                save_kpi_metrics(type_data)
            else:
                # Generic save for other data types
                save_financial_model_data(data_type, type_data)
        
        return True
    except Exception as e:
        st.error(f"Error saving to Supabase: {e}")
        return False

def load_from_supabase() -> Dict[str, Any]:
    """Load all data from Supabase"""
    try:
        data = {}
        
        # Load from different tables
        data["revenue_assumptions"] = load_revenue_assumptions()
        data["headcount"] = load_headcount_data()
        data["liquidity"] = load_liquidity_data()
        data["kpis"] = load_kpi_metrics()
        
        # Load other financial data
        financial_data = load_financial_model_data()
        data.update(financial_data)
        
        return data
    except Exception as e:
        st.error(f"Error loading from Supabase: {e}")
        return {}

# Specific functions for each table
def save_financial_model_data(data_type: str, type_data: Dict[str, Any]) -> bool:
    """Save data to the main financial_model_data table"""
    try:
        supabase = init_supabase()
        records = []
        
        if isinstance(type_data, dict):
            for category, category_data in type_data.items():
                if isinstance(category_data, dict):
                    for month, value in category_data.items():
                        year = int(month.split('-')[0]) if '-' in month else 2025
                        
                        record = {
                            'data_type': data_type,
                            'month': month,
                            'year': year,
                            'category': category,
                            'value': float(value) if value else 0
                        }
                        records.append(record)
        
        if records:
            # Delete existing records for this data_type
            supabase.table('financial_model_data').delete().eq('data_type', data_type).execute()
            # Insert new records
            supabase.table('financial_model_data').insert(records).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving financial model data: {e}")
        return False

def load_financial_model_data() -> Dict[str, Any]:
    """Load data from the main financial_model_data table"""
    try:
        supabase = init_supabase()
        response = supabase.table('financial_model_data').select("*").execute()
        
        data = {}
        for record in response.data:
            data_type = record['data_type']
            category = record['category']
            month = record['month']
            value = float(record['value'])
            
            if data_type not in data:
                data[data_type] = {}
            if category not in data[data_type]:
                data[data_type][category] = {}
            
            data[data_type][category][month] = value
        
        return data
    except Exception as e:
        st.error(f"Error loading financial model data: {e}")
        return {}

def save_revenue_assumptions(revenue_data: Dict[str, Any]) -> bool:
    """Save revenue assumptions data"""
    try:
        supabase = init_supabase()
        records = []
        
        for product_category, category_data in revenue_data.items():
            if isinstance(category_data, dict):
                for metric_name, metric_data in category_data.items():
                    if isinstance(metric_data, dict):
                        for month, value in metric_data.items():
                            year = int(month.split('-')[0]) if '-' in month else 2025
                            
                            record = {
                                'month': month,
                                'year': year,
                                'product_category': product_category,
                                'metric_name': metric_name,
                                'value': float(value) if value else 0
                            }
                            records.append(record)
        
        if records:
            # Clear existing data
            supabase.table('revenue_assumptions').delete().neq('id', 0).execute()
            # Insert new records
            supabase.table('revenue_assumptions').insert(records).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving revenue assumptions: {e}")
        return False

def load_revenue_assumptions() -> Dict[str, Any]:
    """Load revenue assumptions data"""
    try:
        supabase = init_supabase()
        response = supabase.table('revenue_assumptions').select("*").execute()
        
        data = {}
        for record in response.data:
            product_category = record['product_category']
            metric_name = record['metric_name']
            month = record['month']
            value = float(record['value'])
            
            if product_category not in data:
                data[product_category] = {}
            if metric_name not in data[product_category]:
                data[product_category][metric_name] = {}
            
            data[product_category][metric_name][month] = value
        
        return data
    except Exception as e:
        st.error(f"Error loading revenue assumptions: {e}")
        return {}

def save_headcount_data(headcount_data: Dict[str, Any]) -> bool:
    """Save headcount/payroll data"""
    try:
        supabase = init_supabase()
        records = []
        
        for department, dept_data in headcount_data.items():
            if isinstance(dept_data, dict):
                for employee_type, type_data in dept_data.items():
                    if isinstance(type_data, dict):
                        for month, value in type_data.items():
                            year = int(month.split('-')[0]) if '-' in month else 2025
                            
                            # Determine if this is headcount or cost data
                            if 'count' in employee_type.lower():
                                record = {
                                    'month': month,
                                    'year': year,
                                    'department': department,
                                    'employee_type': 'full_time' if 'contractor' not in employee_type.lower() else 'contractor',
                                    'headcount': int(value) if value else 0,
                                    'total_cost': 0
                                }
                            else:
                                record = {
                                    'month': month,
                                    'year': year,
                                    'department': department,
                                    'employee_type': 'full_time' if 'contractor' not in employee_type.lower() else 'contractor',
                                    'headcount': 0,
                                    'total_cost': float(value) if value else 0
                                }
                            records.append(record)
        
        if records:
            supabase.table('headcount_data').delete().neq('id', 0).execute()
            supabase.table('headcount_data').insert(records).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving headcount data: {e}")
        return False

def load_headcount_data() -> Dict[str, Any]:
    """Load headcount/payroll data"""
    try:
        supabase = init_supabase()
        response = supabase.table('headcount_data').select("*").execute()
        
        data = {}
        for record in response.data:
            department = record['department']
            employee_type = record['employee_type']
            month = record['month']
            headcount = record['headcount']
            total_cost = float(record['total_cost'])
            
            if department not in data:
                data[department] = {}
            
            # Store both headcount and cost
            if headcount > 0:
                key = f"{employee_type}_count"
                if key not in data[department]:
                    data[department][key] = {}
                data[department][key][month] = headcount
            
            if total_cost > 0:
                key = f"{employee_type}_cost"
                if key not in data[department]:
                    data[department][key] = {}
                data[department][key][month] = total_cost
        
        return data
    except Exception as e:
        st.error(f"Error loading headcount data: {e}")
        return {}

def save_liquidity_data(liquidity_data: Dict[str, Any]) -> bool:
    """Save liquidity/cash flow data"""
    try:
        supabase = init_supabase()
        records = []
        
        for flow_type, type_data in liquidity_data.items():
            if isinstance(type_data, dict):
                for category, category_data in type_data.items():
                    if isinstance(category_data, dict):
                        for month, amount in category_data.items():
                            year = int(month.split('-')[0]) if '-' in month else 2025
                            
                            record = {
                                'month': month,
                                'year': year,
                                'flow_type': 'inflow' if flow_type in ['revenue', 'investment', 'other_receipts'] else 'outflow',
                                'category': category,
                                'amount': float(amount) if amount else 0
                            }
                            records.append(record)
        
        if records:
            supabase.table('liquidity_data').delete().neq('id', 0).execute()
            supabase.table('liquidity_data').insert(records).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving liquidity data: {e}")
        return False

def load_liquidity_data() -> Dict[str, Any]:
    """Load liquidity/cash flow data"""
    try:
        supabase = init_supabase()
        response = supabase.table('liquidity_data').select("*").execute()
        
        data = {}
        for record in response.data:
            flow_type = record['flow_type']
            category = record['category']
            month = record['month']
            amount = float(record['amount'])
            
            if category not in data:
                data[category] = {}
            
            data[category][month] = amount
        
        return data
    except Exception as e:
        st.error(f"Error loading liquidity data: {e}")
        return {}

def save_kpi_metrics(kpi_data: Dict[str, Any]) -> bool:
    """Save KPI metrics"""
    try:
        supabase = init_supabase()
        records = []
        
        for kpi_name, kpi_values in kpi_data.items():
            if isinstance(kpi_values, dict):
                for month, value in kpi_values.items():
                    year = int(month.split('-')[0]) if '-' in month else 2025
                    
                    # Determine unit based on KPI name
                    if '%' in str(value) or 'margin' in kpi_name.lower():
                        unit = 'percentage'
                    elif '$' in str(value) or 'revenue' in kpi_name.lower() or 'cost' in kpi_name.lower():
                        unit = 'currency'
                    else:
                        unit = 'number'
                    
                    record = {
                        'month': month,
                        'year': year,
                        'kpi_name': kpi_name,
                        'kpi_value': float(str(value).replace('%', '').replace('$', '').replace(',', '')) if value else 0,
                        'unit': unit
                    }
                    records.append(record)
        
        if records:
            supabase.table('kpi_metrics').delete().neq('id', 0).execute()
            supabase.table('kpi_metrics').insert(records).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving KPI metrics: {e}")
        return False

def load_kpi_metrics() -> Dict[str, Any]:
    """Load KPI metrics"""
    try:
        supabase = init_supabase()
        response = supabase.table('kpi_metrics').select("*").execute()
        
        data = {}
        for record in response.data:
            kpi_name = record['kpi_name']
            month = record['month']
            value = float(record['kpi_value'])
            
            if kpi_name not in data:
                data[kpi_name] = {}
            
            data[kpi_name][month] = value
        
        return data
    except Exception as e:
        st.error(f"Error loading KPI metrics: {e}")
        return {}

# Migration function
def migrate_json_to_supabase(json_file: str = "financial_model_data.json"):
    """One-time migration from JSON to Supabase"""
    try:
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            
            if save_to_supabase(json_data):
                st.success("✅ Data migrated to Supabase successfully!")
                # Optionally rename the JSON file to indicate it's been migrated
                os.rename(json_file, f"{json_file}.migrated")
                return True
        else:
            st.warning("⚠️ No JSON file found to migrate")
        return False
    except Exception as e:
        st.error(f"Migration error: {e}")
        return False

# Backward compatibility functions
def save_data(data: dict) -> bool:
    """Save data to Supabase using simple single-table approach"""
    try:
        # Use hardcoded credentials for consistency
        url = "https://gdltscxgbhgybppbngeo.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdkbHRzY3hnYmhneWJwcGJuZ2VvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTQ5NzAsImV4cCI6MjA2ODY3MDk3MH0.0wmAJx0zTrHuTvk1ihIdltEN-7sQBbR5BpVQKDvYPlQ"
        supabase = create_client(url, key)
        
        # Check if any records exist
        check_result = supabase.table('financial_data').select('id').limit(1).execute()
        
        if check_result.data:
            # Update existing record
            result = supabase.table('financial_data').update({
                'data': data
            }).eq('id', check_result.data[0]['id']).execute()
        else:
            # Insert new record
            result = supabase.table('financial_data').insert({
                'data': data
            }).execute()
        
        return bool(result.data)
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def load_data() -> dict:
    """Load data from Supabase using simple single-table approach"""
    try:
        # Use hardcoded credentials for consistency  
        url = "https://gdltscxgbhgybppbngeo.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdkbHRzY3hnYmhneWJwcGJuZ2VvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTQ5NzAsImV4cCI6MjA2ODY3MDk3MH0.0wmAJx0zTrHuTvk1ihIdltEN-7sQBbR5BpVQKDvYPlQ"
        supabase = create_client(url, key)
        
        # Load from the financial_data table (single JSONB record)
        result = supabase.table('financial_data').select('data').order('updated_at', desc=True).limit(1).execute()
        
        if result.data:
            return result.data[0]['data']
    except Exception as e:
        print(f"Error loading from Supabase: {e}")
    
    # Fallback to JSON file
    json_file = 'financial_model_data.json'
    if not os.path.exists(json_file):
        json_file = 'financial_model_data.json.migrated'
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading from JSON file: {e}")
    
    return {}