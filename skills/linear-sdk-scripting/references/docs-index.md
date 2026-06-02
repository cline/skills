# Linear developer docs index

Fetch the specific page you need when you do not know an exact method, input, field, or filter name. Do not guess the schema; read the relevant page and use the names from it.

This skill uses the TypeScript SDK as the way to talk to Linear, not raw GraphQL. The SDK is a typed wrapper over the same GraphQL schema, so the filtering and pagination semantics and every field name are shared. That is why the schema-level references below are useful even though you are writing SDK calls.

## TypeScript SDK

- Getting started: https://linear.app/developers/sdk
- Fetching and modifying data: https://linear.app/developers/sdk-fetching-and-modifying-data
- Errors: https://linear.app/developers/sdk-errors
- Advanced usage (includes the raw GraphQL escape hatch, `linear.client.rawRequest`): https://linear.app/developers/advanced-usage
- SDK source on GitHub: https://github.com/linear/linear/tree/master/packages/sdk

## Shared API reference (the SDK mirrors this schema)

The SDK's `filter` objects, cursor pagination, and field names come straight from the GraphQL schema. Use these when a method, field, or filter name is unknown.

- Full GraphQL schema reference (every type, field, and filter): https://studio.apollographql.com/public/Linear-API/schema/reference?variant=current
- Filtering (the same filter syntax the SDK passes through): https://linear.app/developers/filtering
- Pagination (the model behind `fetchNext` / `pageInfo`): https://linear.app/developers/pagination

## Account settings (for the user)

- Create and manage personal API keys: https://linear.app/settings/account/security

## Which page to read for common needs

- "What SDK method creates / updates / fetches X" -> SDK fetching and modifying data.
- "How do I filter issues by X" -> Filtering, then the schema reference for the exact field.
- "How do I page through all results" -> Pagination.
- "What fields does an Issue / Project / Cycle have" -> schema reference.
- "There is no SDK method for what I need" -> Advanced usage, then drop to `linear.client.rawRequest(query, variables)` with a query built from the schema reference.
