<template>
    <div class="gallery-wrapper">
        <ClientOnly>
            <div ref="grid" class="grid">
                <div class="grid-sizer"></div>
                <div 
                    v-for="(item, index) in visibleImages" 
                    :key="item.id + '-' + index" 
                    class="grid-item"
                    :style="{ 
                        width: item.dimensions?.width + 'px',
                        height: item.height + 'px'
                    }"
                    @click="openModal(item)"
                >
                    <div class="media-container">
                        <template v-if="item.video">
                            <video 
                                :src="item.video" 
                                autoplay 
                                muted 
                                loop 
                                playsinline 
                                class="media video"
                                @loadeddata="handleMediaLoad" 
                            />
                        </template>
                        <template v-else>
                            <img 
                                :src="item.image" 
                                :alt="item.title" 
                                class="media image" 
                                @load="handleMediaLoad"
                                loading="lazy"
                            />
                        </template>
                    </div>
                    <div class="caption-container">
                        <p class="caption">{{ item.title }}</p>
                    </div>
                </div>
            </div>
        </ClientOnly>

        <button 
            class="view-more" 
            :class="{ loading: isLoading }"
            v-if="hasMore" 
            @click="loadMore"
            :disabled="isLoading"
        >
            {{ isLoading ? 'Loading...' : 'View more' }}
        </button>
        
        <ImageModal v-if="selected" :item="selected" @close="selected = null" />
    </div>
</template>

<script setup>
import { useGalleryData } from '~/composables/useGalleryData';
import ImageModal from './ImageModal.vue';

const images = useGalleryData();
const visibleImages = ref([]);
const selected = ref(null);
const grid = ref(null);
const masonryInstance = ref(null);
const isLoading = ref(false);
const batchSize = 6;
let currentIndex = 0;
let Masonry = null;
let loadedCount = 0;

// Generate varied dimensions for natural masonry layout
const generateDimensions = () => {
  const widths = [300, 350, 280, 320, 400, 250, 380];
  const aspectRatios = [0.75, 1.2, 0.9, 1.5, 0.6, 1.1, 1.3, 0.8, 1.4];
  
  return {
    width: widths[Math.floor(Math.random() * widths.length)],
    aspectRatio: aspectRatios[Math.floor(Math.random() * aspectRatios.length)]
  };
};

const openModal = (item) => {
    selected.value = item;
};

const loadMasonry = async () => {
    if (process.client) {
        const MasonryModule = await import('masonry-layout');
        Masonry = MasonryModule.default;

        await nextTick();

        if (grid.value) {
            masonryInstance.value = new Masonry(grid.value, {
                itemSelector: '.grid-item',
                columnWidth: 250,
                percentPosition: false,
                transitionDuration: '0.4s',
                gutter: 20,
                fitWidth: true,
                horizontalOrder: false,
                stamp: '.grid-sizer'
            });
        }
    }
};

const layoutMasonry = () => {
    if (masonryInstance.value) {
        nextTick(() => {
            masonryInstance.value.reloadItems();
            masonryInstance.value.layout();
        });
    }
};

const handleMediaLoad = (event) => {
    loadedCount++;
    const el = event.target.closest('.grid-item');
    
    if (el && !el.classList.contains('loaded')) {
        el.classList.add('loaded');
        
        // Random animation delay for more natural effect
        const randomDelay = Math.random() * 300 + 50;
        setTimeout(() => {
            el.classList.add('visible');
        }, randomDelay);

        if (masonryInstance.value) {
            masonryInstance.value.layout();
        }
    }

    // If all current batch items are loaded, enable interactions
    if (loadedCount >= visibleImages.value.length) {
        isLoading.value = false;
    }
};

const loadMore = async () => {
    if (isLoading.value) return;
    
    isLoading.value = true;
    
    const nextBatch = images.slice(currentIndex, currentIndex + batchSize).map(item => {
        const dimensions = generateDimensions();
        return {
            ...item,
            dimensions,
            height: Math.round(dimensions.width / dimensions.aspectRatio)
        };
    });
    
    visibleImages.value.push(...nextBatch);
    currentIndex += batchSize;

    await nextTick();

    // Add varied animation classes to new items
    const newItems = grid.value?.querySelectorAll('.grid-item:not(.loaded)');
    newItems?.forEach((el, index) => {
        const randomDirection = Math.random() > 0.5 ? 1 : -1;
        const randomRotation = (Math.random() - 0.5) * 10;
        const randomScale = 0.7 + Math.random() * 0.2;
        
        el.style.setProperty('--random-direction', randomDirection);
        el.style.setProperty('--random-rotation', `${randomRotation}deg`);
        el.style.setProperty('--random-scale', randomScale);
        el.style.animationDelay = `${Math.random() * 0.5}s`;
    });

    layoutMasonry();
};

const hasMore = computed(() => currentIndex < images.length);

onMounted(async () => {
    if (process.client) {
        const firstBatch = images.slice(0, batchSize).map(item => {
            const dimensions = generateDimensions();
            return {
                ...item,
                dimensions,
                height: Math.round(dimensions.width / dimensions.aspectRatio)
            };
        });
        visibleImages.value = firstBatch;
        currentIndex = batchSize;
        isLoading.value = true;

        await loadMasonry();

        // Handle window resize
        const handleResize = () => {
            if (masonryInstance.value) {
                masonryInstance.value.layout();
            }
        };

        window.addEventListener('resize', handleResize);

        // Cleanup on unmount
        onUnmounted(() => {
            window.removeEventListener('resize', handleResize);
            if (masonryInstance.value) {
                masonryInstance.value.destroy();
            }
        });
    }
});
</script>

<style lang="scss" scoped>
.gallery-wrapper {
    padding: 2rem 1rem;
    max-width: 1400px;
    margin: 0 auto;

    .grid {
        margin: 0 auto;
        position: relative;
    }

    .grid-sizer {
        width: 250px;
        height: 0;
        
        @media (max-width: 1200px) {
            width: 200px;
        }
        
        @media (max-width: 768px) {
            width: calc(50% - 10px);
        }
        
        @media (max-width: 480px) {
            width: calc(100% - 20px);
        }
    }

    .grid-item {
        margin-bottom: 20px;
        border-radius: 16px;
        cursor: pointer;
        background-color: #fff;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        overflow: hidden;
        opacity: 0;
        transform: translateY(calc(40px * var(--random-direction, 1))) 
                   rotate(var(--random-rotation, 0deg)) 
                   scale(var(--random-scale, 0.8));
        transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        
        @media (max-width: 768px) {
            width: calc(50% - 10px) !important;
            height: auto !important;
        }
        
        @media (max-width: 480px) {
            width: calc(100% - 20px) !important;
            height: auto !important;
        }

        &.visible {
            opacity: 1;
            transform: translateY(0) rotate(0deg) scale(1);
        }

        &:hover {
            transform: translateY(-8px) scale(1.03) rotate(1deg);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
            z-index: 2;
        }

        &:nth-child(even) {
            animation-direction: reverse;
        }

        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, 
                rgba(102, 126, 234, 0.1) 0%, 
                rgba(118, 75, 162, 0.1) 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1;
        }

        &:hover::before {
            opacity: 1;
        }

        .media-container {
            position: relative;
            width: 100%;
            overflow: hidden;
            background: #f5f5f5;
        }

        .media {
            width: 100%;
            height: 100%;
            display: block;
            object-fit: cover;
            transition: transform 0.4s ease;
            position: relative;
            z-index: 2;
            
            &.image {
                filter: brightness(1.02) contrast(1.05);
            }
            
            &.video {
                filter: brightness(1.02) contrast(1.05);
            }
        }

        .caption-container {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 1.5rem 1rem 1rem;
            background: linear-gradient(to top, 
                rgba(0, 0, 0, 0.8) 0%, 
                rgba(0, 0, 0, 0.4) 50%,
                transparent 100%);
            transform: translateY(100%);
            transition: transform 0.3s ease;
            z-index: 3;
        }

        &:hover .caption-container {
            transform: translateY(0);
        }

        .caption {
            margin: 0;
            font-size: 0.85rem;
            color: white;
            font-weight: 600;
            line-height: 1.3;
            text-align: left;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
            letter-spacing: 0.5px;
        }
    }

    .view-more {
        display: block;
        margin: 2rem auto 0;
        padding: 0.75rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        position: relative;
        min-width: 140px;

        &:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        &:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }

        &.loading::after {
            content: '';
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            width: 16px;
            height: 16px;
            animation: spin 0.8s linear infinite;
        }
    }

    @keyframes spin {
        to {
            transform: translateY(-50%) rotate(360deg);
        }
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0px) rotate(0deg);
        }
        50% {
            transform: translateY(-5px) rotate(1deg);
        }
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.02);
        }
    }

    @keyframes slideInRotate {
        0% {
            transform: translateY(50px) rotate(10deg) scale(0.7);
            opacity: 0;
        }
        100% {
            transform: translateY(0) rotate(0deg) scale(1);
            opacity: 1;
        }
    }

    // Add subtle floating animation to loaded items
    .grid-item.visible {
        animation: float 6s ease-in-out infinite;
        
        &:nth-child(odd) {
            animation-delay: 0s;
            animation-duration: 8s;
        }
        
        &:nth-child(even) {
            animation-delay: 2s;
            animation-duration: 6s;
            animation-direction: reverse;
        }

        &:nth-child(3n) {
            animation: pulse 4s ease-in-out infinite;
            animation-delay: 1s;
        }
    }
}
</style>