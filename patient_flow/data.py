from google.oauth2 import service_account
import pandas as pd
# from pandas.io import gbq #bigquery
import pandas_gbq

# def load_and_prepare_data():
#     data = pd.read_csv('patient_flow_test.csv')
#     return data

def load_with_bigquery(query):
    # Path to your service account key file
    key_path = 'autonomous-gist-424810-j8-7e79a590be48.json'

    # Set up authentication using the service account key file
    credentials = service_account.Credentials.from_service_account_file(key_path)

    try:
        return pandas_gbq.read_gbq(query, project_id='autonomous-gist-424810-j8', credentials=credentials)
    except:
        print('Error reading the dataset')

def load_with_bigquery_sankey():
    query = """
        SELECT *
        FROM (
            SELECT * FROM `filtered_data.patient_flow_linkID` 
            WHERE value > 200 --241 links
            ORDER BY value DESC
            )
        """

    return load_with_bigquery(query)

## example
# query = """
#     SELECT *
#     FROM
#     `physionet-data.mimiciv_hosp.transfers`
#     LIMIT
#     10
#     """

# df = load_with_bigquery(query)
# df.head()
