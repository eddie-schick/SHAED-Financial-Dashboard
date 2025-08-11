import os
from supabase import create_client, Client
import streamlit as st
from typing import Dict, Any, List
import json
import time
from datetime import datetime

# Helper functions for logging that work both in and out of Streamlit context
def log_error(message: str):
    """Log an error message, works both in and out of Streamlit"""
    try:
        st.error(message)
    except:
        print(f"ERROR: {message}")

def log_warning(message: str):
    """Log a warning message, works both in and out of Streamlit"""
    try:
        st.warning(message)
    except:
        print(f"WARNING: {message}")

def log_success(message: str):
    """Log a success message, works both in and out of Streamlit"""
    try:
        st.success(message)
    except:
        print(f"SUCCESS: {message}")

def log_info(message: str, data=None):
    """Log info message, works both in and out of Streamlit"""
    try:
        st.write(message, data if data else "")
    except:
        print(f"INFO: {message}")
        if data:
            print(data)

# Initialize Supabase client
def init_supabase() -> Client:
    """Initialize Supabase client preferring the service role key for write access.

    Resolution improvements:
    - Reads config from Streamlit secrets OR environment variables (SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY)
    - Warns when only the anon key is available (writes may be blocked by RLS)
    - Retains SSL-aware retry logic and a final fallback path
    """
    import time

    def get_supabase_config():
        url = None
        service_key = None
        anon_key = None

        # Streamlit secrets (preferred)
        try:
            url = st.secrets.get("SUPABASE_URL", None)  # type: ignore[attr-defined]
            service_key = st.secrets.get("SUPABASE_SERVICE_KEY", None)  # type: ignore[attr-defined]
            anon_key = st.secrets.get("SUPABASE_ANON_KEY", None)  # type: ignore[attr-defined]
        except Exception:
            pass

        # Environment variables (fallback)
        url = url or os.environ.get("SUPABASE_URL")
        service_key = service_key or os.environ.get("SUPABASE_SERVICE_KEY")
        anon_key = anon_key or os.environ.get("SUPABASE_ANON_KEY")

        return url, service_key, anon_key

    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            url, service_key, anon_key = get_supabase_config()
            if not url:
                raise KeyError("SUPABASE_URL is not set in Streamlit secrets or environment variables")

            key_to_use = service_key or anon_key
            if not key_to_use:
                raise KeyError("Neither SUPABASE_SERVICE_KEY nor SUPABASE_ANON_KEY is set")

            if service_key is None:
                # Using anon key → warn about possible RLS restrictions
                log_warning("Using anon key for Supabase. Writes may be blocked by RLS. Configure SUPABASE_SERVICE_KEY for full access.")

            supabase = create_client(url, key_to_use)

            # Test connection with a simple query
            supabase.table('business_segments').select('id').limit(1).execute()
            return supabase

        except Exception as e:
            error_msg = str(e)

            # Check if it's an SSL error
            if "SSL" in error_msg or "sslv3" in error_msg.lower() or "bad record mac" in error_msg.lower():
                print(f"SSL error on attempt {attempt + 1}/{max_retries}: {error_msg[:50]}...")

                # Clear cached client if it exists
                try:
                    get_supabase_client.clear()
                except Exception:
                    pass

                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 10)
                    continue
            elif attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 10)
                continue

            # Final fallback (hardcoded anon) — may be blocked by RLS
            try:
                print("Trying fallback connection...")
                url = "https://gdltscxgbhgybppbngeo.supabase.co"
                key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdkbHRzY3hnYmhneWJwcGJuZ2VvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwOTQ5NzAsImV4cCI6MjA2ODY3MDk3MH0.0wmAJx0zTrHuTvk1ihIdltEN-7sQBbR5BpVQKDvYPlQ"
                supabase = create_client(url, key)

                # Test connection
                supabase.table('business_segments').select('id').limit(1).execute()
                print("Fallback connection successful")
                log_warning("Connected to Supabase using fallback anon key. Writes may fail due to RLS.")
                return supabase

            except Exception as fallback_error:
                print(f"Fallback also failed: {str(fallback_error)[:50]}...")
                return None

def get_supabase_connection_info() -> Dict[str, Any]:
    """Return connection configuration info for diagnostics (no secrets exposed)."""
    url = None
    has_service_key = False
    has_anon_key = False
    try:
        try:
            url = st.secrets.get("SUPABASE_URL", None)  # type: ignore[attr-defined]
            has_service_key = bool(st.secrets.get("SUPABASE_SERVICE_KEY", None))  # type: ignore[attr-defined]
            has_anon_key = bool(st.secrets.get("SUPABASE_ANON_KEY", None))  # type: ignore[attr-defined]
        except Exception:
            pass
        url = url or os.environ.get("SUPABASE_URL")
        has_service_key = has_service_key or bool(os.environ.get("SUPABASE_SERVICE_KEY"))
        has_anon_key = has_anon_key or bool(os.environ.get("SUPABASE_ANON_KEY"))
    except Exception:
        pass

    mode = "service" if has_service_key else ("anon" if has_anon_key else "none")
    return {"url_configured": bool(url), "mode": mode, "has_service_key": has_service_key, "has_anon_key": has_anon_key}

def clear_data_caches():
    """Clear cached loaders so UI can force-refresh from Supabase."""
    try:
        load_revenue_assumptions_from_database.clear()
    except Exception:
        pass
    try:
        load_comprehensive_revenue_data_from_database.clear()
    except Exception:
        pass
    try:
        load_data_from_source.clear()
    except Exception:
        pass

@st.cache_resource
def get_supabase_client() -> Client:
    """Get cached Supabase client"""
    return init_supabase()

def get_fresh_supabase_client() -> Client:
    """Get a fresh non-cached Supabase client for critical operations"""
    return init_supabase()

def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            return False
        
        # Test with a simple query
        result = supabase.table('business_segments').select('id').limit(1).execute()
        return True
    except:
        return False

def show_connection_status():
    """Display database connection status"""
    if check_database_connection():
        st.success("🟢 Database Connected")
    else:
        st.error("🔴 Database Connection Failed")

def clear_connection_cache():
    """Clear Streamlit cache and force fresh database connection"""
    try:
        # Clear the cached Supabase client
        get_supabase_client.clear()
        st.success("🔄 Connection cache cleared. Reconnecting...")
        return True
    except Exception as e:
        st.error(f"❌ Error clearing cache: {str(e)}")
        return False

def clear_all_data_cache():
    """Clear all cached data to force fresh database queries"""
    try:
        # Clear all cached data functions
        load_revenue_assumptions_from_database.clear()
        load_payroll_data_from_database.clear() 
        # load_hosting_costs_from_database.clear()  # Function removed
        load_budget_data_from_database.clear()
        # load_gross_profit_data_from_database.clear()  # Function removed
        load_revenue_and_cogs_from_database.clear()
        load_liquidity_data_from_database.clear()
        load_revenue_calculations_from_database.clear()
        load_comprehensive_revenue_data_from_database.clear()
        get_supabase_client.clear()
        st.success("🔄 All data caches cleared. Next page load will fetch fresh data.")
        return True
    except Exception as e:
        st.error(f"❌ Error clearing data cache: {str(e)}")
        return False

# ===== COMPREHENSIVE SAVE FUNCTIONS MAPPED TO EXISTING TABLES =====

def ensure_business_segments_exist(supabase) -> Dict[str, int]:
    """Ensure all required business segments exist in the database"""
    # List of all required stakeholders/segments
    required_segments = [
        "Dealership", "End User", "Equipment Manufacturer", "Upfitter",
        "Depot", "Fleet Management Company", "Logistics", "OEM",
        "Traditional Finance Provider", "Channel Partner", "Charging OEM", "Insurance Provider",
        "Maintenance Provider", "Charging as a Service", "EPC", "Government Agency",
        "Grant Administrator", "Operating and Maintenance Provider", "Remarketing Specialists", "Technology Solutions",
        "Utility Provider"
    ]
    
    # Also add transactional segments
    transactional_categories = ["Charging", "Vehicle", "Financing", "Other Revenue"]
    for category in transactional_categories:
        required_segments.append(f"Transactional-{category}")
    
    # Get existing segments
    segments_response = supabase.table('business_segments').select('id, segment_name').limit(10000).execute()
    existing_segments = {row['segment_name']: row['id'] for row in segments_response.data}
    
    # Create missing segments
    new_segments = []
    for segment_name in required_segments:
        if segment_name not in existing_segments:
            new_segments.append({
                'segment_name': segment_name,
                'description': f'Business segment for {segment_name}'
            })
    
    if new_segments:
        # Insert new segments
        insert_response = supabase.table('business_segments').insert(new_segments).execute()
        # Update mapping with new segments
        for segment in insert_response.data:
            existing_segments[segment['segment_name']] = segment['id']
    
    return existing_segments

def save_revenue_assumptions_to_database(data: Dict[str, Any]) -> bool:
    """Save revenue assumptions to customer_assumptions and pricing_data tables"""
    try:
        # Get a fresh client for saving operations
        supabase = get_fresh_supabase_client()
        if supabase is None:
            log_error("❌ Database connection failed. Please check your connection settings.")
            return False
            
        # Ensure all business segments exist and get mapping
        segment_mapping = ensure_business_segments_exist(supabase)
        
        def get_segment_id(stakeholder_name):
            """Get segment ID from mapping. Returns None if not found."""
            if stakeholder_name in segment_mapping:
                return segment_mapping[stakeholder_name]
            return None
        
        # Don't delete existing data - use upsert instead to preserve existing records
        
        customer_records = []
        pricing_records = []
        
        # Process revenue assumption data
        revenue_data_mappings = [
            ('subscription_new_customers', 'subscription', 'new_customers'),
            ('transactional_volume', 'transactional', 'volume'),  # Fixed: Use correct key
            ('implementation_new_customers', 'implementation', 'new_customers'),
            ('maintenance_new_customers', 'maintenance', 'new_customers'),
        ]
        
        pricing_data_mappings = [
            ('subscription_pricing', 'subscription'),
            ('transactional_price', 'transactional'),  # Fixed: Use correct key
            ('implementation_pricing', 'implementation'),
            ('maintenance_pricing', 'maintenance'),
        ]
        
        # Save customer assumptions
        for data_key, service_type, metric_name in revenue_data_mappings:
            if data_key in data:
                for stakeholder_or_category, monthly_data in data[data_key].items():
                    # Handle transactional data specially - it uses categories not stakeholders
                    if service_type == 'transactional':
                        # Create a generic segment for transactional data using the category name
                        segment_name = f"Transactional-{stakeholder_or_category}"
                        segment_id = get_segment_id(segment_name)
                        if segment_id:
                            for month_str, value in monthly_data.items():
                                try:
                                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                                    customer_records.append({
                                        'year_month': year_month,
                                        'business_segment_id': segment_id,
                                        'service_type': service_type,
                                        'metric_name': metric_name,
                                        'value': float(value) if value is not None else 0.0
                                    })
                                except:
                                    continue
                    else:
                        # For non-transactional data, use the stakeholder-to-segment mapping
                        segment_id = get_segment_id(stakeholder_or_category)
                        if segment_id:
                            for month_str, value in monthly_data.items():
                                try:
                                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                                    customer_records.append({
                                        'year_month': year_month,
                                        'business_segment_id': segment_id,
                                        'service_type': service_type,
                                        'metric_name': metric_name,
                                        'value': float(value) if value else 0
                                    })
                                except:
                                    continue
        
        # Save pricing data
        for data_key, service_type in pricing_data_mappings:
            if data_key in data:
                for stakeholder_or_category, monthly_data in data[data_key].items():
                    # Handle transactional pricing data specially - it uses categories not stakeholders
                    if service_type == 'transactional':
                        # Create a generic segment for transactional data using the category name
                        segment_name = f"Transactional-{stakeholder_or_category}"
                        segment_id = get_segment_id(segment_name)
                        if segment_id:
                            for month_str, price_value in monthly_data.items():
                                try:
                                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                                    pricing_records.append({
                                        'year_month': year_month,
                                        'business_segment_id': segment_id,
                                        'service_type': service_type,
                                        'price_per_unit': float(price_value) if price_value is not None else 0.0,
                                        'referral_fee_percent': 0.0  # Default, will be updated separately
                                    })
                                except:
                                    continue
                    else:
                        # For non-transactional pricing, use the stakeholder-to-segment mapping
                        segment_id = get_segment_id(stakeholder_or_category)
                        if segment_id:
                            for month_str, price_value in monthly_data.items():
                                try:
                                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                                    pricing_records.append({
                                        'year_month': year_month,
                                        'business_segment_id': segment_id,
                                        'service_type': service_type,
                                        'price_per_unit': float(price_value) if price_value else 0,
                                        'referral_fee_percent': 0.0  # Default, will be updated separately
                                    })
                                except:
                                    continue
        
        # Handle referral fees by updating existing pricing records or creating new ones
        if 'transactional_referral_fee' in data:
            # Create a lookup dictionary for existing pricing records
            pricing_lookup = {}
            for i, record in enumerate(pricing_records):
                if 'business_segment_id' in record and record['business_segment_id']:
                    key = (record['year_month'], record['business_segment_id'], record['service_type'])
                    pricing_lookup[key] = i
            
            for category, monthly_data in data['transactional_referral_fee'].items():
                # Create the same segment naming convention as used for pricing
                segment_id = get_segment_id(f"Transactional-{category}")
                if segment_id:
                    for month_str, fee_percent in monthly_data.items():
                        try:
                            year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                            key = (year_month, segment_id, 'transactional')
                            
                            if key in pricing_lookup:
                                # Update existing record
                                pricing_records[pricing_lookup[key]]['referral_fee_percent'] = float(fee_percent) / 100 if fee_percent else 0
                            else:
                                # Create new record
                                pricing_records.append({
                                    'year_month': year_month,
                                    'business_segment_id': segment_id,
                                    'service_type': 'transactional',
                                    'price_per_unit': 0.0,
                                    'referral_fee_percent': float(fee_percent) / 100 if fee_percent else 0
                                })
                        except:
                            continue
        
        # Upsert records to preserve existing data
        # Save customer records with retry logic
        if customer_records:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                                        # Use upsert with the unique constraint columns to avoid duplicates and preserve existing data
                    result = supabase.table('customer_assumptions').upsert(
                        customer_records,
                        on_conflict='year_month,business_segment_id,service_type,metric_name'
                    ).execute()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        log_warning(f"⚠️ Connection issue (attempt {attempt + 1}/{max_retries}). Retrying...")
                        # Get a fresh connection
                        time.sleep(1)  # Brief delay before retry
                        supabase = get_fresh_supabase_client()
                        if supabase is None:
                            raise Exception("Failed to reconnect to database")
                        continue
                    else:
                        raise e
        
        # Save pricing records with retry logic
        if pricing_records:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Use upsert with the unique constraint columns to avoid duplicates
                    result = supabase.table('pricing_data').upsert(
                        pricing_records, 
                        on_conflict='year_month,business_segment_id,service_type'
                    ).execute()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        log_warning(f"⚠️ Connection issue (attempt {attempt + 1}/{max_retries}). Retrying...")
                        # Get a fresh connection
                        time.sleep(1)  # Brief delay before retry
                        supabase = get_fresh_supabase_client()
                        if supabase is None:
                            raise Exception("Failed to reconnect to database")
                        continue
                    else:
                        raise e
        
        # Handle churn rates for subscription service
        churn_records = []
        if 'subscription_churn_rates' in data:
            for stakeholder, monthly_data in data['subscription_churn_rates'].items():
                segment_id = get_segment_id(stakeholder)
                if segment_id:
                    for month_str, churn_rate in monthly_data.items():
                        try:
                            year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                            churn_records.append({
                                'year_month': year_month,
                                'business_segment_id': segment_id,
                                'service_type': 'subscription',
                                'churn_rate': float(churn_rate) / 100 if churn_rate else 0  # Convert percentage to decimal
                            })
                        except:
                            continue
        
        # Upsert churn records to preserve existing data
        if churn_records:
            supabase.table('churn_rates').upsert(
                churn_records, 
                on_conflict='year_month,business_segment_id,service_type'
            ).execute()
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        
        # Handle SSL-specific errors
        if "SSL" in error_msg or "sslv3" in error_msg.lower() or "bad record mac" in error_msg.lower():
            log_error("❌ SSL connection error detected. This is usually temporary.")
            log_info("Solutions to try:")
            log_info("1. Wait a moment and try again")
            log_info("2. Refresh the page (F5)")
            log_info("3. Clear browser cache and reload")
            log_info("4. Check your internet connection")
            
            # Clear the cached client to force reconnection next time
            get_supabase_client.clear()
            
            # Try one more time with fresh connection
            try:
                time.sleep(2)  # Brief pause
                log_info("Attempting automatic reconnection...")
                supabase_retry = get_fresh_supabase_client()
                if supabase_retry:
                    # Try the save one more time with fresh connection
                    return save_revenue_assumptions_to_database(data)
            except:
                pass
                
        elif "forcibly closed" in error_msg.lower() or "winError 10054" in error_msg:
            log_error("❌ Network connection lost. Please check your internet connection and try again.")
            # Clear the cached client to force reconnection next time
            get_supabase_client.clear()
        elif "timeout" in error_msg.lower():
            log_error("❌ Database connection timed out. Please try again.")
            get_supabase_client.clear()
        else:
            log_error(f"❌ Error saving revenue assumptions to database: {error_msg}")
            import traceback
            log_info("Full error trace:", traceback.format_exc())
        return False

def save_payroll_data_to_database(data: Dict[str, Any]) -> bool:
    """Save payroll data to employees, employee_bonuses, pay_periods, contractors, and model_settings tables"""
    try:
        supabase = get_supabase_client()

        
        # IMPORTANT: Use upsert operations when schema supports it. Handle legacy schemas defensively.
        # Detect employees table identifier shape
        employees_table_uses_employee_id = True
        try:
            probe = supabase.table('employees').select("*").limit(1).execute()
            sample_row = (probe.data or [{}])[0]
            employees_table_uses_employee_id = 'employee_id' in sample_row
        except Exception:
            employees_table_uses_employee_id = True
        
        # 1. Save employees to employees table using UPSERT to avoid deletion issues
        if "payroll_data" in data and "employees" in data["payroll_data"]:
            employee_records = []
            for emp_id, emp_data in data["payroll_data"]["employees"].items():
                if emp_data.get("name", "").strip():  # Only save if name exists
                    base_record = {
                        'name': emp_data.get('name', ''),
                        'title': emp_data.get('title', ''),
                        'department': emp_data.get('department', 'Opex'),
                        'pay_type': emp_data.get('pay_type', 'Salary'),
                        'weekly_hours': float(emp_data.get('weekly_hours', 40)),
                        'annual_salary': float(emp_data.get('annual_salary', 0)),
                        'hourly_rate': float(emp_data.get('hourly_rate', 0)),
                        'hire_date': emp_data.get('hire_date'),
                        'termination_date': emp_data.get('termination_date'),
                        'is_active': emp_data.get('termination_date') is None
                    }
                    if employees_table_uses_employee_id:
                        base_record['employee_id'] = str(emp_id)
                    else:
                        # We'll update by integer primary key if possible; for new rows, we'll insert without id
                        base_record['__legacy_pk__'] = str(emp_id)
                    employee_records.append(base_record)

            if employee_records:
                if employees_table_uses_employee_id:
                    # Use upsert on logical key
                    supabase.table('employees').upsert(
                        [{k: v for k, v in rec.items() if k != '__legacy_pk__'} for rec in employee_records],
                        on_conflict='employee_id'
                    ).execute()
                else:
                    # Legacy table with serial id: update existing rows by id when provided; insert new otherwise
                    to_update = []
                    to_insert = []
                    for rec in employee_records:
                        legacy_pk = rec.get('__legacy_pk__', '')
                        payload = {k: v for k, v in rec.items() if k not in ('__legacy_pk__', 'employee_id')}
                        if legacy_pk.isdigit():
                            to_update.append((int(legacy_pk), payload))
                        else:
                            to_insert.append(payload)
                    for pk, payload in to_update:
                        try:
                            supabase.table('employees').update(payload).eq('id', pk).execute()
                        except Exception:
                            # Continue best-effort
                            continue
                    if to_insert:
                        try:
                            supabase.table('employees').insert(to_insert).execute()
                        except Exception:
                            pass
        
        # 2. Save employee bonuses AFTER employees are saved
        if "payroll_data" in data and "employee_bonuses" in data["payroll_data"]:
            # Build a reliable mapping from employee name -> employee_id (string key used in our model)
            employees = data.get("payroll_data", {}).get("employees", {})
            employee_name_to_id_map = {}
            for emp_id, emp in employees.items():
                emp_name = str(emp.get("name", "")).strip()
                if emp_name and emp_id:
                    # First write wins to keep deterministic mapping
                    employee_name_to_id_map.setdefault(emp_name, emp_id)

            # Prepare bonus records with correct employee_id and validate amounts
            bonus_records = []
            for _, bonus_data in data["payroll_data"].get("employee_bonuses", {}).items():
                employee_name = str(bonus_data.get("employee_name", "")).strip()
                month_label = str(bonus_data.get("month", "")).strip()
                bonus_amount = float(bonus_data.get('bonus_amount', 0) or 0)

                # Skip invalid or zero-amount bonuses
                if not employee_name or not month_label or bonus_amount <= 0:
                    continue

                # Resolve to employee identifier; skip if not resolvable
                resolved_emp_id = employee_name_to_id_map.get(employee_name)
                if not resolved_emp_id:
                    continue

                try:
                    year_month = datetime.strptime(month_label, "%b %Y").strftime("%Y-%m-%d")
                except Exception:
                    continue

                # Cast identifier for legacy integer FK
                employee_id_value = (
                    int(resolved_emp_id) if (not employees_table_uses_employee_id and str(resolved_emp_id).isdigit()) else str(resolved_emp_id)
                )

                bonus_records.append({
                    'employee_id': employee_id_value,
                    'year_month': year_month,
                    'bonus_type': bonus_data.get('bonus_type', 'performance'),
                    'bonus_amount': bonus_amount,
                    'bonus_reason': f'Bonus for {month_label}',
                    'approved_by': 'System',
                    'bonus_date': year_month
                })

            # Best-effort cleanup of any historical invalid bonus rows where employee_id doesn't match an existing employee_id
            try:
                existing_emp_ids = set(employees.keys())
                # Fetch a small sample of bonus rows to detect invalid references (bounded for safety)
                invalid_bonus_rows = []
                bonus_resp = supabase.table('employee_bonuses').select('id, employee_id').limit(10000).execute()
                for r in bonus_resp.data or []:
                    emp_ref = r.get('employee_id')
                    if emp_ref and emp_ref not in existing_emp_ids:
                        invalid_bonus_rows.append(r.get('id'))
                # Delete invalid rows in small batches
                if invalid_bonus_rows:
                    # Supabase Python client supports .in_ for filters
                    supabase.table('employee_bonuses').delete().in_('id', invalid_bonus_rows).execute()
            except Exception:
                # Non-fatal cleanup step; continue with proper upsert below
                pass

            if bonus_records:
                try:
                    supabase.table('employee_bonuses').upsert(
                        bonus_records,
                        on_conflict='employee_id,year_month,bonus_type'
                    ).execute()
                except Exception:
                    # Fallback: insert row-by-row (best effort)
                    for rec in bonus_records:
                        try:
                            supabase.table('employee_bonuses').insert(rec).execute()
                        except Exception:
                            continue
        
        # 3. Save pay periods
        if "payroll_data" in data and "pay_periods" in data["payroll_data"]:
            period_records = []
            for month_str, periods in data["payroll_data"]["pay_periods"].items():
                try:
                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                    period_records.append({
                        'year_month': year_month,
                        'pay_periods_count': int(periods)
                    })
                except:
                    continue
            
            if period_records:
                supabase.table('pay_periods').upsert(period_records, on_conflict='year_month').execute()
        
        # 4. Save payroll configuration to model_settings
        if "payroll_data" in data and "payroll_config" in data["payroll_data"]:
            config = data["payroll_data"]["payroll_config"]
            tax_rate = config.get("payroll_tax_percentage", 10.0)  # Changed from 23.0 to 10.0
            
            setting_record = {
                'setting_category': 'payroll',
                'setting_name': 'payroll_tax_percentage',
                'setting_value': json.dumps(tax_rate),
                'description': 'Payroll tax and benefits percentage',
                'data_type': 'number'
            }
            
            supabase.table('model_settings').upsert(setting_record, on_conflict='setting_category,setting_name').execute()
        
        # 5. Save contractors to contractors table
        if "payroll_data" in data and "contractors" in data["payroll_data"]:
            contractor_records = []
            for contractor_id, contractor_data in data["payroll_data"]["contractors"].items():
                if contractor_data.get("vendor", "").strip():
                    contractor_records.append({
                        'contractor_id': contractor_id,
                        'vendor': contractor_data.get('vendor', ''),
                        'role': contractor_data.get('role', ''),
                        'department': contractor_data.get('department', 'Product Development'),
                        'resources': float(contractor_data.get('resources', 0)),
                        'hourly_rate': float(contractor_data.get('hourly_rate', 0)),
                        'start_date': contractor_data.get('start_date'),
                        'end_date': contractor_data.get('end_date'),
                        'is_active': contractor_data.get('end_date') is None
                    })
            
            if contractor_records:
                supabase.table('contractors').upsert(contractor_records, on_conflict='contractor_id').execute()
        
        # 6. Calculate and save payroll costs (integrated)
        try:
            save_calculated_payroll_costs_to_database(data)
        except Exception as e:
            pass
            pass  # Silent error handling
        
        return True
        
    except Exception as e:
        pass  # Silent error handling for save operations
        return False

def save_calculated_payroll_costs_to_database(data: Dict[str, Any]) -> bool:
    """Calculate and save monthly payroll costs to payroll_costs table (individual employee records + department totals)"""
    try:
        supabase = get_supabase_client()
        
        if "payroll_data" not in data:
            return True  # No payroll data to save
        
        payroll_data = data["payroll_data"]
        
        # Generate months from 2025-2030 (matching payroll_model.py)
        months = []
        for year in range(2025, 2031):
            for month in range(1, 13):
                from datetime import date
                months.append(f"{date(year, month, 1).strftime('%b %Y')}")
        
        # Helper function to check if employee is active for a month (matches payroll_model.py logic)
        def is_employee_active_for_month(emp_data, month_str):
            try:
                month_date = datetime.strptime(month_str, "%b %Y")
                
                hire_date_str = emp_data.get("hire_date")
                if hire_date_str:
                    hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d")
                    if month_date < hire_date:
                        return False
                
                termination_date_str = emp_data.get("termination_date")
                if termination_date_str:
                    termination_date = datetime.strptime(termination_date_str, "%Y-%m-%d")
                    if month_date >= termination_date:
                        return False
                
                return True
            except (ValueError, TypeError):
                return emp_data.get("active", True)
        
        # Calculate monthly payroll costs (matches payroll_model.py logic)
        employees = payroll_data.get("employees", {})
        pay_periods = payroll_data.get("pay_periods", {})
        payroll_config = payroll_data.get("payroll_config", {})
        employee_bonuses = payroll_data.get("employee_bonuses", {})
        
        # Get payroll tax rate
        payroll_tax_rate = payroll_config.get("payroll_tax_percentage", 10.0) / 100.0  # Changed from 23.0 to 10.0
        
        # Prepare payroll cost records
        payroll_records = []
        
        for month in months:
            try:
                year_month = datetime.strptime(month, "%b %Y").strftime("%Y-%m-%d")
                
                # Calculate costs for each individual employee
                employee_records_for_month = []
                
                for emp_id, emp_data in employees.items():
                    if not is_employee_active_for_month(emp_data, month):
                        continue
                    
                    department = emp_data.get("department", "Opex")
                    pay_type = emp_data.get("pay_type", "Salary")
                    
                    # Calculate base pay
                    if pay_type == "Salary":
                        annual_salary = emp_data.get("annual_salary", 0)
                        pay_periods_count = pay_periods.get(month, 2)
                        base_pay = (annual_salary / 26) * pay_periods_count
                    else:  # Hourly
                        hourly_rate = emp_data.get("hourly_rate", 0)
                        weekly_hours = emp_data.get("weekly_hours", 40.0)
                        monthly_hours = weekly_hours * 4.33  # Average weeks per month
                        base_pay = hourly_rate * monthly_hours
                    
                    # Find bonuses for this employee in this month
                    employee_name = emp_data.get("name", "")
                    bonus_pay = 0
                    for bonus_data in employee_bonuses.values():
                        if (bonus_data.get("employee_name", "") == employee_name and 
                            bonus_data.get("month", "") == month):
                            bonus_pay += bonus_data.get("bonus_amount", 0)
                    
                    # Calculate taxes and benefits (applied to base + bonus)
                    taxable_amount = base_pay + bonus_pay
                    payroll_taxes = taxable_amount * payroll_tax_rate
                    
                    # For benefits_cost, we'll use half of payroll_taxes as an estimate
                    # (you can adjust this logic based on your needs)
                    benefits_cost = payroll_taxes * 0.5
                    payroll_taxes = payroll_taxes * 0.5  # Remaining half for actual taxes
                    
                    if base_pay > 0 or bonus_pay > 0:
                        payroll_records.append({
                            'year_month': year_month,
                            'employee_id': emp_id,
                            'department': department,
                            'base_pay': round(base_pay, 2),
                            'overtime_pay': 0.0,  # No overtime in current model
                            'bonus_pay': round(bonus_pay, 2),
                            'payroll_taxes': round(payroll_taxes, 2),
                            'benefits_cost': round(benefits_cost, 2)
                        })
                        
            except Exception as e:
                continue
        
        if payroll_records:
            # Batch insert payroll records using upsert
            supabase.table('payroll_costs').upsert(payroll_records, on_conflict='year_month,employee_id').execute()
        
        return True
        
    except Exception as e:
        return False

# REMOVED: Table hosting_costs deleted
def save_hosting_costs_to_database(data: Dict[str, Any]) -> bool:
    """Save hosting costs to hosting_costs table"""
    try:
        supabase = get_supabase_client()
        
        if "hosting_costs_data" not in data or "cost_structure" not in data["hosting_costs_data"]:
            return False
        
        hosting_records = []
        cost_structure = data["hosting_costs_data"]["cost_structure"]
        
        # Generate months from 2025-2030 for full coverage
        months = []
        for year in range(2025, 2031):
            for month in range(1, 13):
                months.append(f"{year}-{month:02d}-01")
        
        # Process each category and service
        for category, services in cost_structure.items():
            for service, costs in services.items():
                fixed_cost = float(costs.get("fixed", 0))
                variable_cost = float(costs.get("variable", 0))
                
                # Only create records if there are actual costs
                if fixed_cost > 0 or variable_cost > 0:
                    for month in months:
                        hosting_records.append({
                            'year_month': month,
                            'cost_category': service,  # Service name as requested
                            'provider': category,      # Category name as requested  
                            'fixed_cost': fixed_cost,  # Fixed cost as requested
                            'variable_cost': variable_cost,  # Per customer cost as requested
                            'active_customers': 0,     # Will be calculated dynamically
                            'is_capitalized': False    # Default, can be updated based on go-live settings
                        })
        
        if hosting_records:
            # Use upsert to safely update/insert hosting costs without losing data
            # Table hosting_costs removed - skipping database save
            pass
        
        # Save hosting configuration to model_settings if available
        hosting_data = data.get("hosting_costs_data", {})
        go_live_settings = hosting_data.get("go_live_settings", {})
        
        if go_live_settings:
            # Save go-live month
            if "go_live_month" in go_live_settings:
                supabase.table('model_settings').upsert({
                    'setting_category': 'hosting',
                    'setting_name': 'go_live_month',
                    'setting_value': json.dumps(go_live_settings["go_live_month"]),
                    'description': 'Month when platform goes live',
                    'data_type': 'text'
                }, on_conflict='setting_category,setting_name').execute()
            
            # Save capitalize setting
            if "capitalize_before_go_live" in go_live_settings:
                supabase.table('model_settings').upsert({
                    'setting_category': 'hosting',
                    'setting_name': 'capitalize_before_go_live',
                    'setting_value': json.dumps(go_live_settings["capitalize_before_go_live"]),
                    'description': 'Whether to capitalize hosting costs before go-live',
                    'data_type': 'boolean'
                }, on_conflict='setting_category,setting_name').execute()
        
        return True
        
    except Exception as e:
        return False

# REMOVED: Duplicate function - using the enhanced version below

def save_budget_data_to_database(data: Dict[str, Any]) -> bool:
    """Save budget data to budget_data table"""
    try:
        supabase = get_supabase_client()

        
        if "budget_data" not in data or "monthly_budgets" not in data["budget_data"]:
            return False
        
        budget_records = []
        monthly_budgets = data["budget_data"]["monthly_budgets"]
        
        for month_str, budget_items in monthly_budgets.items():
            try:
                # Handle budget keys that may have "_budget" suffix
                clean_month_str = month_str.replace("_budget", "")
                
                # Handle YTD budget keys - skip them as they're aggregated data
                if "ytd" in clean_month_str.lower():
                    continue
                
                # Parse the month string to get the date
                year_month = datetime.strptime(clean_month_str, "%b %Y").strftime("%Y-%m-%d")
                
                for item_name, budget_amount in budget_items.items():
                    # Determine budget type
                    if 'revenue' in item_name:
                        budget_type = 'revenue'
                        category = item_name.replace('_revenue', '').replace('_', ' ').title()
                    else:
                        budget_type = 'expense'
                        category = item_name.replace('_', ' ').title()
                    
                    budget_records.append({
                        'year_month': year_month,
                        'budget_type': budget_type,
                        'category': category,
                        'subcategory': None,  # Explicitly set subcategory for upsert conflict resolution
                        'budget_amount': float(budget_amount) if budget_amount else 0,
                        'actual_amount': 0  # Will be updated separately
                    })
            except:
                continue
        
        if budget_records:
            # Much simpler approach: Just use insert and let the unique constraint handle duplicates
            # But first, we need to delete existing records to avoid constraint violations
            
            # Group records by month to batch delete operations
            months_to_clear = set(record['year_month'] for record in budget_records)
            
            # Delete existing records for these months in one batch operation per month
            for month in months_to_clear:
                supabase.table('budget_data').delete().eq('year_month', month).execute()
            
            # Now insert all new records - this should be fast since we cleared the conflicts
            supabase.table('budget_data').insert(budget_records).execute()
        
        return True
        
    except Exception as e:
        return False

def save_gross_profit_data_to_database(data: Dict[str, Any]) -> bool:
    """Save gross profit data to model_settings tables (gross_profit_data table removed)"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            return False

        
        if "gross_profit_data" not in data:
            return False
        
        gross_profit_data = data["gross_profit_data"]
        
        # Revenue category operations removed with gross_profit_data table
        
        # Save hosting configuration to model_settings
        if "saas_hosting_structure" in gross_profit_data:
            hosting_config = gross_profit_data["saas_hosting_structure"]
            
            # Save go-live month
            if "go_live_month" in hosting_config:
                go_live_value = hosting_config["go_live_month"]
                supabase.table('model_settings').upsert({
                    'setting_category': 'hosting',
                    'setting_name': 'go_live_month',
                    'setting_value': json.dumps(go_live_value),
                    'description': 'Month when platform goes live',
                    'data_type': 'text'
                }, on_conflict='setting_category,setting_name').execute()
            
            # Save capitalize setting
            if "capitalize_before_go_live" in hosting_config:
                supabase.table('model_settings').upsert({
                    'setting_category': 'hosting',
                    'setting_name': 'capitalize_before_go_live',
                    'setting_value': json.dumps(hosting_config["capitalize_before_go_live"]),
                    'description': 'Whether to capitalize hosting costs before go-live',
                    'data_type': 'boolean'
                }, on_conflict='setting_category,setting_name').execute()
            
            # Save monthly fixed costs
            if "monthly_fixed_costs" in hosting_config:
                supabase.table('model_settings').upsert({
                    'setting_category': 'hosting',
                    'setting_name': 'monthly_fixed_costs',
                    'setting_value': json.dumps(hosting_config["monthly_fixed_costs"]),
                    'description': 'Monthly fixed hosting costs',
                    'data_type': 'json'
                }, on_conflict='setting_category,setting_name').execute()
            
            # Save monthly variable costs
            if "monthly_variable_costs" in hosting_config:
                supabase.table('model_settings').upsert({
                    'setting_category': 'hosting',
                    'setting_name': 'monthly_variable_costs',
                    'setting_value': json.dumps(hosting_config["monthly_variable_costs"]),
                    'description': 'Monthly variable hosting costs per customer',
                    'data_type': 'json'
                }, on_conflict='setting_category,setting_name').execute()
        
        # Save gross profit percentages as model settings
        if "gross_profit_percentages" in gross_profit_data:
            for stream, monthly_values in gross_profit_data["gross_profit_percentages"].items():
                supabase.table('model_settings').upsert({
                    'setting_category': 'gross_profit',
                    'setting_name': f'{stream.lower()}_gp_percentages',
                    'setting_value': json.dumps(monthly_values),
                    'description': f'Gross profit percentages for {stream}',
                    'data_type': 'json'
                }, on_conflict='setting_category,setting_name').execute()
        
        # Note: gross_profit_data table operations removed - data can be calculated from revenue/cogs
        
        return True
        
    except Exception as e:
        pass  # Silent error handling for save operations
        return False

def save_revenue_and_cogs_to_database(data: Dict[str, Any]) -> bool:
    """Save revenue and COGS data to revenue_data and cost_of_sales tables"""
    try:
        supabase = get_supabase_client()

        
        # Get revenue categories
        categories_response = supabase.table('revenue_categories').select('id, category_name').limit(10000).execute()
        category_mapping = {row['id']: row['category_name'] for row in categories_response.data}
        
        def get_or_create_revenue_category(category_name):
            if category_name in category_mapping:
                return category_mapping[category_name]
            
            try:
                result = supabase.table('revenue_categories').insert({
                    'category_name': category_name,
                    'description': f'Revenue category for {category_name}'
                }).execute()
                category_id = result.data[0]['id']
                category_mapping[category_name] = category_id
                return category_id
            except:
                return None
        
        revenue_records = []
        cogs_records = []
        
        # Save revenue data
        if "revenue" in data:
            for category_name, monthly_data in data["revenue"].items():
                category_id = get_or_create_revenue_category(category_name)
                if category_id:
                    for month_str, amount in monthly_data.items():
                        try:
                            year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                            revenue_records.append({
                                'year_month': year_month,
                                'revenue_category_id': category_id,
                                'amount': float(amount) if amount else 0
                            })
                        except:
                            continue
        
        # Save COGS data
        if "cogs" in data:
            for category_name, monthly_data in data["cogs"].items():
                category_id = get_or_create_revenue_category(category_name)
                if category_id:
                    for month_str, amount in monthly_data.items():
                        try:
                            year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                            cogs_records.append({
                                'year_month': year_month,
                                'revenue_category_id': category_id,
                                'amount': float(amount) if amount else 0
                            })
                        except:
                            continue
        
        # Insert records - revenue_data table removed, skipping
        if revenue_records:
            # Table revenue_data removed - revenue calculations handled in memory
            pass
        
        if cogs_records:
            # Table cost_of_sales removed - skipping database save
            pass
        
        return True
        
    except Exception as e:
        return False

# ===== COMPREHENSIVE LOAD FUNCTIONS FROM EXISTING TABLES =====

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_revenue_assumptions_from_database() -> Dict[str, Any]:
    """Load revenue assumptions from customer_assumptions and pricing_data tables"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            st.error("❌ Database connection failed. Cannot load revenue assumptions.")
            return {}
        
        # Ensure all business segments exist first
        ensure_business_segments_exist(supabase)
        
        # Get business segments mapping
        segments_response = supabase.table('business_segments').select('id, segment_name').limit(10000).execute()
        segment_mapping = {row['id']: row['segment_name'] for row in segments_response.data}
        
        # Define all expected stakeholders (first 21 business segments)
        all_stakeholders = [
            "Dealership", "End User", "Equipment Manufacturer", "Upfitter",
            "Depot", "Fleet Management Company", "Logistics", "OEM",
            "Traditional Finance Provider", "Channel Partner", "Charging OEM", "Insurance Provider",
            "Maintenance Provider", "Charging as a Service", "EPC", "Government Agency",
            "Grant Administrator", "Operating and Maintenance Provider", "Remarketing Specialists", "Technology Solutions",
            "Utility Provider"
        ]
        
        # Segment mapping loaded successfully
        
        # Define all months from 2025-2030
        months = []
        for year in range(2025, 2031):
            for month in range(1, 13):
                months.append(datetime(year, month, 1).strftime("%b %Y"))
        
        revenue_data = {}
        
        # Initialize all data structures with all stakeholders and months
        # IMPORTANT: Only initialize structure, don't set default values yet
        data_keys = [
            'subscription_new_customers', 'subscription_pricing', 'subscription_churn_rates',
            'implementation_new_customers', 'implementation_pricing',
            'maintenance_new_customers', 'maintenance_pricing'
        ]
        
        for data_key in data_keys:
            revenue_data[data_key] = {}
            for stakeholder in all_stakeholders:
                revenue_data[data_key][stakeholder] = {}
                # Don't set default values here - will be set after loading from DB
        
        # Initialize transactional data structures
        transactional_categories = ["Charging", "Vehicle", "Financing", "Other Revenue"]
        transactional_keys = ['transactional_volume', 'transactional_price', 'transactional_referral_fee']
        
        for data_key in transactional_keys:
            revenue_data[data_key] = {}
            for category in transactional_categories:
                revenue_data[data_key][category] = {}
                # Don't set default values here - will be set after loading from DB
        
        # Load customer assumptions - explicitly set high limit and order by date to ensure we get all records
        customer_response = supabase.table('customer_assumptions').select("*").order('year_month').limit(10000).execute()
        
        for record in customer_response.data:
            segment_name = segment_mapping.get(record['business_segment_id'], 'Unknown')
            service_type = record['service_type']
            metric_name = record['metric_name']
            month_str = datetime.strptime(record['year_month'], "%Y-%m-%d").strftime("%b %Y")
            data_key = f"{service_type}_{metric_name}"
            
            # Process the record
            
            # Handle transactional data specially - it uses categories not stakeholders
            if service_type == 'transactional' and metric_name in ['volume', 'new_customers']:
                # Extract category from the new "Transactional-" prefixed segment names
                if segment_name.startswith("Transactional-"):
                    category = segment_name.replace("Transactional-", "")
                else:
                    # Fallback to old mapping for backwards compatibility
                    category_mapping = {
                        "Charging as a Service": "Charging",
                        "Charging Hardware": "Charging",
                        "Equipment Manufacturer": "Vehicle",
                        "Finance Partner": "Financing",
                        "Dealership": "Vehicle",
                        "Corporate": "Charging"
                    }
                    category = category_mapping.get(segment_name, "Other Revenue")
                
                # Use 'transactional_volume' as the key for consistency
                volume_key = 'transactional_volume'
                if volume_key in revenue_data and category in transactional_categories:
                    revenue_data[volume_key][category][month_str] = record['value']
            else:
                # Only update if the segment_name is in our expected stakeholders
                if segment_name in all_stakeholders and data_key in revenue_data:
                    revenue_data[data_key][segment_name][month_str] = record['value']
        
        # Load pricing data - explicitly set high limit and order by date
        pricing_response = (
            supabase.table('pricing_data')
            .select("*")
            .order('year_month')
            .limit(10000)
            .execute()
        )
        for record in pricing_response.data:
            segment_name = segment_mapping.get(record['business_segment_id'], 'Unknown')
            service_type = record['service_type']
            month_str = datetime.strptime(record['year_month'], "%Y-%m-%d").strftime("%b %Y")
            
            # Handle transactional pricing specially - uses categories not stakeholders
            if service_type == 'transactional':
                # Extract category from the new "Transactional-" prefixed segment names
                if segment_name.startswith("Transactional-"):
                    category = segment_name.replace("Transactional-", "")
                else:
                    # Fallback to old mapping for backwards compatibility
                    category_mapping = {
                        "Charging as a Service": "Charging",
                        "Charging Hardware": "Charging",
                        "Equipment Manufacturer": "Vehicle",
                        "Finance Partner": "Financing",
                        "Dealership": "Vehicle",
                        "Corporate": "Charging"
                    }
                    category = category_mapping.get(segment_name, "Other Revenue")
                
                # Transactional price data
                if category in transactional_categories:
                    revenue_data['transactional_price'][category][month_str] = record['price_per_unit']
                    
                    # Transactional referral fee data
                    if record['referral_fee_percent'] > 0:
                        revenue_data['transactional_referral_fee'][category][month_str] = record['referral_fee_percent'] * 100
            else:
                # Non-transactional pricing data
                price_key = f"{service_type}_pricing"
                if segment_name in all_stakeholders and price_key in revenue_data:
                    revenue_data[price_key][segment_name][month_str] = record['price_per_unit']
        
        # Load churn rates - explicitly set high limit
        churn_response = (
            supabase.table('churn_rates')
            .select("*")
            .order('year_month')
            .limit(10000)
            .execute()
        )
        for record in churn_response.data:
            segment_name = segment_mapping.get(record['business_segment_id'], 'Unknown')
            service_type = record['service_type']
            month_str = datetime.strptime(record['year_month'], "%Y-%m-%d").strftime("%b %Y")
            
            churn_key = f"{service_type}_churn_rates"
            
            if segment_name in all_stakeholders and churn_key in revenue_data:
                # Convert from decimal back to percentage for consistency with UI
                revenue_data[churn_key][segment_name][month_str] = record['churn_rate'] * 100
        
        
        # Now fill in zeros ONLY for months that don't have data
        # This prevents overwriting existing data with defaults
        for data_key in data_keys:
            if data_key in revenue_data:
                for stakeholder in all_stakeholders:
                    if stakeholder in revenue_data[data_key]:
                        for month in months:
                            if month not in revenue_data[data_key][stakeholder]:
                                revenue_data[data_key][stakeholder][month] = 0.0
        
        for data_key in transactional_keys:
            if data_key in revenue_data:
                for category in transactional_categories:
                    if category in revenue_data[data_key]:
                        for month in months:
                            if month not in revenue_data[data_key][category]:
                                revenue_data[data_key][category][month] = 0.0
        
        # Revenue data loaded successfully
        
        return revenue_data
        
    except Exception as e:
        st.error(f"❌ Error loading revenue assumptions from database: {str(e)}")
        return {}

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_payroll_data_from_database() -> Dict[str, Any]:
    """Load payroll data from employees, employee_bonuses, pay_periods, and model_settings tables"""
    try:
        supabase = get_supabase_client()
        
        payroll_data = {
            "employees": {},
            "contractors": {},
            "employee_bonuses": {},
            "pay_periods": {},
            "payroll_config": {"payroll_tax_percentage": 10.0}  # Changed from 23.0 to 10.0
        }
        
        # Load employees (supports both schemas: with 'employee_id' or legacy integer 'id')
        try:
            employees_response = supabase.table('employees').select("*").limit(10000).execute()
            rows = employees_response.data or []
            # Detect identifier field
            uses_employee_id = False
            if len(rows) > 0:
                sample = rows[0]
                uses_employee_id = 'employee_id' in sample
            for emp in rows:
                key = str(emp['employee_id']) if uses_employee_id and 'employee_id' in emp else str(emp.get('id'))
                if not key or key == 'None':
                    continue
                payroll_data["employees"][key] = {
                    'name': emp.get('name', ''),
                    'title': emp.get('title', ''),
                    'department': emp.get('department', 'Opex'),
                    'pay_type': emp.get('pay_type', 'Salary'),
                    'annual_salary': float(emp.get('annual_salary', 0) or 0),
                    'hourly_rate': float(emp.get('hourly_rate', 0) or 0),
                    'weekly_hours': float(emp.get('weekly_hours', 40) or 40),
                    'hire_date': emp.get('hire_date'),
                    'termination_date': emp.get('termination_date')
                }
        except Exception:
            pass
        
        # Load contractors (if table exists)
        try:
            contractors_response = supabase.table('contractors').select("*").limit(10000).execute()
            for contractor in contractors_response.data:
                payroll_data["contractors"][contractor['contractor_id']] = {
                    'vendor': contractor['vendor'],
                    'role': contractor['role'],
                    'department': contractor.get('department', 'Product Development'),
                    'resources': float(contractor.get('resources', 0)),
                    'hourly_rate': float(contractor.get('hourly_rate', 0)),
                    'start_date': contractor.get('start_date'),
                    'end_date': contractor.get('end_date')
                }
        except Exception as e:
            pass
            pass
        
        # Load employee bonuses (map to employee name; support legacy integer employee_id)
        try:
            bonuses_response = supabase.table('employee_bonuses').select("*").limit(10000).execute()
            employee_id_to_name = {str(emp_id): emp_data['name'] for emp_id, emp_data in payroll_data["employees"].items()}
            for bonus in bonuses_response.data or []:
                try:
                    bonus_id = str(bonus.get('id'))
                    month_str = datetime.strptime(bonus['year_month'], "%Y-%m-%d").strftime("%b %Y")
                    emp_ref = str(bonus.get('employee_id')) if bonus.get('employee_id') is not None else ''
                    employee_name = employee_id_to_name.get(emp_ref, '')
                    if not employee_name:
                        continue
                    payroll_data["employee_bonuses"][bonus_id] = {
                        'employee_name': employee_name,
                        'bonus_amount': float(bonus.get('bonus_amount', 0) or 0),
                        'month': month_str
                    }
                except Exception:
                    continue
        except Exception:
            pass
        
        # Load pay periods
        try:
            periods_response = supabase.table('pay_periods').select("*").limit(10000).execute()
            for period in periods_response.data:
                month_str = datetime.strptime(period['year_month'], "%Y-%m-%d").strftime("%b %Y")
                payroll_data["pay_periods"][month_str] = period['pay_periods_count']
        except Exception as e:
            pass
            pass
        
        # Load payroll configuration
        try:
            config_response = supabase.table('model_settings').select("*").eq('setting_category', 'payroll').eq('setting_name', 'payroll_tax_percentage').execute()
            if config_response.data:
                tax_rate = json.loads(config_response.data[0]['setting_value'])
                payroll_data["payroll_config"]["payroll_tax_percentage"] = float(tax_rate)
        except Exception as e:
            pass
            pass
        
        return payroll_data
        
    except Exception as e:

        return {
            "employees": {},
            "contractors": {},
            "employee_bonuses": {},
            "pay_periods": {},
            "payroll_config": {"payroll_tax_percentage": 10.0}
        }

# REMOVED: Table hosting_costs deleted
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_hosting_costs_from_database() -> Dict[str, Any]:
    """Load hosting costs from hosting_costs table"""
    try:
        supabase = get_supabase_client()
        
        hosting_data = {
            "hosting_costs_data": {
                "cost_structure": {},
                "go_live_settings": {
                    "go_live_month": "Jan 2025",
                    "capitalize_before_go_live": True
                }
            }
        }
        
        # Load hosting costs
        # Table hosting_costs removed - returning empty response
        hosting_response = type('Response', (), {'data': []})()  # Mock empty response
        
        # Group by category (provider) and service (cost_category)
        for record in hosting_response.data:
            category = record['provider']      # Category name 
            service = record['cost_category']  # Service name
            
            if category not in hosting_data["hosting_costs_data"]["cost_structure"]:
                hosting_data["hosting_costs_data"]["cost_structure"][category] = {}
            
            # Only add unique services (avoid duplicates from multiple months)
            if service not in hosting_data["hosting_costs_data"]["cost_structure"][category]:
                hosting_data["hosting_costs_data"]["cost_structure"][category][service] = {
                    "fixed": float(record['fixed_cost']),
                    "variable": float(record['variable_cost'])
                }
        
        # Load go-live settings from model_settings
        try:
            settings_response = supabase.table('model_settings').select("*").eq('setting_category', 'hosting').limit(10000).execute()
            for setting in settings_response.data:
                if setting['setting_name'] == 'go_live_month':
                    hosting_data["hosting_costs_data"]["go_live_settings"]["go_live_month"] = json.loads(setting['setting_value'])
                elif setting['setting_name'] == 'capitalize_before_go_live':
                    hosting_data["hosting_costs_data"]["go_live_settings"]["capitalize_before_go_live"] = json.loads(setting['setting_value'])
        except Exception as e:
            pass  # Use default settings
        
        return hosting_data
        
    except Exception as e:
        return {
            "hosting_costs_data": {
                "cost_structure": {},
                "go_live_settings": {
                    "go_live_month": "Jan 2025",
                    "capitalize_before_go_live": True
                }
            }
        }

# Removed duplicate function - using the newer version below

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_budget_data_from_database() -> Dict[str, Any]:
    """Load budget data from budget_data table"""
    try:
        supabase = get_supabase_client()
        
        budget_data = {"monthly_budgets": {}}
        
        # Load budget data
        budget_response = supabase.table('budget_data').select("*").order('year_month').limit(10000).execute()
        
        for record in budget_response.data:
            month_str = datetime.strptime(record['year_month'], "%Y-%m-%d").strftime("%b %Y")
            
            # Create budget key format that matches the KPI Dashboard expectations
            budget_key = f"{month_str}_budget"
            
            if budget_key not in budget_data["monthly_budgets"]:
                budget_data["monthly_budgets"][budget_key] = {}
            
            # Convert category to key format
            category = record['category']
            if record['budget_type'] == 'revenue':
                item_key = category.lower().replace(' ', '_') + '_revenue'
            else:
                item_key = category.lower().replace(' ', '_').replace('&', 'and').replace('/', '_')
            
            budget_data["monthly_budgets"][budget_key][item_key] = float(record['budget_amount'])
        
        return budget_data
        
    except Exception as e:

        return {"monthly_budgets": {}}

# load_gross_profit_data_from_database function removed - data loaded from model_settings via other functions
def load_gross_profit_data_from_database() -> Dict[str, Any]:
    """Function stub - gross_profit_data functionality moved to other functions"""
    return {}

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_revenue_and_cogs_from_database() -> Dict[str, Any]:
    """Load revenue and COGS data from revenue_data and cost_of_sales tables"""
    try:
        supabase = get_supabase_client()
        
        # Get revenue categories
        categories_response = supabase.table('revenue_categories').select('id, category_name').limit(10000).execute()
        category_mapping = {row['id']: row['category_name'] for row in categories_response.data}
        
        revenue_data = {}
        cogs_data = {}
        
        # Load revenue data - revenue_data table removed
        # Revenue calculations are done in memory from source data
        # Keeping revenue_data empty for compatibility
        
        # Load COGS data
        # Table cost_of_sales removed - returning empty response
        cogs_response = type('Response', (), {'data': []})()  # Mock empty response
        for record in cogs_response.data:
            category_name = category_mapping.get(record['revenue_category_id'], 'Unknown')
            month_str = datetime.strptime(record['year_month'], "%Y-%m-%d").strftime("%b %Y")
            
            if category_name not in cogs_data:
                cogs_data[category_name] = {}
            
            cogs_data[category_name][month_str] = float(record['amount'])
        
        return {"revenue": revenue_data, "cogs": cogs_data}
        
    except Exception as e:

        return {"revenue": {}, "cogs": {}}

# ===== LIQUIDITY DATA SAVE/LOAD FUNCTIONS =====

def save_liquidity_data_to_database(data: Dict[str, Any]) -> bool:
    """Save liquidity data (starting_balance, investment, other_cash_receipts, expenses) to Supabase"""
    try:
        supabase = get_supabase_client()
        
        liquidity_data = data.get("liquidity_data", {})
        if not liquidity_data:
            st.error("No liquidity_data found in data structure")
            return False
        
        # Save starting balance to model_settings (store as JSON number)
        starting_balance = liquidity_data.get("starting_balance", 0)
        supabase.table('model_settings').upsert({
            'setting_category': 'liquidity',
            'setting_name': 'starting_balance',
            'setting_value': json.dumps(float(starting_balance)),
            'description': 'Starting cash balance for liquidity model',
            'data_type': 'number'
        }, on_conflict='setting_category,setting_name').execute()
        
        # Save monthly cash flow data to cash_flow table
        cash_flow_records = []
        
        # Process revenue data (from Income Statement)
        revenue_data = liquidity_data.get("revenue", {})
        for month_str, amount in revenue_data.items():
            try:
                # Only add non-zero values
                if amount and float(amount) != 0:
                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                    cash_flow_records.append({
                        'year_month': year_month,
                        'flow_type': 'inflow',
                        'category': 'Revenue',
                        'subcategory': None,
                        'amount': float(amount),
                        'description': 'Revenue cash inflow'
                    })
            except Exception as e:
                continue
        
        # Process investment data
        investment_data = liquidity_data.get("investment", {})
        for month_str, amount in investment_data.items():
            try:
                # Only add non-zero values
                if amount and float(amount) != 0:
                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                    cash_flow_records.append({
                        'year_month': year_month,
                        'flow_type': 'inflow',
                        'category': 'Investment',
                        'subcategory': None,
                        'amount': float(amount),
                        'description': 'Investment cash inflow'
                    })
            except Exception as e:
                continue
        
        # Process other cash receipts data
        other_receipts_data = liquidity_data.get("other_cash_receipts", {})
        for month_str, amount in other_receipts_data.items():
            try:
                # Only add non-zero values
                if amount and float(amount) != 0:
                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                    cash_flow_records.append({
                        'year_month': year_month,
                        'flow_type': 'inflow',
                        'category': 'Other Cash Receipts',
                        'subcategory': None,
                        'amount': float(amount),
                        'description': 'Other cash receipts inflow'
                    })
            except Exception as e:
                continue
        
        # Process expenses data
        expenses_data = liquidity_data.get("expenses", {})
        
        for category_name, monthly_data in expenses_data.items():
            # Clean up category name - remove extra spaces and normalize
            clean_category_name = ' '.join(category_name.split()).strip()
            
            for month_str, amount in monthly_data.items():
                try:
                    # Only add non-zero values
                    if amount and float(amount) != 0:
                        year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                        cash_flow_records.append({
                            'year_month': year_month,
                            'flow_type': 'outflow',
                            'category': clean_category_name,
                            'subcategory': None,
                            'amount': float(amount),
                            'description': f'Cash disbursement - {clean_category_name}'
                        })
                except Exception as e:
                    continue
        
        # Save records to database
        if cash_flow_records:
            try:
                # Get all unique categories we're about to save
                categories_to_save = list(set(record['category'] for record in cash_flow_records))
                
                # Also ensure we delete old Revenue, Investment, Other Cash Receipts records
                all_liquidity_categories = ['Revenue', 'Investment', 'Other Cash Receipts']
                # Add expense categories (cleaned)
                if expenses_data:
                    all_liquidity_categories.extend([' '.join(cat.split()).strip() for cat in expenses_data.keys()])
                
                # Delete existing records for ALL liquidity-related categories
                delete_response = supabase.table('cash_flow').delete().in_('category', all_liquidity_categories).execute()
                
            except Exception as delete_e:
                # Continue anyway as upsert should handle updates
                pass
            
            try:
                # Insert new records in batches to avoid timeout
                batch_size = 100
                for i in range(0, len(cash_flow_records), batch_size):
                    batch = cash_flow_records[i:i+batch_size]
                    response = supabase.table('cash_flow').upsert(batch, on_conflict='year_month,flow_type,category,subcategory').execute()
                
                return True
                
            except Exception as insert_e:
                st.error(f"❌ Error saving cash flow records: {insert_e}")
                return False
        else:
            # No non-zero records to save is OK
            return True
        
    except Exception as e:
        # Add debug info for troubleshooting
        st.error(f"❌ Error saving liquidity data: {str(e)}")
        st.error(f"❌ Error details: {type(e).__name__}")
        return False

def cleanup_category_names_in_database():
    """Clean up category names with duplicate spaces in the cash_flow table"""
    try:
        supabase = get_supabase_client()
        
        # Get all records with potential spacing issues
        response = supabase.table('cash_flow').select('*').execute()
        
        if response.data:
            records_to_update = []
            for record in response.data:
                original_category = record['category']
                clean_category = ' '.join(original_category.split())
                
                if original_category != clean_category:
                    record['category'] = clean_category
                    records_to_update.append(record)
            
            if records_to_update:
                # Update records with clean category names
                for record in records_to_update:
                    supabase.table('cash_flow').update({'category': record['category']}).eq('id', record['id']).execute()
                
                st.success(f"✅ Cleaned up {len(records_to_update)} category names")
                return True
        
        return True
    except Exception as e:
        st.error(f"❌ Error cleaning category names: {str(e)}")
        return False

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_liquidity_data_from_database() -> Dict[str, Any]:
    """Load liquidity data (starting_balance, investment, other_cash_receipts, expenses) from Supabase"""
    try:
        supabase = get_supabase_client()
        liquidity_data = {}
        
        # Load starting balance from model_settings
        try:
            settings_response = supabase.table('model_settings').select('setting_value').eq('setting_category', 'liquidity').eq('setting_name', 'starting_balance').execute()
            if settings_response.data:
                raw_value = settings_response.data[0]['setting_value']
                # Handle jsonb that may come back as str or numeric
                if isinstance(raw_value, str):
                    try:
                        parsed = json.loads(raw_value)
                    except Exception:
                        parsed = raw_value
                else:
                    parsed = raw_value
                liquidity_data["starting_balance"] = float(parsed)
            else:
                liquidity_data["starting_balance"] = 1773162  # Default value
        except Exception as e:
            liquidity_data["starting_balance"] = 1773162
        
        # Initialize monthly data structures
        months = []
        for year in range(2025, 2031):
            for month_name in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                months.append(f"{month_name} {year}")
        
        liquidity_data["revenue"] = {month: 0 for month in months}
        liquidity_data["investment"] = {month: 0 for month in months}
        liquidity_data["other_cash_receipts"] = {month: 0 for month in months}
        liquidity_data["expenses"] = {}
        
        # Load cash flow data using limit as specified in memory
        try:
            cash_flow_response = supabase.table('cash_flow').select('*').order('year_month').limit(10000).execute()
            
            for record in cash_flow_response.data:
                try:
                    month_str = datetime.strptime(record['year_month'], "%Y-%m-%d").strftime("%b %Y")
                    amount = float(record['amount'])
                    category = record['category']
                    flow_type = record['flow_type']
                    
                    if flow_type == 'inflow':
                        if category == 'Revenue':
                            liquidity_data["revenue"][month_str] = amount
                        elif category == 'Investment':
                            liquidity_data["investment"][month_str] = amount
                        elif category == 'Other Cash Receipts':
                            liquidity_data["other_cash_receipts"][month_str] = amount
                    elif flow_type == 'outflow':
                        # Handle expense categories
                        if category not in liquidity_data["expenses"]:
                            liquidity_data["expenses"][category] = {month: 0 for month in months}
                        liquidity_data["expenses"][category][month_str] = amount
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            pass  # Silent error handling
        
        return liquidity_data
        
    except Exception as e:
        return {}

def load_starting_balance_from_database() -> float:
    """Load starting balance from model_settings table"""
    try:
        supabase = get_supabase_client()
        settings_response = supabase.table('model_settings').select('setting_value').eq('setting_category', 'liquidity').eq('setting_name', 'starting_balance').execute()
        if settings_response.data:
            return float(settings_response.data[0]['setting_value'])
        else:
            return 1773162  # Default value
    except Exception as e:
        return 1773162

def save_starting_balance_to_database(starting_balance: float) -> bool:
    """Save starting balance to model_settings table"""
    try:
        supabase = get_supabase_client()
        supabase.table('model_settings').upsert({
            'setting_category': 'liquidity',
            'setting_name': 'starting_balance',
            'setting_value': json.dumps(float(starting_balance)),
            'description': 'Starting cash balance for liquidity model',
            'data_type': 'number'
        }, on_conflict='setting_category,setting_name').execute()
        return True
    except Exception as e:
        return False

# ===== ENHANCED REVENUE ASSUMPTIONS SAVE/LOAD FUNCTIONS =====

def save_revenue_calculations_to_database(data: Dict[str, Any]) -> bool:
    """Save calculated revenue totals - table removed, returning success"""
    # Note: revenue_data table has been removed from schema
    # Revenue calculations are handled in memory and don't need database storage
    # Returning True to maintain compatibility
    return True

def save_comprehensive_revenue_assumptions_to_database(data: Dict[str, Any]) -> bool:
    """Comprehensive save of all revenue assumptions data to Supabase"""
    try:
        # Clear the connection cache to ensure fresh connection
        get_supabase_client.clear()
        
        # Save the detailed revenue assumptions (customer data, pricing, etc.)
        revenue_assumptions_success = save_revenue_assumptions_to_database(data)
        
        # Save the calculated revenue totals
        revenue_success = save_revenue_calculations_to_database(data)
        
        # Clear cache to ensure fresh data on next load
        load_revenue_assumptions_from_database.clear()
        load_comprehensive_revenue_data_from_database.clear()
        try:
            # Also clear the top-level loader cache so other pages refresh correctly
            load_data_from_source.clear()
        except Exception:
            pass
        
        # Clear connection cache after save to prevent stale connections
        get_supabase_client.clear()
        
        return revenue_assumptions_success and revenue_success
        
    except Exception as e:
        # Clear connection cache on error
        get_supabase_client.clear()
        log_error(f"❌ Error in comprehensive revenue save: {str(e)}")
        log_info("Debug info - Available data keys:", list(data.keys()) if data else "No data")
        import traceback
        log_info("Full error trace:", traceback.format_exc())
        return False

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_revenue_calculations_from_database() -> Dict[str, Any]:
    """Load calculated revenue totals - table removed, returning empty"""
    # Note: revenue_data table has been removed from schema
    # Revenue calculations are done in memory from the source data
    # Returning empty dict to maintain compatibility
    return {}

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_comprehensive_revenue_data_from_database() -> Dict[str, Any]:
    """Load all revenue-related data from Supabase"""
    try:
        # Load revenue assumptions (detailed data)
        revenue_assumptions = load_revenue_assumptions_from_database()
        
        # Load calculated revenue totals
        revenue_calculations = load_revenue_calculations_from_database()
        
        # Combine the data
        combined_data = {}
        combined_data.update(revenue_assumptions)
        combined_data.update(revenue_calculations)
        
        return combined_data
        
    except Exception as e:

        return {}

# REMOVED: Table sga_expenses deleted
def save_sga_expenses_to_database(data: Dict[str, Any]) -> bool:
    """Save SG&A expenses to sga_expenses table"""
    try:
        supabase = get_supabase_client()
        
        if "sga_expenses" not in data or not data["sga_expenses"]:
            return False
        
        # First, get all expense categories to map names to IDs
        categories_response = supabase.table('expense_categories').select('id, category_name').limit(10000).execute()
        category_id_map = {cat['category_name']: cat['id'] for cat in categories_response.data}
        
        sga_records = []
        sga_expenses = data["sga_expenses"]
        
        # Generate months from 2025-2030 (same as in other files)
        months = []
        for year in range(2025, 2031):
            for month in range(1, 13):
                months.append(f"{datetime(year, month, 1).strftime('%b %Y')}")
        
        for category_name, monthly_data in sga_expenses.items():
            # Skip if category doesn't exist in database
            if category_name not in category_id_map:
                continue
                
            category_id = category_id_map[category_name]
            
            for month_str in months:
                try:
                    year_month = datetime.strptime(month_str, "%b %Y").strftime("%Y-%m-%d")
                    amount = monthly_data.get(month_str, 0)
                    
                    sga_records.append({
                        'year_month': year_month,
                        'expense_category_id': category_id,
                        'amount': float(amount) if amount else 0,
                        'notes': f'Auto-saved from liquidity forecast for {category_name}'
                    })
                except (ValueError, KeyError):
                    continue
        
        if sga_records:
            # Use upsert to update existing records or insert new ones
            # Table sga_expenses removed - skipping database save
            pass
        # supabase.table('sga_expenses').upsert(
        #         sga_records, 
        #         on_conflict='year_month,expense_category_id'
        #     ).execute()
        
        return True
        
    except Exception as e:
        return False

# ===== ENHANCED MAIN SAVE FUNCTION =====

def save_data_to_source(data: Dict[str, Any]) -> bool:
    """Enhanced comprehensive save function that handles all data types including revenue and liquidity"""
    try:
        # Save all the existing data types
        success_flags = []
        
        # 1. Save payroll data
        if any(key in data for key in ["employees", "contractors", "employee_bonuses", "pay_periods"]):
            success_flags.append(save_payroll_data_to_database(data))
        
        # 2. Save hosting costs
        if "hosting_costs_data" in data:
            # Function save_hosting_costs_to_database removed - table deleted
            success_flags.append(True)  # Mock success
        
        # 3. Save budget data
        if "budget_data" in data:
            success_flags.append(save_budget_data_to_database(data))
        
        # 4. Save SG&A expenses
        if "sga_expenses" in data:
            # Function save_sga_expenses_to_database removed - table deleted
            success_flags.append(True)  # Mock success
        
        # 5. Save revenue assumptions and calculations (NEW)
        if any(key in data for key in ["subscription_new_customers", "subscription_pricing", "transactional_volume", "revenue"]):
            success_flags.append(save_comprehensive_revenue_assumptions_to_database(data))
        
        # 6. Save gross profit data (NEW)
        if "gross_profit_data" in data:
            success_flags.append(save_gross_profit_data_to_database(data))
        
        # 7. Save liquidity data (NEW)
        if "liquidity_data" in data:
            success_flags.append(save_liquidity_data_to_database(data))
        
        # Check overall success
        if all(success_flags):
                    return True
        elif any(success_flags):

            return True
        else:
            st.error("❌ Failed to save data")
            return False
        
    except Exception as e:
        st.error(f"❌ Error in comprehensive save: {e}")
        return False

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_data_from_source() -> Dict[str, Any]:
    """Enhanced comprehensive load function that loads all data including revenue and liquidity"""
    try:
        # Initialize empty model data 
        model_data = {}
        
        # Load additional data from Supabase with individual error handling
        try:
            # Load payroll data
            payroll_data = load_payroll_data_from_database()
            if payroll_data and isinstance(payroll_data, dict):
                # Properly nest payroll data under 'payroll_data' key
                model_data["payroll_data"] = payroll_data
        except Exception as e:
            pass
    
            
        try:
            # Load hosting costs
            # Function load_hosting_costs_from_database removed - table deleted
            hosting_data = {"hosting_costs_data": {"cost_structure": {}, "go_live_settings": {}}}
            if hosting_data and isinstance(hosting_data, dict):
                model_data.update(hosting_data)
        except Exception as e:
            pass
    
            
        try:
            # Load budget data
            budget_data = load_budget_data_from_database()
            if budget_data and isinstance(budget_data, dict):
                # Wrap budget data in the expected structure
                model_data["budget_data"] = budget_data
        except Exception as e:
            pass
    
            
        # SG&A expenses are loaded as part of budget data - no separate function needed
        
        try:
            # Load comprehensive revenue data (NEW)
            revenue_data = load_comprehensive_revenue_data_from_database()
            if revenue_data and isinstance(revenue_data, dict):
                model_data.update(revenue_data)
        except Exception as e:
            pass
    
            
        try:
            # Load gross profit data from model_settings (inline functionality)
            supabase = get_supabase_client()
            if supabase is not None:
                gross_profit_data = {}
                
                # Generate months from 2025-2030
                months = []
                for year in range(2025, 2031):
                    for month in range(1, 13): 
                        from datetime import date
                        months.append(f"{date(year, month, 1).strftime('%b %Y')}")
                
                gross_profit_data = {
                    "gross_profit_percentages": {},
                    "saas_hosting_structure": {
                        "go_live_month": "Jan 2025",
                        "capitalize_before_go_live": True,
                        "monthly_fixed_costs": {month: 15400.0 for month in months},
                        "monthly_variable_costs": {month: 5.0 for month in months}
                    }
                }
                
                # Load settings from model_settings table
                settings_response = supabase.table('model_settings').select("*").limit(10000).execute()
            
                for setting in settings_response.data:
                    if setting['setting_category'] == 'hosting':
                        if setting['setting_name'] == 'go_live_month':
                            gross_profit_data["saas_hosting_structure"]["go_live_month"] = json.loads(setting['setting_value'])
                        elif setting['setting_name'] == 'capitalize_before_go_live':
                            gross_profit_data["saas_hosting_structure"]["capitalize_before_go_live"] = json.loads(setting['setting_value'])
                        elif setting['setting_name'] == 'monthly_fixed_costs':
                            loaded_fixed_costs = json.loads(setting['setting_value'])
                            gross_profit_data["saas_hosting_structure"]["monthly_fixed_costs"].update(loaded_fixed_costs)
                        elif setting['setting_name'] == 'monthly_variable_costs':
                            loaded_variable_costs = json.loads(setting['setting_value'])
                            gross_profit_data["saas_hosting_structure"]["monthly_variable_costs"].update(loaded_variable_costs)
                    elif setting['setting_category'] == 'gross_profit':
                        if '_gp_percentages' in setting['setting_name']:
                            stream = setting['setting_name'].replace('_gp_percentages', '').title()
                            gross_profit_data["gross_profit_percentages"][stream] = json.loads(setting['setting_value'])
                
                # Initialize default values if not loaded
                if not gross_profit_data["gross_profit_percentages"]:
                    for stream in ["Subscription", "Transactional", "Implementation", "Maintenance"]:
                        gross_profit_data["gross_profit_percentages"][stream] = {
                            month: 70.0 for month in months
                        }
                
                if gross_profit_data:
                    model_data["gross_profit_data"] = gross_profit_data
        except Exception as e:
            pass
    
        try:
            # Load liquidity data (NEW)
            liquidity_data = load_liquidity_data_from_database()
            if liquidity_data and isinstance(liquidity_data, dict):
                # Replace entire liquidity_data instead of updating to ensure clean state
                model_data["liquidity_data"] = liquidity_data
        except Exception as e:
            model_data["liquidity_data"] = {}
    
        
        return model_data
        
    except Exception as e:

        # Return minimal data structure to prevent complete failure
        return {
            "liquidity_data": {},
            "revenue": {},
            "sga_expenses": {},
            "employees": {},
            "contractors": {}
        }

# Legacy functions for backward compatibility
def save_to_supabase(data: Dict[str, Any]) -> bool:
    """Legacy function - redirects to save_data_to_source"""
    return save_data_to_source(data)

def load_data() -> Dict[str, Any]:
    """Legacy function - redirects to load_data_from_source"""
    return load_data_from_source()

def save_data(data: Dict[str, Any]) -> bool:
    """Legacy function - redirects to save_data_to_source"""
    return save_data_to_source(data)

# Legacy JSON functions removed - now using 100% Supabase

def show_supabase_access_info():
    """Display Supabase connection information and table status"""
    try:
        supabase = get_supabase_client()
        

        
        # Test connection and show basic info
        st.write("**Connection Status:** ✅ Connected")
        
        # Show available tables
        st.write("**Available Tables:**")
        table_names = [
            "employees", "employee_bonuses", "pay_periods", 
            "hosting_costs", "customer_assumptions", "pricing_data",
            "budget_data", "sga_expenses", "revenue_data", 
            "cash_flow", "model_settings", "business_segments"
        ]
        
        for table in table_names:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                count = len(result.data) if result.data else 0
                st.write(f"  • {table}: ✅ Available")
            except Exception as e:
                pass
                st.write(f"  • {table}: ❌ Error - {str(e)[:50]}...")
        
        st.write("**Database URL:** Configured via Streamlit secrets")
        st.write("**Authentication:** Using service role key")
        
    except Exception as e:
        st.error(f"❌ Error getting Supabase info: {str(e)}")

def save_all_to_supabase_enhanced(data: Dict[str, Any]) -> bool:
    """Enhanced save function that maps all data to appropriate Supabase tables"""
    try:
        success_count = 0
        total_operations = 0
        
        # Map different data types to their respective save functions
        save_functions = {
            'revenue': save_revenue_assumptions_to_database,
            'payroll': save_payroll_data_to_database,
            # 'hosting': save_hosting_costs_to_database,  # Function removed
            'liquidity': save_liquidity_data_to_database,
            'budget': save_budget_data_to_database,
            # 'gross_profit': save_gross_profit_data_to_database,  # Function kept but table operations removed
            'income_statement': save_income_statement_to_database
        }
        
        for data_type, save_func in save_functions.items():
            if data_type in data and data[data_type]:
                total_operations += 1
                try:
                    if save_func(data):
                        success_count += 1
        
                    else:
                        pass
                        
                except Exception as e:
                    pass
        
        
        # Show summary
        if total_operations > 0:
            return success_count == total_operations
        else:
            return False
            
    except Exception as e:
        return False

def save_income_statement_to_database(data: Dict[str, Any]) -> bool:
    """Save complete income statement data to Supabase income_statement table"""
    try:
        # Use service role client to bypass RLS
        from supabase import create_client, Client
        
        # Get Supabase client with service role key to bypass RLS
        try:
            supabase_url = st.secrets["SUPABASE_URL"]
            # Use service key to bypass RLS policies
            if "SUPABASE_SERVICE_KEY" in st.secrets:
                supabase_service_key = st.secrets["SUPABASE_SERVICE_KEY"]
                supabase: Client = create_client(supabase_url, supabase_service_key)
            else:
                # Fallback to anon key
                supabase_anon_key = st.secrets["SUPABASE_ANON_KEY"]
                supabase: Client = create_client(supabase_url, supabase_anon_key)
        except KeyError as e:
            st.error(f"❌ Missing Supabase configuration in secrets: {str(e)}")
            return False

        # Extract the comprehensive income statement data
        revenue_data = data.get("revenue", {})
        cogs_data = data.get("cogs", {})
        gross_profit_data = data.get("gross_profit", {})
        sga_expenses = data.get("sga_expenses", {})
        liquidity_data = data.get("liquidity_data", {})
        
        # Check if we have any data to save
        if not revenue_data and not sga_expenses:
            st.error("❌ No revenue or SGA data found to save!")
            return False
        
        # Define time structure (months from 2025-2030)
        months = []
        for year in range(2025, 2031):
            for month_name in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                months.append(f"{month_name} {year}")
        
        # Define categories
        revenue_categories = ["Subscription", "Transactional", "Implementation", "Maintenance"]
        
        # Get SG&A categories from liquidity data
        if liquidity_data and "category_order" in liquidity_data:
            sga_categories = liquidity_data["category_order"]
        else:
            sga_categories = [
                "Payroll", "Contractors", "License Fees", "Travel", "Shows", "Associations",
                "Marketing", "Company Vehicle", "Grant Writer", "Insurance", "Legal / Professional Fees",
                "Permitting/Fees/Licensing", "Shared Services", "Consultants/Audit/Tax", "Pritchard Amex", "Contingencies"
            ]
        
        # Clear existing data for this save
        try:
            supabase.table('income_statement').delete().neq('id', 0).execute()
        except Exception as e:
            # Continue anyway - this might be the first save or a permission issue
            pass
        
        # Prepare records for batch insert
        income_statement_records = []
        
        # Process each month
        for month in months:
            # Parse month for database
            month_parts = month.split(' ')
            month_name = month_parts[0]
            year = int(month_parts[1])
            
            # Convert month name to number
            month_num = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(month_name) + 1
            year_month = f"{year}-{month_num:02d}-01"
            
            # Calculate monthly totals
            total_revenue = sum(revenue_data.get(cat, {}).get(month, 0) for cat in revenue_categories)
            total_cogs = sum(cogs_data.get(cat, {}).get(month, 0) for cat in revenue_categories)
            total_gross_profit = total_revenue - total_cogs
            total_sga = sum(sga_expenses.get(cat, {}).get(month, 0) for cat in sga_categories)
            net_income = total_gross_profit - total_sga
            gross_margin = (total_gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
                        # Create record for each revenue category
            for category in revenue_categories:
                revenue_amount = revenue_data.get(category, {}).get(month, 0)
                cogs_amount = cogs_data.get(category, {}).get(month, 0)
                gross_profit_amount = revenue_amount - cogs_amount
                category_gross_margin = (gross_profit_amount / revenue_amount * 100) if revenue_amount > 0 else 0

                income_statement_records.append({
                    'year_month': year_month,
                    'category_type': 'revenue_line',
                    'category_name': category,
                    'revenue_amount': float(revenue_amount),
                    'cogs_amount': float(cogs_amount),
                    'gross_profit_amount': float(gross_profit_amount),
                    'sga_amount': 0.0,  # SG&A is tracked separately
                    'net_income_amount': 0.0,  # Net income is calculated at total level
                    'gross_margin_percentage': float(category_gross_margin),
                    'is_total_row': False
                })
            
            # Create record for each SG&A category
            for category in sga_categories:
                sga_amount = sga_expenses.get(category, {}).get(month, 0)
                
                income_statement_records.append({
                    'year_month': year_month,
                    'category_type': 'sga_expense',
                    'category_name': category,
                    'revenue_amount': 0.0,
                    'cogs_amount': 0.0,
                    'gross_profit_amount': 0.0,
                    'sga_amount': float(sga_amount),
                    'net_income_amount': 0.0,
                    'gross_margin_percentage': 0.0,
                    'is_total_row': False
                })
            
            # Create monthly total record
            income_statement_records.append({
                'year_month': year_month,
                'category_type': 'monthly_total',
                'category_name': 'Total',
                'revenue_amount': float(total_revenue),
                'cogs_amount': float(total_cogs),
                'gross_profit_amount': float(total_gross_profit),
                'sga_amount': float(total_sga),
                'net_income_amount': float(net_income),
                'gross_margin_percentage': float(gross_margin),
                'is_total_row': True
            })
        
                # Batch insert records
        if income_statement_records:
            batch_size = 100  # Insert in batches to avoid overwhelming the database

            for i in range(0, len(income_statement_records), batch_size):
                batch = income_statement_records[i:i + batch_size]
                try:
                    result = supabase.table('income_statement').insert(batch).execute()
                except Exception as batch_error:
                    st.error(f"❌ Error saving income statement data: {str(batch_error)}")
                    return False

            return True
        else:
            st.error("❌ No income statement records were prepared for saving!")
            return False

    except Exception as e:
        st.error(f"❌ Error saving income statement data: {str(e)}")
        return False

"""
INCOME STATEMENT TABLE STRUCTURE FOR SUPABASE:

CREATE TABLE public.income_statement (
    id SERIAL PRIMARY KEY,
    year_month DATE NOT NULL,                    -- Format: YYYY-MM-01
    category_type VARCHAR(50) NOT NULL,          -- 'revenue_line', 'sga_expense', 'monthly_total'
    category_name VARCHAR(100) NOT NULL,         -- Category name (Subscription, Payroll, Total, etc.)
    revenue_amount DECIMAL(15,2) DEFAULT 0,      -- Revenue amount for this category/month
    cogs_amount DECIMAL(15,2) DEFAULT 0,         -- Cost of Goods Sold amount
    gross_profit_amount DECIMAL(15,2) DEFAULT 0, -- Gross Profit (Revenue - COGS)
    sga_amount DECIMAL(15,2) DEFAULT 0,          -- SG&A expense amount
    net_income_amount DECIMAL(15,2) DEFAULT 0,   -- Net Income (Gross Profit - SG&A)
    gross_margin_percentage DECIMAL(5,2) DEFAULT 0, -- Gross Margin %
    is_total_row BOOLEAN DEFAULT FALSE,          -- True for total/summary rows
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_income_statement_year_month ON public.income_statement(year_month);
CREATE INDEX idx_income_statement_category ON public.income_statement(category_type, category_name);
CREATE INDEX idx_income_statement_totals ON public.income_statement(is_total_row, year_month);

-- Enable Row Level Security
ALTER TABLE public.income_statement ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users
CREATE POLICY "Enable all operations for authenticated users" ON public.income_statement
    FOR ALL USING (auth.role() = 'authenticated');
"""

def clean_up_cash_disbursement_categories(data: Dict[str, Any]) -> bool:
    """Clean up and reset cash disbursement categories to ensure consistency across income statement and KPI dashboard"""
    try:
        # The correct categories in the exact order the user needs
        correct_categories = [
            "Payroll",                    # Must be first - syncs with payroll headcount
            "Contractors",                # Second - syncs with contractor headcount  
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
            "Pritchard Amex",             # User preference: Amex (title case)
            "Contingencies"
        ]
        
        # Initialize liquidity_data if not exists
        if "liquidity_data" not in data:
            data["liquidity_data"] = {}
        
        # Set the correct category order
        data["liquidity_data"]["category_order"] = correct_categories.copy()
        
        # Initialize expenses structure if not exists
        if "expenses" not in data["liquidity_data"]:
            data["liquidity_data"]["expenses"] = {}
        
        # Initialize sga_expenses structure if not exists
        if "sga_expenses" not in data:
            data["sga_expenses"] = {}
        
        # Create months list (2025-2030)
        months = []
        for year in range(2025, 2031):
            for month_name in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                months.append(f"{month_name} {year}")
        
        # Ensure all categories exist in both expenses and sga_expenses with proper structure
        for category in correct_categories:
            # Initialize liquidity expenses (cash disbursements)
            if category not in data["liquidity_data"]["expenses"]:
                data["liquidity_data"]["expenses"][category] = {month: 0 for month in months}
            
            # Initialize SG&A expenses (for income statement)
            if category not in data["sga_expenses"]:
                data["sga_expenses"][category] = {month: 0 for month in months}
            
            # Ensure all months exist for existing categories
            for month in months:
                if month not in data["liquidity_data"]["expenses"][category]:
                    data["liquidity_data"]["expenses"][category][month] = 0
                if month not in data["sga_expenses"][category]:
                    data["sga_expenses"][category][month] = 0
        
        # Initialize expense_categories structure if not exists (needed for UI)
        if "expense_categories" not in data["liquidity_data"]:
            data["liquidity_data"]["expense_categories"] = {}
        
        # Set up proper category definitions (preserving payroll/contractor sync flags)
        category_definitions = {
            "Payroll": {"classification": "Personnel", "editable": False},        # Non-editable - syncs with headcount
            "Contractors": {"classification": "Personnel", "editable": True},     # Editable - manual contractor costs
            "License Fees": {"classification": "Product Development", "editable": False},
            "Travel": {"classification": "Sales and Marketing", "editable": True},
            "Shows": {"classification": "Sales and Marketing", "editable": True},
            "Associations": {"classification": "Sales and Marketing", "editable": True},
            "Marketing": {"classification": "Sales and Marketing", "editable": True},
            "Company Vehicle": {"classification": "Opex", "editable": True},
            "Grant Writer": {"classification": "Opex", "editable": True},
            "Insurance": {"classification": "Opex", "editable": True},
            "Legal / Professional Fees": {"classification": "Opex", "editable": True},
            "Permitting/Fees/Licensing": {"classification": "Opex", "editable": True},
            "Shared Services": {"classification": "Opex", "editable": True},
            "Consultants/Audit/Tax": {"classification": "Opex", "editable": True},
            "Pritchard Amex": {"classification": "Opex", "editable": True},
            "Contingencies": {"classification": "Opex", "editable": True},
        }
        
        # Apply category definitions
        for category, definition in category_definitions.items():
            data["liquidity_data"]["expense_categories"][category] = definition
        
        # Clean up any old/incorrect categories that might exist
        categories_to_remove = []
        for existing_category in data["liquidity_data"]["expenses"].keys():
            if existing_category not in correct_categories:
                categories_to_remove.append(existing_category)
        
        for category_to_remove in categories_to_remove:

            data["liquidity_data"]["expenses"].pop(category_to_remove, None)
            data["sga_expenses"].pop(category_to_remove, None)
            data["liquidity_data"]["expense_categories"].pop(category_to_remove, None)
        

        
        return True
        
    except Exception as e:
        st.error(f"❌ Error cleaning up categories: {str(e)}")
        return False

# ===== AUTOSAVE FUNCTIONALITY =====

def enable_autosave():
    """Enable autosave functionality for the current session"""
    if 'autosave_enabled' not in st.session_state:
        st.session_state.autosave_enabled = True

def auto_save_data(data: Dict[str, Any], page_name: str):
    """Auto-save data to the database with user feedback"""
    try:
        if not st.session_state.get('autosave_enabled', False):
            return
        
        # Save data using the comprehensive save function
        success = save_data_to_source(data)
        
        if not success:
            # Try individual save functions as fallback
            try:
                if page_name == "Revenue Assumptions":
                    save_comprehensive_revenue_assumptions_to_database(data)
            except Exception:
                pass  # Silent fail for autosave
                
    except Exception as e:
        pass  # Silent fail for autosave


