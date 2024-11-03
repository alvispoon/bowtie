import pandas as pd
import re

# Load the Excel file
file_path = 'tech-assessment-2024sep-questio4-creative.xlsx'

# Read the Tracking Raw sheet
tracking_raw = pd.read_excel(file_path, sheet_name='Tracking Raw')

# Read the Campaign Raw sheet
campaign_raw = pd.read_excel(file_path, sheet_name='Campaign Raw')

# Function to extract the ad content from the URL
def extract_ad_content(url):
    content = re.search(r'Term\|([^|{}]+)', url)
    return content.group(1).strip() if content else ''

# Apply the function to extract ad content
campaign_raw['Ad Content'] = campaign_raw['Landing page'].apply(extract_ad_content)

# Adjust 'Session manual ad content' to remove the 'Term|' prefix if present
tracking_raw['Session manual ad content'] = tracking_raw['Session manual ad content'].apply(
    lambda x: x.replace('Term|', '').strip()
)

# Convert 'Month' in Campaign Raw from datetime to abbreviated month format
campaign_raw['Month'] = pd.to_datetime(campaign_raw['Month']).dt.strftime('%b')

# Define the chronological order for months
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Convert 'Month' columns to categorical with the defined order
campaign_raw['Month'] = pd.Categorical(campaign_raw['Month'], categories=month_order, ordered=True)
tracking_raw['Month'] = pd.Categorical(tracking_raw['Month'], categories=month_order, ordered=True)

# Output the full, ungrouped data to one Excel file
full_output_file_path = 'full_data_all_ad_content.xlsx'
campaign_raw.to_excel(full_output_file_path, index=False)

# Group Campaign Raw data by 'Ad Content' and 'Month' to sum 'Cost' and 'Clicks'
grouped_campaign = campaign_raw.groupby(['Ad Content', 'Month']).agg({
    'Cost': 'sum',
    'Clicks': 'sum'
}).reset_index()

# Group Tracking Raw data by 'Session manual ad content' and 'Month' to sum 'Event count'
grouped_tracking = tracking_raw.groupby(['Session manual ad content', 'Month']).agg({
    'Event count': 'sum'
}).reset_index()

# Perform a left outer join on 'Ad Content' and 'Session manual ad content'
merged_data = pd.merge(
    grouped_campaign,
    grouped_tracking,
    left_on=['Ad Content', 'Month'],
    right_on=['Session manual ad content', 'Month'],
    how='left'
)

# Calculate Lead CVR (Event count/Clicks) and Lead CPA (Cost/Event count)
merged_data['Lead CVR'] = merged_data['Event count'] / merged_data['Clicks']
merged_data['Lead CPA'] = merged_data['Cost'] / merged_data['Event count']

# Filter out rows where Cost, Clicks, and Event count are all zero
filtered_data = merged_data[~((merged_data['Cost'] == 0) & (merged_data['Clicks'] == 0) & (merged_data['Event count'] == 0))]

# Sort by 'Ad Content' and 'Month'
filtered_data.sort_values(by=['Ad Content', 'Month'], inplace=True)

# Output grouped data to another Excel file
grouped_output_file_path = 'grouped_data_all_ad_content.xlsx'
filtered_data.to_excel(grouped_output_file_path, index=False)

print(f"\nFull data exported to {full_output_file_path}")
print(f"Grouped data exported to {grouped_output_file_path}")