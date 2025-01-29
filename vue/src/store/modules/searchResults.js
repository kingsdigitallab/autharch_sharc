import Api from '../../services/Api';

const state = {
    results: [],
    resultsTotal: 0,
    loadMoreResultsUrl: ''
};

const getters = {
    getSearchResults: (state) => state.results,
    getSearchResultsTotal: (state) => state.resultsTotal
};

const actions = {
    async fetchSearchResults({ commit }, params) {
        // params:
        // {
        //     pages: 1,
        //     searchTerm: ''
        // }
        // information pages are Bibliography, Glossary, Acknowledgements and Events in Wagtail (all information pages use the same Rich text page template).
        
        // PKs on the information pages are Wagtail page id's, PKs on the object pages are rcins/references, 
        // PKs for groups should be coming from autharch, but we have not added groups there yet.
        const response = await Api.get('/search', params);

        //console.log(response);

        // const response = {
        //     data: {
        //         total: 10,
        //         results: [
        //             // pages from autharch
        //             {
        //                 pk: 0,
        //                 page: 'object',
        //                 title: 'Object title',
        //                 snippet: 'object snippet'
        //             },
        //             // I was trying to set up friendlier URLs here, e.g., /groups/the-entry-of-bolingbroke, and not /groups/1,
        //             // that is why the The Entry of Bolingbroke below has url_slug and all other pages don't.
        //             // I am fine with any alternative solution that could help achieve /groups/the-entry-of-bolingbroke
        //             {
        //                 pk: 1,
        //                 page: 'group',
        //                 url_slug: 'the-entry-of-bolingbroke',
        //                 title: 'The Entry of Bolingbroke',
        //                 snippet: 'group page snippet'
        //             },
        //             // wagtail pages
        //             {
        //                 pk: 11,
        //                 page: 'glossary',
        //                 title: 'Glossary',
        //                 snippet: 'glossary page snippet'
        //             },
        //             {
        //                 pk: 10,
        //                 page: 'bibliography',
        //                 title: 'Bibliography',
        //                 snippet: 'bibliography page snippet'
        //             },
        //             // Show only if events has show_in_menus checked in Wagtail
        //             {
        //                 pk: 12,
        //                 page: 'events',
        //                 title: 'Events',
        //                 snippet: 'events page snippet'
        //             },
        //             {
        //                 pk: 9,
        //                 page: 'acknowledgements',
        //                 title: 'Acknowledgements',
        //                 snippet: 'acknowledgements page snippet'
        //             },
        //             {
        //                 pk: 5,
        //                 page: 'resources',
        //                 title: 'Resources',
        //                 snippet: 'resources'
        //             },
        //             {
        //                 pk: 6,
        //                 page: 'about',
        //                 title: 'About',
        //                 snippet: 'about page snippet'
        //             }
        //         ]
        //     }
        // };
        commit('setSearchResults', response.data.results);
        commit('setSearchResultsTotal', response.data.count);
        if (response.data.next) {

            commit('setloadMoreResultsUrl', response.data.next);
            // if (response.data.next.includes('localhost')) {
            //     commit('setloadMoreResultsUrl', response.data.next);
            // } else{
            //     commit('setloadMoreResultsUrl', response.data.next.replace('http:', 'https:'));
            // }

        }else{
            commit('setloadMoreResultsUrl', '');
        }
    },
    // TODO add load more records
    async loadMoreSearchResults({commit}) {
        // await Api.getUrl(state.loadMoreResultsUrl)
        const response = await Api.getUrl(state.loadMoreResultsUrl);

        if (response.data.next) {
            commit('setloadMoreResultsUrl', response.data.next);
            // if (response.data.next.includes('localhost')) {
            //     commit('setloadMoreResultsUrl', response.data.next);
            // } else{
            //     commit('setloadMoreResultsUrl', response.data.next.replace('http:', 'https:'));
            // }

        }else{
            commit('setloadMoreResultsUrl', '');
        }



        commit('setMoreSearchResults', response.data.results);
    }
};

const mutations = {
    setSearchResults: (state, results) => (state.results = results),
    setSearchResultsTotal: (state, resultsTotal) => (state.resultsTotal = resultsTotal),
    setloadMoreResultsUrl: (state, nextUrl) => (state.loadMoreResultsUrl = nextUrl),
    setMoreSearchResults: (state, moreSearchResults) => moreSearchResults.forEach(element => state.results.push(element))
};

export default {
    state,
    getters,
    actions,
    mutations
}
