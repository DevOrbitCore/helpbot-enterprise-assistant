<template>
  <div class="portal-shell">
    <aside class="portal-sidebar" aria-label="CampusDesk navigation">
      <div class="brand-block">
        <span class="brand-mark" aria-hidden="true">CD</span>
        <div class="brand-text">
          <h1>CampusDesk</h1>
          <p>Student Services Portal (Demo Host)</p>
        </div>
      </div>

      <nav aria-label="Portal modules">
        <div class="nav-section-label">Modules</div>
        <ul class="nav-list">
          <li v-for="item in navItems" :key="item.path">
            <router-link class="nav-link" :to="item.path">
              <svg
                v-if="item.meta.module_id === 'student-profile'"
                class="nav-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              <svg
                v-else-if="item.meta.module_id === 'course-registration'"
                class="nav-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <rect x="3" y="4" width="18" height="16" rx="2" />
                <path d="M7 8h10M7 12h10M7 16h6" />
              </svg>
              <svg
                v-else-if="item.meta.module_id === 'library-services'"
                class="nav-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
              </svg>
              <svg
                v-else-if="item.meta.module_id === 'examination-help'"
                class="nav-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <path d="M16 2v4M8 2v4M3 10h18" />
              </svg>
              <svg
                v-else-if="item.meta.module_id === 'campus-facilities'"
                class="nav-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M3 21h18" />
                <path d="M5 21V7l8-4v18" />
                <path d="M19 21V11l-6-4" />
                <path d="M9 9v.01M9 12v.01M9 15v.01" />
              </svg>
              <svg
                v-else
                class="nav-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <rect x="2" y="5" width="20" height="14" rx="2" />
                <path d="M2 10h20" />
              </svg>
              <span class="nav-link-text">
                <span class="nav-link-title">{{ item.meta.page_title }}</span>
                <small>{{ item.meta.nav_subtitle }}</small>
              </span>
            </router-link>
          </li>
        </ul>
      </nav>

      <div class="sidebar-footer">
        <strong>Host Boundary Demo</strong>
        Fictional test data only. HelpBot runs as an independent service on port 8200.
      </div>
    </aside>

    <div class="portal-main">
      <header class="portal-header">
        <div class="header-meta">
          <h2>{{ currentContext.page_title }}</h2>
          <div class="context-tags">
            <span class="tag">
              <span class="tag-label">Module</span>
              <span class="tag-value">{{ currentContext.module_id }}</span>
            </span>
            <span class="tag">
              <span class="tag-label">Screen</span>
              <span class="tag-value">{{ currentContext.screen_id }}</span>
            </span>
            <span class="tag">
              <span class="tag-label">Route</span>
              <span class="tag-value">{{ currentContext.route }}</span>
            </span>
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
            <span class="status-dot" aria-hidden="true"></span>
            {{ helpbotState.connected ? "HelpBot Connected" : "HelpBot Offline (Portal Active)" }}
          </span>
        </div>
      </header>

      <main class="portal-content">
        <ContextPreviewCard :context="currentContext" :status-reason="helpbotState.reason" />
        <router-view v-slot="{ Component }">
          <Transition name="erp-page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
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
