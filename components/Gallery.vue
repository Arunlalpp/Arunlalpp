<template>
    <div class="gallery-wrapper">
        <ClientOnly>
            <div ref="grid" class="grid">
                <div class="grid-sizer"></div>
                <div 
                    v-for="(item, index) in visibleImages" 
                    :key="item.id + '-' + index" 
                    class="grid-item"
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
                columnWidth: '.grid-sizer',
                percentPosition: true,
                transitionDuration: '0.3s',
                gutter: 16,
                fitWidth: true,
                horizontalOrder: true
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
        
        // Trigger animation after a short delay
        setTimeout(() => {
            el.classList.add('visible');
        }, 100);

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
    
    const nextBatch = images.slice(currentIndex, currentIndex + batchSize);
    visibleImages.value.push(...nextBatch);
    currentIndex += batchSize;

    await nextTick();

    // Add animation classes to new items
    const newItems = grid.value?.querySelectorAll('.grid-item:not(.loaded)');
    newItems?.forEach((el, index) => {
        setTimeout(() => {
            el.style.animationDelay = `${index * 0.1}s`;
        }, 50);
    });

    layoutMasonry();
};

const hasMore = computed(() => currentIndex < images.length);

onMounted(async () => {
    if (process.client) {
        const firstBatch = images.slice(0, batchSize);
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
        width: 350px;
        
        @media (max-width: 1200px) {
            width: calc(50% - 8px);
        }
        
        @media (max-width: 768px) {
            width: calc(50% - 8px);
        }
        
        @media (max-width: 480px) {
            width: 100%;
        }
    }

    .grid-item {
        width: 350px;
        margin-bottom: 16px;
        border-radius: 12px;
        cursor: pointer;
        background-color: #fff;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        opacity: 0;
        transform: translateY(30px) scale(0.95);
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        
        @media (max-width: 1200px) {
            width: calc(50% - 8px);
        }
        
        @media (max-width: 768px) {
            width: calc(50% - 8px);
        }
        
        @media (max-width: 480px) {
            width: 100%;
        }

        &.visible {
            opacity: 1;
            transform: translateY(0) scale(1);
        }

        &:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .media-container {
            position: relative;
            width: 100%;
            overflow: hidden;
            background: #f5f5f5;
        }

        .media {
            width: 100%;
            height: auto;
            display: block;
            object-fit: cover;
            transition: transform 0.3s ease;
            
            &.image {
                aspect-ratio: 4/5;
            }
            
            &.video {
                aspect-ratio: 4/5;
            }
        }

        .caption-container {
            padding: 1rem;
            background: #fff;
        }

        .caption {
            margin: 0;
            font-size: 0.9rem;
            color: #333;
            font-weight: 500;
            line-height: 1.4;
            text-align: center;
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

    // Staggered animation for grid items
    .grid-item {
        &:nth-child(1) { animation-delay: 0.1s; }
        &:nth-child(2) { animation-delay: 0.2s; }
        &:nth-child(3) { animation-delay: 0.3s; }
        &:nth-child(4) { animation-delay: 0.4s; }
        &:nth-child(5) { animation-delay: 0.5s; }
        &:nth-child(6) { animation-delay: 0.6s; }
    }
}
</style>