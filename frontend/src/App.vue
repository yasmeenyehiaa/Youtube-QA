<script setup>
import { ref, onMounted } from "vue";
import VideoSidebar from "./components/VideoSidebar.vue";
import VideoPlayer from "./components/VideoPlayer.vue";
import ChatPanel from "./components/ChatPanel.vue";
import { listVideos } from "./api";

const videos = ref([]);
const selectedId = ref(null);
const seek = ref({ videoId: null, t: 0 });
const sessionId = crypto.randomUUID();

async function refresh() {
  videos.value = await listVideos();
}

function onSelect(id) {
  selectedId.value = id;
  seek.value = { videoId: id, t: 0 };
}

function onSeek({ videoId, t }) {
  selectedId.value = videoId;
  seek.value = { videoId, t };
}

onMounted(refresh);
</script>

<template>
  <div class="layout">
    <VideoSidebar
      :videos="videos"
      :selected-id="selectedId"
      @select="onSelect"
      @changed="refresh"
    />
    <main class="center">
      <VideoPlayer :video-id="selectedId" :seek="seek" />
    </main>
    <ChatPanel
      :session-id="sessionId"
      :video-id="selectedId"
      :videos="videos"
      @seek="onSeek"
    />
  </div>
</template>
