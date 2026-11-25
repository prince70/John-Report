<template>
  <div class="login-container">

    <!-- Logo -->
    <img 
      class="logo"
      src="../photo/logo.png"
    />

    <div class="login-box">
      <div class="input-group">
        <input
          v-model="form.username"
          placeholder="账号"
          @keyup.enter="handleLogin"
        />
      </div>
      <div class="input-group">
        <input
          v-model="form.password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="请输入密码"
          @keyup.enter="handleLogin"
        />
        <img
          :src="showPassword ? eyeOpen : eyeClose"
          @click="togglePasswordVisibility"
          class="eye-icon"
        />
      </div>
      <div class="form-helper">
        <label class="remember-me">
          <input type="checkbox" v-model="rememberMe"/>
          记住账号
        </label>
        <!-- <a @click="showChangePasswordDialog" class="forgot-password">修改密码</a> -->
      </div>

      <button 
        class="login-btn"
        @click="handleLogin"
        :disabled="loading"
      >
        <span v-if="loading">登录中...</span>
        <span v-else>立即登录</span>
      </button>
    </div>

    <!--修改密码弹窗-->
    <div v-if="showPasswordDialog" class="dialog-mask">
      <div class="dialog-wrapper">
        <div class="dialog-content">
          <h3>修改密码</h3>
          <div class="input-group">
              <input
                v-model="passwordForm.oldPassword"
                :type="showOldPassword ? 'text' : 'password'"
                placeholder="旧密码"
              />
              <img
                :src="showOldPassword? eyeOpen : eyeClose"
                @click="toggleOldPasswordVisibility"
                class="eye-icon"
              />
          </div>
          <div class="input-group">
            <input
              v-model="passwordForm.newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              placeholder="新密码"
            />
            <img
              :src="showNewPassword? eyeOpen : eyeClose"
              @click="toggleNewPasswordVisibility"
              class="eye-icon"
            />
          </div>
          <div class="input-group">
            <input
              v-model="passwordForm.newPassword2"
              :type="showNewPassword ? 'text' : 'password'"
              placeholder="确认新密码"
            />
            <img
              :src="showNewPassword? eyeOpen : eyeClose"
              @click="toggleNewPasswordVisibility"
              class="eye-icon"
            />
          </div>
          <div class="button-group">
            <button 
              class="cancel-btn"
              @click="handleChangePassword"
              :disabled="loading"
            >
              <span v-if="loading">提交中...</span>
              <span v-else>确认</span>
            </button>
            <button class="cancel-btn" @click="closePasswordDialog">取消</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDialogFlag" class="dialog-mask">
      <div class="dialog-ws">
        <div class="dialog-content">
          <h3>{{ dialogTitle }}</h3>
          <p>{{ dialogMessage }}</p>
          <button @click="showDialogFlag = false">确定</button>
        </div>
      </div>
    </div>
    <div class="login-footer">
      <p>萬暉五金(深圳)有限公司</p>
      <p>© 2025 All Rights Reserved</p>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      form: {
        username: '',
        password: '',
      },
      passwordForm:{
        oldPassword:'',
        newPassword:'',
        newPassword2:''
      },
      showPassword: false,
      loading: false,
      rememberMe: false,
      showDialogFlag: false,
      showPasswordDialog: false,
      showOldPassword: false,
      showNewPassword: false,
      dialogTitle: '',
      dialogMessage: '',
      eyeOpen: require('../photo/eye.png'),
      eyeClose: require('../photo/eyeClose.png'),
    }
  },
  created() {
    this.showPasswordDialog = this.$route.query.showPasswordDialog === 'true';
    // 如果从首页跳转过来修改密码，接收传递的用户名
    if (this.$route.query.username) {
      this.form.username = this.$route.query.username;
    }
  },
  mounted(){
    const savedUsername=localStorage.getItem('savedUsername')
    if(savedUsername){
      this.form.username=savedUsername;
      this.e=true;
    }
  },
  methods: {
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword
    },
    toggleOldPasswordVisibility() {
      this.showOldPassword = !this.showOldPassword; 
    },
    toggleNewPasswordVisibility() {
      this.showNewPassword = !this.showNewPassword; 
    },
    async handleLogin() {
      if(!this.form.username || !this.form.password){
        this.showDialog('错误','请输入账号和密码');
        return;
      }

      this.loading = true
      try {
        const response = await axios.post('/api/login',this.form);
        if(response.data.status === 'success'){
          // 保存token
          localStorage.setItem('token', response.data.data.token);
          // 保存用户信息（包括角色）
          const userInfo = {
            username: response.data.data.username,
            role: response.data.data.role || 'normal'
          };
          localStorage.setItem('userInfo', JSON.stringify(userInfo));
          
          // 更新 Vuex 中的用户名
          this.$store.commit('setUsername', response.data.data.username);

          if (this.rememberMe) {
            // 勾选记住账号时持久化用户名
            localStorage.setItem('savedUsername', this.form.username);
          } else {
            // 未勾选则移除存储的用户名
            localStorage.removeItem('savedUsername');
          }
          
          this.showDialog('登录成功', response.data.message || '欢迎使用系统');
          
          // 使用 setTimeout 确保对话框显示后再跳转
          setTimeout(() => {
            // 根据角色跳转到不同页面
            if (userInfo.role === 'file_viewer') {
              this.$router.push('/file');
            } else {
              this.$router.push('/home');
            }
          }, 1000);
        } else {
          this.showDialog('登录失败', response.data.message || '登录失败，请重试');
        }
      }catch(error){
        console.error('Login error:', error);
        let message = '登录失败,请检查网络';
        if(error.response){
          message = error.response.data.detail || message;
        }
        this.showDialog('登录失败',message);
      }finally{
        this.loading = false;
      }
    },

    async handleChangePassword(){
      if(!this.passwordForm.oldPassword || !this.passwordForm.newPassword ||!this.passwordForm.newPassword2){
        this.showDialog('错误','请填写完整信息');
        return;
      }
      if (this.passwordForm.newPassword !== this.passwordForm.newPassword2) {
        this.showDialog('错误', '新密码和确认密码不一致,请重新输入');
        return;
      }
      // 密码强度验证正则表达式
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&^]+$/;
      if (!passwordRegex.test(this.passwordForm.newPassword)) {
        this.showDialog('错误', '新密码必须包含大写字母、小写字母、数字和特殊符号');
        return;
      }
      
      // 获取当前用户名（优先使用输入框的值，其次使用本地存储）
      const currentUsername = (this.form.username && this.form.username.trim()) || localStorage.getItem('savedUsername');
      if (!currentUsername || currentUsername.trim() === '') {
        this.showDialog('错误', '请先在登录框中输入用户名，然后再修改密码');
        return;
      }
      
      this.loading=true
      try{
        console.log('修改密码 - 用户名:', currentUsername)
        await axios.post('/api/change-password',{
          old_password:this.passwordForm.oldPassword,
          new_password:this.passwordForm.newPassword2
        },{
          params:{
            username: currentUsername
          },
          
        });
        this.showDialog('成功', '密码修改成功，请重新登录');
        this.closePasswordDialog();
        this.form.password='';
      }catch(error){
        let message='密码修改失败';
        if(error.response){
          message=error.response.data.detail ||message;
        }
        this.showDialog('错误', message);
      }finally{
        this.loading=false;
      }
    },
    showChangePasswordDialog() {
      // 确保有用户名才能修改密码（优先使用输入框的值，其次使用本地存储）
      const currentUsername = (this.form.username && this.form.username.trim()) || localStorage.getItem('savedUsername');
      if (!currentUsername || currentUsername.trim() === '') {
        this.showDialog('错误', '请先在登录框中输入用户名');
        return;
      }
      this.showPasswordDialog = true;
    },
    closePasswordDialog() {
      this.showPasswordDialog = false;
      this.passwordForm = { oldPassword: '', newPassword: '' };
    },
    showDialog(title, message) {
      this.dialogTitle = title;
      this.dialogMessage = message;
      this.showDialogFlag = true;
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #002060;
  background-image:url('../photo/background.png');
  position: relative;
}

.logo {
  width: 250px;
  margin-bottom: 50px;
}

.login-box {
  background: white;
  width: 400px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,32,96,0.1);
}


.input-group {
  position: relative;
  margin-bottom: 20px;
}



.input-group input {
  width: 100%;
  height: 48px;
  padding: 0 15px;
  border: 1px solid #E8E8E8;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s;
}


.input-group input:focus {
  border-color: #002060;
  outline: none;
}

.eye-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  cursor: pointer;
}

.code-group {
  display: flex;
  gap: 10px;
}

.send-code {
  width: 120px;
  flex-shrink: 0;
  background: #002060;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.send-code:disabled {
  opacity: 0.7;
  background: #666;
  cursor: not-allowed;
}

.form-helper {
  display: flex;
  justify-content: space-between;
  margin: 20px 0;
  font-size: 14px;
  color: #666;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
}

.login-btn {
  width: 100%;
  height: 48px;
  background: #002060;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 弹窗样式 */
.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog-wrapper {
  background: white;
  padding: 30px;
  border-radius: 12px;
  min-width: 300px;
  text-align: center;
  z-index: 100;
}
.dialog-ws {
  background: white;
  padding: 30px;
  border-radius: 12px;
  min-width: 300px;
  text-align: center;
  z-index: 99999;
}

.dialog-content h3 {
  color: #002060;
  margin-bottom: 15px;
}

.dialog-content button {
  margin-top: 20px;
  padding: 8px 20px;
  background: #002060;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.login-footer {
  position: absolute;
  bottom: 30px;
  text-align: center;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}
.forgot-password {
  color: rgb(167, 33, 33);
  text-decoration: underline;
}
.cancel-btn {
  margin-top: 10px;
  background-color: #ccc;
  padding: 12px 24px;
  font-size: 16px;
}

.button-group {
  display: flex;
  justify-content: space-between; /* 按钮之间的间距 */
  gap: 10px; /* 按钮之间的间距 */
}
</style>