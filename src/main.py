import argparse
import logging
import sys
from typing import List

from src.services.big_query_runner import BigQueryRunner

from src.graph.state import AgentState
from src.config.config_loader import ConfigLoader

import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from src.graph.runner import run_chat_once

def configure_logging(config: Dict[str, Any]) -> None:
    log_config = config.get("logging", {})
    level = log_config.get("level", "INFO").upper()
    log_format = log_config.get("format", "%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    logging.basicConfig(
        level=level,
        format=log_format,
    )

def print_table_schema(table_name: str, columns: List[dict]) -> None:
    print(f"\n=== Schema: {table_name} ===")
    for col in columns:
        name = col.get("name", "")
        col_type = col.get("type", "")
        mode = col.get("mode", "")
        desc = col.get("description", "") or ""
        print(f"- {name} ({col_type}, {mode}){': ' + desc if desc else ''}")


def cmd_check_bq(config: Dict[str, Any], tables_csv: str) -> int:
    configure_logging(config)
    bq_config = config.get("bigquery", {})
    try:
        runner = BigQueryRunner(project_id=bq_config.get("project_id"), dataset_id=bq_config.get("dataset_id"))
    except Exception as e:
        logging.error(f"Failed to initialize BigQuery client: {e}")
        return 1

    # List tables in dataset
    try:
        print(f"Using dataset: {runner.dataset_id}")
        tables_iter = runner.client.list_tables(runner.dataset_id)
        tables = sorted([t.table_id for t in tables_iter])
        print("\nTables in dataset:")
        for t in tables:
            print(f"- {t}")
    except Exception as e:
        print(f"Failed to list tables: {e}")
        print("Hint: Verify the dataset id is in the form 'project.dataset'.")
        return 1

    # Show schema for requested tables
    target_tables = [t.strip() for t in (tables_csv or "orders,order_items,products,users").split(",") if t.strip()]
    for table in target_tables:
        try:
            schema = runner.get_table_schema(table)
            print_table_schema(table, schema)
        except Exception as e:
            print(f"Failed to fetch schema for {table}: {e}")

    return 0


def build_parser() -> argparse.ArgumentParser:
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
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    config_loader = ConfigLoader()
    config = config_loader.merge_with_args(args)

    if args.command == "check-bq":
        exit_code = cmd_check_bq(config, args.tables)
        sys.exit(exit_code)
    elif args.command == "chat":
        configure_logging(config)
        # Ensure API key is present
        if not os.getenv("GOOGLE_API_KEY"):
            print("GOOGLE_API_KEY is not set.")
            sys.exit(1)
        
        bq_config = config.get("bigquery", {})
        agent_config = config.get("agent", {})

        # Simple REPL
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
                summary = run_chat_once(
                    question=user_input, 
                )
                print(f"Agent: {summary}\n")
            except Exception as e:
                logging.error(f"An error occurred during chat execution: {e}", exc_info=True)
                print(f"Error: {e}")
                continue
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()