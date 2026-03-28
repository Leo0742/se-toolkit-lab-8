name observability
description Use observability MCP tools for logs and traces
always true

Use observability MCP tools when the user asks about recent errors, failures, traces, logs, or debugging.

Reasoning flow:
  * For error questions, call mcp_obs_logs_error_count first.
  * If there are recent errors, call mcp_obs_logs_search to inspect the matching log lines.
  * If a useful trace_id appears in logs, call mcp_obs_traces_get for that trace.
  * Summarize findings briefly. Do not dump raw JSON.

Important field mapping:
  * For LMS backend questions, service_name is "Learning Management Service".
  * Prefer recent windows from the user question, for example 10 minutes.

Available tools and when to use them:
  * mcp_obs_logs_search: inspect recent log lines and extract event, severity, message, trace_id.
  * mcp_obs_logs_error_count: count recent errors per service.
  * mcp_obs_traces_list: list recent traces for one service.
  * mcp_obs_traces_get: inspect one trace by trace_id.
