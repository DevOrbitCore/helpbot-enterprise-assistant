import { createRouter, createWebHistory } from "vue-router";

import StudentProfilePage from "../pages/StudentProfilePage.vue";
import CourseRegistrationPage from "../pages/CourseRegistrationPage.vue";
import LibraryServicesPage from "../pages/LibraryServicesPage.vue";
import ExaminationHelpPage from "../pages/ExaminationHelpPage.vue";
import CampusFacilitiesPage from "../pages/CampusFacilitiesPage.vue";
import FeeInformationPage from "../pages/FeeInformationPage.vue";

export const PORTAL_ROUTES = [
  {
    path: "/",
    redirect: "/profile",
  },
  {
    path: "/profile",
    name: "student-profile",
    component: StudentProfilePage,
    meta: {
      module_id: "student-profile",
      screen_id: "profile-summary",
      page_title: "Student Profile",
      nav_subtitle: "Identity & Advising",
    },
  },
  {
    path: "/courses",
    name: "course-registration",
    component: CourseRegistrationPage,
    meta: {
      module_id: "course-registration",
      screen_id: "registration-overview",
      page_title: "Course Registration",
      nav_subtitle: "Enroll, Add & Drop",
    },
  },
  {
    path: "/library",
    name: "library-services",
    component: LibraryServicesPage,
    meta: {
      module_id: "library-services",
      screen_id: "borrowing-rules",
      page_title: "Library Services",
      nav_subtitle: "Loans & Renewals",
    },
  },
  {
    path: "/exams",
    name: "examination-help",
    component: ExaminationHelpPage,
    meta: {
      module_id: "examination-help",
      screen_id: "exam-schedule",
      page_title: "Examination Help",
      nav_subtitle: "Timetable & Policies",
    },
  },
  {
    path: "/facilities",
    name: "campus-facilities",
    component: CampusFacilitiesPage,
    meta: {
      module_id: "campus-facilities",
      screen_id: "facility-booking",
      page_title: "Campus Facilities",
      nav_subtitle: "Study Pods & Hours",
    },
  },
  {
    path: "/fees",
    name: "fee-information",
    component: FeeInformationPage,
    meta: {
      module_id: "fee-information",
      screen_id: "tuition-summary",
      page_title: "Fee Information",
      nav_subtitle: "Demo Statement",
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: PORTAL_ROUTES,
});

export default router;
