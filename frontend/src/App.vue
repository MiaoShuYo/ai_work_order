<script setup lang="ts">
import NavBar from './components/layout/NavBar.vue'
</script>
<template>
    <nav-bar />
    <router-view />
</template>

<script setup lang="ts">
</script>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html,
body,
#app {
    height: 100%;
    width: 100%;
}
</style>