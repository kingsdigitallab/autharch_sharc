import Vuex from 'vuex';
import Vue from 'vue';
import VuePluralize from 'vue-pluralize';
import secondaryPage from './modules/secondary_page';
import archivalRecords from './modules/archivalRecords';
import archiveSingle from './modules/archiveSingle';
import home from './modules/home';
import objectStories from './modules/objectStories';
import searchResults from './modules/searchResults';


Vue.use(Vuex);
Vue.use(VuePluralize);

export default new Vuex.Store({
    modules: {
        home,
        secondaryPage,
        archivalRecords,
        archiveSingle,
        searchResults,
        objectStories,
        VuePluralize
    }
})