# L-E-COURS deployment notes

## Frontend — Cloudflare Pages
Build command: `npm run build`  
Build output directory: `dist`  
Root directory: `frontend`  
Environment variable: `VITE_API_BASE_URL=https://YOUR-API-DOMAIN/api`

## Backend — Django host
Install `backend/requirements.txt`, configure WSGI to point to `config.wsgi.application`,
set environment variables from `.env.example`, run migrations, and run `collectstatic`.
Set `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, correct `DJANGO_ALLOWED_HOSTS`,
and `CORS_ALLOWED_ORIGINS` to the deployed frontend origin. Serve the API only over HTTPS.

## PostgreSQL / Supabase
Use the server-side PostgreSQL connection string as `DATABASE_URL`. Never place it in
frontend variables. Confirm the chosen hosting plan can reach the database host and port.
Use provider-recommended connection settings and SSL requirements.

## Object storage
For production uploads, use a private S3-compatible bucket. Supabase Storage can be
configured through the S3-compatible endpoint using the backend-only variables documented
in the main README. Keep credentials out of React and Git. Configure bucket CORS for the
frontend origin if browser downloads follow signed URLs.

## PythonAnywhere caution
Before choosing the Free plan, verify current outbound database/network access and
custom-domain/WSGI restrictions against PythonAnywhere's current documentation.
Do not assume every external PostgreSQL endpoint is reachable from every plan.

## Google Drive
No OAuth credentials are included. Do not paste service account keys or OAuth secrets into
the frontend or commit them to Git. Implement OAuth and permissions only after choosing
the account ownership/consent flow.
