<template>
  <div class="archival-list">
    <div class="list-summary">
      <div class="summary">
        <form @submit.prevent="searchRecords" class="search-field">
            <input type="search" v-model="searchTerm" aria-label="Search by title, reference, description, and references" placeholder="Search by name, date, category, creator" onfocus="this.placeholder=''" onblur="this.placeholder='Search by name, date, category, creator'"/>
            <input type="submit" class="search-button" aria-label="Search button" value=""/>
        </form>
        <p><a @click="clearSearch()" href="#">X</a> {{getTotalArchives}} {{'object' | pluralize(getTotalArchives)}} found</p>
        <div class="sort-by-section">
          <fieldset>
            <label for="sort-by">Sort by</label>
            <select id="sort-by" class="sort-by" aria-label="Sort by" v-model="sortBy" v-on:change="changeSortBy()">
              <option value="_score" v-bind:selected="sortBy == '_score'">Relevance</option>
              <option value="unittitle" v-bind:selected="sortBy == 'unittitle'">Title</option>
              <option value="date_of_creation" v-bind:selected="sortBy == 'date_of_creation'">Creation year</option>
              <option value="date_of_acquisition" v-bind:selected="sortBy == 'date_of_acquisition'">Acquisition year</option>
            </select>
          </fieldset>
          <button class="transparent asc-desc" v-on:click="sortAscDesc()"><span hidden>Sort</span><i :class="sortDescVal ? 'far fa-sort-alpha-down-alt' : 'far fa-sort-alpha-down'"></i></button>
          <button class="button-primary filter display-mobile" v-on:click="toggleFilters" aria-label="filter objects"><span>Filter</span></button>
        </div>
      </div>
    </div>
    <div class="two-column-20-80">
      <div class="filters">
        <button class="display-mobile filter-button" v-on:click="toggleFilters" aria-label="filter objects">Close</button>
        <h2>Filters</h2>

        <div>
          <div class="filtergroup">
            <h3>Dates</h3>
            <fieldset id="creation_year" class="range" v-if="getArchivalFacets.creation_years && getArchivalFacets.creation_years[0] > 0 && getArchivalFacets.creation_years[1] > 0">
              <legend>Creation year</legend>
              <div id="creation-year-slider" ref="creationSlider"></div>
              <br>
              <input type="number" name="creation_start_year" aria-label="creation year start" class="range-year" :min="creationSlider.min" :max="creationSlider.max" v-model="minCreationRange" v-on:change="updateCreationSlider(minCreationRange, maxCreationRange)" />
              -
              <input type="number" name="creation_end_year" aria-label="creation year end" class="range-year" :min="creationSlider.min" :max="creationSlider.max" v-model="maxCreationRange" v-on:change="updateCreationSlider(minCreationRange, maxCreationRange)" />
              <input type="submit" class="button-primary" value="Filter" v-on:click="filterByYear('creation_years', minCreationRange, maxCreationRange)"/>
            </fieldset>
            

                      <fieldset id="acquisition_year" class="range" v-if="getArchivalFacets.acquisition_years && getArchivalFacets.acquisition_years[0] > 0 && getArchivalFacets.acquisition_years[1] > 0">
                <legend>Acquisition year</legend>
                <span hidden>Acquisition year range</span>
                <div id="acquisition-year-slider" ref="acquisitionSlider"></div>
                <br>
                <input type="number" name="acquisition_start_year" aria-label="acquisition year start" class="range-year" :min="acquisitionSlider.min" :max="acquisitionSlider.max" v-model="minAcquisitionRange" v-on:change="updateAcquisitionSlider(minAcquisitionRange, maxAcquisitionRange)" />
                -
                <input type="number" name="acquisition_end_year" aria-label="acquisition year end" class="range-year" :min="acquisitionSlider.min" :max="acquisitionSlider.max" v-model="maxAcquisitionRange" v-on:change="updateAcquisitionSlider(minAcquisitionRange, maxAcquisitionRange)" />
                <input type="submit" class="button-primary" value="Filter" v-on:click="filterByYear('acquisition_years', minAcquisitionRange, maxAcquisitionRange)"/>
            </fieldset>
           
          </div>

          <div class="filtergroup">
            <h3>People 
              <span class="tooltip">
                <span class="tooltiptext">
                  Some people are listed under more than one title. E.g. Elizabeth Bowes-Lyon as 'Elizabeth (1900-2002), Duchess of York' and 'Queen Elizabeth (1900-2002), the Queen Mother'. Clicking on one title for a person will show all objects they acquired under any of their titles.
                </span>
              </span>
            </h3>
             <fieldset v-if="getArchivalFacets.acquirer && getArchivalFacets.acquirer.length > 0">
              <legend>Acquirers <span class="count">{{getArchivalFacets.acquirer.length}}</span></legend>
              <input type="checkbox" id="acquirers-toggle" class="toggle-checkbox"/>
              <label for="acquirers-toggle" class="toggle-label"><span hidden>Expand/collapse acquirers</span></label>
              <div class="toggle-section">
                <div class="facets">
                  <label v-for="(acquirer, index) in sortedData(getArchivalFacets.acquirer, searchRelatedAcquirers, 'alphabetical')" v-bind:key="index" class="facet" v-show="index < 100 || relatedAcquirersCheckbox">
                    <input type="checkbox" name="acquirer" v-bind:aria-label="acquirer.key" :value="acquirer.key" v-on:click="filter('acquirer', acquirer.key)" :checked="checkedOption('acquirer', acquirer.key)"/> {{acquirer.key | capitalize}} <span class="count">{{acquirer.doc_count}}</span>
                  </label>
                </div>
              </div>
            </fieldset>

            <!-- TODO: Change to Creator values -->
             <fieldset v-if="getArchivalFacets.acquirer && getArchivalFacets.acquirer.length > 0">
              <legend>All People <span class="count"><template v-if="getArchivalFacets.people.length >100">100+</template><template v-else>{{getArchivalFacets.people.length}}</template></span></legend>
              <input type="checkbox" id="people-toggle" class="toggle-checkbox"/>
              <label for="people-toggle" class="toggle-label"><span hidden>Expand/collapse acquirers</span></label>
              <div class="toggle-section">
                <input type="text" id="people-autocomplete" v-on:keyup="filterPeople" v-model="searchRelatedPeople"/>
                <div class="facets">
                  <label v-for="(person, index) in getArchivalFacets.people" v-bind:key="index" class="facet" v-show="index < 100 || relatedPeopleCheckbox">
                    <input type="checkbox" name="people" v-bind:aria-label="person.key" :value="person.key" v-on:click="filter('people', person.key)" :checked="checkedOption('people', person.key)"/> {{person.key | capitalize}} <span class="count">{{person.doc_count}}</span>
                  </label>
                </div>
              </div>
            </fieldset>
          </div>

          <div class="filtergroup">
            <h3>Objects</h3>
                      <!-- convert to a template -->
          <fieldset v-if="getArchivalFacets.works && getArchivalFacets.works.length > 0">
            <legend>Works <span class="count">{{getArchivalFacets.works.length}}</span></legend>
            <input type="checkbox" id="works-toggle" class="toggle-checkbox"/>
            <label for="works-toggle" class="toggle-label"><span hidden>Expand/collapse works</span></label>
            <div class="toggle-section">
              <div class="facets">
                <label v-for="(work, index) in sortedData(getArchivalFacets.works, searchWorks, 'alphabetical')" v-bind:key="index" class="facet" v-show="index < 100 || worksCheckbox">
                    <input type="checkbox" name="work" v-bind:aria-label="work.key" :value="work.key" v-on:click="filter('work', work.key)" :checked="checkedOption('work', work.key)" /> {{work.key | capitalize}} <span class="count">{{work.doc_count}}</span>
                </label>
              </div>
            </div>
          </fieldset>
          <fieldset v-if="getArchivalFacets.individual_connections && getArchivalFacets.individual_connections.length > 0">
            <legend>Shakespeare as Individual <span class="count">{{getArchivalFacets.individual_connections.length}}</span></legend>
            <input type="checkbox" id="connections-toggle" class="toggle-checkbox"/>
            <label for="connections-toggle" class="toggle-label"><span hidden>Expand/collapse connections</span></label>
            <div class="toggle-section">
              <div class="facets">
                <label v-for="(connection, index) in sortedData(getArchivalFacets.individual_connections, searchConnections, 'alphabetical')" v-bind:key="index" class="facet" v-show="index < 100 || connectionsCheckbox">
                  <input type="checkbox" name="individual_connections" v-bind:aria-label="connection.key" :value="connection.key" v-on:click="filter('individual_connections', connection.key)" :checked="checkedOption('individual_connection', connection.key)" /> {{connection.key | capitalize}} <span class="count">{{connection.doc_count}}</span>
                </label>
              </div>
            </div>
          </fieldset>
          <fieldset v-if="getArchivalFacets.texts && getArchivalFacets.texts.length > 0">
            <legend>Texts <span class="count">{{getArchivalFacets.texts.length}}</span></legend>
            <input type="checkbox" id="texts-toggle" class="toggle-checkbox"/>
            <label for="texts-toggle" class="toggle-label"><span hidden>Expand/collapse texts</span></label>
            <div class="toggle-section">
              <div class="facets">
                <label v-for="(text, index) in sortedData(getArchivalFacets.texts, searchTexts, 'alphabetical')" v-bind:key="index" class="facet" v-show="index < 100 || textsCheckbox">
                  <input type="checkbox" name="text" v-bind:aria-label="text.key" :value="text.key" v-on:click="filter('text', text.key)" :checked="checkedOption('text', text.key)" /> {{text.key | capitalize}} <span class="count">{{text.doc_count}}</span>
                </label>
              </div>
            </div>
          </fieldset>
          <fieldset v-if="getArchivalFacets.performances && getArchivalFacets.performances.length > 0">
            <legend>Performances <span class="count">{{getArchivalFacets.performances.length}}</span></legend>
            <input type="checkbox" id="performances-toggle" class="toggle-checkbox"/>
            <label for="performances-toggle" class="toggle-label"><span hidden>Expand/collapse performances</span></label>
            <div class="toggle-section">
              <div class="facets">
                <label v-for="(performance, index) in sortedData(getArchivalFacets.performances, searchPerformances, 'alphabetical')" v-bind:key="index" class="facet" v-show="index < 100 || performancesCheckbox">
                  <input type="checkbox" name="text" v-bind:aria-label="performance.key" :value="performance.key" v-on:click="filter('performance', performance.key)" :checked="checkedOption('performance', performance.key)" /> {{performance.key | capitalize}} <span class="count">{{performance.doc_count}}</span>
                </label>
              </div>
            </div>
          </fieldset>
          <fieldset v-if="getArchivalFacets.sources && getArchivalFacets.sources.length > 0">
            <legend>Sources <span class="count">{{getArchivalFacets.sources.length}}</span></legend>
            <input type="checkbox" id="sources-toggle" class="toggle-checkbox"/>
            <label for="sources-toggle" class="toggle-label"><span hidden>Expand/collapse sources</span></label>
            <div class="toggle-section">
              <div class="facets">
                <label v-for="(source, index) in sortedData(getArchivalFacets.sources, searchSources, 'alphabetical')" v-bind:key="index" class="facet" v-show="index < 100 || sourcesCheckbox">
                  <input type="checkbox" name="text" v-bind:aria-label="source.key" :value="source.key" v-on:click="filter('source', source.key)" :checked="checkedOption('source', source.key)" /> {{source.key | capitalize}} <span class="count">{{source.doc_count}}</span>
                </label>
              </div>
            </div>
          </fieldset>

          <fieldset v-if="getArchivalFacets.category && getArchivalFacets.category.length > 0">
            <legend>Categories <span class="count">{{getArchivalFacets.category.length}}</span></legend>
            <input type="checkbox" id="categories-toggle" class="toggle-checkbox"/>
            <label for="categories-toggle" class="toggle-label"><span hidden>Expand/collapse categories</span></label>
            <div class="toggle-section">
              <div class="facets">
                <label v-for="(category, index) in sortedData(getArchivalFacets.category, searchCategories, 'alphabetical')" v-bind:key="index" class="facet" v-show="index < 100 || categoriesCheckbox">
                  <input type="checkbox" name="category" :value="category.key" v-if="category.key.length > 0" v-bind:aria-label="category.key" v-on:click="filter('category', category.key)" :checked="checkedOption('category', category.key)"/> {{category.key | capitalize}} <span class="count">{{category.doc_count}}</span>
                </label>
              </div>
            </div>
          </fieldset>
          </div>
        </div>
      </div>

      <div class="objects">
        <template v-if="!loadingRecords">
          <fieldset class="selected-facets" v-if="selectedFacets.length > 0 || creationYears[0] != 0 &&  creationYears[1] != 0 || acquisitionYears[0] != 0 &&  acquisitionYears[1] != 0">
            <legend hidden>Selected filters</legend>
            <template v-if="creationYears[0] != 0 &&  creationYears[1] != 0">
              <label class="facet">
                <input type="checkbox" name="creation_years" :value="creationYears[0]+ '-' + creationYears[1]" aria-label="creation years" v-on:click="filterByYear('creation_years', creationYears[0], creationYears[1])" checked/> 
                  Creation years: {{creationYears[0] + '-' + creationYears[1]}}
              </label>
            </template>
            <template v-if="acquisitionYears[0] != 0 &&  acquisitionYears[1] != 0">
              <label class="facet">
                <input type="checkbox" name="acquisition_years" :value="acquisitionYears[0]+ '-' + acquisitionYears[1]" aria-label="acquisition years" v-on:click="filterByYear('acquisition_years', acquisitionYears[0], acquisitionYears[1])" checked/> 
                  Acquisition years: {{acquisitionYears[0] + '-' + acquisitionYears[1]}}
              </label>
            </template>
            <template v-if="selectedFacets.length > 0">
              <label v-for="(selectedFacet, index) in selectedFacets" v-bind:key="index" class="facet">
                <input type="checkbox" v-bind:name="selectedFacet.category" :value="selectedFacet.key" v-bind:aria-label="selectedFacet.key" v-on:click="filter(selectedFacet.category, selectedFacet.key)" checked/> 
                  {{ selectedFacet.key }}
              </label>
            </template>
            <button class="clear-filters" v-on:click="clearFacets">Clear all filters</button>
          </fieldset>
          <ul class="list">
            <li :key="index" v-for="(item, index) in getArchivalRecords" class="list-item">
                <router-link :to="{name: 'rct-object', params: {reference: item.reference}}" v-bind:aria-label="'link to ' + item.unittitle">
                  <div class="object-thumbnail">
                    <img v-if="item.media[0].thumbnail_url != 'PLACEHOLDER'" :src="item.media[0].thumbnail_url" :alt="item.media[0].title"/>
                    <img v-else src="@/assets/images/sharc-imageplaceholder-light.jpg" height="1602" width="1644" alt="Image placeholder"/>
                  </div>

                  <div class="object-description">
                    <p class="details">
                      <span v-if="item.date_of_creation_range">{{item.date_of_creation_range}}</span>
                      <span class="delimiter">|</span>
                      <template v-if="item.category && item.category.length > 0">{{item.category}}</template>
                    </p>
                    <h4>
                      {{item.unittitle | truncate(100)}}
                    </h4>
                    <p class="details" v-if="item.creators">
                      <span v-bind:key="index" v-for="(creator, index) in item.creators.slice(0,sliceList)">
                        {{creator.name}}<template v-if="index != item.creators.length - 1">;&#160;</template>
                      </span><template v-if="item.creators.length > sliceList">...</template>
                    </p>
                  </div>
                </router-link>
                <div class="connected-to" v-if="item.related_entities && item.related_entities.length > 0">
                  <p class="details">Connected to: </p>
                  <p class="details" :key="index" v-for="(related, index) in item.related_entities.slice(0,sliceList)">
                    <a :href="$router.resolve({name: 'objects', query: {page: 1, work: [related.key]}}).href">{{related.key}}</a>
                    <span v-if="index != item.related_entities.length - 1">;&#160;</span>
                  </p>
                </div>
            </li>
          </ul>
          <div v-if="loadingMoreRecords" class="loader"></div>
          <template v-else>
            <button type="button" v-if="getArchivalRecords && getArchivalRecords.length < getTotalArchives" class="button-secondary" @click="moreRecords()">Show more objects</button>
          </template>
        </template>
        <div v-else class="loader"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import noUiSlider from 'nouislider';
import 'nouislider/distribute/nouislider.css';

export default {
  name: 'ArchiveList',
  computed: mapGetters(['getArchivalRecords', 'getTotalArchives', 'getArchivalFacets']),
  data: function() {
    return {
      loadingRecords: true,
      loadingMoreRecords: false,

      sortBy: '_score',
      sortDescVal: false,

      // creation year range filter
      // dynamic values
      minCreationRange: 0,
      maxCreationRange: 0,
      // static values onInit
      creationSlider: {
          startMin: 0,
          startMax: 0,
          min: 0,
          max: 0
      },

      // acqiusition year range filter
      // dynamic values
      minAcquisitionRange: 0,
      maxAcquisitionRange: 0,
      // static values onInit
      acquisitionSlider: {
          startMin: 0,
          startMax: 0,
          min: 0,
          max: 0
      },

      // instant search
      searchWorks: '',
      searchConnections: '',
      searchCategories: '',
      searchTexts: '',
      searchPerformances: '',
      searchSources: '',
      searchRelatedAcquirers: '',
      searchRelatedPeople: '',

      // see all buttons
      worksCheckbox: false,
      categoriesCheckbox: false,
      connectionsCheckbox: false,
      textsCheckbox: false,
      performancesCheckbox: false,
      sourcesCheckbox: false,
      relatedAcquirersCheckbox: false,
      relatedPeopleCheckbox: false,
      
      // params
      pageNum: 1,
      selectedFacets: [],
      creationYears: [0,0],
      acquisitionYears:[0,0],
      searchTerm: '',

      // TODO change to 3 once the data is structured properly
      sliceList: 3,
    }
  },
  methods: {

      // year range filters
      initCreationYearRange(min, max) {
      // init min and max year range dynamic toggles if they have not been updated based on the URL params
			if (this.minCreationRange == 0) {
				this.minCreationRange = min;
			} 
			if (this.maxCreationRange == 0){
				this.maxCreationRange = max;
			}
      
      // init static values
			this.creationSlider.startMin = this.minCreationRange;
			this.creationSlider.startMax = this.maxCreationRange;
			this.creationSlider.min = min;
      this.creationSlider.max = max;

      // init slider with static values
      noUiSlider.create(this.$refs.creationSlider, {
        start: [this.creationSlider.startMin, this.creationSlider.startMax],
        step: 1,
        range: {
          'min': this.creationSlider.min,
          'max': this.creationSlider.max
        }
      }); 
              
      this.$refs.creationSlider.noUiSlider.on('update',(values, handle) => {
        this[handle ? 'maxCreationRange' : 'minCreationRange'] = parseInt(values[handle]);
      });
    },
    initAcquisitionYearRange(min, max) {
      // init min and max year range dynamic toggles if they have not been updated based on the URL params
			if (this.minAcquisitionRange == 0) {
				this.minAcquisitionRange = min;
			} 
			if (this.maxAcquisitionRange == 0){
				this.maxAcquisitionRange = max;
			}

      // init static values
			this.acquisitionSlider.startMin = this.minAcquisitionRange;
			this.acquisitionSlider.startMax = this.maxAcquisitionRange;
			this.acquisitionSlider.min = min;
      this.acquisitionSlider.max = max;

      // init slider with static values
      noUiSlider.create(this.$refs.acquisitionSlider, {
        start: [this.acquisitionSlider.startMin, this.acquisitionSlider.startMax],
        step: 1,
        range: {
          'min': this.acquisitionSlider.min,
          'max': this.acquisitionSlider.max
        }
      }); 
              
      this.$refs.acquisitionSlider.noUiSlider.on('update',(values, handle) => {
        this[handle ? 'maxAcquisitionRange' : 'minAcquisitionRange'] = parseInt(values[handle]);
      });
    },
    updateCreationSlider(min, max) {
      this.$refs.creationSlider.noUiSlider.set([min, max]);
    },
    updateAcquisitionSlider(min, max) {
      this.$refs.acquisitionSlider.noUiSlider.set([min, max]);
    },

    // check options in the facets based on selected facets
    checkedOption(category, key) {
      return this.selectedFacets.filter(obj => obj.key.toLowerCase().replace(/[’’']/g, "")===key.toLowerCase().replace(/[’’']/g, "") && obj.category===category).length > 0;
    },

    // sort the list of options displayed in filters
    sortedData(list, query, sortingOrder) {
      query = query.toLowerCase();
			var sortedList = list.slice().filter(function (item) {
				var name = item.key.toLowerCase();
				return name.match(query);
			})
			if (sortingOrder == 'alphabetical')  {
				sortedList.sort((a, b) => a.key.localeCompare(b.key));
			} else if (sortingOrder == 'count') {
				sortedList.sort((a, b) => b.doc_count - a.doc_count);
			} 
			return sortedList;
    },

    async filterByYear(facet, min_year, max_year) {
      this.loadingRecords = true;

      const setQuery = this.$route.query;
      this.pageNum = 1;
      setQuery['page'] = this.pageNum;
      const yearString = min_year + '-' + max_year;
      
      if (setQuery[facet] && setQuery[facet] == yearString) {
        // change values to default
        if (facet == 'creation_years') {
          this.creationYears = [0,0];
          this.minCreationRange = this.creationSlider.min;
          this.maxCreationRange = this.creationSlider.max;
          this.updateCreationSlider(this.creationSlider.min, this.creationSlider.max);
        }
        if (facet == 'acquisition_years') {
          this.acquisitionYears = [0,0];
          this.minAcquisitionRange = this.acquisitionSlider.min;
          this.maxAcquisitionRange = this.acquisitionSlider.max;
          this.updateAcquisitionSlider(this.acquisitionSlider.min, this.acquisitionSlider.max);
        }
        delete setQuery[facet];
      } else {
        // set new values
        if (facet == 'creation_years') {
          // set facet values
          this.creationYears[0] = min_year;
          this.creationYears[1] = max_year;

          // set dynamic values on the frontend
          this.minCreationRange = min_year;
          this.maxCreationRange = max_year;
        } else {
          // set facet values
          this.acquisitionYears[0] = min_year;
          this.acquisitionYears[1] = max_year;
          
          // set dynamic values on the frontend
          this.minAcquisitionRange = min_year;
          this.maxAcquisitionRange = max_year;
        }
        setQuery[facet] = min_year + '-' + max_year;
      }

      this.$router.replace({ query: {} });
			this.$router.push({query: setQuery});
      await this.fetchArchivalRecords({'searchTerm': this.searchTerm, 
                                        'pages': this.pageNum, 
                                        'creation_years': JSON.parse(JSON.stringify(this.creationYears)), 
                                        'acquisition_years': JSON.parse(JSON.stringify(this.acquisitionYears)), 
                                        'selectedFacets': JSON.parse(JSON.stringify(this.selectedFacets)),  
                                        'sort': {'sort_by': this.sortBy, 'desc': this.sortDescVal}
                                      });
      this.loadingRecords = false;
    },
    /**
     * Toggle the sort direction
     * @returns {Promise<void>}
     */
    async sortAscDesc() {
      this.getSortedRecords(true);
    },
    /**
     * Change the field we're sorting by
     * (but not direction)
     * @returns {Promise<void>}
     */
    async changeSortBy() {
      this.getSortedRecords(false);
    },
    async getSortedRecords(toggleAscdesc) {
      this.loadingRecords = true;

      const setQuery = this.$route.query;
      setQuery['sort_by'] = this.sortBy;
      // true = Z-A/9-0, false = A-Z/0-9

      if (toggleAscdesc) {
        this.sortDescVal = !this.sortDescVal;
      }
      setQuery['desc'] = this.sortDescVal;

      this.$router.replace({ query: {} });
      this.$router.push({query: setQuery});
      await this.fetchArchivalRecords({'searchTerm': this.searchTerm, 
                                        'pages': this.pageNum, 
                                        'creation_years': JSON.parse(JSON.stringify(this.creationYears)), 
                                        'acquisition_years': JSON.parse(JSON.stringify(this.acquisitionYears)), 
                                        'selectedFacets': JSON.parse(JSON.stringify(this.selectedFacets)), 
                                        'sort': {'sort_by': this.sortBy, 'desc': this.sortDescVal}
                                      });
      this.loadingRecords = false;
    },
    async searchRecords() {
      this.loadingRecords = true;

      //this.selectedFacets = [];
      //this.creationYears = [0,0];
      //this.acquisitionYears = [0,0];
      this.pageNum = 1;

      this.$router.replace({ query: {} });
      if(this.searchTerm != '') {
        this.$router.push({query: {page: this.pageNum, q: this.searchTerm}});
      } else {
        this.$router.push({query: {page: this.pageNum}});
      }

      await this.fetchArchivalRecords({'searchTerm': this.searchTerm, 
                                      'pages': this.pageNum, 
                                      'creation_years': JSON.parse(JSON.stringify(this.creationYears)), 
                                      'acquisition_years': JSON.parse(JSON.stringify(this.acquisitionYears)), 
                                      'selectedFacets': JSON.parse(JSON.stringify(this.selectedFacets)),  
                                      'sort': {'sort_by': this.sortBy, 'desc': this.sortDescVal}
                                      });

      this.loadingRecords = false;
    },
		async filter(facet, option) {
      this.loadingRecords = true;

      const setQuery = this.$route.query;
      this.pageNum = 1;
      setQuery['page'] = this.pageNum;

			if (this.selectedFacets.filter(obj => obj.key===option && obj.category===facet).length > 0) {
        this.selectedFacets = this.selectedFacets.filter(object => !(object.category === facet && object.key === option));
        if (!Array.isArray(setQuery[facet])) {
          delete setQuery[facet];
        }
				else {
          setQuery[facet].splice(setQuery[facet].indexOf(option),1);
        }
			} else {
				this.selectedFacets.push({'category': facet, 'key': option});
				if (setQuery[facet])  {
					if (!Array.isArray(setQuery[facet])) {
						setQuery[facet] = [setQuery[facet]];
					}
					setQuery[facet].push(option);
				} 
				else {
					setQuery[facet] = [option];
				}
			}

			this.$router.replace({ query: {} });
			this.$router.push({query: setQuery});

      await this.fetchArchivalRecords({'searchTerm': this.searchTerm, 
                                        'pages': this.pageNum, 
                                        'creation_years': JSON.parse(JSON.stringify(this.creationYears)), 
                                        'acquisition_years': JSON.parse(JSON.stringify(this.acquisitionYears)), 
                                        'selectedFacets': JSON.parse(JSON.stringify(this.selectedFacets)), 
                                        'sort': {'sort_by': this.sortBy, 'desc': this.sortDescVal}
                                      });	
      this.loadingRecords = false;
    },
    async clearSearch(){
      this.searchTerm = '';

      await this.fetchArchivalRecords({'searchTerm': this.searchTerm,
                                        'pages': this.pageNum,
                                        'creation_years': JSON.parse(JSON.stringify(this.creationYears)),
                                        'acquisition_years': JSON.parse(JSON.stringify(this.acquisitionYears)),
                                        'selectedFacets': JSON.parse(JSON.stringify(this.selectedFacets)),
                                        'sort': {'sort_by': this.sortBy, 'desc': this.sortDescVal}
                                      });
      this.loadingRecords = false;

    },


    async clearFacets() {
      this.loadingRecords = true;

      this.pageNum = 1;
      this.selectedFacets = [];
      this.creationYears = [0,0];
      this.acquisitionYears = [0,0];

      // change dynamic toggles to static values and update year range sliders
      this.minCreationRange = this.creationSlider.min;
      this.maxCreationRange = this.creationSlider.max;
      this.minAcquisitionRange = this.acquisitionSlider.min;
      this.maxAcquisitionRange = this.acquisitionSlider.max;
      this.updateCreationSlider(this.creationSlider.min, this.creationSlider.max);
      this.updateAcquisitionSlider(this.acquisitionSlider.min, this.acquisitionSlider.max);
      this.searchRelatedPeople = '';

      this.$router.replace({ query: {} });
      await this.fetchArchivalRecords({'searchTerm': this.searchTerm, 
                                        'pages': this.pageNum, 
                                        'creation_years': JSON.parse(JSON.stringify(this.creationYears)), 
                                        'acquisition_years': JSON.parse(JSON.stringify(this.acquisitionYears)),  
                                        'selectedFacets': JSON.parse(JSON.stringify(this.selectedFacets)),
                                        'sort': {'sort_by': this.sortBy, 'desc': this.sortDescVal}
                                      });
      this.loadingRecords = false;
    },
    async getPeople(){
      let personFacet = await this.fetchPeople(this.searchRelatedPeople);
      if (this.getArchivalFacets && personFacet){
        this.getArchivalFacets.people = personFacet;
      }
    },
    async filterPeople(){
      if (this.timer) {
        clearTimeout(this.timer);
        this.timer = null;
      }
      this.timer = setTimeout(this.getPeople, 800);
    },
		async moreRecords() {
      this.loadingMoreRecords = true;

			this.pageNum = Number(this.pageNum) + 1;

			const setQuery = this.$route.query;
			setQuery['page'] = Number(this.pageNum);
			this.$router.replace({ query: {} });
			this.$router.push({query: setQuery});

      // ?: change to await this.fetchArchivalRecords(...);	
			await this.loadMoreArchivalRecords();

			this.loadingMoreRecords = false;
    },

    toggleFilters() {
      const filters = document.querySelector('.filters');
      filters.classList.toggle('active');
    },
    ...mapActions(['fetchArchivalRecords', 'fetchPeople', 'searchArchivalRecords', 'loadMoreArchivalRecords'])
  },
  filters: {
    capitalize: function (value) {
      if (!value) {
        return '';
      }
      value = value.toString();
      return value.charAt(0).toUpperCase() + value.slice(1);
    }
  },
  async created() {
    const setQuery = this.$route.query;

    for (var key in setQuery) {
      switch (key){
        case 'q':
          this.searchTerm = setQuery[key];
          break;
        case 'sort_by':
          this.sortBy = setQuery[key];
          break;
        case 'desc':
          this.sortDescVal = setQuery[key];
          break;
        case 'page':
          this.pageNum = Number(setQuery[key]);
          break;
        case 'creation_years':
          // init selected filters
          this.creationYears[0] = Number(setQuery[key].split('-')[0]);
          this.creationYears[1] = Number(setQuery[key].split('-')[1]);

          // init dynamic year range values
          this.minCreationRange = Number(setQuery[key].split('-')[0]);
          this.maxCreationRange = Number(setQuery[key].split('-')[1]);
          break;
        case 'acquisition_years':
          // init selected filters
          this.acquisitionYears[0] = Number(setQuery[key].split('-')[0]);
          this.acquisitionYears[1] = Number(setQuery[key].split('-')[1]);

          // init dynamic year range values
          this.minAcquisitionRange = Number(setQuery[key].split('-')[0]);
          this.maxAcquisitionRange = Number(setQuery[key].split('-')[1]);
          break;
        default:
          if (Array.isArray(setQuery[key])) {
            for (var i in setQuery[key]) {
              this.selectedFacets.push({'category': key, 'key': setQuery[key][i]});
            }
          } else {
              this.selectedFacets.push({'category': key, 'key': setQuery[key]});
          }
      }
    }
    
    // check router params
    await this.fetchArchivalRecords({'searchTerm': this.searchTerm, 
                                      'pages': this.pageNum, 
                                      'creation_years': JSON.parse(JSON.stringify(this.creationYears)), 
                                      'acquisition_years': JSON.parse(JSON.stringify(this.acquisitionYears)),  
                                      'selectedFacets': JSON.parse(JSON.stringify(this.selectedFacets)), 
                                      'sort': {'sort_by': this.sortBy, 'desc': this.sortDescVal}
                                    });
    

    // set up the year range filter if creation years is sent in response
		if (this.getArchivalFacets.creation_years && this.getArchivalFacets.creation_years[0] > 0 && this.getArchivalFacets.creation_years[1] > 0) {
      this.initCreationYearRange(this.getArchivalFacets.creation_years[0], this.getArchivalFacets.creation_years[1]);
    }
    if (this.getArchivalFacets.acquisition_years && this.getArchivalFacets.acquisition_years[0]> 0 && this.getArchivalFacets.acquisition_years[1] > 0) {
      this.initAcquisitionYearRange(this.getArchivalFacets.acquisition_years[0], this.getArchivalFacets.acquisition_years[1]);
    }

    this.loadingRecords = false;
  }
}
</script>
