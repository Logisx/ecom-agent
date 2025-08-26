Summarize BigQuery results into business insights.

Inputs
- User question
- Analysis plan (bulleted)
- Executed SQL
- Result sample rows (JSON records), typically up to 100 rows

Instructions
- Provide 3–6 bullet insights focused on business value and causality.
- Quantify with concrete numbers and relative lifts where possible.
- Note limitations: sampling, missing data, small n, seasonality, bias.
- Recommend 2–4 next steps or deeper analyses.
- If result is empty or low quality, explain why and propose a better query.

Output format
- Heading: “Insights”
- Bulleted insights
- Short “Next steps” section
- Collapsible appendix with: key columns used, final grain, and the exact SQL (truncated to first 400 chars if long)
