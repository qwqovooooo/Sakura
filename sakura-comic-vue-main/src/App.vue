<template>
  <div class="common-layout">
    <el-container >
      <el-header style="width: 100%; position: sticky; border-bottom: 1px solid #dcdfe6; top: 0; left: 0; z-index:1000; padding: 0">
      <div class="sakura-header">
        <SakuraMenu/>
      </div>
      </el-header>
      <el-main style="overflow: hidden; top: 0; left: 0; padding: 0;">
        <!-- <MovieCardListVue/> -->
        <!-- <router-view /> -->
        <div class="sakura-main">
          <!-- <router-view /> -->
          <router-view v-slot="{ Component }" :key="key">
          <keep-alive :exclude="['MovDetailPageVue', 'MovieKeywordPageVue', 'LoginVue']">
            <component :is="Component"/>
          </keep-alive>
          </router-view>
        </div>
        
      </el-main>
      <el-footer style="padding: 0">
        <FooterVue/>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import SakuraMenu from './components/SakuraMenu.vue'
import MovieCardList from './components/MovieCardList.vue'
import FooterVue from './components/Footer.vue'
import MovDetailPageVue from './views/MovDetailPage.vue'
import MovieKeywordPageVue from './views/MovieKeywordPage.vue'
import LoginVue from './views/Login.vue'

export default {
  name: 'App',
  components: {
    SakuraMenu,
    MovieCardList,
    FooterVue,
    MovDetailPageVue,
    MovieKeywordPageVue,
    LoginVue
  },

  computed: {
    key() {
      // 只要保证 key 唯一性就可以了，保证不同页面的 key 不相同
      // console.log(this.$route.fullPath);
      return this.$route.fullPath
    }
  },
}
</script>

<style>
.common-layout {
  background: transparent;
  min-height: 100vh;
}

.el-container {
  background: transparent;
}

.el-header {
  background: rgba(255, 248, 235, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 2px 10px rgba(139, 90, 60, 0.15);
}

.el-main {
  background: transparent;
}

.el-footer {
  background: rgba(255, 248, 235, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 -2px 10px rgba(139, 90, 60, 0.15);
}
</style>
