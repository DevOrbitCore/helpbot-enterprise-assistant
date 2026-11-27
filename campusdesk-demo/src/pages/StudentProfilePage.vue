<template>
  <div>
    <div class="card-grid">
      <section class="card">
        <h3>Active Demo Profile</h3>
        <p><strong>Name:</strong> {{ demoSession.currentUser.display_name }}</p>
        <p><strong>User ID:</strong> <code>{{ demoSession.currentUser.user_id }}</code></p>
        <p><strong>Role:</strong> {{ demoSession.currentUser.role }}</p>
      </section>

      <section class="card">
        <h3>Academic Affiliation</h3>
        <p><strong>Program:</strong> {{ demoSession.currentUser.program }}</p>
        <p><strong>Advisor:</strong> {{ demoSession.currentUser.advisor }}</p>
        <p><strong>Campus:</strong> {{ demoSession.currentUser.campus }}</p>
      </section>
    </div>

    <section class="card">
      <h3>Contact Preferences (Local Demo Form)</h3>
      <p class="muted">
        Changes here stay strictly in local browser memory to demonstrate that private form values
        are never transmitted to HelpBot.
      </p>
      <form style="display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end" @submit.prevent="saveNote">
        <label style="display: flex; flex-direction: column; gap: 4px; font-size: 13px">
          Preferred Notification Channel
          <select v-model="channel" style="padding: 8px; border-radius: 8px; border: 1px solid #cbd5e1">
            <option>Campus Email</option>
            <option>Portal Inbox Only</option>
          </select>
        </label>
        <button type="submit" class="btn btn-primary">Save Local Preference</button>
      </form>
      <p v-if="savedMessage" class="notice-box">{{ savedMessage }}</p>
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
