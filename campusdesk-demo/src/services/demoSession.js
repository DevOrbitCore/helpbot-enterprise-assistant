import { reactive } from "vue";
import { DEMO_USERS } from "../data/mockPortalData.js";

/**
 * Development-only demo user state.
 * Never use client-side role switching as an authorization mechanism in production.
 */
export const demoSession = reactive({
  currentUser: DEMO_USERS[0],
  users: DEMO_USERS,
  selectUserById(userId) {
    const found = DEMO_USERS.find((u) => u.user_id === userId);
    if (found) {
      this.currentUser = found;
    }
  },
});
