<template>
  <div>
    <section class="card">
      <div class="card-header">
        <div class="card-header-text">
          <h3>Fall 2026 Course Registration (Fictional Catalog)</h3>
          <p class="card-subtitle">
            Review sample courses below. Try opening HelpBot and asking about add/drop deadlines or
            credit limits after seeding the sample knowledge files.
          </p>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Course Title</th>
              <th class="col-numeric">Credits</th>
              <th>Schedule</th>
              <th class="col-numeric">Open Seats</th>
              <th>Status</th>
              <th class="col-action">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.code">
              <td>
                <span class="erp-code-pill">{{ course.code }}</span>
              </td>
              <td class="cell-primary">{{ course.title }}</td>
              <td class="col-numeric">{{ course.credits }}</td>
              <td class="cell-nowrap">{{ course.schedule }}</td>
              <td class="col-numeric">{{ course.seatsAvailable }}</td>
              <td>
                <span
                  class="erp-badge"
                  :class="course.status === 'Enrolled' ? 'erp-badge-success' : 'erp-badge-neutral'"
                >
                  {{ course.status }}
                </span>
              </td>
              <td class="col-action">
                <button
                  type="button"
                  class="btn btn-sm"
                  :class="course.status === 'Enrolled' ? 'btn-subtle-danger' : 'btn-primary'"
                  @click="toggleEnrollment(course)"
                >
                  {{ course.status === "Enrolled" ? "Drop (Demo)" : "Add (Demo)" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

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
