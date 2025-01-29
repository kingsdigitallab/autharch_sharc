<template>
  <div class="archive-single" v-if="!loading">
    <h1 class="page-title">{{ getArchive.unittitle }}</h1>
    <div class="object-image" v-if="getArchive.media && getArchive.media.length > 0">
      <div class="image-block">
        <div id="openseadragon" ref="openSeaDragon" class="image"></div>
        <div id="navigation-pane" class="image-control">
          <span class="nav-icon" id="prev"></span>
          <div class="control">
            <span class="nav-icon" id="zoom-in"></span>
            <span class="nav-icon" id="zoom-out"></span>
            <span class="nav-icon" id="rotate-left"></span>
            <span class="nav-icon" id="rotate-right"></span>
            <span class="nav-icon" id="default"></span>
            <span class="nav-icon" id="full-mode"></span>
          </div>
          <span class="nav-icon" id="next"></span>
        </div>
      </div>
      <div class="thumbnails" id="referenceStrip">
        <button class="thumbnail-button prev" aria-label="previous slide" @click="showPrev"><span hidden>Previous</span>
        </button>
        <VueSlickCarousel class="thumbnail-list" ref="carousel" v-bind="sliderOptions">
          <div v-for="(image, index) in getArchive.media" v-bind:key="index" class="thumbnail"
               v-on:click="updateImage(index)">
            <!-- span is necessary for a mobile version; otherwise, VueSlickCarousel won't preload properly to fit images -->
            <span></span>
            <img :src="image.thumbnail_url" alt=""/>
          </div>
        </VueSlickCarousel>
        <button class="thumbnail-button next" aria-label="next slide" @click="showNext"><span hidden>Next</span>
        </button>
      </div>
    </div>
    <div class="object-description">
      <div class="two-column-50-50">
        <section>
          <!-- Details -->
          <h2>Details</h2>
          <span v-if="getArchive.unittitle">
                        <p>Title:</p>
                        <p v-html="getArchive.unittitle"></p>
                    </span>
          <!-- TO DO : Add Unitid" -->
          <span>
                        <p>RA / RCT ref.:</p>
                        <p>{{ getArchive.reference }}</p>
                    </span>
          <!-- End TO DO : Add Unitid" -->
          <span v-if="getArchive.category && getArchive.category != ''">
                        <p>Category:</p>
                        <p>
                            <router-link :to="{name: 'objects', query: {category: [getArchive.category]}}">{{
                                getArchive.category
                              }}</router-link>
                        </p>
                    </span>
          <span v-if="getArchive.date_of_creation && getArchive.date_of_creation != ''">
                        <p>Date of Creation:</p>
                        <p v-if="getArchive.date_of_creation_notes">{{ getArchive.date_of_creation_notes }}</p>
                        <p v-else>{{ getArchive.date_of_creation[0] }}</p>
                    </span>
          <span v-if="getArchive.date_of_acquisition && getArchive.date_of_acquisition != ''">
                        <p>Date of Acquisition:</p>
                        <p v-if="getArchive.date_of_acquisition_notes">{{ getArchive.date_of_acquisition_notes }}</p>
                        <p v-else>{{ getArchive.date_of_acquisition[0] }}</p>
                    </span>
          <span v-if="getArchive.place_of_origin && getArchive.place_of_origin != ''">
                        <p>Place of Origin:</p>
                        <p v-html="getArchive.place_of_origin"></p>
                    </span>
          <span v-if="getArchive.medium && getArchive.medium != ''">
                        <p>Medium:</p>
                        <p v-html="getArchive.medium"></p>
                    </span>
          <span v-if="getArchive.size && getArchive.size != ''">
                        <p>Size:</p>
                        <p v-html="getArchive.size"></p>
                    </span>
          <span v-if="getArchive.provenance && getArchive.provenance.html.length >0">
                        <p>Provenance:</p>
                        <p v-html="getArchive.provenance.html"></p>
                    </span>
          <span v-if="getArchive.label && getArchive.label != ''">
                        <p>Label or Inscription:</p>
                        <p v-html="getArchive.label"></p>
                    </span>
          <span v-if="getArchive.reference && getArchive.reference != '' && !/^[A-Z].*/.test(getArchive.reference)">
                        <p>Link:</p>
                        <p>
                            <a :href="'https://www.rct.uk/collection/search#/5/collection/'+getArchive.rct_link">{{
                                getArchive.unittitle
                              }} at the Royal Collection Trust</a></p>
                    </span>
        </section>
        <section>
          <!-- Shakespeare Associations -->
          <div
              v-if="getArchive.related_sources && ((getArchive.related_sources.individuals && getArchive.related_sources.individuals.length > 0 )|| (getArchive.related_sources.works && getArchive.related_sources.works.length > 0 )|| (getArchive.related_sources.texts && getArchive.related_sources.texts.length > 0) || (getArchive.related_sources.performances && getArchive.related_sources.performances.length > 0) || (getArchive.related_sources.sources && getArchive.related_sources.sources.length > 0 )|| (getArchive.related_sources.groups && getArchive.related_sources.groups.length > 0))">
            <h2>Shakespeare Associations</h2>
            <span v-if="getArchive.related_sources.individuals && getArchive.related_sources.individuals.length > 0">
                            <router-link class="link-button-primary small" :key="i"
                                         v-for="(connection, i) in getArchive.related_sources.individuals"
                                         :to="{name: 'objects', query: {individual_connections: [connection]}}">{{
                                connection
                              }}</router-link>
                        </span>
            <span v-if="getArchive.related_sources.works && getArchive.related_sources.works.length > 0">
                            <router-link class="link-button-primary small" :key="i"
                                         v-for="(work, i) in getArchive.related_sources.works"
                                         :to="{name: 'objects', query: {work: [work]}}">{{ work }}</router-link>
                        </span>
            <span v-if="getArchive.related_sources.texts && getArchive.related_sources.texts.length > 0">
                            <router-link class="link-button-primary small" :key="i"
                                         v-for="(text, i) in getArchive.related_sources.texts"
                                         :to="{name: 'objects', query: {text: [text]}}">{{ text }}</router-link>
                        </span>
            <span v-if="getArchive.related_sources.performances && getArchive.related_sources.performances.length > 0">
                            <router-link class="link-button-primary small" :key="i"
                                         v-for="(performance, i) in getArchive.related_sources.performances"
                                         :to="{name: 'objects', query: {performance: [performance]}}">{{
                                performance
                              }}</router-link>
                        </span>
            <span v-if="getArchive.related_sources.sources && getArchive.related_sources.sources.length > 0">
                            <router-link class="link-button-primary small" :key="i"
                                         v-for="(source, i) in getArchive.related_sources.sources"
                                         :to="{name: 'objects', query: {source: [source]}}">{{
                                source
                              }}</router-link>
                        </span>
            <span v-if="getArchive.related_sources.groups && getArchive.related_sources.groups.length > 0">
                            <h3>Related groups</h3>
                            <router-link class="link-button-primary small" :key="i"
                                         v-for="(group, i) in getArchive.related_sources.groups"
                                         :to="{name: 'group', params: {subpage: group.url_slug}}">{{
                                group.title
                              }}</router-link>
                        </span>
          </div>
          <!-- TODO: add read more -->
          <!-- Related People -->
          <div
              v-if="getArchive.related_people && (getArchive.related_people.acquirers > 0 || getArchive.related_people.all_people.length > 0)">
            <h2>Related People</h2>
            <span v-if="getArchive.related_people.acquirers && getArchive.related_people.acquirers.length > 0">
                            <p>{{ 'Acquirer' | pluralize(getArchive.related_people.acquirers.length) }}:</p>
                            <p :key="index" v-for="(acquirer, index) in getArchive.related_people.acquirers">
                                {{ acquirer }}<template v-if="index != getArchive.related_people.acquirers.length - 1">;&#160;</template>
                            </p>
                        </span>
            <span v-for="(people, type) in sortedPeople(getArchive.related_people.all_people)" :key="type">

                              <p> {{ type | capitalize | pluralize(people.length) }}:</p>
                              <p>
                                <ul>
              <li v-for="person in people" v-bind:key="person.facet_label" v-html="person.name"></li>
                                </ul>

                              </p>


                        </span>

          </div>
          <!-- References -->
          <div
              v-if="(getArchive.references_published && getArchive.references_published.length > 0) || (getArchive.references_unpublished && getArchive.references_unpublished.length > 0)">
            <h2>References</h2>
            <template v-if="getArchive.references_published && getArchive.references_published.length > 0">
              <h4>Published references</h4>
              <ul v-if="getArchive.references_published">
                <li v-for="reference in getArchive.references_published" v-bind:key="reference">
                  {{ reference.reference }}
                </li>
              </ul>
            </template>
            <br v-if="getArchive.references_unpublished && getArchive.references_unpublished.length > 0 && getArchive.references_published && getArchive.references_published.length > 0"/>
            <template v-if="getArchive.references_unpublished && getArchive.references_unpublished.length > 0">
              <h4>Unpublished references</h4>
              <ul v-if="getArchive.references_unpublished">
                <li v-for="reference in getArchive.references_unpublished" v-bind:key="reference">
                  {{ reference.reference }}
                </li>
              </ul>

            </template>
          </div>
        </section>
      </div>
      <div>
        <section>
          <!-- Additional Notes -->
          <div
              v-if="notes && notes != '' || getArchive.publication_details && getArchive.publication_details != '' || getArchive.label && getArchive.label != ''">
            <h2>Additional Notes</h2>
            <p v-if="notes && notes != ''" v-html="notes"></p>
          </div>
        </section>
          <!--<section>
         Related Material
          <div
              v-if="getArchive.related_material_parsed && getArchive.related_material_parsed.length >0 && getArchive.related_material_parsed != 'None' ">
            <h2>Related material</h2>
            <p v-html="getArchive.related_material_parsed"></p>
          </div>
        </section> -->
      </div>
    </div>
    <related-objects-template v-if="getArchive.related_entries && getArchive.related_entries.length > 0"
                              v-bind:relatedObjects="getArchive.related_entries"></related-objects-template>
  </div>
  <div v-else class="loader"></div>
</template>
<script>
import OpenSeadragon from 'openseadragon'
import VueSlickCarousel from 'vue-slick-carousel'
import 'vue-slick-carousel/dist/vue-slick-carousel.css'
import 'vue-slick-carousel/dist/vue-slick-carousel-theme.css'
import {mapActions, mapGetters} from 'vuex'

import RelatedObjectsTemplate from '../templates/RelatedObjectsTemplate.vue';

let tileSources = []
let viewer = {}

function startOpenSeaDragon(index) {
  if (document.getElementsByClassName("openseadragon-container").length == 0) {
    viewer = OpenSeadragon({
      id: 'openseadragon',
      tileSources: [
        tileSources
      ],
      sequenceMode: true,
      zoomInButton: "zoom-in",
      zoomOutButton: "zoom-out",
      homeButton: "default",
      fullPageButton: "full-mode",
      rotateLeftButton: "rotate-left",
      rotateRightButton: "rotate-right",
      nextButton: "next",
      previousButton: "prev",
      degrees: 0,
      showRotationControl: true,
      gestureSettingsTouch: {
        pinchRotate: true
      }
    })

  }

  viewer.goToPage(index)
}

export default {
  name: 'ArchiveSingle',
  components: {VueSlickCarousel, RelatedObjectsTemplate},
  computed: mapGetters(['getArchive']),
  data: function () {
    return {
      loading: true,
      tab: "summary",
      viewer: '',
      notes: '',
      placeholder_image: require('../../assets/images/sharc-imageplaceholder-light.jpg'),
      sliderOptions: {
        "arrows": false,
        "dots": false,
        "vertical": true,
        "verticalSwiping": true,
        "initialSlide": 0,
        "responsive": [{
          "breakpoint": 600,
          "settings": {
            "vertical": false,
            "verticalSwiping": false,
            "slidesToShow": 2,
            "slidesToScroll": 2,
          }
        },]
      }
    }
  },
  filters: {
    // from vue docs
    capitalize: function (value) {
      if (!value) return ''
      value = value.toString()
      return value.charAt(0).toUpperCase() + value.slice(1)
    }
  },
  methods: {
    async updatePage() {
      if (this.$route.params.id) {
        await this.fetchArchive(this.$route.params.id);
      } else if (this.$route.params.reference) {
        await this.fetchRCTArchive(this.$route.params.reference);
      }
      // Changing to notes_parsed
      this.notes = this.getArchive.notes_parsed;
     /* if (this.getArchive.notes_parsed) {
        if (this.getArchive.notes_parsed.length > 499) {
          this.notes = this.getArchive.notes_parsed.substring(0, 500);
        } else {
          this.notes = this.getArchive.notes_parsed;
        }

      }*/
      this.loading = false;
    },
    initOpenSeaDragon() {
      // Clear tile sources
      tileSources = []
      for (let index in this.getArchive.media) {
        if (this.getArchive.media[index].iiif_image_url != 'PLACEHOLDER') {
          tileSources.push(this.getArchive.media[index].iiif_image_url);
        } else {
          //Placeholder image
          tileSources.push({
            type: 'image',
            url: this.placeholder_image,
            buildPyramid: false
          });
        }

      }

      startOpenSeaDragon(0);
    },
    showNext() {
      this.$refs.carousel.next();
    },
    showPrev() {
      this.$refs.carousel.prev();
    },
    updateImage(index) {
      startOpenSeaDragon(index);
    },
    sortedList(list) {
      return list.slice().sort((a, b) => a.localeCompare(b));
    },
    // sort the list of people by group, then surname when it works
    sortedPeople(list) {
      let peopleList = list.slice().sort((a, b) => a.type.localeCompare(b.type));
      let sortedPeople = {};
      for (var person in peopleList) {
        if (sortedPeople[peopleList[person].type] == null) {
          sortedPeople[peopleList[person].type] = [];
        }
        sortedPeople[peopleList[person].type].push(peopleList[person]);
      }
      for (var index in sortedPeople) {
        // Doing this in two stages because surname isn't yet reliable
        sortedPeople[index] = sortedPeople[index].slice().sort((a, b) => a.surname.localeCompare(b.surname));
      }
      return sortedPeople;
    },
    ...mapActions(['fetchArchive']),
    ...mapActions(['fetchRCTArchive']),
  },
  created() {
    this.updatePage();
  },
  mounted() {

    setTimeout(() => {
      if (this.$refs.openSeaDragon && !this.loading) {
        this.initOpenSeaDragon();
      }
    }, 1000);
  },
  watch: {
    $route() {
      this.updatePage();
    }
  }
}
</script>