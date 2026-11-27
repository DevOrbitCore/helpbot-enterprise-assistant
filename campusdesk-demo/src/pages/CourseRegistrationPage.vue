<template>
  <div>
    <section class="card">
      <h3>Fall 2026 Course Registration (Fictional Catalog)</h3>
      <p class="muted">
        Review sample courses below. Try opening HelpBot and asking about add/drop deadlines or
        credit limits after seeding the sample knowledge files.
      </p>
      <table class="data-table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Course Title</th>
            <th>Credits</th>
            <th>Schedule</th>
            <th>Open Seats</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="course in courses" :key="course.code">
            <td><strong>{{ course.code }}</strong></td>
            <td>{{ course.title }}</td>
            <td>{{ course.credits }}</td>
            <td>{{ course.schedule }}</td>
            <td>{{ course.seatsAvailable }}</td>
            <td>{{ course.status }}</td>
            <td>
              <button type="button" class="btn" @click="toggleEnrollment(course)">
                {{ course.status === "Enrolled" ? "Drop (Demo)" : "Add (Demo)" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="notice-box">
        Total demo enrolled credits: <strong>{{ totalCredits }}</strong> (local browser state only).
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive } from "vue";
import { SAMPLE_COURSES } from "../data/mockPortalData.js";

const courses = reactive(SAMPLE_COURSES.map((c) => ({ ...c })));

const totalCredits = computed(() =>
  courses
    .filter((c) => c.status === "Enrolled")
    .reduce((sum, c) => sum + c.credits, 0)
);

function toggleEnrollment(course) {
  course.status = course.status === "Enrolled" ? "Open" : "Enrolled";
}
</script>
