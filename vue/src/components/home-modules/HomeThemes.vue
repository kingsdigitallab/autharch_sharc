<template>
  <div class="home-themes">
        <template v-if="!loading">
            <div class="category" v-for='(category, index) in themesList' v-bind:key='index'>
                <h2>{{category.title}}</h2>
                <div class="slider-container">
                    <VueSlickCarousel class="slider" ref="carousel" v-bind="sliderOptions">
                        <div class="object-single" v-for='(object, index) in category.featuredObjects' v-bind:key='index'>
                            <router-link :to="{name: 'object', params: {id: object.id}}">
                                <div class="object-thumbnail">
                                    <!-- an empty span is required here: vue slick carousel is not working on mobile without a pre-defined span of the image size (it doesn't wait for the image to load) -->
                                    <span></span>
                                    <img v-bind:src="object.resource" v-bind:alt="object.title"/>
                                </div>
                                <div class="object-description">
                                    <p class="details">{{object.creation_date}}<span class="delimiter" v-if="object.creation_date">|</span>{{object.category}}</p>
                                    <h4>{{object.title | truncate(100)}}</h4>
                                    <p class="details">
                                        <span v-bind:key="index" v-for="(entity, index) in object.creators">
                                            {{entity}}<span v-if="index != object.creators.length - 1">;&#160;</span>
                                        </span>
                                    </p>
                                </div>
                            </router-link>
                        </div>
                    </VueSlickCarousel>
                </div>
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
  name: 'fetchThemes',
  components: {VueSlickCarousel},
  computed: mapGetters(['themesList']),
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
                "breakpoint": 1000,
                "settings": {
                    "slidesToShow": 3,
                    "slidesToScroll": 3,
                    }
                },
                {
                "breakpoint": 850,
                "settings": {
                    "slidesToShow": 2,
                    "slidesToScroll": 2,
                    }
                },
                {
                "breakpoint": 450,
                "settings": {
                    "slidesToShow": 1,
                    "slidesToScroll": 1,
                    }
                }
            ]
        },
        loading: true
    }
  },
  methods: {
    ...mapActions(['fetchThemes']),
  },
  async created() {
    await this.fetchThemes();
    this.loading = false;
  },
}
</script>