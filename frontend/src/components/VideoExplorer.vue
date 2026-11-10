<script setup>
defineProps({
  videos: { type: Array, default: () => [] },
  currentVideoId: { type: String, default: null },
  collapsed: { type: Boolean, default: false },
});

defineEmits(["select", "toggle"]);
</script>

<template>
  <aside class="video-explorer" :class="{ collapsed }" aria-label="Video navigation">
    <div class="explorer-topbar">
      <h2 v-if="!collapsed" class="explorer-heading">EXPLORER</h2>
      <button
        class="explorer-toggle"
        type="button"
        :aria-label="collapsed ? 'Expand video explorer' : 'Collapse video explorer'"
        :aria-expanded="!collapsed"
        :title="collapsed ? 'Expand explorer' : 'Collapse explorer'"
        @click="$emit('toggle')"
      >
        {{ collapsed ? "›" : "‹" }}
      </button>
    </div>
    <nav class="explorer-nav" aria-label="Videos">
      <button
        class="explorer-item library-item"
        :aria-current="currentVideoId ? undefined : 'page'"
        title="All videos"
        @click="$emit('select', null)"
      >
        <span class="explorer-icon" aria-hidden="true">⌂</span>
        <span v-if="!collapsed">All videos</span>
      </button>
      <div v-if="!collapsed" class="explorer-section-title">YOUR VIDEOS</div>
      <button
        v-for="video in videos"
        :key="video.video_id"
        class="explorer-item"
        :class="{ active: currentVideoId === video.video_id }"
        :aria-current="currentVideoId === video.video_id ? 'page' : undefined"
        :title="video.title"
        @click="$emit('select', video.video_id)"
      >
        <span class="explorer-icon" aria-hidden="true">▶</span>
        <span v-if="!collapsed" class="explorer-video-title">{{ video.title }}</span>
      </button>
      <p v-if="!videos.length && !collapsed" class="explorer-empty">No videos yet</p>
    </nav>
  </aside>
</template>
