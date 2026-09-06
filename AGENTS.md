# Codex Project Development Instructions

You are working on a Django / Django REST Framework project.

Your responsibility is not only to write code. You must first understand the requirement, inspect the existing repository, design the smallest appropriate solution, create an implementation plan, implement it carefully, test it, and verify the result.

---

# Development Workflow

For every substantial requirement, follow this sequence:

**Requirement
→ Repository Analysis
→ Architecture Analysis
→ Implementation Plan
→ Implementation
→ Testing
→ Verification**

Do not immediately start coding for substantial features.

For small, isolated bug fixes, the workflow may be shortened, but you must still inspect the relevant existing code before making changes.

---

# 1. Requirement Analysis

When receiving a new requirement:

1. Read the complete requirement.
2. Inspect the existing repository.
3. Identify which Django app owns the functionality.
4. Search for related:
   - Models
   - Managers / QuerySets
   - Serializers
   - Views / ViewSets
   - URLs / Routers
   - Services
   - Permissions
   - Signals
   - Tasks
   - Utilities
   - Tests

5. Identify existing functionality that can be reused.
6. Identify business rules and edge cases.
7. Identify potential database, security, permission, performance, and concurrency implications.
8. Do not create duplicate functionality when equivalent logic already exists.

Create or update:

`.agents/requirements/current_requirement.md`

The requirement document should contain:

- Original requirement
- Technical interpretation
- Business rules
- Expected behavior
- Edge cases
- Assumptions
- Dependencies
- Open questions, if any

If uncertainty can be resolved by inspecting the repository, inspect the repository instead of asking the user.

Only ask the user when a genuine business or product decision cannot be determined from the repository or requirement.

---

# 2. Repository and Architecture Analysis

Before designing the solution, understand the relevant existing architecture.

Determine:

- Which Django app owns the feature
- Existing models involved
- Model relationships
- Existing APIs
- Existing serializers
- Existing permissions
- Existing services/business logic
- Existing query patterns
- Existing tests
- Existing project conventions

## Django Feature Application Architecture

This project uses a layered Django application architecture.

For non-trivial feature applications, use the following structure by default:

apps/<feature>/
├── migrations/
├── tests/
├── **init**.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── selectors.py
├── services.py
├── repositories.py
├── permissions.py
├── urls.py
└── views.py

Responsibilities:

### models.py

Contains:

- database schema
- model fields
- relationships
- enums / choices
- simple model invariants

Do not place large business workflows in models.

### selectors.py

Contains read/query logic.

Examples:

- list queries
- retrieve queries
- filters
- annotations
- `select_related()`
- `prefetch_related()`
- optimized read operations

Complex or reusable ORM read logic should not be duplicated in views.

### services.py

Contains business logic and application use cases.

Examples:

- create workflows
- update workflows
- state transitions
- multi-model operations
- transactional operations
- concurrency-sensitive operations

Views should call services instead of implementing business workflows directly.

### repositories.py

Contains reusable persistence operations when database write/read abstraction is useful.

Examples:

- reusable object creation
- reusable update operations
- persistence helpers
- database operations shared by multiple services

Do not use repositories merely to wrap every trivial ORM call.

### serializers.py

Contains:

- request validation
- response representation
- serializer-specific validation

Do not place substantial business workflows in serializers.

### permissions.py

Contains reusable authorization and object-access rules.

### views.py

Views must remain thin.

Views should primarily:

1. validate HTTP input
2. invoke selectors/services
3. return HTTP responses

Avoid complex ORM queries and business logic directly inside views.

### urls.py

Routing only.

## Architecture Enforcement

For every new non-trivial feature app, Codex should consider:

- `selectors.py`
- `services.py`
- `repositories.py`
- `permissions.py`

as part of the default architecture.

If one of these files is intentionally unnecessary for a very small feature,
the implementation plan should explain why before omitting it.

Update when necessary:

`.agents/architecture/project_architecture.md`

---

# 3. Planning

Before substantial implementation, create or update:

`.agents/plans/implementation_plan.md`

Include:

## Objective

What needs to be achieved.

## Existing Implementation

Relevant existing behavior and architecture.

## Proposed Solution

The technical approach and why it fits the existing project.

## Files to Modify

List the expected files.

## Database Changes

Document:

- Model changes
- Migrations
- Constraints
- Indexes
- Data migrations

If none:

`No database changes required.`

## API Changes

Document:

- Endpoint
- HTTP method
- Request structure
- Response structure
- Permissions
- Validation
- Error cases

## Concurrency Considerations

Determine whether concurrent requests could:

- Modify the same record
- Cause lost updates
- Create duplicate records
- Oversell/decrement stock incorrectly
- Process the same operation twice
- Produce invalid state transitions

Specify whether the implementation requires:

- `F()`
- `transaction.atomic()`
- `select_for_update()`
- Database constraints
- Idempotency protection

## Implementation Steps

Break implementation into small logical phases.

## Risks

Consider:

- Backward compatibility
- Data integrity
- Concurrency
- Permissions
- Security
- Performance
- Migration safety
- API compatibility

---

# 4. Implementation

After planning:

1. Implement one logical phase at a time.
2. Make the smallest necessary change.
3. Follow existing project conventions.
4. Reuse existing functionality where appropriate.
5. Avoid unrelated refactoring.
6. Avoid changing public behavior unless required.
7. Test each meaningful change before continuing.
8. Keep the implementation focused on the current requirement.

Do not rewrite working code simply because another implementation might look cleaner.

---

# 5. Django ORM and Database Rules

## Query Optimization

Use `select_related()` for:

- ForeignKey
- OneToOneField

when related objects will be accessed.

Use `prefetch_related()` for:

- ManyToManyField
- Reverse ForeignKey
- Other multi-valued relationships

when related collections will be accessed.

Avoid N+1 queries.

Do not add `select_related()` or `prefetch_related()` blindly. Only fetch relationships that are actually required.

---

## F Expressions

Use `F()` expressions when updates should happen directly at the database level and concurrent modifications could otherwise cause lost updates.

Example:

```python
Product.objects.filter(pk=product_id).update(
    stock=F("stock") - quantity
)
```

Prefer `F()` when the operation can safely be expressed as a database-side update.

---

## Transactions

Use `transaction.atomic()` when multiple database operations must succeed or fail as one unit.

Example situations:

- Stock transfer
- Payment processing
- Order creation with related records
- Multi-model updates
- State transitions involving multiple writes

Keep transactions as short as reasonably possible.

Do not perform unnecessary external/network operations while holding a database transaction open.

---

## Row-Level Locking

Use `select_for_update()` when a workflow requires:

**Read → Validate Current State → Modify**

and another concurrent request must not modify the same row before the operation finishes.

`select_for_update()` must be used inside an active transaction.

Example:

```python
from django.db import transaction


@transaction.atomic
def deduct_stock(product_id, quantity):
    product = (
        Product.objects
        .select_for_update()
        .get(pk=product_id)
    )

    if product.stock < quantity:
        raise ValueError("Insufficient stock")

    product.stock -= quantity
    product.save(update_fields=["stock"])
```

Consider `select_for_update()` for operations such as:

- Inventory deduction
- Stock transfers
- Order processing
- Payment state transitions
- Invoice processing
- Sequential numbering
- Preventing duplicate processing
- Critical state transitions

Do not use `select_for_update()` for ordinary reads.

Before using row locking, consider whether an atomic database update, `F()` expression, conditional update, or database constraint can solve the problem more simply.

---

# 6. Database Integrity

Do not rely only on Python validation when the database can enforce an important invariant.

Consider appropriate:

- `UniqueConstraint`
- `CheckConstraint`
- Foreign key constraints
- Database indexes

Use database constraints for critical integrity rules where appropriate.

Validate at the application layer as well when a useful API error message is required.

---

# 7. API and DRF Rules

Use proper HTTP semantics.

Typical methods:

- `GET` → retrieve
- `POST` → create/action
- `PUT` → full replacement
- `PATCH` → partial update
- `DELETE` → remove

Use appropriate HTTP status codes.

Examples:

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict`

Keep API error responses consistent with the existing project.

Do not expose internal exception details, stack traces, secrets, or sensitive implementation information through API responses.

---

# 8. Validation

Do not trust frontend validation.

Validate important rules on the backend.

Consider:

- Required fields
- Invalid values
- Duplicate records
- Object existence
- Object ownership
- Invalid relationships
- Impossible state transitions
- Quantity/range restrictions
- Business rules

Place validation at the appropriate layer.

Serializer-specific input validation belongs in serializers.

Complex multi-model business rules generally belong in the project's business/service layer when such a layer exists or is justified.

---

# 9. Permissions and Security

Authentication does not automatically mean authorization.

For every endpoint determine:

- Who can access it
- Who can create data
- Who can modify data
- Who can delete data
- Object ownership rules
- Role requirements
- Permission requirements

Reuse the existing permission system whenever possible.

Never hard-code secrets, passwords, API keys, tokens, or production credentials.

Never commit `.env` secrets.

Do not weaken existing authentication or permission checks simply to make a feature work.

---

# 10. Migration Safety

When modifying Django models:

1. Review the proposed model change.
2. Generate the migration.
3. Inspect the generated migration.
4. Determine its impact on existing data.
5. Check constraints and defaults.
6. Consider whether the migration could lock or rewrite a large table.
7. Run appropriate tests/checks.

Do not perform destructive data migrations unless explicitly required.

Do not delete existing production data to solve a migration problem.

---

# 11. Testing

Every significant feature or bug fix should include appropriate tests where practical.

Consider testing:

- Successful behavior
- Validation failures
- Authentication failures
- Permission failures
- Missing resources
- Invalid state transitions
- Edge cases
- Duplicate requests
- Concurrency-sensitive behavior

Run relevant existing tests first when useful.

After implementation run appropriate project checks.

For a standard Django project:

```bash
python manage.py check
python manage.py test
```

If the repository uses pytest or another test runner, follow the existing project configuration.

Do not replace the project's existing testing conventions unnecessarily.

---

# 12. Safety and Autonomy

You may automatically:

- Read repository files
- Search repository files
- Inspect Git history when useful
- Create project documentation
- Create implementation plans
- Modify source code related to the current requirement
- Create or modify tests
- Generate normal Django migrations
- Run Django checks
- Run tests
- Run formatting/linting tools already configured in the project
- Run `git status`
- Run `git diff`
- Run other non-destructive local development commands required to validate the implementation

You must ask before:

- Deleting files or directories
- Deleting significant database data
- Dropping tables
- Dropping databases
- Running destructive migrations
- Running Django `flush`
- Running destructive Git operations
- Running `git reset --hard`
- Running `git clean`
- Running `git push`
- Force pushing
- Deploying
- Modifying production infrastructure
- Modifying production databases
- Changing secrets or credentials
- Performing actions outside the repository
- Making significant unrelated architectural changes

Never perform a destructive operation simply because it is the easiest way to fix an error.

Diagnose the root cause first.

---

# 13. Scope Control

Stay within the requirement.

Do not:

- Refactor unrelated modules
- Rename unrelated files
- Change unrelated APIs
- Reformat the entire repository
- Upgrade unrelated dependencies
- Introduce unnecessary packages
- Introduce unnecessary architecture

If a broader change is genuinely necessary, explain why before expanding the implementation scope.

Prefer:

**Small, focused, reversible changes**

over:

**Large architectural rewrites**

---

# 14. Progress Tracking

Maintain:

`.agents/progress/implementation_progress.md`

Track:

## Completed

Tasks already completed.

## In Progress

Current implementation work.

## Remaining

Work still required.

## Files Changed

Files created or modified.

## Important Decisions

Record architectural or implementation decisions that will matter later.

## Validation Performed

Record tests, checks, or commands used to validate the implementation.

Update progress as meaningful implementation phases are completed.

---

# 15. Final Verification

Before declaring a requirement complete:

- Re-read the original requirement
- Verify every requirement is addressed
- Review changed files
- Check imports
- Check URLs and routing
- Check serializers
- Check validation
- Check permissions
- Check database queries
- Check for N+1 queries
- Check transaction boundaries
- Check concurrency implications
- Check migrations
- Check backward compatibility
- Check error handling
- Run relevant tests
- Run `python manage.py check`
- Review `git diff`
- Update implementation progress

Do not declare the work complete merely because the code runs.

The implementation is complete only when the requirement has been implemented, validated, and reviewed.

---

# 16. Core Principle

For substantial work, always follow:

**Understand → Inspect → Plan → Implement → Test → Verify**

Prefer existing project patterns over unnecessary invention.

Prefer database correctness over application assumptions.

Prefer explicit permissions over implicit trust.

Prefer safe concurrency handling over race conditions.

Prefer small changes over unnecessary rewrites.

Prefer root-cause fixes over temporary workarounds.
