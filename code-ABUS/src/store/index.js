import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

const savedUser = JSON.parse(localStorage.getItem('user')) || { username: null };
const store = new Vuex.Store({
  state: {
    user: {
      username: savedUser.username // ��ʼ���û���Ϣ
    }
  },
  mutations: {
    setUsername(state, username) { 
      state.user.username = username;
      localStorage.setItem('user', JSON.stringify(state.user));
    },
    clearUser(state) {
      state.user.username = null;
      localStorage.removeItem('user');
    }
  },
  actions: {
  },
  modules: {
  }
});

export default store;