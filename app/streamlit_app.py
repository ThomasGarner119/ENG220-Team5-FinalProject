import streamlit as st
import pandas as pd
import numpy as np
import math
from pathlib import Path

# -----------------------------------------------------------------------------

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Food Production Emissions Dashboard',
    page_icon=':seedling:',
    layout='wide'
)

# -----------------------------------------------------------------------------

# load datasets

@st.cache_data
def get_food_data():

    DATA_FILENAME = Path(__file__).parent.parent/'data/Food_Production.csv'
    food_df = pd.read_csv(DATA_FILENAME)

    food_df.rename(columns={'Food product': 'Food_product'}, inplace=True)
    
    return food_df

food_df = get_food_data()

# -----------------------------------------------------------------------------

# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :seedling: Food Production Emissions Dashboard

Browse environmental impact data for various food products. Data is sourced from research on **Global Food System Emissions**.
'''

# Add some spacing
''
''

# --- Input Widgets ---

# 1. Select the Metric to compare
metric_cols = food_df.columns[1:] # All columns after 'Food_product' are metrics

# We'll default to 'Total emissions' if it exists, otherwise the first column
default_metric = 'Total emissions' if 'Total emissions' in metric_cols else metric_cols[0]
default_index = list(metric_cols).index(default_metric) if default_metric in metric_cols else 0

selected_metric = st.selectbox(
    'Which **Environmental Metric** would you like to compare?',
    metric_cols,
    index=default_index,
    help="Select a column to visualize and use for comparison metrics."
)

# 2. Select the Food Products
products = food_df['Food_product'].unique()

if not len(products):
    st.warning("No food products found in data. Please check your CSV file.")

# Set a few default products for a good initial view
default_selection = [p for p in ['Beef (beef herd)', 'Cheese', 'Tofu', 'Oatmeal'] if p in products]

selected_products = st.multiselect(
    'Which **Food Products** would you like to view?',
    products,
    default_selection
)

''
''
''

# --- Visualization ---

# Filter the data
filtered_food_df = food_df[
    (food_df['Food_product'].isin(selected_products))
].sort_values(by=selected_metric, ascending=False) # Sort by the selected metric

st.header(f'Comparison of {selected_metric}', divider='gray')

''

# Create a bar chart for comparison
if not filtered_food_df.empty:
    chart_df = filtered_food_df[['Food_product', selected_metric]].set_index('Food_product')
    
    st.bar_chart(
        chart_df,
        y=selected_metric,
        use_container_width=True
    )
else:
    st.info("Please select at least one food product to display the chart.")

''
''

# --- Metrics ---

st.header(f'Highest Impact Products for {selected_metric}', divider='gray')

if not filtered_food_df.empty:
    # Get the top 3 (or fewer if less than 3 are selected)
    top_products = filtered_food_df.head(3)
    
    cols = st.columns(3)

    for i, (index, row) in enumerate(top_products.iterrows()):
        with cols[i]:
            product_name = row['Food_product']
            metric_value = row[selected_metric]
            
            # Check for NaN and display a message if so
            if np.isnan(metric_value):
                st.metric(
                    label=product_name,
                    value='N/A',
                    delta_color='off'
                )
            else:
                # Format the value to 2 decimal places
                formatted_value = f'{metric_value:,.2f}'
                
                # The 'delta' can show the difference from the average of the selected products
                avg_value = filtered_food_df[selected_metric].mean()
                delta_value = metric_value - avg_value
                
                st.metric(
                    label=product_name,
                    value=formatted_value,
                    delta=f'{delta_value:,.2f} from Avg',
                    delta_color='inverse' if delta_value < 0 else 'normal'
                )
else:
    st.info("No products selected to calculate metrics.")
