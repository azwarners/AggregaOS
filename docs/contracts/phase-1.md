# Phase 1 contracts

These contracts define the smallest shared vocabulary needed to compose independently useful components. They are versioned as `v1` examples, not a promise that every field is mandatory for every deployment. A producer may omit unknown optional data; it must not claim a capability it cannot perform.

Machine-readable shapes live in [`../../schemas/v1/`](../../schemas/v1/): host inventory, application catalog, adapter result, and bounded execution request/result. The eight reference flows are collected in [`../../examples/v1/composition.json`](../../examples/v1/composition.json).

## Ownership

| Component | Owns |
| --- | --- |
| AggregaOS | Application catalog, presets, and install composition |
| Ladcemas | Control-plane orchestration and management-system adapters |
| Ansible | Default desired-state and configuration execution |
| Semaphore UI | Optional automation UI, API, inventory, and job system |
| Beszel | Optional lightweight host and resource monitoring |
| Grafana | Optional visualization and observability |
| Ysparr | AI transport and composition |
| Sidecaravan | Reusable capabilities and controlled invocation |
| OpenIPE | Productivity orchestration |
| Apmatia | Optional identity and continuity context |
| Execution engines (including Redless) | Their own execution loops |
| Third-party applications | Their business logic and data |

## Host identity and state

A host record uses a stable `host_id`; `name` is a display or network name. Platform, resource summary, roles, installed applications, services, revision, and integration references are optional when unavailable. `connectivity` records reachability or enrollment, not trust. Discovery or enrollment alone never authorizes an operation.

## Application catalog

An application entry has a stable `id`, upstream `source`, one or more supported `install_methods`, and explicitly declared capabilities. `dependencies`, `conflicts`, `services`, `configuration`, and integration references are descriptive metadata used for composition; they do not transfer ownership of application data or behavior to AggregaOS. Secrets are named by reference only, never embedded as values. Unsupported operations are listed explicitly.

Capabilities are operation names (`install`, `update`, `remove`, `verify`) with boolean support values. A consumer must treat a missing or false capability as unsupported. Integrations and adapters may add their own namespaced operations.

## Adapter results and errors

An adapter advertises its `type`, `version`, `availability`, supported operations, and authentication requirements. Each invocation returns a structured `status` (`succeeded`, `failed`, or `unavailable`), optional external resource identifiers/links, and a structured error on failure. Error `code` is machine-readable; `message` is for operators. Secrets and credential material must not appear in these records.

## Execution and AI boundaries

Each run has exactly one `loop_owner`. A coordinator can submit a bounded request to an execution engine and observe its result, but must not run a second agent loop around that same task. Requests state allowed tools, scope, and limits; the receiving runtime enforces tool authorization at invocation time. Prompt text is not an authorization boundary. Application/session permissions remain separate from host-administration permissions.

Identity context is optional and may be absent. Providers and runtimes advertise their real capabilities. Use the smallest transport that fits a component; HTTP is not a requirement for local or library integrations.

## Reference flows

The companion JSON examples demonstrate all eight phase 1 paths: direct Ansible installation; Ladcemas coordinating a Semaphore-backed Ansible change; Beszel observation without desired-state authority; an optional Grafana dashboard; plain Ysparr without Apmatia; an Apmatia-managed character context; a bounded Redless task with Redless owning its loop; and installing a third-party application without the AggregaOS stack. These examples are illustrative payloads, not requirements that every deployment install every integration.

## Evolution rule

Add fields when a real component or integration needs them. Keep component boundaries public and independently usable; a missing optional integration must not prevent direct use of another component.
