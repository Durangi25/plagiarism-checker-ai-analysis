import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [authMode, setAuthMode] = useState("login");
  const [user, setUser] = useState(null);

  const [signupData, setSignupData] = useState({
    name: "",
    email: "",
    password: "",
    role: "student",
  });

  const [loginData, setLoginData] = useState({
    email: "",
    password: "",
  });

  const [inputMode, setInputMode] = useState("upload");
  const [file, setFile] = useState(null);
  const [textTitle, setTextTitle] = useState("");
  const [pastedText, setPastedText] = useState("");

  const [assignments, setAssignments] = useState([]);
  const [message, setMessage] = useState("");
  const [report, setReport] = useState(null);

  const isLecturer = user?.role === "lecturer";

  const resetLoginForm = () => {
    setLoginData({
      email: "",
      password: "",
    });
  };

  const resetSignupForm = () => {
    setSignupData({
      name: "",
      email: "",
      password: "",
      role: "student",
    });
  };

  const clearPasteText = () => {
    setTextTitle("");
    setPastedText("");
    setMessage("Pasted text cleared");
  };

  const loadAssignments = async (currentUser = user) => {
    if (!currentUser) {
      return;
    }

    try {
      const response = await axios.get(`${API_URL}/assignments`, {
        params: {
          user_id: currentUser.id,
          role: currentUser.role,
        },
      });

      setAssignments(response.data);
    } catch (error) {
      console.error(error);
      setMessage("Failed to load assignments");
    }
  };

  const handleSignup = async () => {
    if (!signupData.name || !signupData.email || !signupData.password) {
      setMessage("Please fill all signup fields");
      return;
    }

    if (signupData.password.length < 6) {
      setMessage("Password must have at least 6 characters");
      return;
    }

    try {
      setMessage("Creating account...");

      const response = await axios.post(`${API_URL}/signup`, signupData);

      setUser(response.data.user);
      resetSignupForm();
      resetLoginForm();
      setMessage("");
      loadAssignments(response.data.user);
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Signup failed");
    }
  };

  const handleLogin = async () => {
    if (!loginData.email || !loginData.password) {
      setMessage("Please enter email and password");
      return;
    }

    try {
      setMessage("Logging in...");

      const response = await axios.post(`${API_URL}/login`, loginData);

      setUser(response.data.user);
      resetLoginForm();
      setMessage("");
      loadAssignments(response.data.user);
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Login failed");
    }
  };

  const handleLogout = () => {
    setUser(null);
    setAssignments([]);
    setReport(null);
    setMessage("");
    resetLoginForm();
    resetSignupForm();
  };

  const uploadFile = async () => {
    if (!file) {
      setMessage("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", user.id);
    formData.append("uploader_name", user.name);
    formData.append("uploader_role", user.role);

    try {
      setMessage("Uploading file...");

      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setMessage(
        `Uploaded successfully. Assignment ID: ${response.data.assignment_id}`
      );

      setFile(null);
      setReport(null);
      loadAssignments();
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Upload failed");
    }
  };

  const submitText = async () => {
    if (!pastedText.trim()) {
      setMessage("Please paste assignment text first");
      return;
    }

    if (pastedText.trim().length < 50) {
      setMessage("Please enter at least 50 characters for better checking accuracy");
      return;
    }

    if (pastedText.trim().length > 3000) {
      setMessage("Pasted text cannot exceed 3000 characters");
      return;
    }

    try {
      setMessage("Submitting text...");

      const response = await axios.post(`${API_URL}/submit-text`, {
        title: textTitle || "Pasted Assignment",
        text: pastedText,
        user_id: user.id,
        uploader_name: user.name,
        uploader_role: user.role,
      });

      setMessage(
        `Text submitted successfully. Assignment ID: ${response.data.assignment_id}`
      );

      setTextTitle("");
      setPastedText("");
      setReport(null);
      loadAssignments();
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Text submission failed");
    }
  };

  const loadExampleText = () => {
    setTextTitle("Sample Cloud Computing Assignment");

    setPastedText(
      "Cloud computing is a technology that provides computing services such as storage, servers, databases, networking, and software through the internet. It helps users access scalable resources without owning physical hardware. Cloud computing is widely used in education, business, healthcare, and software development because it reduces cost and improves flexibility. The main service models of cloud computing are Infrastructure as a Service, Platform as a Service, and Software as a Service."
    );

    setMessage("Example text loaded");
  };

  const getFullReport = async (assignmentId) => {
    if (!isLecturer) {
      setMessage("Only lecturers can view report details");
      return;
    }

    try {
      setMessage("Generating report...");

      const response = await axios.get(`${API_URL}/full-report/${assignmentId}`);

      setReport(response.data);
      setMessage("Report generated successfully");
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Report generation failed");
    }
  };

  const deleteAssignment = async (assignmentId) => {
    const confirmDelete = window.confirm("Confirm delete this assignment?");

    if (!confirmDelete) {
      return;
    }

    try {
      setMessage("Deleting assignment...");

      await axios.delete(`${API_URL}/assignments/${assignmentId}`, {
        params: {
          user_id: user.id,
          role: user.role,
        },
      });

      setMessage("Assignment deleted successfully");
      setReport(null);
      loadAssignments();
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Delete failed");
    }
  };

  if (!user) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="brand-area">
            <h1>Plagiarism Checker</h1>
            <p className="subtitle">
              Upload assignments, detect similarity, and review AI-writing patterns.
            </p>
          </div>

          {authMode === "login" ? (
            <div className="auth-form">
              <h2>Login</h2>
              <p className="form-note">Enter account details to continue</p>

              <input
                type="email"
                name="login_email_clean"
                autoComplete="off"
                placeholder="Email address"
                value={loginData.email}
                onChange={(e) =>
                  setLoginData({ ...loginData, email: e.target.value })
                }
              />

              <input
                type="password"
                name="login_password_clean"
                autoComplete="new-password"
                placeholder="Password"
                value={loginData.password}
                onChange={(e) =>
                  setLoginData({ ...loginData, password: e.target.value })
                }
              />

              <button className="full-btn" onClick={handleLogin}>
                Login
              </button>

              <p className="switch-text">
                New user?{" "}
                <span
                  onClick={() => {
                    setAuthMode("signup");
                    setMessage("");
                    resetLoginForm();
                  }}
                >
                  Create account
                </span>
              </p>
            </div>
          ) : (
            <div className="auth-form">
              <h2>Create Profile</h2>
              <p className="form-note">
                Choose Student or Lecturer account type
              </p>

              <input
                type="text"
                name="signup_name_clean"
                autoComplete="off"
                placeholder="Full name"
                value={signupData.name}
                onChange={(e) =>
                  setSignupData({ ...signupData, name: e.target.value })
                }
              />

              <input
                type="email"
                name="signup_email_clean"
                autoComplete="off"
                placeholder="Email address"
                value={signupData.email}
                onChange={(e) =>
                  setSignupData({ ...signupData, email: e.target.value })
                }
              />

              <input
                type="password"
                name="signup_password_clean"
                autoComplete="new-password"
                placeholder="Password"
                value={signupData.password}
                onChange={(e) =>
                  setSignupData({ ...signupData, password: e.target.value })
                }
              />

              <select
                value={signupData.role}
                onChange={(e) =>
                  setSignupData({ ...signupData, role: e.target.value })
                }
              >
                <option value="student">Student</option>
                <option value="lecturer">Lecturer</option>
              </select>

              <button className="full-btn" onClick={handleSignup}>
                Create Account
              </button>

              <p className="switch-text">
                Already have an account?{" "}
                <span
                  onClick={() => {
                    setAuthMode("login");
                    setMessage("");
                    resetSignupForm();
                    resetLoginForm();
                  }}
                >
                  Login
                </span>
              </p>
            </div>
          )}

          {message && <p className="message">{message}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="topbar">
        <div>
          <h1>Plagiarism Checker</h1>
          <p>
            Logged in as <strong>{user.name}</strong> ({user.role})
          </p>
        </div>

        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <div className="card hero-card">
        <h2>Check Your Assignment</h2>
        <p>
          Students and lecturers can upload PDF, DOCX, TXT files or paste text.
          Students can view and delete their own uploaded files. Detailed reports are visible only to lecturers.
        </p>
      </div>

      <div className="card checker-card">
        <h2>Input Assignment</h2>

        <div className="input-tabs">
          <button
            className={inputMode === "upload" ? "active-tab" : ""}
            onClick={() => {
              setInputMode("upload");
              setMessage("");
            }}
          >
            Upload File
          </button>

          <button
            className={inputMode === "paste" ? "active-tab" : ""}
            onClick={() => {
              setInputMode("paste");
              setMessage("");
            }}
          >
            Paste Text
          </button>
        </div>

        {inputMode === "upload" ? (
          <div className="upload-box">
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => setFile(e.target.files[0])}
            />

            <button onClick={uploadFile}>Upload</button>

            <p className="small-note">Accepted file types: PDF, DOCX, TXT</p>
          </div>
        ) : (
          <div className="paste-box">
            <input
              type="text"
              placeholder="Assignment title"
              value={textTitle}
              onChange={(e) => setTextTitle(e.target.value)}
            />

            <textarea
              placeholder="Paste assignment text here..."
              value={pastedText}
              maxLength={3000}
              onChange={(e) => setPastedText(e.target.value)}
            ></textarea>

            <p className="small-note">
              Characters: {pastedText.length}/3000 | Minimum recommended: 50 characters
            </p>

            <div className="paste-actions">
              <button onClick={submitText}>Submit Text</button>

              <button className="example-btn" onClick={loadExampleText}>
                Try Example
              </button>

              <button className="clear-btn" onClick={clearPasteText}>
                Clear Text
              </button>
            </div>
          </div>
        )}

        {message && <p className="message">{message}</p>}

        <p className="privacy-note">
          Upload is available for both students and lecturers. Reports and matched sources
          are available only for lecturer accounts.
        </p>
      </div>

      <div className="card">
        <h2>{isLecturer ? "Saved Assignments" : "My Uploaded Files"}</h2>

        {!isLecturer && (
          <p className="student-note">
            Report details are visible only to lecturers. Submitted files are listed below.
          </p>
        )}

        {assignments.length === 0 ? (
          <p>No assignments uploaded yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Filename</th>
                <th>Text Length</th>
                <th>Uploaded At</th>
                {isLecturer && <th>Uploaded By</th>}
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {assignments.map((assignment) => (
                <tr key={assignment.id}>
                  <td>{assignment.id}</td>
                  <td>{assignment.filename}</td>
                  <td>{assignment.text_length}</td>
                  <td>{assignment.uploaded_at}</td>

                  {isLecturer && (
                    <td>{assignment.uploader_name || "Unknown"}</td>
                  )}

                  <td>
                    {isLecturer && (
                      <button onClick={() => getFullReport(assignment.id)}>
                        Check Report
                      </button>
                    )}

                    <button
                      className="delete-btn"
                      onClick={() => deleteAssignment(assignment.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {isLecturer && report && (
        <div className="card report">
          <h2>Full Report</h2>

          <div className="result-grid">
            <div className="result-box">
              <h3>Plagiarism</h3>
              <p className="big-score">
                {report.plagiarism_result.plagiarism_percentage}%
              </p>
            </div>

            <div className="result-box">
              <h3>Originality</h3>
              <p className="big-score">
                {report.plagiarism_result.originality_percentage}%
              </p>
            </div>

            <div className="result-box">
              <h3>Human Writing</h3>
              <p className="big-score">
                {report.ai_writing_result.human_percentage}%
              </p>
            </div>

            <div className="result-box">
              <h3>AI Writing</h3>
              <p className="big-score">
                {report.ai_writing_result.ai_percentage}%
              </p>
            </div>

            <div className="result-box">
              <h3>Human + AI Mixed</h3>
              <p className="big-score">
                {report.ai_writing_result.human_ai_mixed_percentage}%
              </p>
            </div>

            <div className="result-box">
              <h3>Total Words</h3>
              <p className="big-score">
                {report.plagiarism_result.total_words}
              </p>
            </div>

            <div className="result-box">
              <h3>Matched Words</h3>
              <p className="big-score">
                {report.plagiarism_result.matched_words}
              </p>
            </div>
          </div>

          <p className="warning-note">
            Note: Plagiarism is calculated using matched weighted words.
            AI percentage is an estimated value, not final academic proof.
          </p>

          <h3>Matched Sources</h3>

          {report.plagiarism_result.matched_sources.length === 0 ? (
            <p>No matched sentences found.</p>
          ) : (
            report.plagiarism_result.matched_sources.map((item, index) => (
              <div className="matched-box" key={index}>
                <p>
                  <strong>Source File:</strong> {item.matched_filename}
                </p>

                <p>
                  <strong>Similarity:</strong> {item.similarity_percentage}%
                </p>

                <p>
                  <strong>Sentence Words:</strong> {item.sentence_word_count}
                </p>

                <p>
                  <strong>Matched Weighted Words:</strong> {item.matched_words}
                </p>

                <p>
                  <strong>Submitted Sentence:</strong>
                </p>
                <p className="sentence-text">{item.submitted_sentence}</p>

                <p>
                  <strong>Matched Sentence:</strong>
                </p>
                <p className="sentence-text">{item.matched_sentence}</p>
              </div>
            ))
          )}

          <h3>Paragraph AI Analysis</h3>

          {report.ai_writing_result.paragraph_results.length === 0 ? (
            <p>No paragraph analysis available.</p>
          ) : (
            report.ai_writing_result.paragraph_results.map((item, index) => (
              <div className="paragraph-box" key={index}>
                <p>
                  <strong>Classification:</strong> {item.classification}
                </p>
                <p>
                  <strong>AI Score:</strong> {item.ai_score}%
                </p>
                <p>
                  <strong>Word Count:</strong> {item.word_count}
                </p>
                <p>{item.paragraph_preview}...</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default App;
