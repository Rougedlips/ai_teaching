import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入我们马上要建的路由
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css' // 引入 Element Plus 的漂亮样式

const app = createApp(App)

app.use(router)
app.use(ElementPlus)
app.mount('#app')