# Implementation Plan

## Objective

Provide an Elasticsearch autocomplete UI with product detail navigation.

## Existing Implementation

The product model and populated Elasticsearch document exist, but there are no product routes, search views, selectors, or templates.

## Proposed Solution

Use a selector for a bounded `multi_match` phrase-prefix search, a thin JSON view for suggestions, and Django templates with debounced browser requests and safe DOM rendering.

## Files to Modify

- `apps/products/selectors.py`
- `apps/products/views.py`
- `apps/products/urls.py`
- `apps/products/templates/products/search.html`
- `apps/products/templates/products/detail.html`
- `apps/products/tests.py`
- `config/urls.py`
- Agent tracking documents

## Database Changes

No database changes required.

## API Changes

- `GET /products/` renders search.
- `GET /products/suggestions/?q=...` returns suggestion JSON.
- `GET /products/<id>/` renders product details.

## Concurrency Considerations

All operations are read-only; stale client requests are aborted.

## Implementation Steps

1. Add Elasticsearch and database selectors.
2. Add thin views and routes.
3. Add responsive search/detail templates.
4. Test and verify against the live index.

## Risks

- Elasticsearch and the relational database can temporarily diverge.
- Prefix matching on analyzed text is suitable for this dataset but a dedicated autocomplete analyzer may scale better.
