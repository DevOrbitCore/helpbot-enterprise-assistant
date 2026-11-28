<template>
  <div>
    <div class="card-grid">
      <section class="card">
        <div class="card-header">
          <div class="card-header-text">
            <h3>Active Demo Profile</h3>
          </div>
          <span class="erp-badge erp-badge-info">{{ demoSession.currentUser.role }}</span>
        </div>
        <dl class="erp-kv-list">
          <div class="erp-kv-row">
            <dt>Name</dt>
            <dd>{{ demoSession.currentUser.display_name }}</dd>
          </div>
          <div class="erp-kv-row">
            <dt>User ID</dt>
            <dd><code>{{ demoSession.currentUser.user_id }}</code></dd>
          </div>
          <div class="erp-kv-row">
            <dt>Role</dt>
            <dd>{{ demoSession.currentUser.role }}</dd>
          </div>
        </dl>
      </section>

      <section class="card">
        <div class="card-header">
          <div class="card-header-text">
            <h3>Academic Affiliation</h3>
          </div>
        </div>
        <dl class="erp-kv-list">
          <div class="erp-kv-row">
            <dt>Program</dt>
            <dd>{{ demoSession.currentUser.program }}</dd>
          </div>
          <div class="erp-kv-row">
            <dt>Advisor</dt>
            <dd>{{ demoSession.currentUser.advisor }}</dd>
          </div>
          <div class="erp-kv-row">
            <dt>Campus</dt>
            <dd>{{ demoSession.currentUser.campus }}</dd>
          </div>
        </dl>
      </section>
    </div>

    <section class="card">
      <div class="card-header">
        <div class="card-header-text">
          <h3>Contact Preferences (Local Demo Form)</h3>
          <p class="card-subtitle">
            Changes here stay strictly in local browser memory to demonstrate that private form
            values are never transmitted to HelpBot.
          </p>
        </div>
      </div>

      <form class="erp-form-inline" @submit.prevent="saveNote">
        <label class="erp-field">
          <span class="erp-field-label">Preferred Notification Channel</span>
          <select v-model="channel" class="erp-select">
            <option>Campus Email</option>
            <option>Portal Inbox Only</option>
          </select>
        </label>
        <button type="submit" class="btn btn-primary">Save Local Preference</button>
      </form>

      <p v-if="savedMessage" class="notice-box notice-success">{{ savedMessage }}</p>
    </section>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { demoSession } from "../services/demoSession.js";

const channel = ref("Campus Email");
const savedMessage = ref("");

function saveNote() {
  savedMessage.value = `Saved "${channel.value}" in local demo state only (not transmitted to HelpBot).`;
}
</script>
