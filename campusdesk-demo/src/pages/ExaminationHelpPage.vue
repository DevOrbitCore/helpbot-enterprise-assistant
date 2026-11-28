<template>
  <div>
    <section class="card">
      <div class="card-header">
        <div class="card-header-text">
          <h3>Upcoming Examination Schedule (Demo Timetable)</h3>
          <p class="card-subtitle">
            Students can query HelpBot about ID requirements, calculator rules, or medical makeup
            exam procedures documented in the examination handbook.
          </p>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Course</th>
              <th>Assessment</th>
              <th>Date</th>
              <th>Time</th>
              <th>Location</th>
              <th>Seat</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="exam in EXAM_SCHEDULE" :key="exam.course">
              <td>
                <span class="erp-code-pill">{{ exam.course }}</span>
              </td>
              <td class="cell-primary">{{ exam.examType }}</td>
              <td class="cell-nowrap">{{ exam.date }}</td>
              <td class="cell-nowrap">{{ exam.time }}</td>
              <td>{{ exam.room }}</td>
              <td><code>{{ exam.seatNumber }}</code></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { EXAM_SCHEDULE } from "../data/mockPortalData.js";
</script>
