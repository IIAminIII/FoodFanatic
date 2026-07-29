# FoodFanatic restaurant management roadmap

## Product direction

FoodFanatic should grow from a customer ordering demo into a dependable restaurant
operations platform. Each phase below has a narrow goal and explicit completion
criteria so the system can remain deployable while it evolves.

## Phase 1 — Safety and order integrity (in progress)

Goal: make the current menu, cart, account, review, and ordering flows reliable.

- Move secrets and deployment settings to environment variables.
- Upgrade to the supported Django 5.2 LTS release line.
- Store immutable order-item snapshots instead of references to temporary carts.
- Make checkout atomic and preserve the price charged at checkout.
- Enforce user ownership on carts, orders, and profile updates.
- Use POST + CSRF protection for cart, checkout, and logout mutations.
- Validate menu prices, discounts, quantities, dates, emails, and review ratings.
- Permit reviews only after a non-cancelled purchase.
- Add automated tests for authorization, pricing, checkout, and record retention.
- Improve admin screens for day-to-day menu and order operations.

Acceptance: checks and tests pass; placing an order clears the cart without losing
the order lines; one user cannot mutate or view another user's records.

## Phase 2 — Core restaurant operations

Goal: support the work happening inside a restaurant.

- Restaurant/branch, service hours, tax profile, and currency settings.
- Dine-in, pickup, and delivery order types.
- Tables, seating, reservations, wait-list, and guest counts.
- Kitchen tickets with received, preparing, ready, served, and cancelled states.
- Menu modifiers (size, add-ons, cooking preference) and allergen information.
- Staff roles for owner, manager, cashier, server, kitchen, and delivery.

Acceptance: staff can take and fulfill an order from arrival to completion without
using Django admin or editing database records.

## Phase 3 — Inventory and purchasing

Goal: connect sales to food cost and stock.

- Ingredients, recipes, units, suppliers, and purchase orders.
- Stock receipts, consumption, waste, adjustments, and low-stock alerts.
- Automatic ingredient deduction when kitchen preparation begins.
- Cost-of-goods and menu-margin reporting.
- Branch-level inventory and stock transfers.

Acceptance: stock movement is auditable and each sold item has a reproducible food
cost.

## Phase 4 — Payments and customer experience

Goal: make ordering and payment production-ready.

- Tax, service charge, tips, coupons, refunds, and split payments.
- Payment-provider integration using idempotent webhooks.
- Guest checkout, saved addresses, order tracking, and receipts.
- Loyalty points, customer notes, promotions, and notification preferences.
- Versioned REST API for web/mobile clients.

Acceptance: payment state is reconciled independently from order state and retries
cannot double-charge or duplicate an order.

## Phase 5 — Reporting, governance, and scale

Goal: give operators control and production visibility.

- Shift opening/closing, cash drawer reconciliation, and daily sales summaries.
- Sales, tax, discount, void, staff performance, and inventory reports.
- Append-only audit log for sensitive staff and financial actions.
- Background jobs for email, exports, and integrations.
- PostgreSQL production deployment, backups, error tracking, metrics, and alerts.
- Accessibility, localization, multi-currency, performance, and load testing.

Acceptance: management can reconcile a business day, investigate every sensitive
change, restore backups, and monitor service health.

## Cross-cutting rules

- Financial values are `Decimal` snapshots, never floating-point calculations.
- Customer and staff access follows least privilege.
- Every state-changing web action is authenticated, authorized, and CSRF protected.
- Database constraints back up application validation.
- Migrations preserve existing data and include a rollback/recovery plan.
- Each phase ships with tests and operational documentation.
