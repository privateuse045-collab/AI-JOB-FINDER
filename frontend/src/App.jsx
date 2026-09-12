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
// MAIN APP
// ============================================================

  function App() {
// ============================================================
// JOB MATCHING
// ============================================================

  const [jobs, setJobs] = useState([]);
// ============================================================
// USER PROFILE
// ============================================================

  const [profileOpen, setProfileOpen] = useState(false);

  const [profile, setProfile] = useState({
    name: "",
    skills: "",
    experience: "",
    location: "",
    preferred_role: "",
    expected_salary: "",
  });

  const [profileLoading, setProfileLoading] = useState(false);
  const [profileMessage, setProfileMessage] = useState("");
  const [profileError, setProfileError] = useState("");
  const [jobLoading, setJobLoading] = useState(false);
  const [jobError, setJobError] = useState("");

  const findJobs = async () => {
    setJobLoading(true);
    setJobError("");
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

      if (data.matched_jobs) {
        setJobs(data.matched_jobs);
      } else {
        setJobError("No matched jobs were returned.");
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
  // SAVE USER PROFILE
  // ============================================================

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

        <section className="welcome-card">

          <h2>
            Welcome to AI Job Finder 👋
          </h2>

          <p>
            Find jobs that match your skills, experience and career goals.
          </p>

          <button
            className="primary-button"
            onClick={findJobs}
            disabled={jobLoading}
          >
            {jobLoading
              ? "⏳ Finding Jobs..."
              : "🔎 Find My Best Jobs"}
          </button>

          {jobError && (
            <p className="error-message">
              ❌ {jobError}
            </p>
          )}

        </section>


        {/* ====================================================
            JOB RESULTS
        ==================================================== */}

        {jobs.length > 0 && (

          <section className="jobs-section">

            <h2>
              🏆 Your Best Job Matches
            </h2>

            <p className="section-description">
              AI analyzed these jobs based on your saved profile.
            </p>


            <div className="jobs-grid">

              {jobs.map((job, index) => (

                <div
                  className="job-card"
                  key={index}
                >

                  <div className="job-header">

                    <h3>
                      {job.title}
                    </h3>

                    <span className="match-score">
                      {job.match_score}%
                    </span>

                  </div>


                  <p>
                    🏢{" "}
                    <strong>
                      {job.company || "Company not specified"}
                    </strong>
                  </p>


                  <p>
                    📍{" "}
                    {job.location || "Location not specified"}
                  </p>


                  {/* MATCHING SKILLS */}

                  {job.matching_skills &&
                    job.matching_skills.length > 0 && (

                      <div>

                        <h4>
                          ✅ Matching Skills
                        </h4>

                        <div className="skills">

                          {job.matching_skills.map(
                            (skill, skillIndex) => (

                              <span key={skillIndex}>
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

                      <div>

                        <h4>
                          📚 Skills to Improve
                        </h4>

                        <div className="skills missing">

                          {job.missing_skills.map(
                            (skill, skillIndex) => (

                              <span key={skillIndex}>
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

                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="job-link"
                    >
                      View Job →
                    </a>

                  )}

                </div>

              ))}

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

            <select
              id="skill"
              value={selectedSkill}
              onChange={(event) =>
                setSelectedSkill(event.target.value)
              }
            >

              <option value="SQLAlchemy">
                SQLAlchemy
              </option>

              <option value="Pytest">
                Pytest
              </option>

              <option value="Docker">
                Docker
              </option>

              <option value="Asyncio">
                Asyncio
              </option>

              <option value="Redis">
                Redis
              </option>

              <option value="CI/CD">
                CI/CD
              </option>

            </select>


            <button
              className="primary-button"
              onClick={() => startTraining(selectedSkill)}
              disabled={trainingLoading}
            >

              {trainingLoading
                ? "⏳ Generating Lesson..."
                : "🎓 Start Training"}

            </button>

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

            <button>
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