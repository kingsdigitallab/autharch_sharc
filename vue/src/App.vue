<template>
  <div id="app">
    <TheHeader/>
    <router-view/>
		<TheFooter />
  </div>
</template>

<script>
import TheHeader from './components/TheHeader.vue'
import TheFooter from './components/TheFooter.vue'

export default {
  name: 'app',
  components: {
    TheHeader,
		TheFooter
  },

}
</script>

<style lang="scss">
@import './scss/style.scss';
@import './scss/all.min.css';
</style>
