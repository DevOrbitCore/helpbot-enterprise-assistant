<template>
  <div>
    <section class="card">
      <h3>Fee Information (Fictional Reference Statement)</h3>
      <p class="muted">
        This page displays static fictional fee line items for demonstration only. CampusDesk does
        not collect payment details or process real financial transactions.
      </p>
      <table class="data-table">
        <thead>
          <tr>
            <th>Fee Item</th>
            <th>Term</th>
            <th>Sample Amount</th>
            <th>Due Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="fee in FEE_STATEMENT_ITEMS" :key="fee.item">
            <td><strong>{{ fee.item }}</strong></td>
            <td>{{ fee.term }}</td>
            <td>{{ fee.amountDisplay }}</td>
            <td>{{ fee.dueDate }}</td>
            <td>{{ fee.status }}</td>
          </tr>
        </tbody>
      </table>
      <div class="notice-box">
        Privacy boundary: No billing credentials or account numbers exist in this portal, and none
        are ever exposed to the HelpBot adapter.
      </div>
    </section>
  </div>
</template>

<script setup>
import { FEE_STATEMENT_ITEMS } from "../data/mockPortalData.js";
</script>
