<template>
    <div class="home-page">
        <div class="main-banner">
            <div class="background"></div>
            <figure>
                <template v-if="!loading">
                    <VueSlickCarousel @init="handleInit" @afterChange="handleAfterChange" ref="carousel" class="slider-images-block" v-bind="sliderOptions">
                        <div v-for='(banner, index) in mainBanners' v-bind:key="index">
                            <router-link :to="{name: 'home', params: {id: banner.id}}">
                                <span></span>
                                <img v-bind:src="banner.resource" v-bind:alt="banner.title" />
                            </router-link>
                        </div>
                    </VueSlickCarousel>
                    <button class="slider-arrow prev" aria-label="previous slide" @click="showPrev">&#xf053;</button>
                    <button class="slider-arrow next" aria-label="next slide" @click="showNext">&#xf054;</button>
                    <div class="main-banner-description">
                        <div class="slider-button-block">
                            <span v-for='(banner, i) in mainBanners' v-bind:key="i">
                                <button class="slider-button" v-on:click="goTo(i)" v-bind:class="{'active': currentSlide == (i)}" aria-label="slider button"><span hidden>{{ banner.title }}</span></button>
                            </span>
                        </div>
                        <!-- Removed for event launch -->
                        <!--<router-link v-if="this.currentImg.id" :to="{name: 'object', params: {id: this.currentImg.id}}">-->
                        <figcaption>
                            <h3>{{ this.currentImg.title }}</h3>
                            <p>
                                <span v-for="(entity, index) in this.currentImg.creators" v-bind:key="index">{{ entity }}
                                    <template v-if="index != currentImg.creators.length-1">, </template>
                                </span>
                            </p>
                            <!-- Removed for event launch -->
                            <!-- <button class="button-secondary arrow">See object</button> -->
                        </figcaption>
                        <!-- Removed for event launch -->
                        <!--</router-link>-->
                    </div>
                </template>
                <div v-else class="loader"></div>
            </figure>
        </div>
        <!-- Static placeholder content -->
        <div class="placeholder">
            <div>
                <span>
                    <p>What has Shakespeare done for the royal family, and what has the royal family done for Shakespeare? This is the central research question of ‘Shakespeare in the Royal Collection’, an AHRC funded project (September 2018  - July 2022), which focuses on the Shakespeare-related holdings in the Royal Collection and Royal Archives and the stories they have to tell, primarily during the period 1714-1945.
                    </p>

                    <p>
                    This website includes a searchable database of the Shakespeare-related objects in the Royal Collection, an online exhibition, an explanatory timeline, and stories from the collection. Educational resources for teachers are also available and are free to download and use.
                    </p>
                </span>
                <br>
                <br>
                <hr>
                <br>
            </div>
            <div class="two-column-50-50">
                <div>
                    <a href="/objects"><img src="@/assets/images/1008422-1606818568.jpg" width="691" height="500" alt="David Garrick Reciting his Ode, at Drury Lane Theatre, on dedicating a Building & erecting a Statue, to Shakespeare, Etching and engraving"></a>
                    <a href="/objects">
                        <h3>Search the Database</h3>
                    </a>
                    <p>How many photographs on the theme of <em>The Winter’s Tale</em>  were acquired by Queen Victoria between 1848 and 1880? The Search page offers various ways to discover the Shakespeare-related holdings in the Royal Collection and Royal Archives, by search and by filter.</p>
                </div>
                <div>
                    <a href="/exhibition">
                    <img src="@/assets/images/912381-1565625545.jpg" width="1000" height="789" alt="rince Arthur and Prince Leopold in the costume of the sons of King Henry IVth, Albumen print hand-coloured with watercolour">
                    <h3>Exhibition</h3>
                    </a>
                    <p>‘Making History: Shakespeare and the Royal Family’ brings together objects from the Royal Collection and Royal Archives with prints, paintings and decorative art objects in collections elsewhere. It explores the tangible effect of royal patronage on the afterlives of Shakespeare’s plays. </p>
                </div>
                <div>
                    <a href="/stories">
                    <img src="@/assets/images/472881-1619192659.jpg" width="1000" height="764" alt="Herne's Oak, Windsor Park, Etching with hand colouring">
                    <h3>Stories</h3>
                    </a>
                    <p>A way to explore some of the key themes that emerge from the Royal Collection's Shakespeare-related objects, including the royals' own forays into Shakespeare-themed art, and the mystery of Herne's Oak.</p>
                </div>
                <div>
                    <a href="/timeline">
                    <img src="@/assets/images/254426-1330619342.jpg" width="684" height="500" alt="Fan depicting 'The Three Eldest Sons of King George III, Ivory brisé fan; the guards (identical) with two blue Wedgwood jasper-ware plaques, strung cut-steel beads and applied marquisites, backed with gold leaf">
                    <h3>Timeline</h3>
                    </a>
                    <p>The timeline gives a sense of the history of Shakespeare in the Royal Collection. It spans the seventeenth century to the present day, placing the objects in our database in context. </p>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'
import VueSlickCarousel from 'vue-slick-carousel'
import 'vue-slick-carousel/dist/vue-slick-carousel.css'

export default {
    name: 'HomeMain',
    components: { VueSlickCarousel },
    computed: mapGetters(['mainBanners']),
    data() {
        return {
            currentImg: 0,
            currentSlide: 0,
            sliderOptions: {
                "arrows": false,
                "dots": false
            },
            loading: true
        }
    },
    methods: {
        showNext() {
            this.$refs.carousel.next();
        },
        showPrev() {
            this.$refs.carousel.prev();
        },
        handleInit() {
            this.currentImg = this.mainBanners[0];
        },
        handleAfterChange(slideIndex) {
            this.currentImg = this.mainBanners[slideIndex];
            this.currentSlide = slideIndex;
        },
        goTo(index) {
            this.$refs.carousel.goTo(index);
        },
        ...mapActions(['fetchBanners']),
    },
    async created() {
        await this.fetchBanners();
        this.loading = false;
    },
}
</script>