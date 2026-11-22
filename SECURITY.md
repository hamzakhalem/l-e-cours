# Security policy

## Reporting a vulnerability

Please **do not open a public issue** for security problems.

Report them privately through GitHub: go to the **Security** tab of this repository and click **Report a vulnerability**. Include the steps to reproduce and the version you tested. You will get a reply within 7 days.

## Supported versions

Only the latest release on `main` receives security fixes.

## Keeping secrets out of the repository

- All secrets are read from environment variables. Copy `backend/.env.example` to `backend/.env` and `frontend/.env.example` to `frontend/.env`; both `.env` files are ignored by git.
- Never put real keys in `settings.py`, in a default value of `os.getenv()`, or in the README.
- Uploaded and imported files live in `backend/media/`, which is ignored by git. Back them up separately.
- GitHub secret scanning and push protection are enabled on this repository: a push that contains a recognised key is blocked.

If a key is ever committed, **revoke it with its provider first**. Removing it from the code does not remove it from the git history.
