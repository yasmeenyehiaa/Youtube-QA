const SESSION_PREFIX = "youtube-qa:session:";
const MESSAGES_PREFIX = "youtube-qa:messages:";
const DETAILS_PREFIX = "youtube-qa:chat-details:";

function messagesKey(sessionId) {
  return `${MESSAGES_PREFIX}${sessionId}`;
}

function detailsKey(videoId) {
  return `${DETAILS_PREFIX}${videoId}`;
}

export function getSessionId(videoId) {
  const key = `${SESSION_PREFIX}${videoId}`;
  let sessionId = localStorage.getItem(key) || sessionStorage.getItem(key);
  if (!sessionId) sessionId = crypto.randomUUID();
  localStorage.setItem(key, sessionId);
  return sessionId;
}

export function getChatDetails(videoId) {
  const sessionId = getSessionId(videoId);
  const key = messagesKey(sessionId);
  let saved = localStorage.getItem(key);
  if (!saved) {
    saved = sessionStorage.getItem(key);
    if (saved) localStorage.setItem(key, saved);
  }
  const messages = saved ? JSON.parse(saved) : [];
  const details = JSON.parse(localStorage.getItem(detailsKey(videoId)) || "{}");
  return { messages, title: details.title || "", updatedAt: details.updatedAt || "" };
}

export function saveChat(videoId, messages) {
  const sessionId = getSessionId(videoId);
  const key = messagesKey(sessionId);
  localStorage.setItem(key, JSON.stringify(messages));
  localStorage.setItem(
    detailsKey(videoId),
    JSON.stringify({ ...getDetails(videoId), updatedAt: new Date().toISOString() }),
  );
}

export function renameChat(videoId, title) {
  localStorage.setItem(
    detailsKey(videoId),
    JSON.stringify({ ...getDetails(videoId), title: title.trim() }),
  );
}

function getDetails(videoId) {
  return JSON.parse(localStorage.getItem(detailsKey(videoId)) || "{}");
}
