---
source_id: class2
model: gemma4:e2b
review_status: pending
---

# APIs and Backends

The backend is the core of an application, handling logic, security, and data management, while APIs act as agreements between systems that allow interaction with the backend.

## Key points

- The backend is the brain behind the app, deciding actions, enforcing rules, and protecting secrets, unlike the frontend which is what the user sees.
- The backend performs functions such as validating requests, applying business rules, reading and writing data, calling external services, and returning a response.
- APIs are an agreement between systems defining what callers can send and what they can rely on receiving, and they should evolve with compatibility and migration paths.
- HTTP methods like GET (read data), POST (create data), PUT (update data), and DELETE (remove data) communicate intent in API design.

## Sources

- [[Sources/class2#Backend: The Brain Behind the App|Backend: The Brain Behind the App]]
- [[Sources/class2#APIs: The Waiter Metaphor|APIs: The Waiter Metaphor]]
- [[Sources/class2#An API is an Agreement Between Systems|An API is an Agreement Between Systems]]
- [[Sources/class2#HTTP Methods|HTTP Methods]]

## Related notes

- [[Localhost and Deployment]] — Where a backend runs and how users reach it
- [[Retrieval Augmented Generation]] — Interfaces connecting the model and retrieval tool
