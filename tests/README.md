# Test Suite

This directory contains tests for the compliance orchestrator application.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_tools.py        # Tests for BigQuery tools (fetch_transaction_by_id)
│   ├── test_prompts.py      # Tests for prompt templates
│   └── test_sub_agents_utils.py  # Tests for sub-agent utilities
├── integration/             # Integration tests for agent workflows
│   ├── test_agent.py
│   └── test_agent_engine_app.py
└── load_test/               # Load testing scripts
    └── load_test.py
```

## Running Tests

### All Tests
```bash
make test
```

### Unit Tests Only
```bash
uv run pytest tests/unit
```

### Integration Tests Only
```bash
uv run pytest tests/integration
```

## Test Coverage

### Unit Tests (`tests/unit/`)

#### `test_tools.py`
Tests for the BigQuery transaction fetching tool:
- `test_fetch_transaction_by_id_found` - Verifies successful transaction retrieval
- `test_fetch_transaction_by_id_not_found` - Handles missing transactions
- `test_fetch_transaction_by_id_error` - Handles BigQuery errors

#### `test_prompts.py`
Tests for agent prompt templates:
- `test_root_orchestrator_prompt_exists` - Validates orchestrator prompt
- `test_root_orchestrator_prompt_contains_key_instructions` - Checks key content
- `test_transaction_agent_prompt_exists` - Validates transaction agent prompt
- `test_transaction_agent_prompt_contains_key_instructions` - Checks key content

#### `test_sub_agents_utils.py`
Tests for sub-agent utility functions:
- `test_store_analysis_in_bigquery_update_existing` - Tests analysis storage (update)
- `test_store_analysis_in_bigquery_insert_new` - Tests analysis storage (insert)
- `test_store_analysis_in_bigquery_error` - Handles storage errors
- `test_update_approval_status_success` - Tests approval status updates
- `test_update_approval_status_error` - Handles update errors
- `test_store_analysis_strips_whitespace` - Validates whitespace handling

## Notes

- Unit tests use mocking to avoid requiring actual BigQuery credentials
- Tests follow Google Python style guide
- All tests include proper error handling validation
