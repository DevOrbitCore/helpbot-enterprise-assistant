<template>
  <div>
    <section class="card">
      <div class="card-header">
        <div class="card-header-text">
          <h3>Fee Information (Fictional Reference Statement)</h3>
          <p class="card-subtitle">
            This page displays static fictional fee line items for demonstration only. CampusDesk
            does not collect payment details or process real financial transactions.
          </p>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Fee Item</th>
              <th>Term</th>
              <th class="col-numeric">Sample Amount</th>
              <th>Due Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="fee in FEE_STATEMENT_ITEMS" :key="fee.item">
              <td class="cell-primary">{{ fee.item }}</td>
              <td class="cell-nowrap">{{ fee.term }}</td>
              <td class="col-numeric">{{ fee.amountDisplay }}</td>
              <td class="cell-nowrap">{{ fee.dueDate }}</td>
              <td>
                <span
                  class="erp-badge"
                  :class="fee.status.startsWith('Paid') ? 'erp-badge-success' : 'erp-badge-warning'"
                >
                  {{ fee.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

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
