<template>
  <div>
    <section class="card">
      <h3>Active Library Loans (Sample Records)</h3>
      <p class="muted">
        Ask HelpBot about loan periods, renewals, or overdue fine caps using the uploaded library
        borrowing guide.
      </p>
      <table class="data-table">
        <thead>
          <tr>
            <th>Call Number</th>
            <th>Book Title</th>
            <th>Branch</th>
            <th>Due Date</th>
            <th>Renewals Left</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loan in LIBRARY_LOANS" :key="loan.callNumber">
            <td><code>{{ loan.callNumber }}</code></td>
            <td>{{ loan.title }}</td>
            <td>{{ loan.branch }}</td>
            <td>{{ loan.dueDate }}</td>
            <td>{{ loan.renewalsLeft }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { LIBRARY_LOANS } from "../data/mockPortalData.js";
</script>
