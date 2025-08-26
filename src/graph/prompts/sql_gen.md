Generate one BigQuery Standard SQL query that implements the given analysis plan on `bigquery-public-data.thelook_ecommerce`.

Requirements
- Use fully-qualified table names.
- SELECT-only; no DDL/DML, temp tables, scripting, or external functions.
- Enforce safety and efficiency:
  - Default to last 12 months unless the plan explicitly requests otherwise.
  - Add `LIMIT 200` unless the plan requires more; prefer aggregated outputs.
  - Use appropriate time truncation: DATE_TRUNC or TIMESTAMP_TRUNC.
  - Explicitly state the grain with GROUP BY.
- Join guidance:
  - `order_items` joins to `products` on `order_items.product_id = products.id`.
  - `orders` may join to `order_items` on order id.
  - `orders` or `order_items` join to `users` on user/customer id where appropriate.
  - Avoid fan-out; ensure the final grain matches the plan.
- Use clear, aliased column names and comments for key steps.
- Prefer CAST with safe types if needed and handle NULLs explicitly.

Return only the SQL inside a single fenced code block labeled sql. No prose.
