const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function parse(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || res.statusText || "Request failed");
  }
  return res.json();
}

export const listVideos = () => fetch(`${BASE}/videos`).then(parse);

export const ingestVideo = (url) =>
  fetch(`${BASE}/videos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  }).then(parse);

export const deleteVideo = (videoId) =>
  fetch(`${BASE}/videos/${videoId}`, { method: "DELETE" }).then(parse);

export const sendChat = (payload) =>
  fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(parse);

export const transcribeAudio = (blob) => {
  const form = new FormData();
  form.append("file", blob, "question.webm");
  return fetch(`${BASE}/transcribe`, { method: "POST", body: form }).then(parse);
};
