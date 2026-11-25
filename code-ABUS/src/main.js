import Vue from 'vue';

import App from './app.vue';
import router from './router';
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import Vuex from 'vuex';  
import store from './store';

Vue.use(ElementUI)

Vue.use(Vuex);

Vue.config.productionTip = false;

// 关闭页面时自动清除登录缓存，退出账号（保留"记住账号"的用户名）
window.addEventListener('beforeunload', () => {
  localStorage.removeItem('token');
  localStorage.removeItem('userInfo');
});

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount('#app');