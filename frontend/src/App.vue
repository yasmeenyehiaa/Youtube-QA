<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import VideoSidebar from "./components/VideoSidebar.vue";
import VideoPlayer from "./components/VideoPlayer.vue";
import ChatPanel from "./components/ChatPanel.vue";
import VideoOverview from "./components/VideoOverview.vue";
import { getSessionId } from "./chatHistory";
import { listVideos } from "./api";

const videos = ref([]);
const currentVideoId = ref(readVideoIdFromPath());
const seek = ref({ videoId: null, t: 0 });
const error = ref("");
const videoColumn = ref(null);
const playerHeight = ref(0);

const selectedVideo = computed(
  () => videos.value.find((video) => video.video_id === currentVideoId.value) ?? null,
);

const playerResizeObserver = new ResizeObserver(([entry]) => {
  playerHeight.value = entry.contentRect.height;
});

function readVideoIdFromPath() {
  const match = window.location.pathname.match(/^\/video\/([^/]+)\/?$/);
  return match ? decodeURIComponent(match[1]) : null;
}

function navigateToVideo(videoId) {
  const path = videoId ? `/video/${encodeURIComponent(videoId)}` : "/";
  if (window.location.pathname !== path) window.history.pushState({}, "", path);
  currentVideoId.value = videoId;
  seek.value = { videoId, t: 0, autoplay: false };
}

function onPopState() {
  currentVideoId.value = readVideoIdFromPath();
}

async function refresh() {
  try {
    videos.value = await listVideos();
    if (
      currentVideoId.value &&
      !videos.value.some((video) => video.video_id === currentVideoId.value)
    ) {
      navigateToVideo(null);
    }
    error.value = "";
  } catch (e) {
    error.value = e.message;
  }
}

async function onSeek({ videoId, t }) {
  if (videoId !== currentVideoId.value) navigateToVideo(videoId);
  seek.value = { videoId, t, autoplay: true };
  await nextTick();
  videoColumn.value?.scrollIntoView({ behavior: "smooth", block: "start" });
}

onMounted(() => {
  window.addEventListener("popstate", onPopState);
  refresh();
});

watch(
  selectedVideo,
  async (video) => {
    if (!video) return;
    await nextTick();
    if (videoColumn.value) playerResizeObserver.observe(videoColumn.value);
  },
  { flush: "post" },
);

onUnmounted(() => {
  window.removeEventListener("popstate", onPopState);
  playerResizeObserver.disconnect();
});
</script>

<template>
  <div v-if="!currentVideoId" class="home-page">
    <header class="home-header">
      <a class="brand" href="/" @click.prevent="navigateToVideo(null)">VidQuery</a>
    </header>
    <main class="library-page">
      <VideoSidebar
        :videos="videos"
        @select="navigateToVideo"
        @changed="refresh"
      />
      <p v-if="error" class="error page-error">{{ error }}</p>
    </main>
  </div>

  <div v-else class="watch-page">
    <header class="watch-header">
      <a class="brand" href="/" @click.prevent="navigateToVideo(null)">VidQuery</a>
      <button class="back-button" @click="navigateToVideo(null)">All videos</button>
      <label class="video-menu">
        <span>Jump to</span>
        <select
          :value="currentVideoId"
          aria-label="Select another video"
          @change="navigateToVideo($event.target.value)"
        >
          <option v-for="video in videos" :key="video.video_id" :value="video.video_id">
            {{ video.title }}
          </option>
        </select>
      </label>
    </header>
    <p v-if="error" class="error page-error">{{ error }}</p>
    <main
      v-if="selectedVideo"
      class="watch-layout"
      :style="playerHeight ? { '--player-height': `${playerHeight}px` } : undefined"
    >
      <div ref="videoColumn" class="video-stage">
        <VideoPlayer :video-id="selectedVideo.video_id" :seek="seek" />
      </div>
      <h1 class="watch-title">{{ selectedVideo.title }}</h1>
      <ChatPanel
        :key="selectedVideo.video_id"
        :session-id="getSessionId(selectedVideo.video_id)"
        :video-id="selectedVideo.video_id"
        :videos="videos"
        @seek="onSeek"
      />
      <VideoOverview
        :key="selectedVideo.video_id"
        :video-id="selectedVideo.video_id"
        :overview="selectedVideo.overview"
        @seek="onSeek"
        @changed="refresh"
      />
    </main>
  </div>
</template>
