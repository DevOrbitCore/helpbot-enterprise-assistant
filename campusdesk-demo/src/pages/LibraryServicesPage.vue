<template>
  <div>
    <section class="card">
      <div class="card-header">
        <div class="card-header-text">
          <h3>Active Library Loans (Sample Records)</h3>
          <p class="card-subtitle">
            Ask HelpBot about loan periods, renewals, or overdue fine caps using the uploaded
            library borrowing guide.
          </p>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Call Number</th>
              <th>Book Title</th>
              <th>Branch</th>
              <th>Due Date</th>
              <th class="col-numeric">Renewals Left</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="loan in LIBRARY_LOANS" :key="loan.callNumber">
              <td><code>{{ loan.callNumber }}</code></td>
              <td class="cell-primary">{{ loan.title }}</td>
              <td>{{ loan.branch }}</td>
              <td class="cell-nowrap">{{ loan.dueDate }}</td>
              <td class="col-numeric">
                <span class="erp-badge erp-badge-info">{{ loan.renewalsLeft }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { LIBRARY_LOANS } from "../data/mockPortalData.js";
</script>
