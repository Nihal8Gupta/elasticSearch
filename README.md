# elasticSearch

Elastic search

## Development

Activate the environment:

    .\env\Scripts\Activate.ps1

Run Django development server:

    python manage.py runserver

Run Daphne when enabled:

    daphne -b 0.0.0.0 -p 8000 config.asgi:application

Run Docker when enabled:

    docker compose up --build

Elasticsearch is available from the host at `http://localhost:9200` and from
the Django container at `http://elasticsearch:9200`.

## Codex

Development instructions:

    AGENTS.md

Current requirement:

    .agents/requirements/current_requirement.md

Implementation plan:

    .agents/plans/implementation_plan.md

Progress:

    .agents/progress/implementation_progress.md

Shared infrastructure:

    apps/common/

JWT endpoints when enabled:

    POST /api/token/
    POST /api/token/refresh/
    POST /api/token/blacklist/

Swagger/OpenAPI when enabled:

    /api/schema/
    /api/docs/
    /api/redoc/
