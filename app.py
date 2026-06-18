import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- PAGE SETUP & CONFIGURATION ---
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling (adds glassmorphic look, custom scrollbars, and sleek cards)
st.markdown("""
    <style>
    /* Main container adjustments */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header style */
    .main-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Sleek metric card styling override */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)


# --- HELPERS: MOCK DATA GENERATOR ---
def generate_mock_data():
    """Generates realistic transaction data for user testing if no CSV is uploaded."""
    np.random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    date_range = [start_date + timedelta(days=i) for i in range(91)]
    
    templates = [
        ("Walmart Supercenter", "Groceries", (30.0, 150.0)),
        ("Target Store", "Groceries", (15.0, 80.0)),
        ("Local Grocery Market", "Groceries", (10.0, 60.0)),
        ("Netflix.com Subscription", "Subscriptions", (15.49, 15.49)),
        ("Spotify Premium", "Subscriptions", (9.99, 9.99)),
        ("Hulu Streaming", "Subscriptions", (7.99, 14.99)),
        ("Shell Gas Station", "Transportation", (25.0, 65.0)),
        ("Uber Trip", "Transportation", (12.0, 45.0)),
        ("Gas & Go", "Transportation", (20.0, 50.0)),
        ("Starbucks Coffee", "Other", (4.50, 12.00)),
        ("Amazon.com Order", "Other", (10.0, 120.0)),
        ("Steam Games Store", "Other", (5.0, 60.0)),
        ("Home Depot", "Other", (15.0, 200.0)),
        ("McDonalds Fast Food", "Other", (8.0, 25.0)),
        ("Electric Utility Bill", "Other", (70.0, 150.0)),
    ]
    
    data = []
    for _ in range(80):
        date = np.random.choice(date_range)
        template = templates[np.random.randint(0, len(templates))]
        desc, _, amt_range = template
        amount = round(np.random.uniform(amt_range[0], amt_range[1]), 2)
        
        # Add random suffix to descriptions for realism
        if "Supercenter" in desc or "Store" in desc or "Gas" in desc or "Trip" in desc or "Order" in desc:
            desc = f"{desc} #{np.random.randint(1000, 9999)}"
            
        data.append({
            "Transaction Date": date.strftime("%Y-%m-%d"),
            "Transaction Description": desc,
            "Amount": amount
        })
        
    df = pd.DataFrame(data)
    # Sort from oldest to newest
    df = df.sort_values(by="Transaction Date").reset_index(drop=True)
    return df


# --- CORE PIPELINE: DATA PROCESSING & CATEGORIZATION ---
def process_data(df):
    """
    Pandas processing pipeline to:
    1. Standardize columns to: Date, Description, Amount
    2. Convert types (Date -> datetime, Amount -> float)
    3. Auto-categorize based on description keywords
    """
    # Create a copy to prevent modifying original data
    df_clean = df.copy()
    
    # 1. Column standardization map
    rename_map = {}
    for col in df_clean.columns:
        col_lower = str(col).lower().strip()
        if 'date' in col_lower:
            rename_map[col] = 'Date'
        elif 'desc' in col_lower or 'memo' in col_lower:
            rename_map[col] = 'Description'
        elif 'amount' in col_lower or 'val' in col_lower or 'price' in col_lower:
            rename_map[col] = 'Amount'
            
    df_clean = df_clean.rename(columns=rename_map)
    
    # Verify that we've found all necessary columns
    required = ['Date', 'Description', 'Amount']
    missing = [col for col in required if col not in df_clean.columns]
    if missing:
        raise ValueError(
            f"Could not map columns to {required}. Missing: {missing}. "
            f"Please ensure your CSV contains headers for Date, Description, and Amount."
        )
        
    # Keep only the required columns to avoid bloating
    df_clean = df_clean[required]
    
    # 2. Type conversions
    # Convert Date column to Datetime
    df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')
    # Convert Amount column to numeric float
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce')
    
    # Drop rows with invalid dates or amounts
    df_clean = df_clean.dropna(subset=['Date', 'Amount'])
    
    # 3. Keyword-based Categorization Engine
    def auto_categorize(description):
        desc = str(description).lower()
        # Groceries
        if any(kw in desc for kw in ['walmart', 'target', 'grocery']):
            return 'Groceries'
        # Subscriptions
        elif any(kw in desc for kw in ['netflix', 'spotify', 'hulu']):
            return 'Subscriptions'
        # Transportation
        elif any(kw in desc for kw in ['gas', 'shell', 'uber']):
            return 'Transportation'
        # Default
        return 'Other'
        
    df_clean['Category'] = df_clean['Description'].apply(auto_categorize)
    return df_clean


# --- MAIN APPLICATION LOGIC ---
def main():
    # Application Title & Header
    st.markdown("<h1 class='main-title'>💰 Personal Finance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Analyze your spending patterns, track monthly trends, and manage budgets in real time.</p>", unsafe_allow_html=True)
    
    # Initialize session state for holding DataFrame
    if 'df_raw' not in st.session_state:
        st.session_state['df_raw'] = None
        st.session_state['df_processed'] = None
        st.session_state['source'] = None
        
    # --- SIDEBAR CONFIGURATION ---
    st.sidebar.header("📁 Data Source")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload bank statement (CSV)",
        type=['csv'],
        help="Upload a standard bank statement or credit card statement CSV file."
    )
    
    # Option to load sample mock data
    if uploaded_file is None:
        st.sidebar.markdown("**OR**")
        if st.sidebar.button("💡 Load Sample Transactions", use_container_width=True):
            with st.spinner("Generating sample transactions..."):
                df_mock = generate_mock_data()
                st.session_state['df_raw'] = df_mock
                st.session_state['df_processed'] = process_data(df_mock)
                st.session_state['source'] = "Sample Mock Data"
                st.success("Sample data loaded successfully!")
                st.rerun()
                
    # If a new file is uploaded
    if uploaded_file is not None:
        try:
            # Read CSV
            df_uploaded = pd.read_csv(uploaded_file)
            st.session_state['df_raw'] = df_uploaded
            st.session_state['df_processed'] = process_data(df_uploaded)
            st.session_state['source'] = f"Uploaded File ({uploaded_file.name})"
        except Exception as e:
            st.sidebar.error(f"Error parsing file: {e}")
            
    # Check if we have loaded data
    df_data = st.session_state['df_processed']
    
    if df_data is None:
        # Show prompt when no data is loaded
        st.info("👈 Get started by uploading your bank statement CSV file in the sidebar, or click **'Load Sample Transactions'** to explore with mock data.")
        return
        
    # Show active data source indicator
    st.sidebar.info(f"🟢 Active Source: {st.session_state['source']}")
    
    # --- DATA NORMALIZATION SETTINGS ---
    st.sidebar.header("⚙️ Data Settings")
    
    # Expense Sign Configuration (Some banks list expenses as negative values, some as positive)
    sign_convention = st.sidebar.selectbox(
        "How are expenses formatted?",
        options=["Auto-detect", "Treat negative values as expenses", "Treat all values as expenses"],
        help="Choose how the app should identify expense amounts. Auto-detect looks for negative values and flips them to positive."
    )
    
    # Process dataset depending on sign convention
    df_expenses = df_data.copy()
    
    if sign_convention == "Auto-detect":
        # If there are negative values, treat negative values as the expenses
        if (df_expenses['Amount'] < 0).any():
            df_expenses = df_expenses[df_expenses['Amount'] < 0]
            df_expenses['Amount'] = df_expenses['Amount'].abs()
        else:
            # Otherwise assume all are positive expenses
            df_expenses['Amount'] = df_expenses['Amount'].abs()
    elif sign_convention == "Treat negative values as expenses":
        df_expenses = df_expenses[df_expenses['Amount'] < 0]
        df_expenses['Amount'] = df_expenses['Amount'].abs()
    elif sign_convention == "Treat all values as expenses":
        df_expenses['Amount'] = df_expenses['Amount'].abs()
        
    # Ensure date range boundary checks
    min_date = df_expenses['Date'].min().date()
    max_date = df_expenses['Date'].max().date()
    
    # --- SIDEBAR INTERACTIVE FILTERS ---
    st.sidebar.header("🔍 Filters")
    
    # 1. Date Range Filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Handle the date range selection state securely
    if isinstance(date_range, list) or isinstance(date_range, tuple):
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = date_range[0]
            end_date = start_date
    else:
        start_date = date_range
        end_date = date_range
        
    # 2. Category Filter
    all_categories = sorted(df_expenses['Category'].unique())
    selected_categories = st.sidebar.multiselect(
        "Select Categories",
        options=all_categories,
        default=all_categories
    )
    
    # Apply filters to the processed dataset
    filtered_df = df_expenses[
        (df_expenses['Date'].dt.date >= start_date) &
        (df_expenses['Date'].dt.date <= end_date) &
        (df_expenses['Category'].isin(selected_categories))
    ]
    
    # Prevent divide-by-zero or empty plots errors gracefully
    if filtered_df.empty:
        st.warning("⚠️ No transactions match the selected filters. Please adjust your date range or category filters in the sidebar.")
        return
        
    # --- VISUALIZATIONS & METRICS SECTION ---
    
    # Calculate Metrics
    total_spending = filtered_df['Amount'].sum()
    num_transactions = len(filtered_df)
    
    # Get top category
    if not filtered_df.empty:
        cat_group = filtered_df.groupby('Category')['Amount'].sum()
        top_category = cat_group.idxmax() if not cat_group.empty else "N/A"
        top_category_val = cat_group.max() if not cat_group.empty else 0.0
    else:
        top_category = "N/A"
        top_category_val = 0.0
        
    # Metric Columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.container(border=True).metric(
            label="Total Spending",
            value=f"${total_spending:,.2f}",
            delta=f"{num_transactions} txs"
        )
        
    with col2:
        st.container(border=True).metric(
            label="Top Expense Category",
            value=top_category,
            delta=f"${top_category_val:,.2f} spent" if top_category != "N/A" else None
        )
        
    with col3:
        st.container(border=True).metric(
            label="Total Transactions",
            value=f"{num_transactions:,}",
            delta="Filtered range"
        )
        
    st.markdown("---")
    
    # Layout with columns for charts
    chart_col1, chart_col2 = st.columns(2)
    
    # CHART 1: Monthly Trend
    with chart_col1:
        st.subheader("📈 Spending Trend Over Time")
        
        # Resample to group by month
        monthly_df = filtered_df.resample('ME', on='Date')['Amount'].sum().reset_index()
        # Format the Month name nicely for the X-axis
        monthly_df['Month'] = monthly_df['Date'].dt.strftime('%b %Y')
        
        # Fallback to daily trend if date range is too short (under 45 days)
        day_span = (end_date - start_date).days
        if day_span <= 45:
            daily_df = filtered_df.groupby(filtered_df['Date'].dt.date)['Amount'].sum().reset_index()
            daily_df.columns = ['Date', 'Amount']
            fig_trend = px.line(
                daily_df,
                x='Date',
                y='Amount',
                markers=True,
                labels={'Amount': 'Amount ($)', 'Date': 'Date'},
                color_discrete_sequence=['#38bdf8']
            )
            st.caption("Showing daily trend due to short date range filter.")
        else:
            fig_trend = px.bar(
                monthly_df,
                x='Month',
                y='Amount',
                labels={'Amount': 'Amount ($)', 'Month': 'Month'},
                color_discrete_sequence=['#818cf8']
            )
            
        fig_trend.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.1)'),
            height=320
        )
        st.plotly_chart(fig_trend, use_container_width=True, theme="streamlit")
        
    # CHART 2: Breakdown by Category
    with chart_col2:
        st.subheader("🍰 Spending Breakdown by Category")
        
        category_df = filtered_df.groupby('Category')['Amount'].sum().reset_index()
        
        # Color mapping to match the modern aesthetics
        color_map = {
            "Groceries": "#34d399",       # Pastel Green
            "Subscriptions": "#f87171",   # Pastel Red
            "Transportation": "#fbbf24",  # Pastel Amber
            "Other": "#a78bfa"            # Pastel Violet
        }
        
        fig_pie = px.pie(
            category_df,
            names='Category',
            values='Amount',
            color='Category',
            color_discrete_map=color_map,
            hole=0.4
        )
        
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#0e1117', width=2))
        )
        
        fig_pie.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            showlegend=False,
            height=320
        )
        st.plotly_chart(fig_pie, use_container_width=True, theme="streamlit")
        
    st.markdown("---")
    
    # --- SEARCHABLE DATA TABLE ---
    st.subheader("🔎 Filtered Transactions List")
    
    # Search Box for manual search filtering
    search_query = st.text_input(
        "Search transactions by description or category...",
        placeholder="Type here to search (e.g. walmart, subscriptions...)"
    )
    
    display_df = filtered_df.copy()
    
    # Apply text filter if any query is entered
    if search_query:
        display_df = display_df[
            display_df['Description'].str.contains(search_query, case=False, na=False) |
            display_df['Category'].str.contains(search_query, case=False, na=False)
        ]
        
    # Formatting for display
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df = display_df.sort_values(by='Date', ascending=False)
    
    # Display styled table
    st.dataframe(
        display_df[['Date', 'Description', 'Category', 'Amount']],
        use_container_width=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="$%.2f"),
            "Date": st.column_config.TextColumn(label="Transaction Date"),
            "Description": st.column_config.TextColumn(label="Merchant / Description"),
            "Category": st.column_config.TextColumn(label="Category")
        },
        hide_index=True
    )
    
    # --- EXPORT DATA BUTTON ---
    # Convert filtered dataset back to CSV bytes for download
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name=f"filtered_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        use_container_width=True
    )

if __name__ == "__main__":
    main()
