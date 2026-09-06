# Current Requirement

## Original requirement

Create a Django template that searches products through Elasticsearch, displays dropdown suggestions, and opens product details when a suggestion is clicked.

## Technical interpretation

- Add a server-rendered product search page.
- Add an Elasticsearch-backed JSON suggestion endpoint.
- Add a product detail page using the selected Elasticsearch document ID.
- Keep views thin by placing reads in a selector module.

## Business rules and expected behavior

- Search begins after two characters and returns at most eight suggestions.
- Suggestions search product names and categories, favoring name matches.
- Clicking a suggestion opens the corresponding active Django product.
- Elasticsearch outages return a controlled 503 JSON response.

## Edge cases

- Empty or one-character queries return no results without contacting Elasticsearch.
- Missing/deleted products return 404.
- Stale browser requests are cancelled while typing.

## Assumptions

- Search and detail pages are public because no product-specific authorization rule exists.

## Dependencies

- Existing Product model, ProductDocument, Django templates, and Elasticsearch service.

## Open questions

None.
