# CS490 Group 1 Backend

## Setup
- Create/activate python venv `python -m venv venv`
- (in venv) `pip install -r requirements.txt`
- `python app.py`
> [!IMPORTANT]  
> Only commit schema changes to the database `craze.db`, try not to add it to your commit otherwise since it is practically always changing since the entire database is in that file. It's intentionally not added to the `.gitignore` since it may be necessary sometimes. (Also, if you do make changes to the schema, add a backup like `craze.db.bak`)

> [!NOTE]  
> API documentation has been moved to SwaggerUI on `/apidocs` endpoint.
