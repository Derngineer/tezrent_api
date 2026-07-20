# Technical Debt

Tracked items to address after the current push-to-launch phase. These were
intentionally deferred so the app keeps working with zero extra config.

## 🔴 Security — Secrets management (HIGH PRIORITY)

**Status:** Deferred (reverted on 2026-07-20 to keep app running without new env vars)

Live credentials are currently hardcoded as fallbacks in `config/settings.py`
and exist in git history. They must be rotated and moved to environment
variables (with no live fallback) before real production traffic / launch.

Affected secrets:

- `SECRET_KEY` — Django signing key
- `DATABASE_URL` — Render Postgres connection string (user/password in clear)
- `EMAIL_HOST_PASSWORD` — Gmail app password
- `ZIINA_API_KEY` — live payment gateway key
- `RECAPTCHA_PUBLIC_KEY` / `RECAPTCHA_PRIVATE_KEY`

**Plan when we return:**

1. Rotate every credential above (they're compromised once in git history):
   - Change Render Postgres password
   - Regenerate Gmail app password
   - Regenerate Ziina API key
   - Generate a new `SECRET_KEY`
2. Set them as environment variables in Render.
3. Remove the hardcoded fallbacks from `settings.py` (raise if missing in prod).
4. Consider `git filter-repo` / BFG to scrub history, or accept rotation as
   sufficient mitigation.

## 🟠 Insecure email backend used in production

**Status:** Deferred

`EMAIL_BACKEND = 'accounts.email_backend.CustomEmailBackend'` is applied
globally. That backend calls `ssl._create_unverified_context()`, disabling
TLS certificate verification (MITM risk for OTP + password-reset emails).

**Plan:** Gate it so `CustomEmailBackend` is only used when `DEBUG=True`;
production should use `django.core.mail.backends.smtp.EmailBackend`.

## 🟠 Production security headers missing

**Status:** Deferred

Add (when `not DEBUG`): `SECURE_SSL_REDIRECT`, HSTS settings, secure cookies,
`SECURE_PROXY_SSL_HEADER` (Render), `SECURE_CONTENT_TYPE_NOSNIFF`.

## 🟡 No automated tests

**Status:** Deferred

No `test_*` functions exist. Add coverage for: OTP verify flow, equipment
ownership checks, payment initiate/verify, and city/vendor visibility filtering.

## 🟡 JWT access token lifetime

Access token lives 1 day. Consider shorter access (15–60 min) + rotating
refresh with blacklist (app already installed).

## 🟡 Python-side aggregation leftovers

E.g. `PaymentStatusView` sums payments in Python; push to `.aggregate(Sum(...))`.

## 🟡 `ALLOWED_HOSTS` wildcard

`.onrender.com` allows any Render tenant host header — tighten to exact domain.

---

_Last updated: 2026-07-20_
