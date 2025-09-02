import sys
import logging
import argparse
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

from src.services.big_query_runner import BigQueryRunner
from src.config.app_config_loader import AppConfigLoader
from src.graph.runner import run_chat_once

# To have logging before config is loaded
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logging.info("--- App started ---") 

def configure_logging(config: Dict[str, Any]) -> None:
    """
    Configure logging based on the provided configuration.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
    """
    log_config = config.get("logging", {})
    level = log_config.get("level", "INFO").upper()
    log_format = log_config.get("format", "%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    logging.basicConfig(level=level, format=log_format)

def print_table_schema(table_name: str, columns: List[Dict[str, Any]]) -> None:
    """
    Print the schema of a BigQuery table.

    Args:
        table_name (str): Name of the table.
        columns (List[Dict[str, Any]]): List of column definitions.
    """
    logging.info(f"Printing schema for table: {table_name}")
    print(f"\n=== Schema: {table_name} ===")
    for col in columns:
        name = col.get("name", "")
        col_type = col.get("type", "")
        mode = col.get("mode", "")
        desc = col.get("description", "") or ""
        print(f"- {name} ({col_type}, {mode}){': ' + desc if desc else ''}")

def cmd_check_bq(config: Dict[str, Any], tables_csv: Optional[str]) -> int:
    """
    Validate BigQuery access and show table schemas.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
        tables_csv (Optional[str]): Comma-separated table names to describe.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    bq_config = config.get("bigquery", {})
    try:
        runner = BigQueryRunner(project_id=bq_config.get("project_id"), dataset_id=bq_config.get("dataset_id"))
        logging.info("BigQuery client initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize BigQuery client: {e}")
        return 1

    try:
        logging.info(f"Listing tables in dataset: {runner.dataset_id}")
        tables_iter = runner.client.list_tables(runner.dataset_id)
        tables = sorted([t.table_id for t in tables_iter])
        print("\nTables in dataset:")
        for t in tables:
            print(f"- {t}")
    except Exception as e:
        logging.error(f"Failed to list tables: {e}")
        print("Hint: Verify the dataset id is in the form 'project.dataset'.")
        return 1

    target_tables = [t.strip() for t in (tables_csv or "orders,order_items,products,users").split(",") if t.strip()]
    for table in target_tables:
        try:
            schema = runner.get_table_schema(table)
            print_table_schema(table, schema)
        except Exception as e:
            logging.error(f"Failed to fetch schema for {table}: {e}")

    return 0

def build_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(description="EcomAgent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_bq = subparsers.add_parser("check-bq", help="Validate BigQuery access and show table schemas")
    check_bq.add_argument("--project", default=None, help="GCP project id (overrides config.yaml)")
    check_bq.add_argument("--dataset", default=None, help="Dataset id 'project.dataset' (overrides config.yaml)")
    check_bq.add_argument("--tables", default=None, help="Comma-separated table names to describe")
    check_bq.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging (overrides config.yaml)")

    chat = subparsers.add_parser("chat", help="Start a chat session with the Ecom agent")
    chat.add_argument("--project", default=None, help="GCP project id (overrides config.yaml)")
    chat.add_argument("--dataset", default=None, help="Dataset id 'project.dataset' (overrides config.yaml)")
    chat.add_argument("--model", default=None, help="Gemini model name (overrides config.yaml)")
    chat.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging (overrides config.yaml)")

    return parser

def main() -> None:
    """
    Main entry point for the EcomAgent CLI.
    """
    try:
        load_dotenv()
        logging.info("Environment variables loaded successfully.")
    except Exception as e:
        logging.warning(f"Failed to load environment variables: {e}")

    parser = build_parser()
    args = parser.parse_args()

    config_loader = AppConfigLoader()
    config = config_loader.merge_with_args(args)

    configure_logging(config)

    if args.command == "check-bq":
        exit_code = cmd_check_bq(config, args.tables)
        sys.exit(exit_code)
    elif args.command == "chat":
        agent_config = config.get("agent", {})

        print("EcomAgent ready. Type 'exit' to quit.\n")
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if user_input.lower() in {"exit", "quit"}:
                break

            try:
                answer = run_chat_once(
                    question=user_input,
                    agent_config=agent_config,
                )
                print(f"Agent: {answer}\n")
            except Exception as e:
                logging.error(f"An error occurred during chat execution: {e}", exc_info=True)
                print(f"Error: {e}")
                continue
    else:
        parser.print_help()
        sys.exit(2)

if __name__ == "__main__":
    main()