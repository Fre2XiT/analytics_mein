
## Execution

### Basic functional tests
```bash
pytest --cov-report term-missing --cov=src tests --log-cli-level=INFO -x
```

### Tests for integration
```bash
pytest tests/test_integration --log-cli-level=INFO -x
```

```bash
uvicorn main:app --env-file environment.txt --port 8008 --reload
```

```bash
panel serve src/analysis_101/query_presences_.ipynb --autoreload
```

```bash
streamlit run src/streamlit/app.py --server.port=8501 --server.address=0.0.0.0
```
