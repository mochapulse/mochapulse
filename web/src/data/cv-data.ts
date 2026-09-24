export const personalInfo = {
  name: "mochapulse",
  title: "Homelab & Embedded Systems Builder",
  location: "Manizales, Colombia",
  email: "mochapulse@gmail.com",
  phone: "+57 3106801331",
  linkedin: "https://linkedin.com/in/david-ramirez-betancourth-b5ba80279",
  github: "https://github.com/mochapulse",
  githubEdu: "https://github.com/dramirezbe",
  summary:
    "Personal engineering account for self-hosted infrastructure, embedded firmware, and local AI. I build 24/7 server daemons and telemetry APIs, ESP32 and SDR sensor nodes, personal cloud storage, and on-device LLM tooling — end-to-end systems that run a homelab from bare metal to dashboard.",
};

export interface Education {
  degree: string;
  institution: string;
  period: string;
  details: string[];
}

export const education: Education[] = [
  {
    degree: "MSc in Industrial Automation",
    institution: "National University of Colombia",
    period: "Jan 2026 - Present",
    details: [
      "Research Areas: Artificial Intelligence, Machine Learning applied to RF, Computational Structures, and Optimization",
    ],
  },
  {
    degree: "BS in Electronic Engineering",
    institution: "National University of Colombia",
    period: "Jul 2022 - Jun 2026",
    details: [
      "Cumulative GPA: 4.2/5.0",
      "Focus Areas: Digital Signal Processing (DSP), Software Defined Radio (SDR), Hardware Design, and IoT Systems",
    ],
  },
];

export interface Experience {
  role: string;
  company: string;
  location: string;
  period: string;
  highlights: string[];
}

export const experience: Experience[] = [
  {
    role: "Researcher and Developer",
    company: "GCPDS Research Group",
    location: "Manizales, Colombia",
    period: "Oct 2024 - Present",
    highlights: [
      "C/Python firmware development for an IoT spectral monitoring sensor based on HackRF SDR on Raspberry Pi 5, with hybrid architecture (C for real-time IQ acquisition, Python for orchestration), autonomous PPM calibration, and WebRTC streaming",
      "Backend platform implementation with REST API (FastAPI), TimescaleDB time-series database, and real-time spectral visualization dashboard",
      "Mobile application development for deployment and validation of Image Segmentation models",
    ],
  },
  {
    role: "Undergraduate Fellow",
    company: "National University of Colombia",
    location: "Manizales, Colombia",
    period: "2024",
    highlights: [
      "Academic teaching assistant for Signals and Systems and Machine Learning Theory, advising groups of 30+ students",
      "Design and instruction of hands-on Python workshops for signal analysis and processing, integrating NumPy, SciPy, and Matplotlib",
    ],
  },
];

export interface SkillCategory {
  category: string;
  items: string[];
}

export const skills: SkillCategory[] = [
  {
    category: "Languages",
    items: ["C99", "C++", "Python", "JavaScript", "TypeScript", "Verilog", "SQL"],
  },
  {
    category: "Frameworks & Platforms",
    items: [
      "FastAPI",
      "Django",
      "React",
      "Vite",
      "Node.js",
      "GNU Radio",
      "SoapySDR",
      "HackRF One",
      "FPGAs (Gowin EDA)",
    ],
  },
  {
    category: "Infrastructure & Tools",
    items: [
      "Linux",
      "Docker",
      "CMake",
      "ZMQ",
      "WebRTC",
      "TimescaleDB",
      "Git",
      "Raspberry Pi",
      "GPS/LTE",
    ],
  },
];

export const languages = [
  { language: "Spanish", level: "Native" },
  { language: "English", level: "Intermediate (B1)" },
];
