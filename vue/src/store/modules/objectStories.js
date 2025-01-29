import Api from '../../services/Api';

const state = {
    storyList: [],
    story: {},
    storyStrap:""
};

const getters = {
    getStoryList: (state) => state.storyList,
    getThemeList: (state) => state.storyList,
    getStory: (state) => state.story,
    getStoryStrap: (state) => state.storyStrap
};

const actions = {
    async fetchThemeList({commit}) {
        /*
        Again a copy in case grouping or other refactoring is done to stories
         */
        let storyList = [];
        const response = await Api.get('wagtail/pages/?type=editor.ThemeObjectCollection&fields=title,body,related_documents');
        if (response.data.items) {
            for (let item_index in response.data.items) {
                let story = response.data.items[item_index];


                storyList.push(
                    {
                        id: story.id,
                        url_slug: story.meta.slug,
                        title: story.title,
                        body: story.body,
                        related_documents: story.related_documents,
                    }
                );
            }
        }
        commit('setStoryList', storyList);
    },
    async fetchStoryList({commit}) {
        let storyList = [];
        const response = await Api.get('wagtail/pages/?type=editor.StoryObjectCollection&fields=title,body,related_documents');
        if (response.data.items) {
            for (let item_index in response.data.items) {
                let story = response.data.items[item_index];

                storyList.push(
                    {
                        id: story.id,
                        url_slug: story.meta.slug,
                        title: story.title,
                        body: story.body,
                        related_documents: story.related_documents,
                    }
                );
            }
        }
        /*const response = {
            data: {
                storyList: [
                    {
                        id: 0,
                        url_slug: 'richard-ii-in-1857',
                        title: 'Richard II in 1857'
                    },
                    {
                        id: 1,
                        url_slug: 'the-entry-of-bolingbroke',
                        title: 'The Entry of Bolingbroke'
                    },
                    {
                        id: 2,
                        url_slug: 'john-bells-shakespeare',
                        title: 'John Bell’s Shakespeare'
                    },
                    {
                        id: 3,
                        url_slug: 'hernes-oak',
                        title: 'Herne’s Oak'
                    }
                ]
            }
        };*/

        commit('setStoryList', storyList);
    },
    async fetchTheme({commit}, slug) {
        /*
        Nearly identical to story except for page type
        I've kept them separate in case the models diverge at a later date
        e.g. Groups for stories
         */
        const response = await Api.getWagtailPage('wagtail/pages/', slug, "editor.ThemeObjectCollection", "title,body,related_documents");
        if (response.data.items) {
            commit('setStory', response.data.items[0]);
        }
    },
    async fetchStoryStrap({commit}) {
        const slug='stories';
        const response = await Api.getWagtailPage('wagtail/pages/', slug, "editor.StreamFieldPage", "title,body");
        if (response.data.items) {

            if (response.data.items[0].body[0]){
                commit('setStoryStrap', response.data.items[0].body[0].value);
            }

        }
    },
    async fetchStory({commit}, slug) {
        const response = await Api.getWagtailPage('wagtail/pages/', slug, "editor.StoryObjectCollection", "title,body,related_documents");
        if (response.data.items) {
            commit('setStory', response.data.items[0]);
        }

        // getWagtailPage
       /* const response = {
            data: {
                story: {
                    title: 'Richard II in 1857',
                    description: `<h3>Introduction</h3>
                        <p>Charles Kean, initially alongside his business partner Robert Keeley, took on the management of the Princess’s Theatre in 1849. Keeley and his wife retired in 1852, but Kean’s management lasted for the rest of the decade. He became well known for grand-scale and ambitious revivals of Shakespeare’s plays, as well as for contemporary melodramas such as Dion Boucicault’s The Corsican Brothers and The Colleen Bawn.</p>
                        <h3>Section 1</h3>
                        <p>Kean devoted himself to historical accuracy in his Shakespeare productions, studying illuminated manuscripts, chronicles, and tomb effigies to inform his staging, and giving detailed instructions to his scene designer Thomas Grieve. In Richard II (1857) this project reached its most successful iteration. Grieve produced scenery precisely calculated to represent the play’s various English settings as they would have appeared during Richard II’s lifetime. The most celebrated moment in the production was the interpolated ‘Historical Episode’ between Acts 3 and 4, based on York’s speech from Act 5 and depicting the re-entry of Richard and Bolingbroke to London.</p>
                        <h3>Section 2</h3>
                        <p>From 1848, Kean had also been the director of the annual ‘Windsor Theatricals’: private performances by a professional cast given at Windsor Castle over the winter period annually from 1848-61. The programme for these performances combined Kean’s Shakespearean repertoire and melodramas with some eighteenth-century comedy and a selection of contemporary farces, usually starring one of the era’s most famous comic actors: the Keeleys, James Baldwin Buckstone, John Pritt Harley and Charles Mathews.</p> 
                        <p>Richard II had its first performance at Windsor in February 1857, in the grand stateroom called ‘St George’s Hall,’ which Kean and Grieve had also selected as the setting for the play’s final scene, in which Richard’s body is presented to the newly crowned Henry IV. After an enthusiastic reception at Windsor, the production opened at the Princess’s Theatre a month later, where the royal family saw it on a further five occasions. Princess Victoria was particularly struck by the production’s sentimental but meticulously ‘correct’ representation of history: she produced a watercolour painting of the ‘Historical Episode’ for her mother’s birthday that year, and several years later she was still periodically referring to the production in her letters: she told her mother in 1859 ‘I do not know when any thing made such an impression on me.’</p>
                        <p>This production was also one of the first to benefit from an emerging relationship between the theatre and commercial photography. Martin Laroche’s character portraits of the cast (which included several of the Princess’s regular stars: Charles and Ellen Kean, Walter Lacy, John Ryder, James Faucit Cathcart and John William Cooper, as well as the thirteen-year-old future star Kate Terry) were widely sold and exhibited. Prince Albert bought a hand-coloured set of Laroche’s photographs as a Christmas present for Queen Victoria in December 1857.</p>
                        <p>The wide variety of objects in the Royal Collection and Archives which relate to this production of Richard II invite reflection on how the Victorian royal family preferred to encounter their own history, as well as demonstrating their efforts to document family theatergoing.</p>`,
                    relatedObjects: [
                        {
                            id: 593,
                            resource: require("@/assets/images/913000.jpg"),
                            type: 'Painting',
                            title: "A Scene from Macbeth, Act I"
                        },
                        {
                            id: 558,
                            resource: require("@/assets/images/605151.jpg"),
                            type: 'Print',
                            title: "Giorgio Frederico Augusto Principe di Galles"
                        },
                        {
                            id: 558,
                            resource: require("@/assets/images/919794.jpg"),
                            type: 'Painting',
                            title: "A performance of Macbeth in the Rubens Room, Windsor Catle, 4 February 1853"
                        },
                        {
                            id: 558,
                            resource: require("@/assets/images/919794.jpg"),
                            type: 'Painting',
                            title: "A performance of Macbeth in the Rubens Room, Windsor Catle, 4 February 1853"
                        },
                        {
                            id: 558,
                            resource: require("@/assets/images/919794.jpg"),
                            type: 'Painting',
                            title: "A performance of Macbeth in the Rubens Room, Windsor Catle, 4 February 1853"
                        }
                    ],
                }
            }
        };*/

    }
}

const mutations = {
    setStory: (state, story) => (state.story = story),
    setStoryList: (state, storyList) => (state.storyList = storyList),
    setThemeList: (state, storyList) => (state.storyList = storyList),
    setStoryStrap: (state, storyStrap) => (state.storyStrap = storyStrap),
};

export default {
    state,
    getters,
    actions,
    mutations
}