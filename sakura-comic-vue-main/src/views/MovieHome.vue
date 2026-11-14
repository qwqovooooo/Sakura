<template>
  <div class="movie-home">
    <!-- 装饰元素 -->
    <div class="floating-decoration">
      <div class="sakura-petal" v-for="i in 8" :key="i" :style="{left: (i * 12) + '%', animationDelay: (i * 0.5) + 's'}"></div>
    </div>

    <!-- Hero Banner 区域 -->
    <div class="hero-section">
      <div class="banner-decoration">
        <div class="corner-ornament top-left"></div>
        <div class="corner-ornament top-right"></div>
      </div>
      <SakuraBigImgVue/>
      <div class="banner-glow"></div>
    </div>
    
    <!-- 装饰性分割线 -->
    <div class="decorative-divider">
      <div class="divider-line"></div>
      <div class="divider-ornament">✦</div>
      <div class="divider-line"></div>
    </div>

    <!-- 管理后台入口 -->
    <div v-if="isAdmin" class="admin-entrance">
      <el-button 
        type="warning" 
        size="large" 
        @click="goToAdmin"
        class="admin-btn"
      >
        <el-icon style="margin-right: 8px;"><Setting /></el-icon>
        进入管理后台
      </el-button>
    </div>

    <!-- 快速导航 -->
    <div class="quick-nav">
      <div class="nav-title">
        <span class="title-text">探索精彩内容</span>
        <div class="title-underline"></div>
      </div>
      <el-row :gutter="24" justify="center">
        <el-col :xs="12" :sm="6" :md="6" v-for="(nav, index) in quickNavs" :key="index">
          <div class="nav-card anime-card" @click="navigateTo(nav.path)">
            <div class="card-border-effect"></div>
            <div class="nav-card-bg" :class="'nav-' + index"></div>
            <div class="nav-card-content">
              <div class="nav-icon-wrapper">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path :d="nav.iconPath"></path>
                </svg>
                <div class="icon-glow"></div>
              </div>
              <h3 class="nav-title-text">{{ nav.title }}</h3>
              <p class="nav-desc">{{ nav.desc }}</p>
              <div class="nav-sparkle">✨</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 内容分类 -->
    <div class="content-sections">
      <!-- 动漫区 -->
      <div class="section-wrapper">
        <div class="section-header">
          <div class="section-title">
            <div class="title-icon">★</div>
            <h2>热门动漫</h2>
            <div class="title-wave"></div>
          </div>
          <router-link to="/movtype/4" class="more-link">
            查看全部 <span class="arrow">→</span>
          </router-link>
        </div>
        <MovLimitCardVue :movtype="4"/>
      </div>

      <!-- 电影区 -->
      <div class="section-wrapper" v-if="showMore">
        <div class="section-header">
          <div class="section-title">
            <div class="title-icon">★</div>
            <h2>精选电影</h2>
            <div class="title-wave"></div>
          </div>
          <router-link to="/movtype/1" class="more-link">
            查看全部 <span class="arrow">→</span>
          </router-link>
        </div>
        <MovLimitCardVue :movtype="1"/>
      </div>

      <!-- 电视剧区 -->
      <div class="section-wrapper" v-if="showMore">
        <div class="section-header">
          <div class="section-title">
            <div class="title-icon">★</div>
            <h2>热播剧集</h2>
            <div class="title-wave"></div>
          </div>
          <router-link to="/movtype/2" class="more-link">
            查看全部 <span class="arrow">→</span>
          </router-link>
        </div>
        <MovLimitCardVue :movtype="2"/>
      </div>

      <!-- 综艺区 -->
      <div class="section-wrapper" v-if="showMore">
        <div class="section-header">
          <div class="section-title">
            <div class="title-icon">★</div>
            <h2>精彩综艺</h2>
            <div class="title-wave"></div>
          </div>
          <router-link to="/movtype/3" class="more-link">
            查看全部 <span class="arrow">→</span>
          </router-link>
        </div>
        <MovLimitCardVue :movtype="3"/>
      </div>
    </div>

    <el-backtop :right="50" :bottom="80" />
  </div>
</template>

<script>
import SakuraBigImgVue from '../components/SakuraBigImg.vue'
import MovLimitCardVue from '../components/MovLimitCard.vue'
import { Setting, ArrowRight } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'MovieHome',
  components: {
    MovLimitCardVue,
    SakuraBigImgVue,
    Setting,
    ArrowRight
  },
  setup() {
    const router = useRouter()
    const store = useStore()
    const isAdmin = ref(false)
    const showMore = ref(false)
    
    const quickNavs = ref([
      {
        title: '电影',
        desc: '精彩影院',
        path: '/movtype/1',
        iconPath: 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z'
      },
      {
        title: '电视剧',
        desc: '热播剧集',
        path: '/movtype/2',
        iconPath: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
      },
      {
        title: '动漫',
        desc: '二次元世界',
        path: '/movtype/4',
        iconPath: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
      },
      {
        title: '综艺',
        desc: '娱乐新鲜事',
        path: '/movtype/3',
        iconPath: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z'
      }
    ])
    
    onMounted(() => {
      const isLoggedIn = store.state.appStore.isLogining
      const user = store.state.appStore.user
      isAdmin.value = isLoggedIn && user && user.is_admin === true
      
      setTimeout(() => {
        showMore.value = true
      }, 1500)
    })
    
    const goToAdmin = () => {
      router.push('/admin/dashboard')
    }

    const navigateTo = (path) => {
      router.push(path)
    }
    
    return {
      goToAdmin,
      isAdmin,
      showMore,
      quickNavs,
      navigateTo
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
.movie-home {
  min-height: 100vh;
  background: transparent;
  position: relative;
  overflow-x: hidden;
}

/* 漂浮装饰 */
.floating-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.sakura-petal {
  position: absolute;
  top: -50px;
  width: 20px;
  height: 20px;
  background: radial-gradient(circle, rgba(255, 192, 128, 0.6) 0%, rgba(255, 154, 60, 0.3) 70%);
  border-radius: 50% 0 50% 0;
  animation: float-down 15s infinite linear;
  opacity: 0;
}

@keyframes float-down {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.8;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(100vh) rotate(360deg);
    opacity: 0;
  }
}

/* Banner 装饰 */
.hero-section {
  padding: 20px 10px;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.banner-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.corner-ornament {
  position: absolute;
  width: 80px;
  height: 80px;
  border: 3px solid rgba(255, 154, 60, 0.3);
  border-radius: 8px;
}

.corner-ornament.top-left {
  top: 20px;
  left: 20px;
  border-right: none;
  border-bottom: none;
  animation: pulse-corner 3s infinite;
}

.corner-ornament.top-right {
  top: 20px;
  right: 20px;
  border-left: none;
  border-bottom: none;
  animation: pulse-corner 3s infinite 1.5s;
}

@keyframes pulse-corner {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.05);
  }
}

.banner-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255, 192, 128, 0.2) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  animation: glow-pulse 4s infinite;
  pointer-events: none;
}

@keyframes glow-pulse {
  0%, 100% {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.8;
    transform: translate(-50%, -50%) scale(1.2);
  }
}

/* 装饰性分割线 */
.decorative-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 40px auto;
  max-width: 600px;
  gap: 20px;
}

.divider-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 154, 60, 0.5) 50%, transparent 100%);
  position: relative;
}

.divider-line::after {
  content: '';
  position: absolute;
  top: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 192, 128, 0.3) 50%, transparent 100%);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0%, 100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

.divider-ornament {
  font-size: 24px;
  color: #FF9A3C;
  text-shadow: 0 0 10px rgba(255, 154, 60, 0.5);
  animation: rotate-ornament 8s infinite linear;
}

@keyframes rotate-ornament {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.admin-entrance {
  text-align: center;
  margin: 30px 0;
}

.admin-btn {
  background: linear-gradient(135deg, #FFB366 0%, #FF9A3C 100%);
  border: none;
  padding: 15px 40px;
  font-size: 16px;
  border-radius: 30px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 20px rgba(255, 154, 60, 0.3);
  font-weight: 600;
}

.admin-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(255, 154, 60, 0.45);
  background: linear-gradient(135deg, #FFC480 0%, #FFAD60 100%);
}

/* 快速导航 */
.quick-nav {
  max-width: 1400px;
  margin: 50px auto;
  padding: 0 20px;
  position: relative;
  z-index: 2;
}

.nav-title {
  text-align: center;
  margin-bottom: 50px;
  padding: 20px;
  background: rgba(255, 248, 235, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(139, 90, 60, 0.2);
}

.title-text {
  font-size: 36px;
  font-weight: bold;
  color: #8B5A2B;
  font-family: 'YouYuan', 'STXingkai', 'KaiTi', cursive, serif;
  letter-spacing: 4px;
  position: relative;
  display: inline-block;
  text-shadow: 2px 2px 0 rgba(255, 192, 128, 0.3),
               4px 4px 8px rgba(255, 154, 60, 0.2);
  transform: skewY(-2deg);
}

.title-underline {
  width: 200px;
  height: 4px;
  background: linear-gradient(90deg, transparent 0%, #FFB366 20%, #FF9A3C 50%, #FFB366 80%, transparent 100%);
  margin: 15px auto 0;
  border-radius: 2px;
  position: relative;
  animation: underline-wave 3s infinite;
}

.title-underline::before,
.title-underline::after {
  content: '✦';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  color: #FF9A3C;
  font-size: 16px;
  animation: sparkle 2s infinite;
}

.title-underline::before {
  left: -25px;
}

.title-underline::after {
  right: -25px;
  animation-delay: 1s;
}

@keyframes underline-wave {
  0%, 100% {
    transform: scaleX(1);
  }
  50% {
    transform: scaleX(1.05);
  }
}

@keyframes sparkle {
  0%, 100% {
    opacity: 0.5;
    transform: translateY(-50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translateY(-50%) scale(1.3);
  }
}

.nav-card {
  position: relative;
  height: 220px;
  border-radius: 20px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 24px;
  background: rgba(255, 248, 235, 0.85);
  backdrop-filter: blur(15px);
  box-shadow: 0 8px 30px rgba(139, 90, 60, 0.3),
              inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* 动漫风边框效果 */
.card-border-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 3px solid transparent;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(255, 179, 102, 0.5), rgba(255, 154, 60, 0.3)) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: destination-out;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s;
}

.nav-card:hover .card-border-effect {
  opacity: 1;
  animation: border-glow 2s infinite;
}

@keyframes border-glow {
  0%, 100% {
    filter: brightness(1);
  }
  50% {
    filter: brightness(1.3);
  }
}

.nav-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.9;
  transition: all 0.5s;
}

.nav-0 .nav-card-bg {
  background: linear-gradient(135deg, #FFD4A3 0%, #FFC480 100%);
}

.nav-1 .nav-card-bg {
  background: linear-gradient(135deg, #FFCA8F 0%, #FFB870 100%);
}

.nav-2 .nav-card-bg {
  background: linear-gradient(135deg, #FFC07B 0%, #FFAD60 100%);
}

.nav-3 .nav-card-bg {
  background: linear-gradient(135deg, #FFB870 0%, #FFA24D 100%);
}

.nav-card:hover {
  transform: translateY(-12px) scale(1.02);
  box-shadow: 0 12px 35px rgba(139, 90, 60, 0.2);
}

.nav-card:hover .nav-card-bg {
  opacity: 1;
}

.nav-card-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 30px 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.nav-icon-wrapper {
  width: 70px;
  height: 70px;
  margin: 0 auto 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s;
  box-shadow: 0 6px 20px rgba(139, 90, 60, 0.25),
              inset 0 2px 5px rgba(255, 255, 255, 0.8);
  position: relative;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 192, 128, 0.6) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.4s;
}

.nav-card:hover .icon-glow {
  opacity: 1;
  animation: icon-pulse 1.5s infinite;
}

@keyframes icon-pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.3);
  }
}

.nav-card:hover .nav-icon-wrapper {
  transform: rotate(360deg) scale(1.15);
  box-shadow: 0 8px 30px rgba(139, 90, 60, 0.4),
              inset 0 2px 5px rgba(255, 255, 255, 0.8);
}

.nav-icon {
  width: 35px;
  height: 35px;
  color: #E67E22;
  stroke-width: 2.5;
}

.nav-title-text {
  font-size: 22px;
  font-weight: bold;
  margin: 10px 0;
  color: #8B5A2B;
  letter-spacing: 2px;
  font-family: 'YouYuan', 'STXingkai', 'KaiTi', cursive, serif;
  text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.5),
               2px 2px 4px rgba(255, 192, 128, 0.3);
  transform: skewX(-3deg);
}

.nav-desc {
  font-size: 14px;
  color: #A0826D;
  margin: 0;
  opacity: 0.9;
}

.nav-sparkle {
  position: absolute;
  bottom: 20px;
  right: 25px;
  font-size: 24px;
  opacity: 0;
  transform: translateX(-10px) rotate(0deg);
  transition: all 0.4s;
}

.nav-card:hover .nav-sparkle {
  opacity: 1;
  transform: translateX(0) rotate(180deg);
  animation: sparkle-shine 1s infinite;
}

@keyframes sparkle-shine {
  0%, 100% {
    filter: brightness(1);
  }
  50% {
    filter: brightness(1.5) drop-shadow(0 0 8px rgba(255, 192, 128, 0.8));
  }
}

/* 内容分类 */
.content-sections {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

.section-wrapper {
  margin: 70px 0;
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 0 10px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title-icon {
  font-size: 28px;
  color: #FF9A3C;
  animation: star-rotate 4s infinite linear;
  filter: drop-shadow(0 0 8px rgba(255, 154, 60, 0.6));
}

@keyframes star-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.title-wave {
  flex: 1;
  height: 3px;
  background: linear-gradient(90deg, #FFB366 0%, transparent 100%);
  position: relative;
  overflow: hidden;
}

.title-wave::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 192, 128, 0.8) 50%, transparent 100%);
  animation: wave-move 3s infinite;
}

@keyframes wave-move {
  to {
    left: 200%;
  }
}

.section-title h2 {
  font-size: 28px;
  font-weight: bold;
  color: #8B5A2B;
  margin: 0;
  letter-spacing: 3px;
  font-family: 'YouYuan', 'STXingkai', 'KaiTi', cursive, serif;
  position: relative;
  text-shadow: 2px 2px 0 rgba(255, 255, 255, 0.5),
               3px 3px 6px rgba(255, 192, 128, 0.4);
  transform: skewY(-1deg);
}

.more-link {
  color: #E67E22;
  text-decoration: none;
  font-size: 15px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  padding: 10px 24px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(255, 192, 123, 0.4), rgba(255, 179, 102, 0.3));
  border: 2px solid rgba(255, 154, 60, 0.3);
  font-family: 'YouYuan', 'KaiTi', sans-serif;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.more-link::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(255, 192, 128, 0.5), transparent);
  transform: translate(-50%, -50%);
  border-radius: 50%;
  transition: width 0.4s, height 0.4s;
}

.more-link:hover::before {
  width: 200px;
  height: 200px;
}

.more-link .arrow {
  display: inline-block;
  transition: transform 0.3s;
  font-size: 18px;
}

.more-link:hover .arrow {
  transform: translateX(5px);
  animation: arrow-bounce 0.6s infinite;
}

@keyframes arrow-bounce {
  0%, 100% {
    transform: translateX(5px);
  }
  50% {
    transform: translateX(10px);
  }
}

.more-link:hover {
  color: #FF9A3C;
  background: linear-gradient(135deg, rgba(255, 192, 123, 0.6), rgba(255, 179, 102, 0.5));
  border-color: rgba(255, 154, 60, 0.6);
  box-shadow: 0 4px 15px rgba(255, 154, 60, 0.3);
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-title {
    font-size: 24px;
    margin-bottom: 30px;
  }

  .section-title h2 {
    font-size: 22px;
  }
  
  .nav-card {
    height: 180px;
  }
  
  .nav-title-text {
    font-size: 18px;
  }
  
  .nav-icon-wrapper {
    width: 55px;
    height: 55px;
  }

  .nav-icon {
    width: 28px;
    height: 28px;
  }

  .title-line {
    width: 25px;
  }
}
</style>
