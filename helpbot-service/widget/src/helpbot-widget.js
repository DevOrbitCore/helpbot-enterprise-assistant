/**
 * <helpbot-assistant> — Browser-native Shadow DOM Web Component.
 *
 * Framework-agnostic: works in Vue, React, Angular, or plain HTML host apps.
 * Receives configuration via `element.configure(config, contextProvider)`.
 */

import { HelpBotApiClient } from "./api-client.js";

const STYLESHEET_PATH = "/widget/styles/helpbot-widget.css";

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export class HelpBotAssistantElement extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });

    this._config = null;
    this._client = null;
    this._contextProvider = () => ({});
    this._isOpen = false;
    this._isLoading = false;
    this._showHistory = false;
    this._conversationId = null;
    this._messages = [];
    this._conversations = [];
    this._connectionState = "connecting"; // connecting | ready | degraded | offline
    this._statusText = "Connecting...";
    this._errorMessage = "";

    this._handleContextChanged = this._handleContextChanged.bind(this);
    this._handleKeyDown = this._handleKeyDown.bind(this);
  }

  connectedCallback() {
    this._renderShell();
    window.addEventListener("helpbot:context-changed", this._handleContextChanged);
    window.addEventListener("keydown", this._handleKeyDown);
  }

  disconnectedCallback() {
    window.removeEventListener("helpbot:context-changed", this._handleContextChanged);
    window.removeEventListener("keydown", this._handleKeyDown);
  }

  /**
   * Initialize the widget with server-returned config and a host context callback.
   * @param {object} config - Response from GET /api/widget-config
   * @param {() => object} contextProvider - Function returning approved HostContext
   */
  async configure(config, contextProvider) {
    this._config = config || {};
    this._contextProvider =
      typeof contextProvider === "function" ? contextProvider : () => ({});
    this._client = new HelpBotApiClient(
      this._config.api_base_url,
      this._contextProvider
    );

    if (this._config.accent_color) {
      this.style.setProperty("--hb-accent", this._config.accent_color);
    }

    this._renderShell();
    this._updateContextBar();
    await this._refreshStatus();
  }

  _renderShell() {
    const apiBase = (this._config && this._config.api_base_url) || "";
    const cssUrl = apiBase ? `${apiBase.replace(/\/+$/, "")}${STYLESHEET_PATH}` : "";
    const title = (this._config && this._config.widget_title) || "HelpBot Support Assistant";

    this.shadowRoot.innerHTML = `
      ${cssUrl ? `<link rel="stylesheet" href="${escapeHtml(cssUrl)}" />` : ""}
      <section
        class="hb-panel"
        role="dialog"
        aria-modal="false"
        aria-label="${escapeHtml(title)}"
        ${this._isOpen ? "" : "hidden"}
      >
        <header class="hb-header">
          <div class="hb-title-group">
            <h2 class="hb-title">${escapeHtml(title)}</h2>
            <span class="hb-status" aria-live="polite">
              <span class="hb-status-dot" data-role="status-dot"></span>
              <span data-role="status-text">${escapeHtml(this._statusText)}</span>
            </span>
          </div>
          <div class="hb-header-actions">
            <button type="button" class="hb-icon-btn" data-action="toggle-history" aria-label="Toggle chat history">
              History
            </button>
            <button type="button" class="hb-icon-btn" data-action="new-chat" aria-label="Start new conversation">
              New
            </button>
            <button type="button" class="hb-icon-btn" data-action="close" aria-label="Close HelpBot">
              ✕
            </button>
          </div>
        </header>

        <div class="hb-context-bar">
          <span>Active context</span>
          <span class="hb-context-pill" data-role="context-pill">No context</span>
        </div>

        <div class="hb-history-drawer" data-role="history-drawer" hidden>
          <ul class="hb-history-list" data-role="history-list"></ul>
        </div>

        <div class="hb-messages" data-role="messages" role="log" aria-live="polite"></div>

        <div class="hb-error-banner" data-role="error-banner" role="alert" hidden></div>

        <form class="hb-composer" data-role="composer">
          <textarea
            class="hb-input"
            data-role="input"
            rows="1"
            placeholder="Ask about policies, courses, library, or exams..."
            aria-label="Message HelpBot"
          ></textarea>
          <button type="submit" class="hb-btn" data-role="send-btn">Send</button>
        </form>
      </section>

      <button
        type="button"
        class="hb-launcher"
        data-action="toggle-open"
        aria-expanded="${this._isOpen ? "true" : "false"}"
        aria-label="Open HelpBot support assistant"
      >
        <span>HelpBot</span>
      </button>
    `;

    this._bindEvents();
    this._renderMessages();
    this._updateStatusIndicator();
    this._updateContextBar();
  }

  _bindEvents() {
    const root = this.shadowRoot;
    root.querySelector('[data-action="toggle-open"]')?.addEventListener("click", () => {
      this._setOpen(!this._isOpen);
    });
    root.querySelector('[data-action="close"]')?.addEventListener("click", () => {
      this._setOpen(false);
    });
    root.querySelector('[data-action="new-chat"]')?.addEventListener("click", () => {
      this._conversationId = null;
      this._messages = [];
      this._showHistory = false;
      this._setError("");
      this._renderHistoryDrawer();
      this._renderMessages();
    });
    root.querySelector('[data-action="toggle-history"]')?.addEventListener("click", async () => {
      this._showHistory = !this._showHistory;
      if (this._showHistory) {
        await this._loadConversationList();
      }
      this._renderHistoryDrawer();
    });

    const form = root.querySelector('[data-role="composer"]');
    const input = root.querySelector('[data-role="input"]');
    form?.addEventListener("submit", async (event) => {
      event.preventDefault();
      await this._submitMessage();
    });
    input?.addEventListener("keydown", async (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        await this._submitMessage();
      }
    });
  }

  _handleKeyDown(event) {
    if (event.key === "Escape" && this._isOpen) {
      this._setOpen(false);
    }
  }

  _handleContextChanged() {
    // Reset active conversation view when the demo user changes so users never see stale history.
    this._conversationId = null;
    this._messages = [];
    this._showHistory = false;
    this._updateContextBar();
    this._renderHistoryDrawer();
    this._renderMessages();
  }

  _setOpen(open) {
    this._isOpen = open;
    const panel = this.shadowRoot.querySelector(".hb-panel");
    const launcher = this.shadowRoot.querySelector('[data-action="toggle-open"]');
    if (panel) panel.hidden = !open;
    if (launcher) launcher.setAttribute("aria-expanded", open ? "true" : "false");

    if (open) {
      this._updateContextBar();
      const input = this.shadowRoot.querySelector('[data-role="input"]');
      if (input) setTimeout(() => input.focus(), 0);
    } else if (launcher) {
      launcher.focus();
    }
  }

  async _refreshStatus() {
    if (!this._client) return;
    try {
      const status = await this._client.getAiStatus();
      if (status.ready) {
        this._connectionState = "ready";
        this._statusText = `Connected (${status.provider})`;
      } else {
        this._connectionState = "degraded";
        this._statusText = "Connected — AI key not configured";
      }
    } catch {
      this._connectionState = "offline";
      this._statusText = "Service unreachable";
    }
    this._updateStatusIndicator();
  }

  _updateStatusIndicator() {
    const dot = this.shadowRoot.querySelector('[data-role="status-dot"]');
    const text = this.shadowRoot.querySelector('[data-role="status-text"]');
    if (text) text.textContent = this._statusText;
    if (dot) {
      dot.classList.remove("warn", "err");
      if (this._connectionState === "degraded") dot.classList.add("warn");
      if (this._connectionState === "offline") dot.classList.add("err");
    }
  }

  _updateContextBar() {
    const pill = this.shadowRoot.querySelector('[data-role="context-pill"]');
    if (!pill) return;
    const ctx = this._contextProvider ? this._contextProvider() : null;
    if (!ctx) {
      pill.textContent = "No context";
      return;
    }
    const label = `${ctx.module_id || "general"} · ${ctx.user_id || "guest"}`;
    pill.textContent = label;
    pill.title = `App: ${ctx.application_id} | Screen: ${ctx.screen_id} | Role: ${ctx.role}`;
  }

  _setError(message) {
    this._errorMessage = message || "";
    const banner = this.shadowRoot.querySelector('[data-role="error-banner"]');
    if (!banner) return;
    banner.textContent = this._errorMessage;
    banner.hidden = !this._errorMessage;
  }

  async _loadConversationList() {
    if (!this._client) return;
    try {
      this._conversations = await this._client.listConversations();
      this._setError("");
    } catch (err) {
      this._setError(err.message || "Could not load conversation history.");
    }
  }

  _renderHistoryDrawer() {
    const drawer = this.shadowRoot.querySelector('[data-role="history-drawer"]');
    const list = this.shadowRoot.querySelector('[data-role="history-list"]');
    if (!drawer || !list) return;
    drawer.hidden = !this._showHistory;
    if (!this._showHistory) return;

    if (!this._conversations.length) {
      list.innerHTML = `<li class="hb-source-meta">No saved conversations for this user yet.</li>`;
      return;
    }

    list.innerHTML = this._conversations
      .map(
        (conv) => `
        <li>
          <button type="button" class="hb-history-item" data-conv-id="${escapeHtml(conv.id)}">
            <span>${escapeHtml(conv.title)}</span>
            <span class="hb-source-meta">${conv.message_count} msgs</span>
          </button>
        </li>`
      )
      .join("");

    list.querySelectorAll("[data-conv-id]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.getAttribute("data-conv-id");
        if (!id || !this._client) return;
        try {
          const detail = await this._client.getConversation(id);
          this._conversationId = detail.id;
          this._messages = detail.messages || [];
          this._showHistory = false;
          this._setError("");
          this._renderHistoryDrawer();
          this._renderMessages();
        } catch (err) {
          this._setError(err.message || "Could not open conversation.");
        }
      });
    });
  }

  _renderMessages() {
    const container = this.shadowRoot.querySelector('[data-role="messages"]');
    if (!container) return;

    if (!this._messages.length) {
      container.innerHTML = `
        <div class="hb-empty">
          Ask a question about uploaded HelpBot documentation. Answers are grounded strictly in available documents.
        </div>`;
      return;
    }

    container.innerHTML = this._messages
      .map((msg) => {
        const sourcesHtml =
          msg.sender === "assistant" && Array.isArray(msg.sources) && msg.sources.length
            ? `
              <div class="hb-sources" aria-label="Document sources">
                <div class="hb-sources-title">Sources (${msg.sources.length})</div>
                ${msg.sources
                  .map((src) => {
                    const loc = src.page_or_section || src.timestamp_range || src.module_id;
                    return `
                      <div class="hb-source-card">
                        <div class="hb-source-name">${escapeHtml(src.title)}</div>
                        <div class="hb-source-meta">${escapeHtml(src.file_name)} · ${escapeHtml(loc)}</div>
                      </div>`;
                  })
                  .join("")}
              </div>`
            : "";

        return `
          <div class="hb-bubble ${msg.sender === "user" ? "user" : "assistant"}">
            <div>${escapeHtml(msg.content)}</div>
            ${sourcesHtml}
          </div>`;
      })
      .join("");

    if (this._isLoading) {
      const loading = document.createElement("div");
      loading.className = "hb-bubble assistant";
      loading.textContent = "Searching HelpBot documents...";
      container.appendChild(loading);
    }

    container.scrollTop = container.scrollHeight;
  }

  async _submitMessage() {
    if (this._isLoading || !this._client) return;
    const input = this.shadowRoot.querySelector('[data-role="input"]');
    const sendBtn = this.shadowRoot.querySelector('[data-role="send-btn"]');
    if (!input) return;

    const text = input.value.trim();
    if (!text) return;

    this._setError("");
    this._isLoading = true;
    if (sendBtn) sendBtn.disabled = true;
    input.value = "";

    this._messages.push({ sender: "user", content: text, sources: [] });
    this._renderMessages();

    try {
      const response = await this._client.sendMessage(text, this._conversationId);
      this._conversationId = response.conversation_id;
      this._messages.pop();
      this._messages.push(response.user_message, response.assistant_message);
    } catch (err) {
      this._setError(err.message || "Unable to send message to HelpBot.");
    } finally {
      this._isLoading = false;
      if (sendBtn) sendBtn.disabled = false;
      this._renderMessages();
      input.focus();
    }
  }
}

if (!customElements.get("helpbot-assistant")) {
  customElements.define("helpbot-assistant", HelpBotAssistantElement);
}
