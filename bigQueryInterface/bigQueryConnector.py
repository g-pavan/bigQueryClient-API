from google.cloud import bigquery
import pandas as pd

class BigQueryConnector:
    def __init__(self, project_id=None, dataset_id=None, table_id=None):
        self.client = None
        self.dataset = None
        self.table = None
        self.df = None

        # Initialize the connector with provided project, dataset, and table IDs
        if project_id and dataset_id and table_id:
            self.connect_to_project(project_id)
            self.connect_to_dataset(dataset_id)
            self.connect_to_table(table_id)

    def connect_to_project(self, project_id):
        self.client = bigquery.Client(project=project_id)

    def connect_to_dataset(self, dataset_id):
        self.dataset = self.client.dataset(dataset_id)

    def connect_to_table(self, table_id):
        if self.dataset is None:
            raise Exception("Dataset should be connected before the table")
        self.table = self.dataset.table(table_id)

    def get_table_data_as_dataframe(self, limit=None):
        if self.table is None:
            raise Exception("Table is not connected")
        
        if self.df is not None:
            if limit is not None:
                return self.df.head(limit)
            return self.df
        
        query_job = self.client.list_rows(self.table)

        self.df = query_job.to_dataframe()

        if limit is not None:
            return self.df.head(limit)

        return self.df