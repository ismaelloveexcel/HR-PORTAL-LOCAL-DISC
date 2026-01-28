# Azure App Settings (Backend & Frontend)

## Backend (App Service → Configuration → Application settings)
- AUTH_SECRET_KEY = (long random string)
- PASSWORD_MIN_LENGTH = 8
- SESSION_TIMEOUT_MINUTES = 480
- DATABASE_URL = postgresql://<user>:<password>@hrportal-db-new.postgres.database.azure.com:5432/<dbname>?sslmode=require
- (optional) APPLICATIONINSIGHTS_CONNECTION_STRING = (auto-added when Application Insights is ON)

**Startup command** (General Settings):
sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

## Frontend (Static Web Apps → Configuration)
- VITE_API_BASE_URL = https://hrportal-backend-new.azurewebsites.net/api
