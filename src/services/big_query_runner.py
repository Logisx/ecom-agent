import logging
import pandas as pd
from typing import Optional, List, Dict, Any

from google.cloud import bigquery

logger = logging.getLogger(__name__)

class BigQueryRunner:
    """A lean BigQuery client for executing SQL queries and returning DataFrame results."""
    
    def __init__(self, project_id: Optional[str] = None, dataset_id: Optional[str] = "bigquery-public-data.thelook_ecommerce") -> None:
        """Initialize BigQuery client.
        
        Args:
            project_id: Google Cloud project ID. If None, uses default credentials.
            dataset_id: BigQuery dataset ID. If None, uses default dataset.
        """
        logger.info("Initializing BigQuery client")
        try:
            self.client = bigquery.Client(project=project_id)
            self.dataset_id = dataset_id
            logger.info(f"BigQuery client initialized for dataset: {self.dataset_id}")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {str(e)}")
            raise
    
    def execute_query(self, sql_query: str, job_config: bigquery.QueryJobConfig) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame.
        
        Args:
            sql_query: The SQL query to execute.
            
        Returns:
            DataFrame containing the query results.
            
        Raises:
            Exception: If query execution fails.
        """
        try:
            logger.info(f"Executing BigQuery query")
            query_job = self.client.query(sql_query, job_config=job_config)
            df = query_job.result().to_dataframe()
            logger.info(f"Query completed successfully, returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"BigQuery execution failed: {str(e)}")
            raise 

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a specific table.
        
        Args:
            table_name: Name of the table (orders, order_items, products, users).
            
        Returns:
            List of dictionaries containing column information.
        """
        try:
            table_ref = f"{self.dataset_id}.{table_name}"
            table = self.client.get_table(table_ref)
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or ""
                })
            logger.info(f"Retrieved schema for table {table_name}")
            return schema_info
        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {str(e)}")
            raise  


