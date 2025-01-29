<template>
  <div class="home-plays">
        <template v-if="!loading">
            <h2>Plays</h2>
            <div class="slider-container">
                <VueSlickCarousel class="slider" ref="carousel" v-bind="sliderOptions">
                    <div v-for='(play, index) in playsList' v-bind:key="index" class="play-single">
                        <router-link :to="{name: 'objects', query: {work: [play.title]}}">
                            <div class="play-image">
                                <span></span>
                                <img v-bind:src="play.resource" v-bind:alt="play.title"/>
                            </div>
                            <div class="play-description">
                              <h4><em>{{play.title}}</em></h4>
                                <p>{{play.count}} objects</p>
                            </div>
                        </router-link>
                    </div>
                </VueSlickCarousel>
            </div>
        </template>
        <div v-else class="loader"></div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import VueSlickCarousel from 'vue-slick-carousel'
import 'vue-slick-carousel/dist/vue-slick-carousel.css'
import 'vue-slick-carousel/dist/vue-slick-carousel-theme.css'

export default {
  name: 'HomePlays',
  components: {VueSlickCarousel},
  computed: mapGetters(['playsList']),
  data () {
    return {
        sliderOptions: {
            "arrows": true,
            "dots": true,
            "slidesToShow": 4,
            "slidesToScroll": 4,
            "initialSlide": 0,
            "responsive": [
                {
                "breakpoint": 1500,
                "settings": {
                    "slidesToShow": 3,
                    "slidesToScroll": 3,
                    }
                },
                {
                "breakpoint": 970,
                "settings": {
                    "slidesToShow": 2,
                    "slidesToScroll": 2,
                    }
                },
                {
                "breakpoint": 600,
                "settings": {
                    "arrows": false,
                    "slidesToShow": 1,
                    "slidesToScroll": 1
                    }
                }
            ]
        },
        loading: true
    }
  },
  methods: {
    ...mapActions(['fetchPlays']),
  },
  async created() {
    await this.fetchPlays();
    this.loading = false;
  },
}
</script>
