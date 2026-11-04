<div align="center">

# L-E-COURS
### مكتبتك الجامعية، منظمة في مكان واحد.

**A public-first academic resource library powered by Django, React and Google Drive.**

![Version](https://img.shields.io/badge/version-1.5.0-2563eb?style=for-the-badge)
![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61dafb?style=for-the-badge&logo=react&logoColor=111827)
![Backend](https://img.shields.io/badge/backend-Django%20REST-0c4b33?style=for-the-badge&logo=django&logoColor=white)
![Database](https://img.shields.io/badge/database-PostgreSQL-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)

**Browse without an account · Organize by academic structure · Import from Google Drive**

</div>

---

## ✨ What is L-E-COURS?

L-E-COURS is an Arabic-first digital library designed to make academic files easy to discover, browse and access. It brings resources from multiple Google Drive folders into one consistent catalogue while keeping administration separate from the public experience.

Visitors can browse and access published resources without creating an account. Administrators sign in only when they need to connect Drive sources, synchronize content or manage the catalogue.

> Product principle: Google Drive is an import/source channel. L-E-COURS is the organized catalogue students use every day.

## 🚀 Highlights in v1.6 (implementation in progress)

### Public learning experience
- Public library with no mandatory registration.
- Arabic RTL interface with Light, Dark and System appearance modes.
- Browse content by **StudyYear → Filiere → Speciality → Subject → ResourceCategory → Files**.
- The folder structure imported from Drive is mapped automatically:
  - First folder level → StudyYear (السنة الدراسية)
  - Second folder level → Filiere (الشعبة)
  - Third folder level → Speciality (التخصص)
  - Fourth folder level → Subject (المادة)
  - Fifth folder level → ResourceCategory (Cours / TD / Examens / Autres)
- Global file-name search across published sources.
- Device-local favourites; no account is required.
- In-app PDF reader for uploaded PDFs, with browser-native zoom, page navigation and print controls.
- Recently opened files stored locally on the current device.
- Private study notes attached to individual files and saved in browser local storage.
- Breadcrumb navigation through the academic folder hierarchy.
- Quick access to favourites and recent files without signing in.
- Open non-PDF resources in their source or download them where available.

### Administration
- Separate administrator sign-in at `/#admin`.
- Connect a shared Google Drive folder using its URL.
- Recursive folder and file inventory.
- Sync an existing source again after Drive content changes.
- Academic catalogue records are available in Django Admin for review and manual adjustments.
- Upload and source-management operations require an authenticated staff/admin account.

### Student privacy in v1.5
- Favourites, recent-file history and study notes stay in the current browser using `localStorage`.
- These personal items are not uploaded to Django and do not synchronize between devices.
- The PDF reader currently embeds uploaded PDF files; Google Drive-only files open through their source link.

### Platform foundation
- React 18 + Vite + TypeScript frontend.
- Django + Django REST Framework backend.
- PostgreSQL for deployment; SQLite for local development.
- Token-based administrator authentication and API throttling.
- Local development storage or optional S3-compatible object storage.
- File metadata, SHA-256 digest and audit events.

## 🧭 Academic catalogue model

```text
Google Drive shared folder
└── StudyYear / السنة الدراسية
    └── Filiere / الشعبة
        └── Speciality / التخصص
            └── Subject / المادة
                ├── Cours
                ├── TD
                ├── Examens
                └── Autres
                ├── PDF notes
                ├── Exercises
                ├── Exams
                └── Other resources
```

The catalogue entities are linked to their source `Folder` records. This keeps the original Drive hierarchy traceable while providing a structured academic layer. The mapping is depth-based in this release; if a Drive folder uses a different structure, adjust its folders in Django Admin or normalize the folder layout before syncing.

## 🧱 Technology stack

| Layer | Technology | Responsibility |
|---|---|---|
| Web UI | React, TypeScript, Vite | Public library and admin workspace |
| UI icons | Lucide React | Interface iconography |
| API | Django, Django REST Framework | Catalogue, authentication and file endpoints |
| Database | PostgreSQL / SQLite | Sources, folders, files and academic entities |
| Object storage | Local / S3-compatible | Uploaded and imported file bytes |
| Import | Google Drive API v3 | Folder traversal and file import |

## 📦 Project structure

```text
L-E-COURS/
├── backend/
│   ├── config/                 # Django settings and URL configuration
│   ├── core/
│   │   ├── migrations/         # Database schema history
│   │   ├── management/         # Demo data and management commands
│   │   ├── models.py           # Sources, folders, files and academic catalogue
│   │   ├── drive_importer.py   # Recursive Google Drive import and mapping
│   │   ├── serializers.py
│   │   ├── views.py            # Public and admin API endpoints
│   │   ├── urls.py
│   │   └── tests.py
│   ├── .env.example
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── lib/api.ts          # API client
│   │   ├── App.tsx             # Public library, admin and login views
│   │   └── styles.css
│   ├── .env.example
│   └── package.json
├── docs/
│   ├── DEPLOYMENT_NOTES.md
│   └── ROADMAP.md
└── README.md
```

## ⚡ Quick start — Windows PowerShell

### 1. Backend

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Backend API: `http://127.0.0.1:8000/api/`  
Django Admin: `http://127.0.0.1:8000/admin/`

### 2. Frontend

Open a second PowerShell terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`.

- **Students / visitors:** open `/` — no registration required.
- **Administrator:** open `http://localhost:5173/#admin` and sign in with the Django superuser credentials.

### 3. Upgrade from v1.3

Back up your database and uploaded media first, then replace the project files with v1.6 and run:

```powershell
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
```

Migration 0004 renames the existing academic entities in place, adds resource categories, and assigns existing files where their folder placement allows it. Review the imported structure in Django Admin before publishing.

## 🔗 Connect Google Drive

1. Create or select a project in Google Cloud Console.
2. Enable **Google Drive API**.
3. Create an API key and restrict it to the Google Drive API where possible.
4. Share the Drive folder as **Anyone with the link — Viewer** if using the API-key import mode.
5. Add the key to `backend/.env`:

```env
GOOGLE_DRIVE_API_KEY=your_google_drive_api_key
```

6. Restart Django.
7. Sign in at `/#admin`, open **ربط Google Drive**, enter the shared folder URL and start the import.
8. Run Sync again whenever you want to refresh the catalogue.

The linked Drive folder is treated as a container. Its immediate child folders become StudyYears. The next four folder levels map to Filiere, Speciality, Subject and ResourceCategory. Category names are detected in Arabic, French and English; unrecognized names are assigned to Autres.

### Import limits

Default safeguards are configured in `backend/.env.example`:

- Maximum imported file size: 50 MB per file.
- Maximum imported bytes per sync: 500 MB.
- Google-native Docs/Sheets/Slides and files that cannot be downloaded remain link-based entries.

Review storage quotas and costs before importing a large library. The importer needs access to the Drive items; public-link access is the simple API-key path, not a substitute for OAuth when importing private drives.

## 🗄️ Database and storage

### SQLite (local development)

No database configuration is required. SQLite is used when `DATABASE_URL` is empty.

### PostgreSQL (deployment)

Set `DATABASE_URL` in the backend environment. Example format:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

Use the SSL requirements of your provider and keep credentials outside source control.

### Local file storage

By default, uploaded/imported files are stored under `backend/media/`. This is suitable for local development only unless the host provides persistent disk storage and backups.

### S3-compatible storage (including Supabase Storage)

Create a private bucket and S3-compatible credentials, then configure the backend only:

```env
STORAGE_BACKEND=s3
S3_ENDPOINT_URL=https://YOUR_PROJECT_REF.storage.supabase.co/storage/v1/s3
S3_BUCKET_NAME=your-private-bucket
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_REGION=us-east-1
S3_SIGNED_URL_TTL=300
```

Never place storage secrets, Django secrets or database credentials in the frontend environment. The backend creates time-limited access URLs for stored files.

## 🔌 API overview

All endpoints are prefixed with `/api/`.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/sources/` | Public | List published Drive sources |
| GET | `/folders/?source=ID&parent=null` | Public | List root folders or children |
| GET | `/files/?source=ID&folder=ID` | Public | List published files |
| GET | `/academic/` | Public | Nested StudyYear / Filiere / Speciality / Subject / ResourceCategory catalogue |
| GET | `/search/?q=term` | Public | Search file names across sources |
| GET | `/dashboard/` | Public | Public library summary |
| POST | `/auth/token/` | Public, throttled | Administrator login |
| POST | `/auth/logout/` | Authenticated | Revoke current token |
| POST | `/admin/drive-sources/` | Admin | Add and import a Drive folder |
| POST | `/admin/drive-sources/{id}/sync/` | Admin | Re-sync a Drive source |
| CRUD | `/admin/study-years/`, `/admin/filieres/`, `/admin/specialities/`, `/admin/subjects/`, `/admin/resource-categories/` | Admin | Manage academic hierarchy and categories |
| POST | `/files/upload/` | Authenticated | Upload a file |
| GET | `/files/{id}/download/` | Public | Access a published stored file |

## 🔐 Security checklist before production

- [ ] Set a strong random `DJANGO_SECRET_KEY`.
- [ ] Set `DJANGO_DEBUG=False` and configure `DJANGO_ALLOWED_HOSTS`.
- [ ] Use HTTPS for the frontend, API and Django Admin.
- [ ] Restrict `CORS_ALLOWED_ORIGINS` to the deployed frontend domain.
- [ ] Use PostgreSQL and persistent private object storage.
- [ ] Keep all API keys and storage credentials on the backend.
- [ ] Back up the database and object storage.
- [ ] Restrict Google API keys and monitor quota usage.
- [ ] Add malware scanning and content-based file validation before accepting uploads from untrusted users.
- [ ] Review which sources and files are marked public before publishing them.

Public browsing is intentionally open. Administrative actions remain authenticated. Do not expose a development server or default secret on the public internet.

## 🧪 Verification

Run backend tests:

```powershell
cd backend
python manage.py check
python manage.py test core
```

Build the frontend:

```powershell
cd frontend
npm run build
```

A successful Python syntax compilation alone does not replace Django checks, migrations or integration tests. Run the commands above in an environment with dependencies installed before deploying.

## 🗺️ Roadmap

| Release | Focus |
|---|---|
| v1.2 | Authentication, upload safeguards and storage foundation |
| v1.3 | Public library and Google Drive import |
| **v1.4** | **Academic catalogue, global search and local favourites** |
| v1.5 | Dedicated PDF/image preview, richer filters, PWA and offline-ready caching |
| v1.6 | PDF text indexing, advanced search, bulk actions and duplicate review |
| v1.7 | AI study assistant, summaries and quiz generation |
| v2.0 | Analytics, refined permissions and mobile client |

## 🤝 Contributing

1. Create a feature branch.
2. Keep migrations committed with model changes.
3. Add or update API tests.
4. Run Django checks and the frontend production build.
5. Document new environment variables and deployment changes.

## 📄 License

This project currently ships without a formal license grant. Add a `LICENSE` file before distributing or accepting external contributions under an open-source license.

---

<div align="center">

**L-E-COURS** · منظم. واضح. متاح للجميع.

</div>


## v1.6 status

The five-level catalogue and migration are implemented in source. Do not deploy until the Django migration/test suite, frontend production build, and a real Drive import have been verified in an environment with project dependencies installed.
