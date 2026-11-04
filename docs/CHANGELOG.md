# Changelog

## 1.6.0 — Five-Level Academic Catalogue (implementation in progress)

- Reworked the academic hierarchy to **StudyYear → Filiere → Speciality → Subject → ResourceCategory**.
- Added standard Cours, TD, Examens and Autres categories.
- Added Arabic, French and English Drive folder-name classification.
- Added admin-only CRUD endpoints and Django Admin management for every academic level and resource category, with manual ordering and visibility controls.
- Added category assignment for Drive-imported and manually uploaded files.
- Updated the public student catalogue to browse all five levels without registration.
- Preserved the v1.5 PDF reader, favourites, notes and recently viewed workspace.
- Added a data migration that renames the previous academic models in place and assigns existing files to categories where possible.

### Verification limitations

- Python source syntax compilation passed.
- Django migrations, runtime checks and tests could not be executed because Django packages are unavailable in the current environment.
- Frontend production build could not be executed because npm dependencies are absent and package registry access is unavailable.
- A live Google Drive import has not been tested; it requires a configured API key and accessible sample Drive folders.

## 1.5.0 — Student Reading Workspace

- Added an in-app PDF reader for uploaded PDF files. The browser's built-in PDF viewer provides page navigation, zoom and print where supported.
- Added breadcrumb navigation across nested folders.
- Added a recent-files list saved locally on the current device.
- Added per-file study notes saved in browser local storage.
- Improved favourites access and added a dedicated recent-files view.
- Added responsive layouts for the reader and notes editor.
- Updated README and roadmap to distinguish delivered features from planned work.

### Notes and limitations

- Notes, favourites and recent history are device/browser-local. They are not synced to a user account or server.
- The embedded PDF reader currently previews uploaded PDFs. Google Drive-only resources open using their source URL.
- Full production build and Django runtime tests require installing the project's dependencies and were not run in this build environment.
