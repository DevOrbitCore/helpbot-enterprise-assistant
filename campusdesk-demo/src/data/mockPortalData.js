/**
 * Fictional test data for CampusDesk Student Services Portal.
 * No real student records, credentials, or payment gateways are used.
 */

export const DEMO_USERS = [
  {
    user_id: "stu-maya-chen",
    display_name: "Maya Chen (Demo Student)",
    role: "student",
    program: "B.Sc. Computer Science — Year 2",
    advisor: "Dr. Elena Navarro",
    campus: "Northridge Academic Campus",
    locale: "en-US",
  },
  {
    user_id: "ta-rohan-kulkarni",
    display_name: "Rohan Kulkarni (Demo Teaching Assistant)",
    role: "ta",
    program: "M.Sc. Data Systems — Graduate TA",
    advisor: "Prof. Samuel Osei",
    campus: "Northridge Academic Campus",
    locale: "en-US",
  },
  {
    user_id: "adv-elena-navarro",
    display_name: "Elena Navarro (Demo Academic Advisor)",
    role: "advisor",
    program: "Office of Undergraduate Advising",
    advisor: "Dean of Academic Services",
    campus: "Northridge Academic Campus",
    locale: "en-US",
  },
];

export const SAMPLE_COURSES = [
  {
    code: "CS-204",
    title: "Data Structures & Algorithms",
    credits: 4,
    schedule: "Mon / Wed 10:00 - 11:30",
    seatsAvailable: 14,
    status: "Enrolled",
  },
  {
    code: "CS-218",
    title: "Web Systems Architecture",
    credits: 3,
    schedule: "Tue / Thu 13:30 - 15:00",
    seatsAvailable: 6,
    status: "Open",
  },
  {
    code: "STAT-210",
    title: "Applied Probability for Computing",
    credits: 3,
    schedule: "Mon / Wed 14:00 - 15:30",
    seatsAvailable: 21,
    status: "Enrolled",
  },
  {
    code: "HUM-142",
    title: "Technical Communication & Ethics",
    credits: 2,
    schedule: "Fri 09:30 - 11:30",
    seatsAvailable: 9,
    status: "Open",
  },
];

export const LIBRARY_LOANS = [
  {
    callNumber: "QA76.9.A43",
    title: "Foundations of Algorithmic Thinking (3rd Ed.)",
    dueDate: "2026-12-12",
    renewalsLeft: 2,
    branch: "Central Science Library",
  },
  {
    callNumber: "TK5105.888",
    title: "Modern Distributed Web Services",
    dueDate: "2026-12-05",
    renewalsLeft: 1,
    branch: "Engineering Reading Room",
  },
];

export const EXAM_SCHEDULE = [
  {
    course: "CS-204",
    examType: "Final Written Exam",
    date: "2026-12-16",
    time: "09:00 - 12:00",
    room: "Hall B — Room 204",
    seatNumber: "B-204-19",
  },
  {
    course: "STAT-210",
    examType: "Final Written Exam",
    date: "2026-12-19",
    time: "14:00 - 17:00",
    room: "Science Pavilion — Auditorium 1",
    seatNumber: "SP-01-42",
  },
];

export const CAMPUS_FACILITIES = [
  {
    name: "Innovation Lab Study Pods (Pods A1 - A8)",
    building: "Technology Commons, Floor 2",
    hours: "07:00 - 22:00",
    bookingRule: "Up to 2 hours per student per day",
  },
  {
    name: "Quiet Reading Conservatory",
    building: "Central Library, Floor 4",
    hours: "08:00 - 23:00",
    bookingRule: "Walk-in seating; silent zone",
  },
  {
    name: "Student Wellness & Recreation Center",
    building: "West Campus Pavilion",
    hours: "06:30 - 21:30",
    bookingRule: "Student ID card required at entry",
  },
];

export const FEE_STATEMENT_ITEMS = [
  {
    item: "Semester Tuition (12 - 18 Credit Band)",
    term: "Fall 2026",
    amountDisplay: "$3,850.00 (Demo)",
    dueDate: "2026-09-15",
    status: "Paid (Sample)",
  },
  {
    item: "Campus Library & Digital Resources Fee",
    term: "Fall 2026",
    amountDisplay: "$120.00 (Demo)",
    dueDate: "2026-09-15",
    status: "Paid (Sample)",
  },
  {
    item: "Laboratory & Computing Access Fee",
    term: "Fall 2026",
    amountDisplay: "$185.00 (Demo)",
    dueDate: "2026-12-01",
    status: "Pending (Sample)",
  },
];
