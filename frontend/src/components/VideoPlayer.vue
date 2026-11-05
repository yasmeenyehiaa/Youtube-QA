<script setup>
import { computed } from "vue";

const props = defineProps({
  videoId: String,
  seek: { type: Object, default: () => ({ videoId: null, t: 0 }) },
});

const src = computed(() => {
  if (!props.videoId) return "";
  const start = props.seek.videoId === props.videoId ? Math.floor(props.seek.t || 0) : 0;
  const autoplay = props.seek.videoId === props.videoId && props.seek.autoplay ? "&autoplay=1" : "";
  return `https://www.youtube.com/embed/${props.videoId}?start=${start}&rel=0${autoplay}`;
});
</script>

<template>
  <div class="player">
    <iframe
      v-if="videoId"
      :src="src"
      title="YouTube video player"
      allow="accelerometer; autoplay; encrypted-media; picture-in-picture"
      allowfullscreen
    ></iframe>
    <div v-else class="placeholder">Add a video, then select it to start.</div>
  </div>
</template>
