<template>
  <div>
    <section class="card">
      <div class="card-header">
        <div class="card-header-text">
          <h3>Campus Facilities & Study Spaces</h3>
          <p class="card-subtitle">
            Sample directory of campus buildings, opening hours, and study pod reservation
            guidelines.
          </p>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Facility</th>
              <th>Building</th>
              <th>Hours</th>
              <th>Booking Rule</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="facility in CAMPUS_FACILITIES" :key="facility.name">
              <td class="cell-primary">{{ facility.name }}</td>
              <td>{{ facility.building }}</td>
              <td class="cell-nowrap">
                <span class="erp-badge erp-badge-neutral">{{ facility.hours }}</span>
              </td>
              <td>{{ facility.bookingRule }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { CAMPUS_FACILITIES } from "../data/mockPortalData.js";
</script>
