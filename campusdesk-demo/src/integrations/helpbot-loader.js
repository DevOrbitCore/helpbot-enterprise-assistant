/**
 * CampusDesk -> HelpBot Host Integration Loader & Adapter Contract.
 *
 * Responsibilities:
 * 1. Register `window.HelpBotHostAdapter.getContext()` with ONLY approved metadata.
 * 2. Fetch `GET /api/widget-config` from the standalone HelpBot service.
 * 3. Dynamically load the Shadow DOM Web Component script and mount `<helpbot-assistant>`.
 * 4. Degrade gracefully if HelpBot is offline so the host portal remains 100% usable.
 */

const APPROVED_CONTEXT_KEYS = [
  "tenant_id",
  "application_id",
  "user_id",
  "role",
  "module_id",
  "screen_id",
  "route",
  "page_title",
  "locale",
];

/**
 * Strip any unexpected or sensitive fields before exposing context to HelpBot.
 * @param {Record<string, unknown>} rawContext
 */
export function buildSafeHostContext(rawContext = {}) {
  const safe = {};
  for (const key of APPROVED_CONTEXT_KEYS) {
    const val = rawContext[key];
    safe[key] = typeof val === "string" ? val : String(val ?? "");
  }
  return safe;
}

/**
 * Register or update `window.HelpBotHostAdapter` and notify the mounted widget.
 * @param {() => Record<string, string>} contextGetter
 */
export function registerHostAdapter(contextGetter) {
  if (typeof window === "undefined") return;
  window.HelpBotHostAdapter = {
    getContext() {
      return buildSafeHostContext(contextGetter());
    },
  };
}

export function notifyHelpBotContextChanged() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("helpbot:context-changed"));
}

/**
 * Initialize HelpBot widget from a remote HelpBot service URL.
 * Returns `{ connected: boolean, reason: string }` and never throws into host rendering.
 *
 * @param {object} options
 * @param {string} options.apiBaseUrl
 * @param {() => Record<string, string>} options.getContext
 * @param {typeof fetch} [options.fetchImpl]
 * @param {Document} [options.doc]
 */
export async function initHelpBotWidget({
  apiBaseUrl,
  getContext,
  fetchImpl = globalThis.fetch,
  doc = typeof document !== "undefined" ? document : null,
}) {
  registerHostAdapter(getContext);

  const normalizedBase = String(apiBaseUrl || "").replace(/\/+$/, "");
  if (!normalizedBase) {
    return { connected: false, reason: "HelpBot API URL is not configured." };
  }

  let config;
  try {
    const response = await fetchImpl(`${normalizedBase}/api/widget-config`, {
      method: "GET",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      return {
        connected: false,
        reason: `HelpBot config endpoint returned HTTP ${response.status}.`,
      };
    }
    config = await response.json();
  } catch {
    return {
      connected: false,
      reason: "HelpBot service is offline — CampusDesk remains fully usable.",
    };
  }

  if (!doc || !doc.body) {
    return { connected: true, reason: "Config loaded (non-DOM environment).", config };
  }

  try {
    await _loadWidgetModuleScript(doc, config.widget_script_url);
    let element = doc.querySelector("helpbot-assistant");
    if (!element) {
      element = doc.createElement("helpbot-assistant");
      doc.body.appendChild(element);
    }
    if (typeof element.configure === "function") {
      await element.configure(config, () => window.HelpBotHostAdapter.getContext());
    }
    return { connected: true, reason: "HelpBot connected.", config };
  } catch {
    return {
      connected: false,
      reason: "HelpBot widget script could not be loaded — CampusDesk remains usable.",
    };
  }
}

function _loadWidgetModuleScript(doc, scriptUrl) {
  return new Promise((resolve, reject) => {
    const existing = doc.querySelector(`script[data-helpbot-src="${scriptUrl}"]`);
    if (existing) {
      resolve();
      return;
    }
    const script = doc.createElement("script");
    script.type = "module";
    script.src = scriptUrl;
    script.setAttribute("data-helpbot-src", scriptUrl);
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load HelpBot widget script."));
    doc.head.appendChild(script);
  });
}
