<template>
  <details class="card">
    <summary style="cursor: pointer; font-weight: 600; font-size: 14px">
      HelpBot Adapter Context Preview (Safe Metadata Only)
    </summary>
    <p class="muted" style="margin: 8px 0">
      This exact payload is exposed via <code>window.HelpBotHostAdapter.getContext()</code>.
      Passwords, payment inputs, private form fields, and page HTML are never sent.
    </p>
    <pre
      style="
        background: #0f172a;
        color: #e2e8f0;
        padding: 12px;
        border-radius: 8px;
        font-size: 12px;
        overflow-x: auto;
        margin: 0;
      "
    >{{ JSON.stringify(context, null, 2) }}</pre>
    <p class="muted" style="margin: 8px 0 0; font-size: 12px">
      Integration status: {{ statusReason }}
    </p>
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
