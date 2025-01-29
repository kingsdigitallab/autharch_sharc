<template>
  <div class="timeline">
      <h1 class="page-title">Timeline</h1>
      <div id="timeline-embed"></div>
  </div>
</template>

<script>
import {TL} from '../../assets/timeline/js/timeline'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Timeline',
  data() {
    return {
        options: {
            hash_bookmark: true,
            zoom_sequence: [0.1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
            initial_zoom: 0,
            scale_factor: 1,
            marker_height_min: 50,
            marker_width_min: 150,
            timenav_height_min: 300,
            dragging: true,
            optimal_tick_width: 150,
        },
    }
  },
  computed: mapGetters(['timelineData']),
  methods: {
        ...mapActions(['fetchTimelineData']),
        loadTimeline: async function (){
            await this.fetchTimelineData();
            new TL.Timeline('timeline-embed', this.timelineData, this.options);
        }
    },
  mounted() {
    this.$nextTick(function () {
        this.loadTimeline();
    })
  }
}
</script>


<style>
@import '../../assets/timeline/css/timeline.css';
@import '../../scss/components/_timeline.scss';
</style>
