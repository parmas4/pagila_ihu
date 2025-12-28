#!/usr/bin/env python
# coding: utf-8

# # Setup - Install Libraries

# In[ ]:


# Run the following commands once, in order to install libraries - DO NOT Uncomment this line.

# Uncomment below lines

# !pip3 install --upgrade pip
# !pip install google-cloud-bigquery
# !pip install pandas-gbq -U
# !pip install db-dtypes
# !pip install packaging --upgrade


# # Import libraries

# In[1]:


# Import libraries
from google.cloud import bigquery
import pandas as pd
from pandas_gbq import to_gbq
import os

print('Libraries imported successfully')


# In[2]:


# Set the environment variable for Google Cloud credentials
# Place the path in which the .json file is located.

# Example (if .json is located in the same directory with the notebook)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "at-arch-416714-6f9900ec7.json"

# -- YOUR CODE GOES BELOW THIS LINE
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\AΘΑΝΑΣΙΑ\\Documents\\script\\smart-column-479018-r8-2adac0889c5a.json" # Edit path
# -- YOUR CODE GOES ABOVE THIS LINE


# In[3]:


# Set your Google Cloud project ID and BigQuery dataset details

# -- YOUR CODE GOES BELOW THIS

project_id = 'smart-column-479018-r8' # Edit with your project id
dataset_id = 'reporting_db' # Modify the necessary schema name: staging_db, reporting_db etc.
table_id = 'rep_revenue_per_period' # Modify the necessary table name: stg_customer, stg_city etc.

# -- YOUR CODE GOES ABOVE THIS LINE


# # SQL Query

# In[4]:


# Create a BigQuery client
client = bigquery.Client(project=project_id)

# -- YOUR CODE GOES BELOW THIS LINE

# Define your SQL query here
query = """
with revenue_data as (
  select 
    p.payment_date,
    p.payment_amount as amount 
  from smart-column-479018-r8.staging_db.stg_payment p
  left join smart-column-479018-r8.staging_db.stg_rental r 
    on p.rental_id = r.rental_id
  left join smart-column-479018-r8.staging_db.stg_inventory i 
    on r.inventory_id = i.inventory_id
  left join smart-column-479018-r8.staging_db.stg_film f 
    on i.film_id = f.film_id
  where f.film_title != 'GOODFELLAS SALUTE' 
)

, reporting_dates as (
  select *
  from smart-column-479018-r8.reporting_db.reporting_periods_table
  where reporting_period in ('Day', 'Month', 'Year')
)

, revenue_per_period as (
  select
    'Day' as reporting_period
    , date(date_trunc(rd.payment_date, day)) as reporting_date
    , sum(rd.amount) as total_revenue
  from revenue_data rd
  group by 1,2
  union all
  select
    'Month' as reporting_period
    , date(date_trunc(rd.payment_date, month)) as reporting_date
    , sum(rd.amount) as total_revenue
  from revenue_data rd
  group by 1,2
  union all
  select
    'Year' as reporting_period
    , date(date_trunc(rd.payment_date, year)) as reporting_date
    , sum(rd.amount) as total_revenue
  from revenue_data rd
  group by 1,2
)

, final as (
  select 
    reporting_dates.reporting_period
    , reporting_dates.reporting_date
    , coalesce(revenue_per_period.total_revenue, 0) as total_revenue
  from reporting_dates
  left join revenue_per_period
    on reporting_dates.reporting_period = revenue_per_period.reporting_period
    and reporting_dates.reporting_date = revenue_per_period.reporting_date
)

select * from final
order by reporting_period, reporting_date
"""

# -- YOUR CODE GOES ABOVE THIS LINE

# Execute the query and store the result in a dataframe
df = client.query(query).to_dataframe()

# Explore some records
df.head()


# # Write to BigQuery

# In[5]:


# Define the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# -- YOUR CODE GOES BELOW THIS LINE
# Define table schema based on the project description

schema = [
    bigquery.SchemaField('reporting_period', 'STRING'),
    bigquery.SchemaField('reporting_date', 'DATE'),
    bigquery.SchemaField('total_revenue', 'NUMERIC'),
    ]

# -- YOUR CODE GOES ABOVE THIS LINE


# In[6]:


# Create a BigQuery client
client = bigquery.Client(project=project_id)

# Check if the table exists
def table_exists(client, full_table_id):
    try:
        client.get_table(full_table_id)
        return True
    except Exception:
        return False

# Write the dataframe to the table (overwrite if it exists, create if it doesn't)
if table_exists(client, full_table_id):
    # If the table exists, overwrite it
    destination_table = f"{dataset_id}.{table_id}"
    # Write the dataframe to the table (overwrite if it exists)
    to_gbq(df, destination_table, project_id=project_id, if_exists='replace')
    print(f"Table {full_table_id} exists. Overwritten.")
else:
    # If the table does not exist, create it
    job_config = bigquery.LoadJobConfig(schema=schema)
    job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    job.result()  # Wait for the job to complete
    print(f"Table {full_table_id} did not exist. Created and data loaded.")


# In[2]:


# Below line converts your i.pynb file to .py python executable file. Modify the input and output names based
# on the table you are processing.
# Example:
# ! jupyter nbconvert stg_customer.ipynb --to python

# -- YOUR CODE GOES BELOW THIS LINE

get_ipython().system('python3 -m jupyter nbconvert stg_actor.ipynb --to python')

# -- YOUR CODE GOES ABOVE THIS LINE


# In[32]:


get_ipython().system('python3 -m pip install nbconvert')


# In[1]:


get_ipython().system('python3 -m pip install nbconvert -U')


# In[ ]:




