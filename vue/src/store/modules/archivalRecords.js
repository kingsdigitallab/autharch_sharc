import Api from '../../services/Api';

const state = {
    description: '',
    archivalRecords: [],
    facets: [],
    loadMoreUrl: '',
    total: 0
};

const getters = {
    pageDescription: (state) => state.description,
    getArchivalRecords: (state) => state.archivalRecords,
    getTotalArchives: (state) => state.total,
    getArchivalFacets: (state) => state.facets
};

const actions = {
    async fetchObjectsPageDescription({ commit }) {
        const response = await Api.getWagtailRichTextPage('wagtail/pages/',
            process.env.VUE_APP_WAGTAIL_OBJECTS_SLUG);
        if (response.data.items && response.data.items[0].body.length > 0) {
            commit('setPageDescription', response.data.items[0].body);
        }
    },
    async fetchPeople({ commit }, query) {
        //const response = await Api.get('documents/suggest/', params);
        const response = await Api.getSingle('documents/','?person_autocomplete='+query);
        if (commit && response && response.data.facets){
            if (response.data.facets._filter_people){
                //Update facets
                return response.data.facets._filter_people.people.buckets;
                //facets.people = response.data.facets._filter_people.people.buckets;
            }
        }
    },
    async fetchArchivalRecords({ commit }, params) {
        /*
        params include page number, selected filters and selected sorting option
        {
            searchTerm: '',
            pages: 1,
            selectedFacets: [
                {category: "shakespeare_connection", display_name: "Individual"},
                {category: "shakespeare_connection", display_name: "Works"},
                {category: "play", display_name: "Henry V"},
                {category: "play", display_name: "Richard III"},
                {category: "relation_to_objects", display_name: "Portrait"},
                {category: "relation_to_objects", display_name: "Performance"}
            ],
            // Put years here rather than in facets
            // I will transform them later in getParams
            acquisition_years:[1700, 2020],
            creation_years:[1700,2020],
            sort: {
                desc: false,
                sort_by: "name"
            }
        }

        NB: If needed, I can also change the structure of the selectedFacets to, for example, {category: "play", selected_options: ["Henry V", "Richard III"]}.

        */

        // extract records = 12 * pages Done
        // TODO: filter records by selectedFacets
        // TODO: sort by the selected sorting option; if sort_by is empty or 'default', display records as they appear in the database
        //Swap response below for raw json to test without api
        const response = await Api.get('documents/', params);

        // Transform API response into something friendlier to the Vue

        let returned_facets = {};
        if (response && response.data.facets){
            if (response.data.facets._filter_acquirer){
                returned_facets.acquirer = response.data.facets._filter_acquirer.acquirer.buckets;
            }
            if (response.data.facets._filter_people){
                returned_facets.people = response.data.facets._filter_people.people.buckets;
            }
            if (response.data.facets._filter_category){
                returned_facets.category = response.data.facets._filter_category.category.buckets;
            }
            if (response.data.facets._filter_individual_connections){
                returned_facets.individual_connections = response.data.facets._filter_individual_connections.individual_connections.buckets;
            }

            if (response.data.facets._filter_performance){
                returned_facets.performances = response.data.facets._filter_performance.performance.buckets;
            }
            if (response.data.facets._filter_source){
                returned_facets.sources = response.data.facets._filter_source.source.buckets;
            }
            if (response.data.facets._filter_text){
                returned_facets.texts = response.data.facets._filter_text.text.buckets;
            }
            if (response.data.facets._filter_work){
                returned_facets.works = response.data.facets._filter_work.work.buckets;
            }
        }
        // todo Add these from response when aggregation complete
        returned_facets.acquisition_years = [1600, 2020];
        returned_facets.creation_years = [1600,2020];
        if (response.data.next) {
            commit('setLoadMoreUrl', Api.stripUrl(response.data.next));
        }else{
            commit('setLoadMoreUrl', '');
        }
        commit('setArchivalRecords', response.data.results);
        commit('setTotal', response.data.count);
        commit('setFacets', returned_facets);
    },
    async loadMoreArchivalRecords({ commit }) {
        const response = await Api.getUrl(state.loadMoreUrl);
        if (response.data.next) {
            commit('setLoadMoreUrl', Api.stripUrl(response.data.next));
        }else{
            commit('setLoadMoreUrl', '');
        }
        commit('setMoreArchivalRecords', response.data.results);
    }
};

const mutations = {
    setArchivalRecords: (state, archivalRecords) => (state.archivalRecords = archivalRecords),
    setPageDescription: (state, description) => (state.description = description),
    setLoadMoreUrl: (state, nextUrl) => (state.loadMoreUrl = nextUrl),
    setTotal: (state, count) => (state.total = count),
    setFacets: (state, facets) => (state.facets = facets),
    setMoreArchivalRecords: (state, moreArchivalRecords) => moreArchivalRecords.forEach(element => state.archivalRecords.push(element))
};

export default {
    state,
    getters,
    actions,
    mutations
}
