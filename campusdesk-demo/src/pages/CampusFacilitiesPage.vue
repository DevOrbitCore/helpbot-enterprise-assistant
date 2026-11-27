<template>
  <div>
    <section class="card">
      <h3>Campus Facilities & Study Spaces</h3>
      <p class="muted">
        Sample directory of campus buildings, opening hours, and study pod reservation guidelines.
      </p>
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
            <td><strong>{{ facility.name }}</strong></td>
            <td>{{ facility.building }}</td>
            <td>{{ facility.hours }}</td>
            <td>{{ facility.bookingRule }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { CAMPUS_FACILITIES } from "../data/mockPortalData.js";
</script>
