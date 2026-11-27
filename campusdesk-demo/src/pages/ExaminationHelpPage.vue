<template>
  <div>
    <section class="card">
      <h3>Upcoming Examination Schedule (Demo Timetable)</h3>
      <p class="muted">
        Students can query HelpBot about ID requirements, calculator rules, or medical makeup exam
        procedures documented in the examination handbook.
      </p>
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
            <td><strong>{{ exam.course }}</strong></td>
            <td>{{ exam.examType }}</td>
            <td>{{ exam.date }}</td>
            <td>{{ exam.time }}</td>
            <td>{{ exam.room }}</td>
            <td><code>{{ exam.seatNumber }}</code></td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { EXAM_SCHEDULE } from "../data/mockPortalData.js";
</script>
