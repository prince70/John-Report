<template>
  <div class="top-bar">
    <div class="search-box">
      <!-- <input type="text" placeholder="搜索..." v-model="searchText" />
      <img class="search-icon" src="../pages/photo/search.png" /> -->
    </div>
    <div class="right-items">
      <div class="message" @click="toggleMessagePopup">
        <img src="../pages/photo/bell.png" />
        <transition name="fade">
          <div v-show="showMessagePopup" class="message-popup">
           <p style="color:red">1、当您的网页出现缺失或者数据与他人不一致时，请清空浏览器存储的数据后关闭浏览器，重新打开网站。</p>
           <p style="color:blue">2、修改密码时请注意需要包含特殊字符、数字、大小写字母等。</p>
          </div>
        </transition>
      </div>
      <div class="user-dropdown" @click="toggleUserDropdown">
        <img class="avatar" :src="avatarImage" />
        <transition name="fade">
          <div v-show="showUserDropdown" class="dropdown-menu">
            <div class="dropdown-item" @click="logout">退出登录</div>
            <div class="dropdown-item" @click="changePassword">修改密码</div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TopBar',
  data() {
    return {
      showUserDropdown: false,
      searchText: '',
      avatarImage: require('../pages/photo/avatar.png'),
      showMessagePopup: false, 
    }
  },
  mounted() {
    if(localStorage.getItem('savedUsername') && !localStorage.getItem('messageShown')){
      this.showMessagePopup = true;
      localStorage.setItem('messageShown', 'true');
      document.addEventListener('click', this.closeMessagePopup);
    }
  },
  methods: {
    toggleUserDropdown() {
      this.showUserDropdown = !this.showUserDropdown;
      if (this.showUserDropdown) {
        document.addEventListener('click', this.closeUserDropdown);
      }
    },
    closeUserDropdown(e) {
      if (!this.$el.contains(e.target)) {
        this.showUserDropdown = false;
        document.removeEventListener('click', this.closeUserDropdown);
      }
    },
    async logout() {
      try {
        await axios.post('/api/cache/clear');
      } catch (error) {
        console.warn('清理服务端缓存失败，将继续退出登录', error);
      }

      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      localStorage.removeItem('savedUsername');
      localStorage.removeItem('messageShown');

      if (this.$store && this.$store.commit) {
        this.$store.commit('clearUser');
      }

      this.$router.replace('/');
    },
    changePassword() {
      // 获取当前登录的用户名（从 Vuex 或 localStorage）
      const currentUsername = this.$store.state.user?.username || localStorage.getItem('savedUsername');
      
      if (!currentUsername) {
        alert('无法获取用户名，请重新登录');
        this.logout();
        return;
      }
      
      // 跳转到登录页，并传递用户名和显示密码对话框的标志
      this.$router.push({
        path: '/',
        query: { 
          showPasswordDialog: true,
          username: currentUsername
        }
      })
      .catch(err => {
        if (err.name !== 'NavigationDuplicated') {
          console.error(err);
        }
      });
    },
    toggleMessagePopup() {
      this.showMessagePopup = !this.showMessagePopup;
      if (this.showMessagePopup) {
        document.addEventListener('click', this.closeMessagePopup);
      }
    },
    closeMessagePopup(e) {
      if(!this.$el.querySelector('.message').contains(e.target)){
        this.showMessagePopup = false;
        document.removeEventListener('click', this.closeMessagePopup);
      }
    },
  },
  beforeDestroy() {
    document.removeEventListener('click', this.closeUserDropdown);
    document.removeEventListener('click', this.closeMessagePopup);
  }
}
</script>

<style scoped>
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.search-box {
  position: relative;
}

.search-box input {
  padding: 8px 32px 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
}

.search-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
}

.right-items {
  display: flex;
  align-items: center;
  gap: 20px;
}


.user-dropdown {
  position: relative;
  cursor: pointer;
}
.message img{
  width: 32px;
  height: 32px;
  border-radius: 50%;
  position: relative;
  z-index: 10;
}
.message-popup {
  position: absolute;
  right: 0;
  top: 40px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 4px;
  padding: 16px;
  min-width: 200px;
  z-index: 1000;
}
.message-popup.active {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 40px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 4px;
  padding: 8px 0;
  min-width: 120px;
}

.dropdown-item {
  padding: 8px 16px;
  transition: background 0.3s;
  white-space: nowrap;
}

.dropdown-item:hover {
  background: #f5f5f5;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style> 