# Changelog

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
