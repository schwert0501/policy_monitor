import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Policies from '../views/Policies.vue'
import Monitor from '../views/Monitor.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/policies',
    name: 'Policies',
    component: Policies
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: Monitor
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router