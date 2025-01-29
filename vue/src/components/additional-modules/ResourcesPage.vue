<template>
    <div class="resources-page">
        <h1 class="page-title">{{getPage.title}}</h1>
        <template v-if="!loading">
            <div class="links">
                <router-link to="/resources/bibliography" class="link-button-primary small arrow">Bibliography</router-link>
                <router-link v-if="getPageStatus" to="/resources/glossary" class="link-button-primary small arrow">Glossary</router-link>
            </div>
            <!-- TODO needs refactoring now that we have API data -->
            <span v-for="block in getResources" v-bind:key="block.id">
            <div class="two-column-50-50">
                <div v-if="block.type == 'heading'"><h2>{{ block.value }}</h2></div>
                <div v-if="block.type == 'document'">
                    <div>
                <div>
                    <h3>{{ block.value.title }}</h3>
                    <p><a :href="block.value.url" class="button-secondary small pdf mgn-right" target="_blank">Download PDF</a>{{ block.value.title }}</p>
                </div>
            </div>
                </div>
                <div v-if="block.type == 'image'">
                    <div>
                <div>
                    <h3>{{ block.value.heading }}</h3>
                    {{ block.value.body }}
                    <img :src="block.value.full_url" :width="block.value.full_width" :height="block.value.full_height" alt=""/>
                </div>
            </div>
                </div>
                <div v-if="block.type == 'embed'">
                    <div>
                <div>
                    <h3>{{ block.value.heading }}</h3>
                    {{ block.value.body }}
                    <p>
                    <iframe width="200" height="113" :src="block.value.url" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                    </p>
                </div>
            </div>
                </div>
                </div>
            </span>
        </template>
        <div v-else class="loader"></div>
    </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'ResourcesPage',
  computed: mapGetters(['getPage', 'getPageStatus', 'getResources']),
  data() {
    return {
        loading: true,
    }
  },
  methods: {
  async updatePage() {
        this.loading = true;
        //await this.fetchPageStatus('resources');
        this.loading = false;
    },
    ...mapActions(['fetchPageStatus']),
    ...mapActions(['fetchResources'])
  },
  async created() {
    //await this.fetchPageStatus('glossary');
    await this.fetchResources();
    this.loading = false;
  }
}
</script>