/**
 * ============================================================================
 *  EDIT THIS FILE TO PERSONALIZE YOUR SITE.
 *  This is the single source of truth for all content on the site.
 * ============================================================================
 */

export const profile = {
  name: "Tushar Sivakumar",
  navMark: "TS",
  tagline: "Student · AI & Robotics · CS Educator",
  location: "Acton, MA",
  headshot: "/headshot.jpg", // replace public/headshot.jpg with your own photo
  resumeUrl: "/resume.pdf", // drop your resume in public/resume.pdf

  hero: {
    blurb:
      "I'm a high schooler from Acton, MA exploring the intersection of computer science, AI, and robotics — through research programs, teaching, and building things that solve real problems.",
  },

  about: [
    "I'm a student at Acton-Boxborough Regional High School with a strong interest in computer science, research, leadership, and community service. Through my school's Computer Science and Research Clubs, I explore emerging technologies, sharpen my technical skills, and apply problem-solving to real-world challenges.",
    "As Co-President of the Acton Institute of Computer Science, I teach advanced Python and help other students get into programming. I've spent recent summers in AI and robotics programs — including the MIT Jameel Clinic AI & Health Bootcamp, Inspirit AI, and a research internship with Mitsubishi Electric Research Laboratories.",
    "Outside of tech, I'm a Second Dan black belt and USA Taekwondo certified referee, a member of my school's marching band, and a School Committee Representative. I'm a two-time recipient of the President's Volunteer Service Award (Gold) for over 100 hours of community service each year.",
  ],

  quickFacts: [
    { label: "Focus", value: "AI/ML, Robotics, CS Education" },
    { label: "School", value: "Acton-Boxborough HS, Class of 2028" },
    { label: "Based in", value: "Acton, Massachusetts" },
    { label: "Also", value: "2nd Dan Black Belt & TKD Referee" },
  ],

  socials: {
    github: "https://github.com/TusharSivakumar",
    linkedin: "https://www.linkedin.com/in/tushar-sivakumar-8a5403344/",
    email: "tushars2028@gmail.com",
    x: "",
    youtube: "",
  },
};

// ---------------------------------------------------------------------------
//  SKILLS
// ---------------------------------------------------------------------------
export const skills: { category: string; items: string[] }[] = [
  { category: "Languages", items: ["Python", "Java", "C++"] },
  {
    category: "AI & Machine Learning",
    items: [
      "Machine Learning",
      "Neural Networks",
      "CNNs",
      "Natural Language Processing",
      "Computer Vision",
      "Data Analysis",
    ],
  },
  {
    category: "Robotics & Hardware",
    items: ["Robotics", "Arduino", "Raspberry Pi", "Electrical Wiring", "Motor Control"],
  },
  {
    category: "Leadership & More",
    items: ["Teaching", "Management", "Presentation Skills", "Refereeing"],
  },
];

// ---------------------------------------------------------------------------
//  EXPERIENCE (most recent first)
// ---------------------------------------------------------------------------
export interface ExperienceItem {
  role: string;
  org: string;
  period: string;
  location?: string;
  description: string;
  tags?: string[];
}

export const experience: ExperienceItem[] = [
  {
    role: "Co-President",
    org: "Acton Institute of Computer Science",
    period: "Mar 2025 - Present",
    location: "Acton, MA",
    description:
      "Lead a student-run computer science institute: teach advanced Python, direct and support other teachers, build curriculum, and recruit students into the Java and Python programs.",
    tags: ["Teaching", "Leadership", "Python", "Curriculum"],
  },
  {
    role: "AI & Health Summer Bootcamp",
    org: "MIT Jameel Clinic",
    period: "Jul 2026",
    location: "Cambridge, MA",
    description:
      "A selective week-long bootcamp on applications of AI in healthcare, taught by MIT professors and practicing doctors.",
    tags: ["Machine Learning", "Neural Networks", "CNNs", "Data Analysis"],
  },
  {
    role: "AI Scholars Program",
    org: "Inspirit AI",
    period: "Jun 2026 - Jul 2026",
    location: "Remote",
    description:
      "An intensive program on the fundamentals of AI and how to build it in code, culminating in a team project and presentation.",
    tags: ["Python", "Machine Learning", "Presentation Skills"],
  },
  {
    role: "Electronics & Robotics",
    org: "Boston Leadership Institute",
    period: "Jul 2025 - Aug 2025",
    location: "Waltham, MA",
    description:
      "A hands-on course in electronics and robotics — building circuits and control systems with Arduino.",
    tags: ["Arduino", "C++", "Electrical Wiring", "Motor Control"],
  },
  {
    role: "AI Scholar",
    org: "Veritas AI",
    period: "Jun 2025 - Jul 2025",
    location: "Remote",
    description:
      "Applied machine learning to cryptocurrency trading strategies in a mentored high-school research program.",
    tags: ["Machine Learning", "Data Analysis"],
  },
  {
    role: "Research Intern — SMART-101 Dataset",
    org: "Mitsubishi Electric Research Laboratories (MERL)",
    period: "Jun 2024 - Aug 2024",
    location: "Remote",
    description:
      "Contributed to the SMART-101 effort — authoring problems to benchmark and improve LLMs' ability to solve grade-school Math Olympiad-style reasoning tasks.",
    tags: ["Python", "LLMs", "Research"],
  },
  {
    role: "Robotics Summer Program",
    org: "Evodyne Robotics",
    period: "Jun 2023 - Jul 2023",
    location: "Remote",
    description:
      "Learned robotics and programming with Arduino and Raspberry Pi, including an introduction to computer vision.",
    tags: ["Robotics", "Computer Vision", "Raspberry Pi"],
  },
  {
    role: "Taekwondo Referee",
    org: "Eastern Collegiate Taekwondo Conference (ECTC)",
    period: "Oct 2025",
    location: "MIT · Cambridge, MA",
    description:
      "Refereed matches at collegiate Taekwondo tournaments hosted at MIT.",
    tags: ["Refereeing", "Taekwondo"],
  },
];

// ---------------------------------------------------------------------------
//  EDUCATION
// ---------------------------------------------------------------------------
export interface EducationItem {
  school: string;
  credential: string;
  period: string;
  description?: string;
  highlights?: string[];
}

export const education: EducationItem[] = [
  {
    school: "Acton-Boxborough Regional High School",
    credential: "High School Diploma · Class of 2028",
    period: "2024 - 2028",
    description:
      "FRC Robotics Team · Marching Band · Research Club · Computer Science Club · School Committee Representative.",
    highlights: [
      "AP Biology: 5",
      "AP Macroeconomics: 5",
      "AP Environmental Science: 5",
      "AP Computer Science A: 4",
    ],
  },
  {
    school: "Harvard University / edX",
    credential: "CS50: Introduction to Artificial Intelligence with Python",
    period: "2025 - 2026",
    description:
      "Machine learning, neural networks, natural language processing, search, and more.",
  },
];

// ---------------------------------------------------------------------------
//  AWARDS & HONORS
// ---------------------------------------------------------------------------
export interface Award {
  title: string;
  issuer: string;
  year: string;
}

export const awards: Award[] = [
  { title: "AP Scholar with Honor", issuer: "College Board", year: "2026" },
  {
    title: "ACSL Senior Division Finals Qualifier",
    issuer: "American Computer Science League",
    year: "2026",
  },
  {
    title: "President's Volunteer Service Award — Gold (100+ hrs)",
    issuer: "Acton-Boxborough RHS",
    year: "2024 & 2025",
  },
  {
    title: "5x Medalist, MA State Tournament",
    issuer: "USA Taekwondo",
    year: "",
  },
  {
    title: "Second Dan Black Belt",
    issuer: "World Taekwondo",
    year: "2025",
  },
  {
    title: "Certified Martial Arts Referee",
    issuer: "USA Taekwondo",
    year: "2025",
  },
];

// ---------------------------------------------------------------------------
//  PROJECTS
//  (Only your portfolio repo is public right now, so these are drawn from your
//   real work. Add GitHub links / more projects any time.)
// ---------------------------------------------------------------------------
export interface Project {
  title: string;
  description: string;
  technologies: string[];
  image?: string;
  emoji?: string;
  link?: string;
  github?: string;
  badge?: string;
}

export const projects: Project[] = [
  {
    title: "SMART-101 — LLM Math Reasoning",
    description:
      "Research at Mitsubishi Electric Research Labs authoring problems to benchmark and improve large language models on grade-school Math Olympiad reasoning.",
    technologies: ["Python", "LLMs", "Research"],
    emoji: "\u{1F9E0}",
    badge: "Research",
  },
  {
    title: "FRC Competition Robotics",
    description:
      "Member of my school's FIRST Robotics Competition team, contributing to build-season engineering for a competition robot.",
    technologies: ["Robotics", "CAD", "Java"],
    emoji: "\u{1F916}",
    badge: "Robotics",
  },
  {
    title: "This Website",
    description:
      "A personal site built from scratch with React, TypeScript, and Tailwind, deployed on GitHub Pages.",
    technologies: ["React", "TypeScript", "Tailwind CSS"],
    emoji: "\u{1F310}",
    link: "https://github.com/TusharSivakumar/tusharsivakumar.github.io",
    github: "https://github.com/TusharSivakumar/tusharsivakumar.github.io",
    badge: "Live",
  },
];
