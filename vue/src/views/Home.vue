<template>
  <main class="home">
    <home-main/>
    <div class="home-main container">
      <!--<div class="tabs">
        <input type="radio" id="explore" v-model="tab" value="explore" name="home-tabs" aria-label="explore" class="tab" checked>
        <label for="explore">EXPLORE</label>
        <input type="radio" id="search" v-model="tab" value="search" name="home-tabs" aria-label="search" class="tab">
        <label for="search">SEARCH</label>
      </div>
      <div class="explore-tab" v-show="tab === 'explore'">
        <home-description />
        <home-plays/>
        <home-themes/>
        <home-timeline/>
      </div>
      <div class="search-tab" v-if='tab == "search"'>
        <home-search/>
      </div>-->
    </div>
  </main>
</template>


<script>
import HomeMain from '../components/home-modules/HomeMain.vue'
/*import HomeDescription from '../components/home-modules/HomeDescription.vue'
 import HomePlays from '../components/home-modules/HomePlays.vue'
import HomeThemes from '../components/home-modules/HomeThemes.vue'
import Timeline from '../components/additional-modules/Timeline.vue' */
// HomeSearch
//HomePlays,
//    HomeThemes,
//    Timeline,
// HomeDescription,
export default {
  name: 'Home',
  components: {
    HomeMain,


  },
  data () {
    return {
      tab: "explore",
    }
  }
}
</script>

