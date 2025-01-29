<template>
  <div class="related-objects">
    <h2 v-if="showTitle">Related objects</h2>
    <div class="slider-container">
      <VueSlickCarousel class="slider" ref="related" v-bind="relatedOptions">
        <div v-for='(object, index) in relatedObjects' v-bind:key="index" class="object-single">
          <router-link :to="{name: 'object', params: {id: object.pk}}">
                    <span class="object-thumbnail">
                      <span></span>
                      <img v-if="object.media[0].thumbnail_url != 'PLACEHOLDER'" :src="object.media[0].thumbnail_url" :alt="object.unittitle"/>
                    <img v-else src="@/assets/images/sharc-imageplaceholder-light.jpg" height="1602" width="1644" alt="Image placeholder"/>
                    </span>
            <div class="object-description">
              <p class="details">{{ object.medium }}</p>
              <h4>{{ object.unittitle }}</h4>
            </div>
          </router-link>
        </div>
      </VueSlickCarousel>
    </div>
  </div>
</template>

<script>
import VueSlickCarousel from 'vue-slick-carousel'
import 'vue-slick-carousel/dist/vue-slick-carousel.css'
import 'vue-slick-carousel/dist/vue-slick-carousel-theme.css'

export default {
  name: 'RelatedObjects',
  props: {
    'relatedObjects':Array,
    'showTitle': {
      type: Boolean,
      default: true
    }
  }
  ,
  components: {VueSlickCarousel},
  data: function () {
    return {
      relatedOptions: {
        "arrows": true,
        "dots": true,
        "slidesToShow": 4,
        "slidesToScroll": 4,
        "initialSlide": 0,
        "responsive": [
          {
            "breakpoint": 1100,
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
      }
    }
  }
}
</script>
