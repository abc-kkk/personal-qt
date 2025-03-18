<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="item.path">
      {{ item.meta.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'Breadcrumb',
  setup() {
    const route = useRoute()
    const breadcrumbs = ref([])

    /**
     * 生成面包屑导航
     */
    const getBreadcrumbs = () => {
      const matched = route.matched.filter(item => item.meta && item.meta.title)
      
      // 首页始终是第一个
      const home = {
        path: '/',
        meta: { title: '首页' }
      }
      
      breadcrumbs.value = [home, ...matched]
    }

    // 监听路由变化
    watch(
      () => route.path,
      () => {
        getBreadcrumbs()
      },
      { immediate: true }
    )

    return {
      breadcrumbs
    }
  }
}
</script>

<style scoped>
.el-breadcrumb {
  font-size: 14px;
  line-height: 1;
}
</style> 