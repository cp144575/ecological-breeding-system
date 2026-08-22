<template>
  <div class="page-container">
    <div v-if="$slots.header_left || $slots.header_right" class="header-actions">
      <div class="header-left">
        <slot name="header_left" />
      </div>
      <div class="header-right">
        <slot name="header_right" />
      </div>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts"></script>

