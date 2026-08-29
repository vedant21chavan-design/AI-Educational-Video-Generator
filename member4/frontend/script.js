const API_URL = "http://127.0.0.1:8000";
const POLL_INTERVAL_MS = 4000;

const form = document.querySelector("#generate-form");
const topicInput = document.querySelector("#topic");
const generateButton = document.querySelector("#generate-button");
const jobPanel = document.querySelector("#job-panel");
const videoPanel = document.querySelector("#video-panel");
const statusTitle = document.querySelector("#status-title");
const statusBadge = document.querySelector("#status-badge");
const statusMessage = document.querySelector("#status-message");
const jobIdText = document.querySelector("#job-id");
const progressBar = document.querySelector("#progress-bar");
const progressTrack = document.querySelector(".progress-track");
const videoPlayer = document.querySelector("#video-player");
const downloadLink = document.querySelector("#download-link");
const toast = document.querySelector("#toast");

let pollTimer = null;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const topic = topicInput.value.trim();
  if (!topic) return showToast("Please enter a topic before generating.", true);

  clearInterval(pollTimer);
  videoPanel.hidden = true;
  videoPlayer.removeAttribute("src");
  videoPlayer.load();
  setButtonLoading(true);
  updateJobPanel("PROCESSING", "", "Starting your video generation job…");

  try {
    const response = await fetch(`${API_URL}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic })
    });
    if (!response.ok) throw new Error("The server could not start the video job.");

    const data = await response.json();
    jobIdText.textContent = `Job ID: ${data.job_id}`;
    updateJobPanel("PROCESSING", data.job_id, "Classifying your topic and preparing its lesson plan.");
    pollJobStatus(data.job_id);
    pollTimer = setInterval(() => pollJobStatus(data.job_id), POLL_INTERVAL_MS);
  } catch (error) {
    updateJobPanel("FAILED", "", "We couldn’t reach the video server. Make sure FastAPI is running on port 8000.");
    setButtonLoading(false);
    showToast(error.message, true);
  }
});

async function pollJobStatus(jobId) {
  try {
    const response = await fetch(`${API_URL}/status/${encodeURIComponent(jobId)}`);
    if (!response.ok) throw new Error("Status request failed.");
    const data = await response.json();
    const status = String(data.status || "PROCESSING").toUpperCase();

    if (status === "COMPLETED") {
      clearInterval(pollTimer);
      updateJobPanel("COMPLETED", jobId, "Your educational video is ready to watch and download.");
      const videoUrl = `${API_URL}/video/${encodeURIComponent(jobId)}`;
      videoPlayer.src = videoUrl;
      downloadLink.href = videoUrl;
      downloadLink.download = `${jobId}.mp4`;
      videoPanel.hidden = false;
      setButtonLoading(false);
    } else if (status === "FAILED" || status === "NOT_FOUND") {
      clearInterval(pollTimer);
      updateJobPanel("FAILED", jobId, data.error || "Video generation did not finish. Please try again.");
      setButtonLoading(false);
      showToast(data.error || "Video generation failed.", true);
    } else {
      const messages = {
        CLASSIFYING: "Classifying your topic.",
        CREATING_SCENES: "Creating the lesson scenes.",
        GENERATING_MEDIA: "Generating scene images and narration.",
        COMPOSING_VIDEO: "Composing your final video."
      };
      updateJobPanel("PROCESSING", jobId, messages[status] || "Preparing your video.");
    }
  } catch (error) {
    clearInterval(pollTimer);
    updateJobPanel("FAILED", jobId, "The connection to the video server was interrupted.");
    setButtonLoading(false);
    showToast("Unable to check video status. Please try again.", true);
  }
}

function updateJobPanel(status, jobId, message) {
  const completed = status === "COMPLETED";
  const failed = status === "FAILED" || status === "NOT_FOUND";
  jobPanel.hidden = false;
  statusTitle.textContent = completed ? "Your video is ready" : failed ? "Generation needs attention" : "Preparing your video";
  statusBadge.textContent = completed ? "Completed" : failed ? "Failed" : "Processing";
  statusBadge.className = `status-badge ${completed ? "completed" : failed ? "failed" : "processing"}`;
  statusMessage.textContent = message;
  if (jobId) jobIdText.textContent = `Job ID: ${jobId}`;
  const progress = completed ? 100 : failed ? 100 : 48;
  progressBar.style.width = `${progress}%`;
  progressTrack.setAttribute("aria-valuenow", progress);
}

function setButtonLoading(isLoading) {
  generateButton.disabled = isLoading;
  generateButton.classList.toggle("loading", isLoading);
  generateButton.querySelector(".button-text").textContent = isLoading ? "Generating…" : "Generate video";
}

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.className = `toast show${isError ? " error" : ""}`;
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove("show"), 4200);
}
