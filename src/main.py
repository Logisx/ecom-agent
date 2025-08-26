import argparse
import logging
import sys
from typing import List

from big_query_runner import BigQueryRunner


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def print_table_schema(table_name: str, columns: List[dict]) -> None:
    print(f"\n=== Schema: {table_name} ===")
    for col in columns:
        name = col.get("name", "")
        col_type = col.get("type", "")
        mode = col.get("mode", "")
        desc = col.get("description", "") or ""
        print(f"- {name} ({col_type}, {mode}){': ' + desc if desc else ''}")


def cmd_check_bq(project: str, dataset: str, tables_csv: str, verbose: bool) -> int:
    configure_logging(verbose)
    try:
        runner = BigQueryRunner(project_id=project or None, dataset_id=dataset or None)
    except Exception as e:
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
    target_tables = [t.strip() for t in tables_csv.split(",") if t.strip()]
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
    check_bq.add_argument("--project", default=None, help="GCP project id (optional; uses ADC default if omitted)")
    check_bq.add_argument("--dataset", default="bigquery-public-data.thelook_ecommerce", help="Dataset id 'project.dataset'")
    check_bq.add_argument("--tables", default="orders,order_items,products,users", help="Comma-separated table names to describe")
    check_bq.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "check-bq":
        exit_code = cmd_check_bq(args.project, args.dataset, args.tables, args.verbose)
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
