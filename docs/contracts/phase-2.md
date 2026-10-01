# Phase 2: application catalog and Ansible foundation

The machine-readable catalog lives in [`../../catalog/v1/index.json`](../../catalog/v1/index.json). Each entry is a standalone JSON document validated by [`../../schemas/v1/application.schema.json`](../../schemas/v1/application.schema.json). The contract names supported platforms and deployment methods separately: Ansible is the current Ubuntu implementation, and OCI containers are used only by applications that advertise that method.

The catalog records ownership, upstream, version/reference, platform support, dependencies, conflicts, service endpoints, persistent data paths, configuration and secret references, operations, optional integrations, and known unsupported operations. A blocked entry stays discoverable while reporting that it has no supported installer. Catalog consumers do not need to import application code or inspect playbooks.

## Direct Ansible use

Install Ansible Core on the Ubuntu control machine (for example, `sudo apt install ansible-core`) and Podman only for the container-backed applications. Copy `ansible/inventory.ini.example` to `ansible/inventory.ini`, remove groups you do not use, and replace example hosts with the intended Ubuntu targets. The normal server roles require Ubuntu 24.04 or later. TroubleShell is a desktop application and currently targets Ubuntu 26.04; keep it in the separate `[desktop]` group. Run commands from the `ansible/` directory so `ansible.cfg` resolves the local roles:

```sh
cd ansible
ansible-playbook -i inventory.ini playbooks/memos.yml
```

`playbooks/site.yml` installs every catalog entry with an implemented Ansible path. It includes all three listed AI applications (llama.cpp, ComfyUI, and LocalLightChat), along with the productivity, automation, and monitoring candidates. It omits Ladcemas and Sidecaravan, whose current upstream repositories do not contain installable application code. Add the `[desktop]` workstation when running the site playbook.

Each supported application has its own playbook. For example, run Ysparr directly with `playbooks/ysparr.yml`; Semaphore, Grafana, and Ysparr credentials are supplied through Ansible Vault variables, never catalog fields or committed defaults. No Semaphore UI, Beszel, Grafana, or Ladcemas service is required to run Ansible.

Container services bind to loopback by default. Configure a separately managed reverse proxy or firewall before exposing an endpoint to another host. Application removal stops the service and removes Aggregare's unit/configuration. Persistent data directories are preserved unless an operator removes them separately. The llama.cpp role builds the CPU server and leaves its service stopped until a model file is supplied under `/var/lib/aggregare/llama.cpp/models`; ComfyUI also uses CPU mode and does not download model weights.

Applications without a long-running service are installed and checked as Python packages. Redless still needs an OpenAI-compatible model server and a repository/workspace to perform tasks; the Ansible role does not grant it host-wide execution authority.

## Verification status

The Ysparr role checks `GET /health`; container roles check the application's configured HTTP endpoint after systemd starts it. Successful runs write `/var/lib/aggregare/status/<application-id>.json`, conforming to [`../../schemas/v1/application-status.schema.json`](../../schemas/v1/application-status.schema.json). The status contains application/version/deployment identifiers and verification outcome, never secret values.

Catalog status `supported` means the repository contains a direct Ansible entry point and verification path. `experimental` signals an install path still subject to platform/upstream limits. `blocked` means there is no usable upstream installer yet. Optional integrations remain optional catalog metadata and never become dependencies of the catalog itself.
