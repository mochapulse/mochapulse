export interface Project {
  title: string;
  description: string;
  technologies: string[];
  repoUrl: string;
  // Whether the GitHub repository is public. Only public projects are shown on
  // the site so every "View on GitHub" link resolves for external visitors.
  public: boolean;
  // Total commits on the default branch; drives display priority.
  commits: number;
  category: "embedded" | "ai" | "web" | "research" | "tools";
  account: "mochapulse";
}

// Ordered by commit count (desc). Public projects first (these are the ones the
// site renders); private ones are kept below with `public: false` so they can
// be surfaced automatically once their repositories are made public.
export const projects: Project[] = [
  {
    title: "nexus-API",
    description:
      "A secure, lightweight 24/7 daemon API to monitor server telemetry (CPU, RAM, GPU), sniff systemd logs, and manage power states (sleep & shutdown). FastAPI backend with a React + TypeScript dashboard in progress.",
    technologies: ["Python", "FastAPI", "React", "TypeScript", "psutil", "systemd"],
    repoUrl: "https://github.com/mochapulse/nexus-API",
    public: true,
    commits: 68,
    category: "web",
    account: "mochapulse",
  },
  {
    title: "lan-controller-esp32",
    description:
      "ESP32 firmware built with ESP-IDF v6.0.2. Connects to Wi-Fi, serves an embedded web dashboard with real-time device status and Wake-on-LAN control, and exposes a JSON REST API. Credentials come from an embedded .env — no recompile needed.",
    technologies: ["C", "ESP32", "ESP-IDF", "Wake-on-LAN", "Web Dashboard"],
    repoUrl: "https://github.com/mochapulse/lan-controller-esp32",
    public: true,
    commits: 34,
    category: "embedded",
    account: "mochapulse",
  },
  {
    title: "MochaEduCardReporter",
    description:
      "A desktop application that reads Excel or CSV gradebooks and generates student report-card PDFs.",
    technologies: ["Python", "Tkinter", "PDF", "Excel/CSV"],
    repoUrl: "https://github.com/mochapulse/MochaEduCardReporter",
    public: true,
    commits: 33,
    category: "tools",
    account: "mochapulse",
  },
  {
    title: "LocalLLMTestingUsingLlamaCpp",
    description:
      "Experiments running and benchmarking local LLM inference on-device with llama.cpp.",
    technologies: ["C", "llama.cpp", "LLMs", "On-device AI"],
    repoUrl: "https://github.com/mochapulse/LocalLLMTestingUsingLlamaCpp",
    public: true,
    commits: 2,
    category: "ai",
    account: "mochapulse",
  },
  {
    title: "KyubeyV1-telegram-bot",
    description:
      "A conversational Telegram bot modeled as an AI agent — user → conversation → options → decision → action — coordinating permissions, tools, and external actions over a chat channel.",
    technologies: ["Python", "Telegram", "AI Agent"],
    repoUrl: "https://github.com/mochapulse/KyubeyV1-telegram-bot",
    public: true,
    commits: 2,
    category: "ai",
    account: "mochapulse",
  },
  {
    title: "wsl-usb-autoattach",
    description:
      "Windows service plus Python tooling that automatically attaches USB devices into WSL via usbipd, with reusable libraries for device tracking and configuration.",
    technologies: ["Python", "usbipd", "WinSW", "pywin32", "WSL"],
    repoUrl: "https://github.com/mochapulse/wsl-usb-autoattach",
    public: true,
    commits: 2,
    category: "tools",
    account: "mochapulse",
  },
  {
    title: "MochaMetadataRadioRecorder",
    description:
      "A passive, out-of-band RTP metadata sniffer and Quantify API integrator for radio dispatch recording. Captures RTP traffic from Omnitronics DRG100 gateways, extracts radio IDs from RFC 5285 header extensions, and pushes metadata to the recorder without touching the audio flow.",
    technologies: ["Python", "C++", "RTP", "Npcap", "REST API", "Kubernetes"],
    repoUrl: "https://github.com/mochapulse/MochaMetadataRadioRecorder",
    public: false,
    commits: 99,
    category: "research",
    account: "mochapulse",
  },
  {
    title: "DotenvFiles",
    description:
      "Personal dotfiles for Ubuntu/WSL + Windows: zsh (Oh My Zsh + custom purple-ai theme) and kitty setup, multi-account Git/SSH conditional identity routing, and Windows/WSL utilities including a .NET USB auto-bind service.",
    technologies: ["Shell", "C#", "AutoHotkey", "WSL", "Git"],
    repoUrl: "https://github.com/mochapulse/DotenvFiles",
    public: false,
    commits: 14,
    category: "tools",
    account: "mochapulse",
  },
  {
    title: "NodeSpectrum",
    description:
      "Hybrid C + Python edge stack for RF/telemetry workflows. C binaries handle the IPC runtime and LTE/GPS + GPIO hardware integration; Python drives async ZeroMQ control, IQ ring orchestration, and PSD capture from SDR devices.",
    technologies: ["C", "Python", "SDR", "ZeroMQ", "LTE/GPS", "Raspberry Pi"],
    repoUrl: "https://github.com/mochapulse/NodeSpectrum",
    public: false,
    commits: 13,
    category: "embedded",
    account: "mochapulse",
  },
  {
    title: "MochaStorageFileSystem",
    description:
      "Personal file system in the cloud: a FastAPI backend and React frontend with SQLite storage, containerized behind Nginx with Docker Compose.",
    technologies: ["TypeScript", "React", "Python", "FastAPI", "SQLite", "Docker"],
    repoUrl: "https://github.com/mochapulse/MochaStorageFileSystem",
    public: false,
    commits: 7,
    category: "web",
    account: "mochapulse",
  },
  {
    title: "MochaChefAgent",
    description:
      "A multi-agent AI meal planner that generates personalized, budget-aware recipes. A Playwright \"Shopper\" agent scrapes regional grocery prices worldwide and vision models parse them, so a \"Chef\" agent can optimize meals against real local supply.",
    technologies: ["Python", "Multi-Agent AI", "Playwright", "Vision Models"],
    repoUrl: "https://github.com/mochapulse/MochaChefAgent",
    public: false,
    commits: 4,
    category: "ai",
    account: "mochapulse",
  },
  {
    title: "ERP-Mapurito",
    description:
      "Sales, inventory, invoicing, accounting, and business-analytics ERP. FastAPI REST backend with a PySide6 desktop client (and a proposed Tauri + React frontend) over PostgreSQL.",
    technologies: ["Python", "FastAPI", "PostgreSQL", "PySide6", "Tauri"],
    repoUrl: "https://github.com/mochapulse/ERP-Mapurito",
    public: false,
    commits: 4,
    category: "web",
    account: "mochapulse",
  },
  {
    title: "NodeSpectrumCpp",
    description:
      "C++ variant of the NodeSpectrum SDR edge stack, with a scripted build/run workflow for RF capture and processing.",
    technologies: ["C++", "SDR", "DSP", "CMake"],
    repoUrl: "https://github.com/mochapulse/NodeSpectrumCpp",
    public: false,
    commits: 3,
    category: "embedded",
    account: "mochapulse",
  },
];

// Projects shown on the site: public only, highest commit count first.
export const featuredProjects = projects
  .filter((p) => p.public)
  .sort((a, b) => b.commits - a.commits);
