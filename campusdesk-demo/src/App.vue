<template>
  <div class="portal-shell">
    <aside class="portal-sidebar" aria-label="CampusDesk navigation">
      <div class="brand-block">
        <h1>CampusDesk</h1>
        <p>Student Services Portal (Demo Host)</p>
      </div>

      <nav>
        <ul class="nav-list">
          <li v-for="item in navItems" :key="item.path">
            <router-link class="nav-link" :to="item.path">
              <span>{{ item.meta.page_title }}</span>
              <small>{{ item.meta.nav_subtitle }}</small>
            </router-link>
          </li>
        </ul>
      </nav>

      <div class="sidebar-footer">
        <strong>Host Boundary Demo</strong><br />
        Fictional test data only. HelpBot runs as an independent service on port 8200.
      </div>
    </aside>

    <div class="portal-main">
      <header class="portal-header">
        <div class="header-meta">
          <h2>{{ currentContext.page_title }}</h2>
          <div class="context-tags">
            <span class="tag">Module: {{ currentContext.module_id }}</span>
            <span class="tag">Screen: {{ currentContext.screen_id }}</span>
            <span class="tag">Route: {{ currentContext.route }}</span>
          </div>
        </div>

        <div class="header-controls">
          <label class="user-switcher">
            <span>Demo User Switcher (Dev Only)</span>
            <select
              :value="demoSession.currentUser.user_id"
              aria-label="Select development demo user"
              @change="onUserChange"
            >
              <option
                v-for="user in demoSession.users"
                :key="user.user_id"
                :value="user.user_id"
              >
                {{ user.display_name }}
              </option>
            </select>
          </label>

          <span
            class="status-badge"
            :class="helpbotState.connected ? 'online' : 'offline'"
            :title="helpbotState.reason"
          >
            {{ helpbotState.connected ? "HelpBot Connected" : "HelpBot Offline (Portal Active)" }}
          </span>
        </div>
      </header>

      <main class="portal-content">
        <ContextPreviewCard :context="currentContext" :status-reason="helpbotState.reason" />
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from "vue";
import { useRoute } from "vue-router";
import { PORTAL_ROUTES } from "./router/index.js";
import { demoSession } from "./services/demoSession.js";
import {
  buildSafeHostContext,
  initHelpBotWidget,
  notifyHelpBotContextChanged,
} from "./integrations/helpbot-loader.js";
import ContextPreviewCard from "./components/ContextPreviewCard.vue";

const route = useRoute();
const navItems = PORTAL_ROUTES.filter((r) => r.meta && r.meta.page_title);

const tenantId = import.meta.env.VITE_TENANT_ID || "campusdesk-dev";
const applicationId = import.meta.env.VITE_APPLICATION_ID || "campusdesk";
const helpbotApiUrl = import.meta.env.VITE_HELPBOT_API_URL || "http://127.0.0.1:8200";

const helpbotState = reactive({
  connected: false,
  reason: "Checking HelpBot service availability...",
});

const currentContext = computed(() =>
  buildSafeHostContext({
    tenant_id: tenantId,
    application_id: applicationId,
    user_id: demoSession.currentUser.user_id,
    role: demoSession.currentUser.role,
    module_id: route.meta?.module_id || "general",
    screen_id: route.meta?.screen_id || "home",
    route: route.fullPath || "/",
    page_title: route.meta?.page_title || "CampusDesk",
    locale: demoSession.currentUser.locale || "en-US",
  })
);

function onUserChange(event) {
  demoSession.selectUserById(event.target.value);
}

watch(
  () => [route.fullPath, demoSession.currentUser.user_id],
  () => {
    notifyHelpBotContextChanged();
  }
);

onMounted(async () => {
  const result = await initHelpBotWidget({
    apiBaseUrl: helpbotApiUrl,
    getContext: () => currentContext.value,
  });
  helpbotState.connected = result.connected;
  helpbotState.reason = result.reason;
});
</script>
