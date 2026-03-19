---
name: Use ABCs not concrete classes in endpoints
description: Always depend on abstract base classes (HypervisorProvider) in endpoints, not concrete implementations (ProxmoxProvider) directly
type: feedback
---

Never reference concrete infrastructure classes directly in endpoints — always go through the ABC (e.g. `HypervisorProvider`, not `ProxmoxProvider`).

**Why:** The user strongly prefers respecting the abstraction layers defined in `adaptive/api/infrastructure/base.py`. Endpoints should depend on the interface, concrete class is only used for instantiation.

**How to apply:** When adding new endpoints or services that use infrastructure providers, type on the ABC and only import the concrete class for construction.
