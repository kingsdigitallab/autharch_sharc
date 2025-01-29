import Api from '../../services/Api';

const state = {
    archive: {},
    images: []
};

const getters = {
    getArchive: (state) => state.archive
};

const actions = {
    async fetchArchive({ commit }, id) {
        const response = await Api.getSingle('/documents/',id);
        commit('setArchive', response.data);
    },
    async fetchRCTArchive({ commit }, reference) {
        const response = await Api.getSingle('/documents/','?reference='+reference);
        if (response.data && response.data.results.length > 0) {
            commit('setArchive', response.data.results[0]);
        }
    }
};

const mutations = {
    setArchive: (state, archive) => (state.archive = archive),
};

export default {
    state,
    getters,
    actions,
    mutations
}
