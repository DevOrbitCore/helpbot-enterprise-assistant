# Host Integration Guide

HelpBot is designed to embed into **any** web application (Vue, React, Angular, or plain HTML) without importing host code or sharing host CSS.

## 1. Configure CORS on HelpBot

Add your host application's origin to `HELPBOT_CORS_ORIGINS` in `helpbot-service/.env`:

```dotenv
HELPBOT_CORS_ORIGINS=http://127.0.0.1:5173,https://portal.your-org.example
```

## 2. Expose the Host Context Adapter

Register `window.HelpBotHostAdapter.getContext()` in your host app returning **only** approved non-sensitive metadata:

```js
window.HelpBotHostAdapter = {
  getContext() {
    return {
      tenant_id: "your-tenant-id",
      application_id: "your-app-id",
      user_id: "current-user-id",
      role: "student",
      module_id: "course-registration",
      screen_id: "registration-overview",
      route: window.location.pathname,
      page_title: document.title,
      locale: navigator.language || "en-US",
    };
  },
};
```

Dispatch `window.dispatchEvent(new CustomEvent("helpbot:context-changed"))` whenever the active route or signed-in user changes.

**Never** place passwords, session tokens, payment fields, personal form inputs, or raw DOM HTML inside `getContext()`.

## 3. Load and Mount `<helpbot-assistant>`

Fetch `/api/widget-config` from your HelpBot base URL, dynamically load `config.widget_script_url` as an ES module, append `<helpbot-assistant>`, and call `configure(config, () => window.HelpBotHostAdapter.getContext())`.

Always wrap the fetch in `try / catch` so a HelpBot outage never blocks your host application. See `campusdesk-demo/src/integrations/helpbot-loader.js` for a complete reference implementation.

## 4. Production Identity & Security Hardening

In local development, `DevelopmentIdentityAdapter` reads `X-HelpBot-Tenant-Id`, `X-HelpBot-User-Id`, and `X-HelpBot-User-Role` headers. **This adapter is strictly unsuitable for production** because browser JavaScript can forge arbitrary headers.

Before deploying to production:

1. Set `HELPBOT_ALLOW_DEV_IDENTITY=false`.
2. Implement a subclass of `IdentityAdapter` (`helpbot-service/backend/app/adapters/identity.py`) that verifies a signed JWT (`Authorization: Bearer <token>`) or server-verified session cookie issued by your identity provider.
3. Extract `tenant_id`, `user_id`, and authoritative `role` strictly from verified token claims—never from browser-supplied context fields.
4. Serve both the host application and HelpBot exclusively over HTTPS with HSTS enabled and replace `InMemoryRateLimiter` with a distributed store (e.g., Redis) or API gateway rate limiting.
