# MC-056 — Planning/native CI impact routing and campaign safety guard

Result: COMPLETED_RESEARCH on the MC-1 adoption branch; integration/issue closure waits for verified merge.

All twenty legacy RCS/native pull-request workflows are explicitly routed away from MC-1 planning-only paths and workflow-definition-only edits. The dedicated `mc1-static` workflow validates the new authority/task/registry contracts. `tools/validate_mc_ci_impact.py` checks the routing and mutation-tests failure when a required marker is removed.

This change does not disable native validation for edits to the historical native code paths. Future MC native implementation must add its own bounded task-specific native verification under the execution-permit contract. No native campaign or runner resize was dispatched by MC-056.
