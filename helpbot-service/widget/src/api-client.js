/**
 * Standalone HelpBot HTTP client.
 * Completely isolated from any host application's API client or state store.
 */

export class HelpBotApiClient {
  /**
   * @param {string} apiBaseUrl - Base URL of the HelpBot service (e.g. http://127.0.0.1:8200)
   * @param {() => Record<string, string>} getContext - Host adapter callback returning approved context
   */
  constructor(apiBaseUrl, getContext) {
    this.apiBaseUrl = String(apiBaseUrl || "").replace(/\/+$/, "");
    this.getContext = typeof getContext === "function" ? getContext : () => ({});
  }

  _buildHeaders(extra = {}) {
    const ctx = this.getContext() || {};
    return {
      Accept: "application/json",
      // Development-only identity headers. Production deployments replace this
      // with a verified Authorization bearer token or server-issued session cookie.
      "X-HelpBot-Tenant-Id": ctx.tenant_id || "campusdesk-dev",
      "X-HelpBot-User-Id": ctx.user_id || "demo-student-001",
      "X-HelpBot-User-Role": ctx.role || "student",
      ...extra,
    };
  }

  async _request(path, options = {}) {
    const response = await fetch(`${this.apiBaseUrl}${path}`, {
      ...options,
      headers: this._buildHeaders(options.headers || {}),
    });

    const contentType = response.headers.get("content-type") || "";
    const body = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const detail =
        (body && body.error && body.error.message) ||
        (body && body.detail) ||
        `Request failed with status ${response.status}`;
      const error = new Error(detail);
      error.status = response.status;
      throw error;
    }
    return body;
  }

  async getHealth() {
    return this._request("/api/health", { method: "GET" });
  }

  async getAiStatus() {
    return this._request("/api/ai/status", { method: "GET" });
  }

  async listConversations() {
    return this._request("/api/conversations", { method: "GET" });
  }

  async getConversation(conversationId) {
    return this._request(`/api/conversations/${encodeURIComponent(conversationId)}`, {
      method: "GET",
    });
  }

  async deleteConversation(conversationId) {
    return this._request(`/api/conversations/${encodeURIComponent(conversationId)}`, {
      method: "DELETE",
    });
  }

  async sendMessage(message, conversationId = null) {
    const context = this.getContext() || {};
    return this._request("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        context,
      }),
    });
  }
}
