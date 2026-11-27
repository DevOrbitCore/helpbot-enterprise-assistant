import test from "node:test";
import assert from "node:assert/strict";
import {
  buildSafeHostContext,
  initHelpBotWidget,
} from "../src/integrations/helpbot-loader.js";

test("buildSafeHostContext keeps only approved fields and strips sensitive data", () => {
  const safe = buildSafeHostContext({
    tenant_id: "campusdesk-dev",
    application_id: "campusdesk",
    user_id: "stu-maya-chen",
    role: "student",
    module_id: "fee-information",
    screen_id: "tuition-summary",
    route: "/fees",
    page_title: "Fee Information",
    locale: "en-US",
    password: "do-not-leak-password",
    credit_card: "4111-1111-1111-1111",
    raw_html: "<html><body>secret</body></html>",
  });

  assert.equal(safe.tenant_id, "campusdesk-dev");
  assert.equal(safe.module_id, "fee-information");
  assert.equal("password" in safe, false);
  assert.equal("credit_card" in safe, false);
  assert.equal("raw_html" in safe, false);
});

test("initHelpBotWidget degrades gracefully when HelpBot service is offline", async () => {
  const failingFetch = async () => {
    throw new Error("ECONNREFUSED");
  };

  const result = await initHelpBotWidget({
    apiBaseUrl: "http://127.0.0.1:8200",
    getContext: () => ({ tenant_id: "campusdesk-dev", user_id: "stu-maya-chen" }),
    fetchImpl: failingFetch,
    doc: null,
  });

  assert.equal(result.connected, false);
  assert.match(result.reason, /offline/i);
});

test("initHelpBotWidget handles non-200 config response without throwing", async () => {
  const errorFetch = async () => ({
    ok: false,
    status: 503,
    json: async () => ({}),
  });

  const result = await initHelpBotWidget({
    apiBaseUrl: "http://127.0.0.1:8200",
    getContext: () => ({ tenant_id: "campusdesk-dev", user_id: "stu-maya-chen" }),
    fetchImpl: errorFetch,
    doc: null,
  });

  assert.equal(result.connected, false);
  assert.match(result.reason, /503/);
});
