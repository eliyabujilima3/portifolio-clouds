# Portfolio Clouds Application

## Backend SMTP reply support

The backend now saves admin replies and attempts to email them to the original sender.

### Configure SMTP

Create a file at `backend/.env` using `backend/.env.example` as a template.

Required values:

- `SMTP_SERVER`: e.g. `smtp.gmail.com`
- `SMTP_PORT`: e.g. `587`
- `SMTP_USER`: the dedicated app email address
- `SMTP_PASSWORD`: the app password or SMTP password

### Recommended Gmail setup

1. Create a dedicated Gmail account for this app.
2. Enable 2FA on that account.
3. Create an App Password for "Mail" and use it as `SMTP_PASSWORD`.

### Run the app

```bash
cd backend
python app.py
```

Then open administration in the browser at `http://127.0.0.1:5000/admin-login.html`.
