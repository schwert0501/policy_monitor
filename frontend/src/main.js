import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'
import VueECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册 ECharts 组件
use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.component('v-chart', VueECharts)
app.mount('#app')
