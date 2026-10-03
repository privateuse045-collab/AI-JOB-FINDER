import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import "./App.css";

// ============================================================
// PROFILE PAGE
// ============================================================

function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState({
    name: "",
    skills: "",
    experience: "",
    location: "",
    preferred_role: "",
    expected_salary: "",
  });

  const [fetchingProfile, setFetchingProfile] = useState(true);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileMessage, setProfileMessage] = useState("");
  const [profileError, setProfileError] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      setFetchingProfile(true);

      try {
        const response = await fetch("http://127.0.0.1:8000/api/profile");

        if (response.ok) {
          const data = await response.json();

          if (data.success && data.profile) {
            setProfile({
              name: data.profile.name || "",
              skills: Array.isArray(data.profile.skills)
                ? data.profile.skills.join(", ")
                : (data.profile.skills || ""),
              experience: data.profile.experience || "",
              location: data.profile.location || "",
              preferred_role: data.profile.preferred_role || "",
              expected_salary: data.profile.expected_salary || "",
            });
          }
        }
      } catch (error) {
        console.error("Failed to load user profile:", error);
      } finally {
        setFetchingProfile(false);
      }
    };

    fetchProfile();
  }, []);

  const saveProfile = async () => {
    setProfileLoading(true);
    setProfileMessage("");
    setProfileError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/profile",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: profile.name,

            skills: profile.skills
              .split(",")
              .map((skill) => skill.trim())
              .filter((skill) => skill !== ""),

            experience: profile.experience,
            location: profile.location,
            preferred_role: profile.preferred_role,
            expected_salary: profile.expected_salary,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Profile save failed");
      }

      const data = await response.json();

      console.log("Profile Save Response:", data);

      if (data.success) {
        setProfileMessage("✅ Profile saved successfully!");
      } else {
        setProfileError(
          data.message || "Profile save nahi ho payi."
        );
      }

    } catch (error) {
      console.error(error);

      setProfileError(
        "Backend se connection nahi ho pa raha. Please check FastAPI server."
      );

    } finally {
      setProfileLoading(false);
    }
  };

  return (
    <div className="app">

      {/* ======================================================
          PROFILE PAGE HEADER
      ====================================================== */}

      <header className="header">

        <div>
          <h1>🤖 AI Job Finder</h1>

          <p>
            Your AI-powered career assistant
          </p>
        </div>

        <button
          className="voice-button">
          🎤 Talk to AI
        </button>

      </header>


      {/* ======================================================
          PROFILE FORM
      ====================================================== */}

      <main className="dashboard">

        <section className="profile-section">

          <div className="profile-card">

            <div className="profile-header">

                <h2>
                  👤 My Profile
                </h2>

                <button
                className="close-button"
                onClick={() => navigate("/")}
                >
                 ✕
                </button>

            </div>

                <p>
                  Complete your profile so AI can find better jobs for you.
                </p>

                {fetchingProfile && (
                  <p className="status-message">
                    ⏳ Loading profile...
                  </p>
                )}
              

            {/* NAME */}

            <label>
              Name
            </label>

            <input
              type="text"
              value={profile.name}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  name: event.target.value
                })
              }
              placeholder="Enter your name"
            />


            {/* SKILLS */}

            <label>
              Skills
            </label>

            <input
              type="text"
              value={profile.skills}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  skills: event.target.value
                })
              }
              placeholder="Python, FastAPI, SQL, Git"
            />

            <small>
              Multiple skills ko comma (,) se separate karo.
            </small>


            {/* EXPERIENCE */}

<label>
  Experience
</label>

<select
  value={profile.experience}
  onChange={(event) =>
    setProfile({
      ...profile,
      experience: event.target.value,
    })
  }
>
  <option value="">Select Experience</option>
  <option value="Fresher">Fresher</option>
  <option value="0-1 Year">0–1 Year</option>
  <option value="1-2 Years">1–2 Years</option>
  <option value="2-3 Years">2–3 Years</option>
  <option value="3-5 Years">3–5 Years</option>
  <option value="5-10 Years">5–10 Years</option>
  <option value="10+ Years">10+ Years</option>
</select>

            {/* LOCATION */}

            <label>
              Location
            </label>

            <input
              type="text"
              value={profile.location}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  location: event.target.value,
                })
              }
              placeholder="Mumbai"
            />


            {/* PREFERRED ROLE */}

            <label>
              Preferred Role
            </label>

            <input
              type="text"
              value={profile.preferred_role}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  preferred_role: event.target.value,
                })
              }
              placeholder="Python Developer"
            />


            {/* EXPECTED SALARY */}

            <label>
              Expected Salary
            </label>

            <input
              type="text"
              value={profile.expected_salary}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  expected_salary: event.target.value,
                })
              }
              placeholder="8 LPA"
            />


            {/* SAVE BUTTON */}

            <button
              className="primary-button"
              onClick={saveProfile}
              disabled={profileLoading}
            >

              {profileLoading
                ? "⏳ Saving Profile..."
                : "💾 Save Profile"}

            </button>


            {/* SUCCESS MESSAGE */}

            {profileMessage && (
              <p className="success-message">
                {profileMessage}
              </p>
            )}


            {/* ERROR MESSAGE */}

            {profileError && (
              <p className="error-message">
                ❌ {profileError}
              </p>
            )}

          </div>

        </section>

      </main>


      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer>

        <p>
          AI Job Finder • AI-powered career assistance
        </p>

      </footer>

    </div>
  );
}

// ============================================================
// SKILL DISPLAY NORMALIZATION
// ============================================================

const SAFE_SKILL_DISPLAY_MAP = {
  // Acronyms & exact casing
  "bms": "BMS",
  "building management system": "BMS",
  "building management systems": "BMS",
  "building management system (bms)": "BMS",
  "building management systems (bms)": "BMS",
  "building automation": "Building Automation Systems",
  "building automation system": "Building Automation Systems",
  "building automation systems": "Building Automation Systems",
  "plc": "PLC",
  "programmable logic controller": "PLC",
  "programmable logic controllers": "PLC",
  "scada": "SCADA",
  "supervisory control and data acquisition": "SCADA",
  "hvac": "HVAC",
  "ddc": "DDC",
  "direct digital control": "DDC",
  "git": "Git",
  "mep": "MEP",
  "elv": "ELV",
  "extra low voltage": "ELV",
  "bacnet": "BACnet",
  "bacnet/ip": "BACnet",
  "modbus": "Modbus",
  "cctv": "CCTV",
  "closed circuit television": "CCTV",
  "access control system": "Access Control",
  "access control systems": "Access Control",
  "access control": "Access Control",
  "access-control": "Access Control",

  // Multi-word specific skills (preserve exact discipline, normalize casing only)
  "hvac controls": "HVAC Controls",
  "hvac automation": "HVAC Automation",
  "bms programming": "BMS Programming",
  "bms systems integration": "BMS Systems Integration",
  "plc/scada": "PLC/SCADA",
  "plc/scada programming": "PLC/SCADA Programming",
  "controls engineering": "Controls Engineering",
  "commissioning": "Commissioning",
  "system commissioning": "System Commissioning",
  "bacnet/modbus protocols": "BACnet/Modbus Protocols",
  "bacnet / modbus protocols": "BACnet/Modbus Protocols",
  "scada / plc": "PLC/SCADA",
  "plc / scada": "PLC/SCADA",
};

function normalizeSkillForDisplay(skill) {
  if (!skill || typeof skill !== "string") return "";
  const trimmed = skill.trim();
  const lower = trimmed.toLowerCase();

  if (SAFE_SKILL_DISPLAY_MAP[lower]) {
    return SAFE_SKILL_DISPLAY_MAP[lower];
  }

  return trimmed;
}

// ============================================================
// MAIN APP
// ============================================================

  function App() {
// ============================================================
// JOB MATCHING
// ============================================================

  const [jobs, setJobs] = useState([]);
  const allMissingSkills = [
    ...new Set(
      jobs
        .flatMap((job) => job.missing_skills || [])
        .map((skill) => normalizeSkillForDisplay(skill))
        .filter(Boolean)
    )
  ];
  const [hasSearched, setHasSearched] = useState(false);
  const [searchMeta, setSearchMeta] = useState(null);
  const [activeProfile, setActiveProfile] = useState(null);

  // Fetch active saved profile on load to show current profile criteria
  useEffect(() => {
    const fetchActiveProfile = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/profile");
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.profile) {
            setActiveProfile(data.profile);
          }
        }
      } catch (err) {
        console.warn("Could not load initial user profile:", err);
      }
    };
    fetchActiveProfile();
  }, []);


  const [jobLoading, setJobLoading] = useState(false);
  const [jobError, setJobError] = useState("");

  const findJobs = async () => {
    setJobLoading(true);
    setJobError("");
    setHasSearched(true);
    setJobs([]);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/jobs/match-profile",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      console.log("Job Matching Response:", data);

      if (data.success) {
        setJobs(data.matched_jobs || []);
        setSearchMeta({
          jobsFound: data.jobs_found || 0,
          profileUsed: data.profile_used || null,
          geminiUsed: data.gemini_used || false,
          message: data.message || "",
        });
        if (data.profile_used) {
          setActiveProfile(data.profile_used);
        }
      } else {
        setJobError(
          data.message || "Failed to fetch matching jobs. Please verify your profile."
        );
      }
    } catch (error) {
      console.error(error);

      setJobError(
        "Backend se connection nahi ho pa raha. Please check FastAPI server."
      );
    } finally {
      setJobLoading(false);
    }
  };



  // ============================================================
  // AI TRAINING
  // ============================================================

  const [training, setTraining] = useState(null);
  const [trainingLoading, setTrainingLoading] = useState(false);
  const [trainingError, setTrainingError] = useState("");
  const [selectedSkill, setSelectedSkill] = useState("SQLAlchemy");

  const startTraining = async (skill = selectedSkill) => {
    setSelectedSkill(skill);
    setTrainingLoading(true);
    setTrainingError("");
    setTraining(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/training/generate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            skill: skill,
            level: "Beginner",
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Training API request failed");
      }

      const data = await response.json();

      console.log("Training Response:", data);

      if (data.success && data.training) {
        setTraining(data.training);
      } else {
        setTrainingError(
          data.message || "Training lesson generate nahi ho saka."
        );
      }
    } catch (error) {
      console.error(error);

      setTrainingError(
        "AI Training load nahi ho rahi. Please check FastAPI server."
      );
    } finally {
      setTrainingLoading(false);
    }
  };

  // ============================================================
  // PRACTICE
  // ============================================================

  const [practiceSetup, setPracticeSetup] = useState({
    target_role: "",
    topic: "",
    difficulty: "Beginner",
    number_of_questions: 5,
  });

  const [practiceQuestions, setPracticeQuestions] = useState([]);
  const [currentPracticeIndex, setCurrentPracticeIndex] = useState(0);
  const [practiceAnswer, setPracticeAnswer] = useState("");
  const [practiceEvaluation, setPracticeEvaluation] = useState(null);
  const [practiceLoading, setPracticeLoading] = useState(false);
  const [practiceEvaluating, setPracticeEvaluating] = useState(false);
  const [practiceError, setPracticeError] = useState("");
  const [practiceCompleted, setPracticeCompleted] = useState(false);
  const [isPracticeActive, setIsPracticeActive] = useState(false);

  // Helper to parse generated questions text into clean question items
  const parseQuestions = (rawText) => {
    if (!rawText || typeof rawText !== "string") return [];

    // Try splitting by standard numbered list: 1. or 1) or Question 1:
    const lines = rawText.split(/\r?\n/);
    const questions = [];
    let currentQuestion = "";

    const questionStartRegex = /^(?:(?:Q(?:uestion)?\s*\d+[\s:.-]+)|(?:\d+[-.)]\s+))/i;

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      if (questionStartRegex.test(trimmed)) {
        if (currentQuestion.trim()) {
          questions.push(currentQuestion.trim());
        }
        currentQuestion = trimmed.replace(questionStartRegex, "").trim();
      } else if (currentQuestion) {
        currentQuestion += " " + trimmed;
      }
    }

    if (currentQuestion.trim()) {
      questions.push(currentQuestion.trim());
    }

    // If numbered regex didn't extract items, fallback to non-empty paragraphs or raw text
    if (questions.length === 0) {
      const paragraphs = rawText
        .split(/\n\s*\n/)
        .map((p) => p.trim())
        .filter((p) => p.length > 5);
      return paragraphs.length > 0 ? paragraphs : [rawText.trim()];
    }

    return questions;
  };

  const handleStartPracticeClick = () => {
    setIsPracticeActive(true);
    // Initialize practiceSetup with role and skill if available
    setPracticeSetup((prev) => ({
      ...prev,
      target_role: prev.target_role || activeProfile?.preferred_role || "Python Developer",
      topic: prev.topic || selectedSkill || (allMissingSkills.length > 0 ? allMissingSkills[0] : "FastAPI"),
    }));

    setTimeout(() => {
      const el = document.getElementById("practice-section");
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
      }
    }, 100);
  };

  const generatePractice = async (e) => {
    if (e && e.preventDefault) e.preventDefault();

    if (!practiceSetup.target_role.trim()) {
      setPracticeError("Please enter a Target Job Role.");
      return;
    }
    if (!practiceSetup.topic.trim()) {
      setPracticeError("Please enter a Topic.");
      return;
    }

    const numQuestions = parseInt(practiceSetup.number_of_questions, 10);
    if (isNaN(numQuestions) || numQuestions < 1 || numQuestions > 20) {
      setPracticeError("Number of questions must be between 1 and 20.");
      return;
    }

    setPracticeLoading(true);
    setPracticeError("");
    setPracticeQuestions([]);
    setCurrentPracticeIndex(0);
    setPracticeAnswer("");
    setPracticeEvaluation(null);
    setPracticeCompleted(false);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/practice/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          target_role: practiceSetup.target_role.trim(),
          topic: practiceSetup.topic.trim(),
          difficulty: practiceSetup.difficulty,
          number_of_questions: numQuestions,
        }),
      });

      if (!response.ok) {
        throw new Error("Practice generation request failed");
      }

      const data = await response.json();

      if (data.success && data.practice_questions) {
        const parsed = parseQuestions(data.practice_questions);
        setPracticeQuestions(parsed);
        setCurrentPracticeIndex(0);
      } else {
        setPracticeError(data.message || "Failed to generate practice questions.");
      }
    } catch (err) {
      console.error(err);
      setPracticeError("Backend se connection nahi ho pa raha. Please check FastAPI server.");
    } finally {
      setPracticeLoading(false);
    }
  };

  const submitPracticeAnswer = async () => {
    if (!practiceAnswer.trim()) {
      setPracticeError("Please type an answer before submitting.");
      return;
    }

    const currentQuestion = practiceQuestions[currentPracticeIndex] || practiceSetup.topic;

    setPracticeEvaluating(true);
    setPracticeError("");
    setPracticeEvaluation(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/practice/evaluate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          target_role: practiceSetup.target_role,
          topic: practiceSetup.topic,
          question: currentQuestion,
          user_answer: practiceAnswer.trim(),
          difficulty: practiceSetup.difficulty,
        }),
      });

      if (!response.ok) {
        throw new Error("Practice evaluation request failed");
      }

      const data = await response.json();

      if (data.success) {
        setPracticeEvaluation({
          score: data.score,
          rawText: data.evaluation,
        });
      } else {
        setPracticeError(data.message || "Failed to evaluate answer.");
      }
    } catch (err) {
      console.error(err);
      setPracticeError("Could not evaluate answer. Please verify backend server.");
    } finally {
      setPracticeEvaluating(false);
    }
  };

  const nextPracticeQuestion = () => {
    if (currentPracticeIndex + 1 < practiceQuestions.length) {
      setCurrentPracticeIndex((prev) => prev + 1);
      setPracticeAnswer("");
      setPracticeEvaluation(null);
      setPracticeError("");
    } else {
      setPracticeCompleted(true);
    }
  };

  const resetPractice = () => {
    setPracticeQuestions([]);
    setCurrentPracticeIndex(0);
    setPracticeAnswer("");
    setPracticeEvaluation(null);
    setPracticeError("");
    setPracticeCompleted(false);
  };

  // Helper to parse sections from the evaluation text
  const parseEvaluationSections = (evalText) => {
    if (!evalText) return null;

    const sections = {
      scoreText: "",
      correct: "",
      missing: "",
      improvement: "",
      understanding: "",
      tip: "",
      nextStep: "",
      general: "",
    };

    // Try extracting structured headings
    const sectionNames = [
      { key: "scoreText", regex: /(?:^|\n)\s*(?:1\.\s*)?Score(?:\s*out\s*of\s*10)?[:\s-]*([\s\S]*?)(?=(?:\n\s*(?:2\.\s*)?What Was Correct|\n\s*\d+\.|$))/i },
      { key: "correct", regex: /(?:^|\n)\s*(?:2\.\s*)?What Was Correct[:\s-]*([\s\S]*?)(?=(?:\n\s*(?:3\.\s*)?What Was Missing|\n\s*\d+\.|$))/i },
      { key: "missing", regex: /(?:^|\n)\s*(?:3\.\s*)?What Was Missing[:\s-]*([\s\S]*?)(?=(?:\n\s*(?:4\.\s*)?What Needs Improvement|\n\s*\d+\.|$))/i },
      { key: "improvement", regex: /(?:^|\n)\s*(?:4\.\s*)?What Needs Improvement[:\s-]*([\s\S]*?)(?=(?:\n\s*(?:5\.\s*)?Correct Understanding|\n\s*\d+\.|$))/i },
      { key: "understanding", regex: /(?:^|\n)\s*(?:5\.\s*)?Correct Understanding[:\s-]*([\s\S]*?)(?=(?:\n\s*(?:6\.\s*)?Interview Tip|\n\s*\d+\.|$))/i },
      { key: "tip", regex: /(?:^|\n)\s*(?:6\.\s*)?Interview Tip[:\s-]*([\s\S]*?)(?=(?:\n\s*(?:7\.\s*)?Recommended Next Step|\n\s*\d+\.|$))/i },
      { key: "nextStep", regex: /(?:^|\n)\s*(?:7\.\s*)?Recommended Next Step[:\s-]*([\s\S]*?)$/i },
    ];

    let foundAny = false;
    for (const sec of sectionNames) {
      const match = evalText.match(sec.regex);
      if (match && match[1] && match[1].trim()) {
        sections[sec.key] = match[1].trim();
        foundAny = true;
      }
    }

    if (!foundAny) {
      sections.general = evalText.trim();
    }

    return sections;
  };

  // ============================================================
  // UI
  // ============================================================

  return (
  <BrowserRouter>

    <Routes>

      <Route path="/profile" element={<ProfilePage />} />

      <Route path="/" element={

        <div className="app">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="header">

        <div>
          <h1>🤖 AI Job Finder</h1>

          <p>
            Your AI-powered career assistant
          </p>
        </div>

        <button className="voice-button">
          🎤 Talk to AI
        </button>

      </header>


      {/* ======================================================
          MAIN DASHBOARD
      ====================================================== */}

      <main className="dashboard">


        {/* ====================================================
            WELCOME CARD
        ==================================================== */}

        {/* ====================================================
            WELCOME CARD
        ==================================================== */}

        <section className="welcome-card">

          <h2>
            Welcome to AI Job Finder 👋
          </h2>

          <p>
            Find jobs that match your skills, experience and career goals.
          </p>

          {activeProfile && (activeProfile.preferred_role || activeProfile.location) ? (
            <div className="active-profile-banner">
              <span className="profile-indicator-dot"></span>
              <span>
                Matching with saved profile: <strong>{activeProfile.preferred_role || "Role"}</strong>
                {activeProfile.location ? ` in ${activeProfile.location}` : ""}
                {activeProfile.experience ? ` • ${activeProfile.experience}` : ""}
              </span>
            </div>
          ) : (
            <div className="active-profile-banner warning">
              <span>💡 Complete your profile so AI can find tailored jobs for you.</span>
              <button
                className="profile-link-btn"
                onClick={() => window.location.href = "/profile"}
              >
                Set Up Profile →
              </button>
            </div>
          )}

          <button
            className="primary-button"
            onClick={findJobs}
            disabled={jobLoading}
          >
            {jobLoading
              ? "⏳ Finding Best Matches..."
              : "🔎 Find My Best Jobs"}
          </button>

        </section>


        {/* ====================================================
            LOADING STATE
        ==================================================== */}

        {jobLoading && (
          <section className="job-status-card loading">
            <div className="spinner"></div>
            <h3>🤖 AI is finding and matching jobs...</h3>
            <p>
              Searching live listings and evaluating match scores with your profile skills & experience.
            </p>
          </section>
        )}


        {/* ====================================================
            ERROR STATE
        ==================================================== */}

        {!jobLoading && jobError && (
          <section className="job-status-card error">
            <div className="status-icon">⚠️</div>
            <h3>Unable to find matched jobs</h3>
            <p>{jobError}</p>
            <div className="status-actions">
              <button className="primary-button" onClick={findJobs}>
                🔄 Try Again
              </button>
              <button
                className="secondary-button"
                onClick={() => window.location.href = "/profile"}
              >
                👤 Update Profile
              </button>
            </div>
          </section>
        )}


        {/* ====================================================
            EMPTY STATE (0 JOBS FOUND)
        ==================================================== */}

        {!jobLoading && !jobError && hasSearched && jobs.length === 0 && (
          <section className="job-status-card empty">
            <div className="status-icon">🔍</div>
            <h3>No matching jobs found</h3>
            <p>
              {searchMeta?.message ||
                "We couldn't find any job postings matching your current target role and location."}
            </p>
            <p className="hint">
              Try adjusting your preferred role or location in your profile.
            </p>
            <button
              className="secondary-button"
              onClick={() => window.location.href = "/profile"}
            >
              ✏️ Update Profile
            </button>
          </section>
        )}


        {/* ====================================================
            JOB RESULTS
        ==================================================== */}

        {!jobLoading && jobs.length > 0 && (

          <section className="jobs-section">

            <div className="jobs-section-header">
              <div>
                <h2>
                  🏆 Your Best Job Matches ({jobs.length})
                </h2>

                <p className="section-description">
                  AI analyzed and ranked these jobs based on your saved profile
                  {searchMeta?.profileUsed?.preferred_role
                    ? ` for "${searchMeta.profileUsed.preferred_role}"`
                    : ""}
                  {searchMeta?.profileUsed?.location
                    ? ` in ${searchMeta.profileUsed.location}`
                    : ""}.
                </p>
              </div>

              {searchMeta?.geminiUsed && (
                <span className="ai-badge">✨ Gemini AI Analyzed</span>
              )}
            </div>


            {/* ================================================
                SKILL GAP OVERVIEW
            ================================================ */}

            {allMissingSkills.length > 0 && (
              <section className="skill-gap-overview">

                <div className="skill-gap-header">
                  <h3>
                    📚 Skill Gap Overview ({allMissingSkills.length})
                  </h3>

                  <p>
                    These are skills missing across the displayed job listings based on your saved profile:
                  </p>
                </div>

                <div className="skills missing">
                  {allMissingSkills.map((skill, index) => (
                    <span key={index} className="skill-pill missing">
                      {skill}
                    </span>
                  ))}
                </div>

              </section>
            )}


            <div className="jobs-grid">

              {jobs.map((job, index) => {
                const score = typeof job.match_score === "number" ? job.match_score : 0;
                const scoreClass =
                  score >= 70 ? "score-high" : score >= 40 ? "score-mid" : "score-low";

                return (
                  <div
                    className="job-card"
                    key={index}
                  >

                    <div className="job-header">

                      <div className="job-title-group">
                        <h3 title={job.title}>
                          {job.title}
                        </h3>

                        <p className="job-company">
                          🏢{" "}
                          <strong>
                            {job.company || "Company not specified"}
                          </strong>
                        </p>

                        <p className="job-location">
                          📍{" "}
                          {job.location || "Location not specified"}
                        </p>
                      </div>

                      <div className={`match-score ${scoreClass}`}>
                        <span className="score-value">{score}%</span>
                        <span className="score-text">Match</span>
                      </div>

                    </div>


                    {/* MATCHING SKILLS */}

                    {job.matching_skills &&
                      job.matching_skills.length > 0 && (

                        <div className="skills-block">

                          <h4>
                            ✅ Matching Skills
                          </h4>

                          <div className="skills">

                            {job.matching_skills.map(
                              (skill, skillIndex) => (

                                <span key={skillIndex} className="skill-pill match">
                                  {skill}
                                </span>

                              )
                            )}

                          </div>

                        </div>

                      )}


                    {/* MISSING SKILLS */}

                    {job.missing_skills &&
                      job.missing_skills.length > 0 && (

                        <div className="skills-block">

                          <h4>
                            📚 Skills to Improve
                          </h4>

                          <div className="skills missing">

                            {job.missing_skills.map(
                              (skill, skillIndex) => (

                                <span key={skillIndex} className="skill-pill missing">
                                  {skill}
                                </span>

                              )
                            )}

                          </div>

                        </div>

                      )}


                    {/* AI RECOMMENDATION */}

                    {job.recommendation && (

                      <div className="recommendation">

                        <h4>
                          💡 AI Recommendation
                        </h4>

                        <p>
                          {job.recommendation}
                        </p>

                      </div>

                    )}


                    {/* JOB LINK */}

                    {job.url && (

                      <div className="job-card-actions">
                        <a
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="job-link"
                        >
                          View Job on Portal →
                        </a>
                      </div>

                    )}

                  </div>
                );
              })}

            </div>

          </section>

        )}


        {/* ====================================================
            AI TRAINING SECTION
        ==================================================== */}

        <section className="training-section">

          <div className="training-header">

            <h2>
              🎓 AI Training
            </h2>

            <p>
              Learn the skills you need for your target job.
            </p>

          </div>


          {/* SKILL SELECTOR */}

          <div className="training-selector">

            <label htmlFor="skill">
              Select Skill
            </label>

            {(() => {
              const effectiveSkill =
                allMissingSkills.length > 0 && !allMissingSkills.includes(selectedSkill)
                  ? allMissingSkills[0]
                  : selectedSkill;

              return (
                <>
                  <select
                    id="skill"
                    value={effectiveSkill}
                    onChange={(event) =>
                      setSelectedSkill(event.target.value)
                    }
                  >

                    {allMissingSkills.length > 0 ? (
                      allMissingSkills.map((skill, index) => (
                        <option key={index} value={skill}>
                          {skill}
                        </option>
                      ))
                    ) : (
                      <>
                        <option value="SQLAlchemy">SQLAlchemy</option>
                        <option value="Pytest">Pytest</option>
                        <option value="Docker">Docker</option>
                        <option value="Asyncio">Asyncio</option>
                        <option value="Redis">Redis</option>
                        <option value="CI/CD">CI/CD</option>
                      </>
                    )}

                  </select>


                  <button
                    className="primary-button"
                    onClick={() => startTraining(effectiveSkill)}
                    disabled={trainingLoading}
                  >

                    {trainingLoading
                      ? "⏳ Generating Lesson..."
                      : "🎓 Start Training"}

                  </button>
                </>
              );
            })()}

          </div>


          {/* TRAINING ERROR */}

          {trainingError && (

            <p className="error-message">
              ❌ {trainingError}
            </p>

          )}


          {/* TRAINING RESULT */}

          {training && (

            <div className="training-result">


              {/* TOPIC */}

              <div className="training-card">

                <h2>
                  📖 {training.topic}
                </h2>

              </div>


              {/* WHAT YOU WILL LEARN */}

              <div className="training-card">

                <h3>
                  🎯 What You Will Learn
                </h3>

                <ul>

                  {training.what_you_will_learn?.map(
                    (item, index) => (

                      <li key={index}>
                        {item}
                      </li>

                    )
                  )}

                </ul>

              </div>


              {/* CONCEPT */}

              <div className="training-card">

                <h3>
                  🧠 Concept Explanation
                </h3>

                <p>
                  {training.concept_explanation}
                </p>

              </div>


              {/* WHY IMPORTANT */}

              <div className="training-card">

                <h3>
                  ⭐ Why This Skill Is Important
                </h3>

                <p>
                  {training.why_important}
                </p>

              </div>


              {/* PRACTICAL EXAMPLE */}

              <div className="training-card">

                <h3>
                  🛠 Practical Example
                </h3>

                <p>
                  {training.practical_example}
                </p>

              </div>


              {/* CODE */}

              <div className="training-card">

                <h3>
                  💻 Code Example
                </h3>

                <pre className="code-block">
                  <code>
                    {training.code_example}
                  </code>
                </pre>

              </div>


              {/* PRACTICE */}

              <div className="training-card">

                <h3>
                  📝 Practice Task
                </h3>

                <p>
                  {training.practice_task}
                </p>

              </div>


              {/* INTERVIEW QUESTIONS */}

              <div className="training-card">

                <h3>
                  🎤 Interview Questions
                </h3>

                <ol>

                  {training.interview_questions?.map(
                    (question, index) => (

                      <li key={index}>
                        {question}
                      </li>

                    )
                  )}

                </ol>

              </div>


              {/* NEXT STEP */}

              <div className="training-card next-step">

                <h3>
                  🚀 Next Step
                </h3>

                <p>
                  {training.next_step}
                </p>

              </div>


            </div>

          )}

        </section>


        {/* ====================================================
            PRACTICE SECTION
        ==================================================== */}

        {isPracticeActive && (
          <section id="practice-section" className="practice-section">
            <div className="practice-header">
              <div>
                <h2>📝 Technical & Interview Practice</h2>
                <p>Sharpen your interview readiness with AI-generated role-specific questions and instant feedback.</p>
              </div>
              <button
                className="close-button"
                onClick={() => setIsPracticeActive(false)}
                title="Close Practice"
              >
                ✕
              </button>
            </div>

            {/* PRACTICE SETUP CARD */}
            <div className="practice-card setup-card">
              <h3>🎯 Practice Setup</h3>
              <form onSubmit={generatePractice} className="practice-form">
                <div className="practice-form-grid">
                  <div className="form-group">
                    <label htmlFor="target-role">Target Job Role</label>
                    <input
                      id="target-role"
                      type="text"
                      placeholder="e.g. BMS Engineer, Python Developer"
                      value={practiceSetup.target_role}
                      onChange={(e) =>
                        setPracticeSetup({ ...practiceSetup, target_role: e.target.value })
                      }
                      disabled={practiceLoading}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="practice-topic">Topic / Skill</label>
                    <input
                      id="practice-topic"
                      type="text"
                      placeholder="e.g. BACnet, SQLAlchemy, System Design"
                      value={practiceSetup.topic}
                      onChange={(e) =>
                        setPracticeSetup({ ...practiceSetup, topic: e.target.value })
                      }
                      disabled={practiceLoading}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="practice-difficulty">Difficulty</label>
                    <select
                      id="practice-difficulty"
                      value={practiceSetup.difficulty}
                      onChange={(e) =>
                        setPracticeSetup({ ...practiceSetup, difficulty: e.target.value })
                      }
                      disabled={practiceLoading}
                    >
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Advanced">Advanced</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="practice-num-questions">Number of Questions</label>
                    <input
                      id="practice-num-questions"
                      type="number"
                      min="1"
                      max="10"
                      value={practiceSetup.number_of_questions}
                      onChange={(e) =>
                        setPracticeSetup({
                          ...practiceSetup,
                          number_of_questions: Math.max(1, Math.min(10, parseInt(e.target.value, 10) || 1)),
                        })
                      }
                      disabled={practiceLoading}
                    />
                  </div>
                </div>

                <div className="practice-actions">
                  <button
                    type="submit"
                    className="primary-button"
                    disabled={practiceLoading}
                  >
                    {practiceLoading ? "⏳ Generating Questions..." : "🚀 Generate Practice Questions"}
                  </button>
                  {practiceQuestions.length > 0 && (
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={resetPractice}
                    >
                      🔄 Reset Session
                    </button>
                  )}
                </div>
              </form>
            </div>

            {/* ERROR MESSAGE */}
            {practiceError && (
              <div className="practice-error-banner">
                <span>⚠️ {practiceError}</span>
              </div>
            )}

            {/* QUESTIONS & EVALUATION WORKFLOW */}
            {practiceQuestions.length > 0 && !practiceCompleted && (
              <div className="practice-workspace">
                <div className="practice-progress-bar">
                  <div className="progress-info">
                    <span>
                      Question <strong>{currentPracticeIndex + 1}</strong> of <strong>{practiceQuestions.length}</strong>
                    </span>
                    <span className="difficulty-badge">{practiceSetup.difficulty}</span>
                  </div>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${((currentPracticeIndex + 1) / practiceQuestions.length) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>

                {/* CURRENT QUESTION CARD */}
                <div className="practice-card question-card">
                  <div className="question-header">
                    <span className="question-tag">Question #{currentPracticeIndex + 1}</span>
                    <span className="topic-tag">{practiceSetup.topic}</span>
                  </div>

                  <p className="question-text">
                    {practiceQuestions[currentPracticeIndex]}
                  </p>

                  <div className="answer-section">
                    <label htmlFor="practice-user-answer">Your Answer:</label>
                    <textarea
                      id="practice-user-answer"
                      rows="6"
                      placeholder="Type your explanation, approach, or technical answer here..."
                      value={practiceAnswer}
                      onChange={(e) => setPracticeAnswer(e.target.value)}
                      disabled={practiceEvaluating}
                    />

                    <div className="answer-actions">
                      <button
                        className="primary-button"
                        onClick={submitPracticeAnswer}
                        disabled={practiceEvaluating || !practiceAnswer.trim()}
                      >
                        {practiceEvaluating ? "⏳ Evaluating Answer..." : "📤 Submit Answer for Evaluation"}
                      </button>
                    </div>
                  </div>
                </div>

                {/* EVALUATION RESULT CARD */}
                {practiceEvaluation && (
                  <div className="practice-card evaluation-card">
                    <div className="evaluation-header">
                      <div className="score-badge">
                        <span className="score-num">{practiceEvaluation.score}</span>
                        <span className="score-denom">/ 10</span>
                      </div>
                      <div className="evaluation-summary">
                        <h4>AI Interviewer Evaluation</h4>
                        <p>Detailed performance breakdown and educational tips.</p>
                      </div>
                    </div>

                    {(() => {
                      const sections = parseEvaluationSections(practiceEvaluation.rawText);

                      if (sections.general) {
                        return (
                          <div className="evaluation-general">
                            <pre className="evaluation-pre">{sections.general}</pre>
                          </div>
                        );
                      }

                      return (
                        <div className="evaluation-grid">
                          {sections.correct && (
                            <div className="eval-item correct">
                              <h5>✅ What Was Correct</h5>
                              <p>{sections.correct}</p>
                            </div>
                          )}

                          {sections.missing && (
                            <div className="eval-item missing">
                              <h5>⚠️ What Was Missing</h5>
                              <p>{sections.missing}</p>
                            </div>
                          )}

                          {sections.improvement && (
                            <div className="eval-item improvement">
                              <h5>🔧 What Needs Improvement</h5>
                              <p>{sections.improvement}</p>
                            </div>
                          )}

                          {sections.understanding && (
                            <div className="eval-item understanding">
                              <h5>💡 Correct Understanding</h5>
                              <p>{sections.understanding}</p>
                            </div>
                          )}

                          {sections.tip && (
                            <div className="eval-item tip">
                              <h5>🎤 Interview Tip</h5>
                              <p>{sections.tip}</p>
                            </div>
                          )}

                          {sections.nextStep && (
                            <div className="eval-item next-step">
                              <h5>🚀 Recommended Next Step</h5>
                              <p>{sections.nextStep}</p>
                            </div>
                          )}
                        </div>
                      );
                    })()}

                    <div className="evaluation-actions">
                      <button
                        className="primary-button next-button"
                        onClick={nextPracticeQuestion}
                      >
                        {currentPracticeIndex + 1 < practiceQuestions.length
                          ? "Next Question ➔"
                          : "Finish Practice Session 🏁"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* COMPLETION CARD */}
            {practiceCompleted && (
              <div className="practice-card completion-card">
                <div className="completion-icon">🎉</div>
                <h3>Practice Session Completed!</h3>
                <p>
                  You finished all <strong>{practiceQuestions.length}</strong> questions on{" "}
                  <strong>{practiceSetup.topic}</strong> for the <strong>{practiceSetup.target_role}</strong> role.
                </p>
                <div className="completion-actions">
                  <button
                    className="primary-button"
                    onClick={() => {
                      resetPractice();
                      generatePractice();
                    }}
                  >
                    🔁 Practice Again
                  </button>
                  <button
                    className="secondary-button"
                    onClick={() => setIsPracticeActive(false)}
                  >
                    ✕ Close Practice
                  </button>
                </div>
              </div>
            )}
          </section>
        )}


        {/* ====================================================
            FEATURES
        ==================================================== */}

        <section className="cards">


          <div className="feature-card">

            <div className="icon">
              👤
            </div>

            <h3>
              My Profile
            </h3>

            <p>
              Manage your skills, experience and career preferences.
            </p>

            <button
             onClick={() => window.location.href = "/profile"}
            >
             Open Profile
            </button>

            </div>

            <div className="feature-card">

            <div className="icon">
              🎯
            </div>

            <h3>
              Job Matching
            </h3>

            <p>
              AI analyzes jobs and gives you a personalized match score.
            </p>

            <button onClick={findJobs}>
              Find Matches
            </button>

          </div>


          <div className="feature-card">

            <div className="icon">
              📚
            </div>

            <h3>
              Skill Gap
            </h3>

            <p>
              Discover which skills you need to improve.
            </p>

            <button>
              View Skills
            </button>

          </div>


          <div className="feature-card">

            <div className="icon">
              🎓
            </div>

            <h3>
              AI Training
            </h3>

            <p>
              Learn the skills recommended by your AI assistant.
            </p>

            <button
              onClick={() => startTraining(selectedSkill)}
            >
              Start Training
            </button>

          </div>


          <div className="feature-card">

            <div className="icon">
              📝
            </div>

            <h3>
              Practice
            </h3>

            <p>
              Practice interview and technical questions.
            </p>

            <button onClick={handleStartPracticeClick}>
              Start Practice
            </button>

          </div>


          <div className="feature-card">

            <div className="icon">
              📊
            </div>

            <h3>
              Progress
            </h3>

            <p>
              Track your learning and interview preparation.
            </p>

            <button>
              View Progress
            </button>

          </div>


                        </section>

      </main>


      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer>

        <p>
          AI Job Finder • AI-powered career assistance
        </p>

      </footer>

    </div>
    } />

    </Routes>

  </BrowserRouter>
  );
}

export default App;