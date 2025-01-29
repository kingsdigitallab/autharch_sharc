import Api from '../../services/Api';

const state = {
    page: {},
    resources: {},
    eventPage_status: false,
    status: false,
    imageUrl: {}
};

const getters = {
    getResources: (state) => state.resources,
    getPage: (state) => state.page,
    getEventsPageStatus: (state) => state.eventPage_status,
    getPageStatus: (state) => state.status,
    getImageURL: (state) => state.imageUrl,
};

const wagtailPageIds = {
    'accessibility': process.env.VUE_APP_WAGTAIL_ACCESSIBILITY_SLUG,
    'events': process.env.VUE_APP_WAGTAIL_EVENTS_SLUG,
    'glossary': process.env.VUE_APP_WAGTAIL_GLOSSARY_SLUG,
    'bibliography': process.env.VUE_APP_WAGTAIL_BIBLIOGRAPHY_SLUG,
    'acknowledgements': process.env.VUE_APP_WAGTAIL_ACKNOWLEDGEMENTS_SLUG,
    'resources': process.env.VUE_APP_WAGTAIL_RESOURCES_SLUG,
    'about': process.env.VUE_APP_WAGTAIL_ABOUT_SLUG,
    'exhibition': process.env.VUE_APP_WAGTAIL_EXHIBITION_SLUG
};

const WAGTAIL_PAGE_API_URL='wagtail/pages/';

const actions = {
    async fetchSecondaryPage({ commit }, page_name) {
        // todo Refactor this once we have clarity on secondary page templates
        // 'editor.RichTextPage'
        const response = await Api.getWagtailPage(WAGTAIL_PAGE_API_URL, wagtailPageIds[page_name], 'editor.StreamFieldPage', 'title,body');
        let image = {};

        if (response.data) {
            if (response.data.image) {
                image = {
                    resource: response.data.meta.parent.meta.html_url + response.data.image.meta.download_url,
                    alt: response.data.image.title
                }
                commit('setImageURL', image);
            }
            if (response.data.items) {
                commit('setPage', response.data.items[0]);
            }
        }


    },
    async fetchResources({ commit }) {
        const response = await Api.getWagtailPage(WAGTAIL_PAGE_API_URL,wagtailPageIds['resources'], 'editor.StreamFieldPage', 'title,body');
        if (response && response.data && response.data.items) {
            commit('setResources', response.data.items[0].body);
        }
    },
    // async fetchStreamFieldPage({commit}, slug) {
    //     const response = await Api.getWagtailPage(WAGTAIL_PAGE_API_URL,wagtailPageIds[slug], 'editor.StreamFieldPage', 'title,body');
    //     return response;
    // },
    //async fetchCustomWagtailPage({ commit }, id) {
        
        // 1. We need to create a Wagtail template based on the Resources page https://sharc-autharch-stg.kdl.kcl.ac.uk/resources 
        // the ShaRC team needs to be able to upload images, pdf files (required on the Resources page)
        // and embed iframe videos, e.g., from YouTube (required on the Resources page)
        // MAO has a similar template where videos are embedded
        // https://maoeraobjects.ac.uk/sources/video-demonstrating-use-chinese-typewriter/
        // if you need some details on how to add this functionality, please ask Jamie.
        // 2. We need to add two pages to ShaRC's Wagtail - Resources and About
        // 3. We need to update AboutPage.vue and ResourcesPage.vue to get the data from Wagtail.

    //},

    // EH: Fetch now working.
    // fetchEventsPageStatus has to be set separately from fetchPageStatus, 
    // otherwise, on the Resources page fetchPageStatus is called twice (for the Events and for the Glossary page) and it is not clear 
    // whether getPageStatus is set for the Events page or for the Glossary page  
    // if there is a more elegant solution, I am happy to update the Vue templates.
    async fetchEventsPageStatus({ commit }) {

        const response = await Api.getWagtailPage(WAGTAIL_PAGE_API_URL,
            wagtailPageIds.events,'editor.StreamFieldPage','show_in_menus');
        if(response.data.items && response.data.items.length > 0 &&
            response.data.items[0].meta && response.data.items[0].meta.show_in_menus) {
            const status = response.data.items[0].meta.show_in_menus;
            commit('setEventsPageStatus', status);
        }
    },
    async fetchPageStatus({ commit }, page_name) {
        // const response = await Api.getSingle('/wagtail/pages/',id);
        const response = await Api.getWagtailRichTextPage(WAGTAIL_PAGE_API_URL,
            wagtailPageIds[page_name]);
        if(response.data.items && response.data.items.length > 0 &&
            response.data.items[0].meta && response.data.items[0].meta.show_in_menus) {
            const status = response.data.items[0].meta.show_in_menus;
            commit('setPageStatus', status);
        }
    }
};

const mutations = {
    setResources: (state, resources) => (state.resources = resources),
    setPage: (state, page) => (state.page = page),
    setEventsPageStatus: (state, eventPage_status) => (state.eventPage_status = eventPage_status),
    setPageStatus: (state, status) => (state.status = status),
    setImageURL: (state, imageUrl) => (state.imageUrl = imageUrl),
};

export default {
    state,
    getters,
    actions,
    mutations
}
