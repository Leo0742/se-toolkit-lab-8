---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

Use LMS MCP tools for live LMS questions.

Available tools and when to use them:
- lms_health: use for backend health checks and item counts.
- lms_labs: use to list available labs and prepare lab choices.
- lms_learners: use when the user asks about learners.
- lms_pass_rates: use for pass rates for one lab.
- lms_timeline: use for submission timeline for one lab.
- lms_groups: use for group performance for one lab.
- lms_top_learners: use for top learners for one lab.
- lms_completion_rate: use for completion rate for one lab.
- lms_sync_pipeline: use when LMS data looks missing or stale.

Rules:
- If the user asks about scores, pass rates, completion, groups, timeline, or top learners and does not name a lab, call lms_labs first.
- If multiple labs are available, ask the user to choose one.
- Use each lab title as the default user-facing label unless the tool output gives a better identifier.
- Let the shared structured-ui skill decide how to present that choice on supported channels.
- Format percentages with a % sign.
- Format counts as whole numbers.
- Keep responses concise.
- When the user asks "what can you do?", clearly explain the current LMS tools and limits.
- Do not claim live LMS data unless it came from an lms_* tool in the current session.
