# Local Architecture

ContextOS Core v1.0 is a local-first CLI system.

It stores documents and chunks in SQLite, retrieves chunks with BM25, and builds prompts from selected local context.

## Question Flow

Question -> BM25 Retriever -> Token Budget Selector -> Context Builder -> AI Adapter -> Response

## Indexing Flow

Reader -> Parser -> Indexer -> Compression -> Memory
