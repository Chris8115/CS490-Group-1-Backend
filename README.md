# CS490 Group 1 Backend

## Setup
- Create/activate python venv `python -m venv venv`
- (in venv) `pip install -r requirements.txt`
- `python app.py`
- Create the database `craze.db` by using the SQL files, `craze_schema.sql` and `craze_data.sql` in that order.
   - Alternatively, copy and paste `craze.db.bak` and rename it to `craze.db`.

> [!NOTE]  
> API documentation has been moved to SwaggerUI on `/apidocs` endpoint.

## Testing
- Run UI testing with `python -m pytest UI_Testing/`
- Run Unit tests with `pytest tests/ --cov=app --cov-report=term-missing -q`

### Add a dot below when you need to redeploy the frontend!
...
