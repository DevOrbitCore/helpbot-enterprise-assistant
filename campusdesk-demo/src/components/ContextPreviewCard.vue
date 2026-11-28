<template>
  <details class="card context-card">
    <summary class="context-summary">
      <span class="context-summary-left">
        <svg
          class="context-summary-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <polyline points="16 18 22 12 16 6" />
          <polyline points="8 6 2 12 8 18" />
        </svg>
        <span>HelpBot Adapter Context Preview (Safe Metadata Only)</span>
      </span>
      <svg
        class="context-chevron"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </summary>
    <div class="context-body">
      <p class="muted">
        This exact payload is exposed via <code>window.HelpBotHostAdapter.getContext()</code>.
        Passwords, payment inputs, private form fields, and page HTML are never sent.
      </p>
      <pre class="context-code">{{ JSON.stringify(context, null, 2) }}</pre>
      <p class="context-status-line">
        Integration status: {{ statusReason }}
      </p>
    </div>
  </details>
</template>

<script setup>
defineProps({
  context: {
    type: Object,
    required: true,
  },
  statusReason: {
    type: String,
    default: "",
  },
});
</script>
