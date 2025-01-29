import Api from '../../services/Api';

const state = {
    menuItems: [],
    banners: [],
    plays: [],
    themes: [],
    tags: [],
    title: '',
    description: '',
    timelineData: {}
};

const getters = {
    getMenuItems: (state) => state.menuItems,
    mainBanners: (state) => state.banners,
    playsList: (state) => state.plays,
    themesList: (state) => state.themes,
    featuredTags: (state) => state.tags,
    title: (state) => state.title,
    briefDescription: (state) => state.description,
    timelineData: (state) => state.timelineData
};

const actions = {
    async fetchTimelineData({commit}) {
        const response = await Api.get('events/', {});
        commit('setTimelineData', response.data);
    },
    async fetchMenuItems({commit}) {
        const response = await Api.getWagtailMenuPages('wagtail/pages/');
        if (response.data.items && response.data.items.length > 0) {

             commit('setMenuItems', response.data.items[0].menu_children);
        }
    },
    async fetchBanners({commit}) {
        // low priority TODO
        // get the banners from Wagtail or from editor?
        const response = {
            data: {
                banners: [
                    {
                        id: 573,
                        resource: require("@/assets/images/Slide1.jpg"),
                        title: "The Entry of Bolingbroke",
                        creators: ['Princess Victoria (1840-1901)']
                    },
                    {
                        id: 593,
                        resource: require("@/assets/images/Slide2.png"),
                        title: "A performance of Macbeth in the Rubens Room, Windsor Catle, 4 February 1853",
                        creators: ['Louis Haghe (1806-85)']
                    },
                    {
                        id: 559,
                        resource: require("@/assets/images/Slide3.jpg"),
                        title: "George IV in 'Prince Florizel' costume",
                        creators: ['Richard Cosway (bapt. 1742, d. 1821)']
                    },
                    {
                        id: 604,
                        resource: require("@/assets/images/Slide4.jpg"),
                        title: "Mr William Shakespeare's comedies, histories & tragedies. Published according to the true original copies.",
                        creators: ['William Shakespeare (1564-1616)', 'Isaac Jaggard (d. 1627)', 'Edward Blount (1562-1632)']
                    },
                    {
                        id: 558,
                        resource: require("@/assets/images/Slide5.png"),
                        title: "Ophelia",
                        creators: ['Photograph attributed to Princess Louise (1848-1939)']
                    },
                ],
            }
        };
        commit('setBanners', response.data.banners);
    },
    async fetchDescription({commit}) {
        const response = await Api.getWagtailRichTextPage('wagtail/pages/',
            process.env.VUE_APP_WAGTAIL_HOME_SLUG);
        if (response.data.items && response.data.items[0].body.length > 0) {
            commit('setTitle', response.data.items[0].title);
            commit('setDescription', response.data.items[0].body);
        }
    },
    async fetchPlays({commit}) {
        const response = await Api.get('documents/', {'size': 0});
        let plays = [
            {
                id: 0,
                resource: require("@/assets/images/PlayKingLear.jpg"),
                title: "King Lear",
                count: 0
            },
            {
                id: 1,
                resource: require("@/assets/images/PlayHamlet.jpg"),
                title: "Hamlet",
                count: 0
            },
            {
                id: 2,
                resource: require("@/assets/images/PlayTheWintersTale.jpg"),
                title: "The Winter's Tale",
                count: 0
            },
            {
                id: 3,
                resource: require("@/assets/images/PlayMerryWivesOfWindsor.jpg"),
                title: "The Merry Wives of Windsor",
                count: 0
            },
            {
                id: 4,
                resource: require("@/assets/images/PlayHenryVIII.jpg"),
                title: "Henry VIII",
                count: 0
            },
            {
                id: 5,
                resource: require("@/assets/images/PlayHenryV.jpg"),
                title: "Henry V",
                count: 0
            },
            {
                id: 6,
                resource: require("@/assets/images/PlayMacbeth.jpg"),
                title: "Macbeth",
                count: 0
            },
            {
                id: 7,
                resource: require("@/assets/images/PlayRichardIII.jpg"),
                title: "Richard III",
                count: 0
            },
            {
                id: 8,
                resource: require("@/assets/images/PlayRomeoAndJuliet.jpg"),
                title: "Romeo and Juliet",
                count: 0
            },
            {
                id: 9,
                resource: require("@/assets/images/PlayMerchantOfVenice.jpg"),
                title: "Merchant of Venice",
                count: 0
            },
            {
                id: 10,
                resource: require("@/assets/images/PlayMidsummerNightsDream.jpg"),
                title: "A Midsummer Night's Dream",
                count: 0
            },
            {
                id: 11,
                resource: require("@/assets/images/PlayRichardII.jpg"),
                title: "Richard II",
                count: 0
            },
        ];
        // Replace numbers in plays with correct counts
        if (response) {
            let works_facet = response.data.facets._filter_work.work.buckets;
            for (let work in works_facet) {
                for (let play in plays) {
                    if (plays[play].title === works_facet[work].key) {
                        plays[play].count += works_facet[work].doc_count;
                    }
                }
            }
        }
        commit('setPlays', plays);
    },
    async fetchThemes({commit}) {
        // TODO
        const response = await Api.get('themes/', {'facet': 'themes'});
        if (response && response.data.themes) {
            commit('setThemes', response.data.themes);
        }

    },
    async fetchTags({commit}) {
        const response = {
            data: {
                featuredTags: ["Print", "Book", "Photograph", "Painting", "Drawing"]
            }
        };
        commit('setFeaturedTags', response.data.featuredTags);
    }
};

const mutations = {
    setMenuItems: (state, menuItems) => (state.menuItems = menuItems),
    setBanners: (state, banners) => (state.banners = banners),
    setPlays: (state, plays) => (state.plays = plays),
    setThemes: (state, themes) => (state.themes = themes),
    setFeaturedTags: (state, tags) => (state.tags = tags),
    setTitle: (state, title) => (state.title = title),
    setDescription: (state, description) => (state.description = description),
    setTimelineData: (state, timelineData) => (state.timelineData = timelineData)
};

export default {
    state,
    getters,
    actions,
    mutations
}
