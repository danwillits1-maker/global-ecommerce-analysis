# Data Cleaning
# Step 1: load in the data and preview
df_raw = pd.read_csv('ecommerce_sales_dataset.csv')
df_raw.info()
df_raw.head(5)

# Step 2: Create copy to protect source
df_cleaned = df_raw.copy()

# Step 3: Fix irregular column header formatting
df_cleaned.columns = (df_cleaned.columns
                      .str.strip()
                      .str.lower()
                      .str.replace(' ', '_')
                      .str.replace('%', 'pct'))

df_cleaned.head(5)

# Step 4: Clean up the data within the colunms
# Ensure proper datetime formatting for order_date column
df_cleaned['order_date'] = pd.to_datetime(
    df_cleaned['order_date'], dayfirst=True)

# Create standardised format within all string columns
text_cols = df_cleaned.select_dtypes(include=['object']).columns
for col in text_cols:
    df_cleaned[col] = df_cleaned[col].str.strip(
    ).str.replace(r'\s+', ' ', regex=True)

    # Missing values in strings go to 'unknown'
for col in text_cols:
    df_cleaned[col] = df_cleaned[col].fillna('unknown')

    # Delete any absolute repeat rows
initial_rows = len(df_cleaned)
df_cleaned = df_cleaned.drop_duplicates()
final_rows = len(df_cleaned)
if initial_rows != final_rows:
    print(f"⚠️ Removed {initial_rows - final_rows} absolute duplicate rows.")

df_cleaned.head(5)


# Creating star schema
# Identified 6 key dimensions that I want to pull out; geography, customer, product, shipping/region, calender, and order status. This seperated data into all different categories allowing for proper cross filtering analysis later.
# STEP 1. GEOGRAPHY DIMENSION
dim_geography = (
    df_cleaned[['region', 'country']]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_geography['geography_key'] = dim_geography.index + 1
dim_geography = dim_geography[['geography_key', 'region', 'country']]

# STEP 2. CUSTOMER DIMENSION
dim_customers = (
    df_cleaned[['customer_id', 'customer_gender', 'customer_segment']]
    .drop_duplicates(subset=['customer_id'])
    .reset_index(drop=True)
)


# STEP 3. PRODUCT DIMENSION (With Category -> Sub-Category -> Name Hierarchy)
# Grouping all product details together
dim_products = (
    df_cleaned[['product_name', 'category', 'sub_category']]
    .drop_duplicates(subset=['product_name'])
    .reset_index(drop=True)
)
dim_products['product_key'] = dim_products.index + 1
dim_products = dim_products[['product_key',
                             'product_name', 'category', 'sub_category']]


# STEP 4. SHIPPING DIMENSION
dim_shipping = (
    df_cleaned[['shipping_method', 'shipping_days']]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_shipping['shipping_key'] = dim_shipping.index + 1
dim_shipping = dim_shipping[['shipping_key',
                             'shipping_method', 'shipping_days']]


# STEP 5. CALENDAR DIMENSION
dim_calendar = (
    df_cleaned[['order_date', 'year', 'month', 'quarter', 'season']]
    .drop_duplicates(subset=['order_date'])
    .reset_index(drop=True)
)


# STEP 6. STATUS DIMENSION - not all orders are successull
# Extract the 4 unique statuses from your cleaned dataframe
dim_statuses = (
    df_cleaned[['order_status']]
    .drop_duplicates()
    .reset_index(drop=True)
)

# Force the text to lowercase so it perfectly matches your dictionaries below
dim_statuses['order_status'] = dim_statuses['order_status'].str.lower()

# 2. Generate the Surrogate Primary Key (status_key: 1, 2, 3, 4)
dim_statuses['status_key'] = dim_statuses.index + 1

# 3. Define the accounting logic matrices using high-performance binary flags
# 1 = True (Apply math), 0 = False (Ignore math)
revenue_rules = {'delivered': 1, 'processing': 0,
                 'returned': 0, 'cancelled': 0}
cost_rules = {'delivered': 1, 'processing': 0, 'returned': 1, 'cancelled': 0}
refund_rules = {'delivered': 0, 'processing': 0, 'returned': 1, 'cancelled': 0}

# 4. Map the rules directly to create the new columns
dim_statuses['is_revenue_earned'] = dim_statuses['order_status'].map(
    revenue_rules)
dim_statuses['is_cost_realized'] = dim_statuses['order_status'].map(cost_rules)
dim_statuses['is_refunded'] = dim_statuses['order_status'].map(refund_rules)

# 5. Reorder for a clean, professional database schema layout
dim_statuses = dim_statuses[[
    'status_key',
    'order_status',
    'is_revenue_earned',
    'is_cost_realized',
    'is_refunded'
]]

# --- VERIFICATION PRINT ---
print("📊 'dim_statuses' successfully engineered for the database layer:")
print(dim_statuses.to_string(index=False))


# STEP 6: FACT TABLE

# 1. Start with a fresh base from your cleaned data
fact_sales = df_cleaned.copy()

# 2. Case Standardization Safeguard
# Force the order_status strings to lowercase so they match our new dim_statuses table perfectly
fact_sales['order_status'] = fact_sales['order_status'].str.lower()


# 3. Sequential Bridging: Merge the surrogate keys from every dimension table
# This maps descriptive attributes to optimized relational integer keys

# Map Geography ID (Matches on both region and country hierarchy)
fact_sales = fact_sales.merge(
    dim_geography, on=['region', 'country'], how='left')

# Map Product ID (Matches on the unique product name)
fact_sales = fact_sales.merge(dim_products, on='product_name', how='left')

# Map Shipping ID (Matches on the courier method and delivery duration)
fact_sales = fact_sales.merge(
    dim_shipping, on=['shipping_method', 'shipping_days'], how='left')

# Map Status ID (Matches on the e-commerce transaction state)
fact_sales = fact_sales.merge(dim_statuses, on='order_status', how='left')


# 4. Final Column Selection & Alignment
# We isolate ONLY the ID hashes, foreign relational keys, and numeric measurements.
# All descriptive text strings are explicitly dropped because they live in the dimensions.
fact_columns = [
    'order_id',
    'customer_id',       # Business ID acting as the direct link to dim_customers
    'product_key',      # Relational key linking to dim_products
    'geography_key',    # Relational key linking to dim_geography
    'shipping_key',     # Relational key linking to dim_shipping
    'status_key',       # Relational key linking to dim_statuses
    'order_date',       # Shared calendar grain column
    'unit_price',
    'quantity',
    'discount',
    'revenue',
    'cost',
    'profit',
    'profit_margin_pct',
    'shipping_cost'
]

# Lock in the chosen columns and reset index structure
fact_sales = fact_sales[fact_columns].reset_index(drop=True)


print("--- PIPELINE CHECKLIST ---")

print(f"✅ dim_customers created! Rows: {len(dim_customers)}")
print(f"✅ dim_geography created! Rows: {len(dim_geography)}")
print(f"✅ dim_products created!  Rows: {len(dim_products)}")
print(f"✅ dim_shipping created!  Rows: {len(dim_shipping)}")
print(f"✅ dim_calendar created!  Rows: {len(dim_calendar)}")
print(f"✅ dim_statuses created!  Rows: {len(dim_statuses)}")
print(f"✅ fact_sales created!    Rows: {len(fact_sales)}")

print("--------------------------")
print("Everything is built and ready for the database")


### Saving data and connecting to PostpreSQL
# Step 1: Save to CSV
dim_customers.to_csv('dim_customers.csv', index=False)
dim_geography.to_csv('dim_geography.csv', index=False)
dim_products.to_csv('dim_products.csv', index=False)
dim_shipping.to_csv('dim_shipping.csv', index=False)
dim_calendar.to_csv('dim_calendar.csv', index=False)
dim_statuses.to_csv('dim_statuses.csv', index=False)
fact_sales.to_csv('fact_sales.csv', index=False)

print("💾 All 7 CSV files saved locally!")
