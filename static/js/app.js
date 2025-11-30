const listEl = document.getElementById("video-list");
const playerEl = document.getElementById("player");
const titleEl = document.getElementById("current-title");
const statusEl = document.getElementById("status");

// Easter egg placeholder: not a real key, used for CTF flavor.
// Encoded so it is not noisy in the UI; decoding reveals the fake credential.
const kironHint = atob("S0lST05fQ1RGMjVfRkFLRV9BQ0NFU1NfS0VZPUtJUk9OLURFTU8tTk9ULVJFQUw=");
console.debug("Diagnostics ready:", kironHint);

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || res.statusText);
  }
  return res.json();
}

function formatSize(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let unit = 0;
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit += 1;
  }
  return `${size.toFixed(1)} ${units[unit]}`;
}

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.style.color = isError ? "#ff6b6b" : "#99a1b3";
}

async function loadVideos() {
  setStatus("Loading library...");
  listEl.innerHTML = "";
  try {
    const data = await fetchJSON("/api/videos");
    const videos = data.videos || [];
    if (!videos.length) {
      setStatus("No .mp4 files found in the bucket");
      return;
    }
    setStatus(`Loaded ${videos.length} clips`);
    videos.forEach((video) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <div>${video.name}</div>
        <div class="video-meta">
          <span>${video.key}</span>
          <span>${formatSize(video.size)}</span>
        </div>
      `;
      li.addEventListener("click", () => selectVideo(video, li));
      listEl.appendChild(li);
    });
  } catch (err) {
    console.error(err);
    setStatus(`Error: ${err.message}`, true);
  }
}

async function selectVideo(video, element) {
  [...listEl.children].forEach((el) => el.classList.remove("active"));
  element.classList.add("active");
  titleEl.textContent = video.name;
  setStatus("Requesting playback URL...");
  playerEl.src = "";
  try {
    const data = await fetchJSON(`/api/videos/url?key=${encodeURIComponent(video.key)}`);
    playerEl.src = data.url;
    playerEl.play().catch(() => {});
    setStatus("Playing");
  } catch (err) {
    console.error(err);
    setStatus(`Error: ${err.message}`, true);
  }
}

loadVideos();
