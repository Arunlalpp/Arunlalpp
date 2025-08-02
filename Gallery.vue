<template>
    <div class="gallery-wrapper">
        <ClientOnly>
            <div ref="grid" class="gallery-grid">
                <div class="grid-sizer"></div>
                <div v-for="(item, index) in visibleImages" :key="item.id + '-' + index" class="gallery-item" :class="[
                    { 'is-loading': !item.loaded, 'is-loaded': item.loaded },
                    item.sizeType ? `size-${item.sizeType}` : '',
                    `animate-${item.animationIndex}`
                ]" :style="{
                    '--animation-delay': `${item.delay || 0}s`
                }" @click="openModal(item)">
                    <div class="media-container">
                        <template v-if="item.video">
                            <video :src="item.video" autoplay muted loop playsinline class="media video"
                                @loadeddata="handleMediaLoad(item)" />
                        </template>
                        <template v-else>
                            <img :src="item.image" :alt="item.title" class="media image"
                                @load="handleMediaLoad(item)" />
                        </template>
                        
                        <!-- Loading overlay -->
                        <div v-if="!item.loaded" class="media-loading">
                            <div class="loading-shimmer"></div>
                        </div>
                    </div>

                    <div class="item-info">
                        <p class="item-description">{{ item.description }}</p>
                    </div>
                </div>
            </div>
        </ClientOnly>
        
        <div class="load-more-container" v-if="hasMore && !isLoading">
            <button class="load-more-btn" @click="loadMore">
                <span>Load More</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M7 13L12 8L17 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round" />
                </svg>
            </button>
        </div>
        
        <div class="loading-container" v-if="isLoading">
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Loading more moments...</p>
            </div>
        </div>

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
const batchSize = 8;
let currentIndex = 0;
let Masonry = null;
const isLoading = ref(false);
const route = useRoute();
const isInitialized = ref(false);
let animationCounter = 0;

const openModal = (item) => {
    selected.value = item;
};

const getRandomHeight = (min = 200, max = 400) => {
    if (min > max) [min, max] = [max, min];
    return Math.floor(Math.random() * (max - min + 1)) + min;
};

const loadMasonry = async () => {
    if (!grid.value) return;

    try {
        const MasonryModule = await import('masonry-layout');
        Masonry = MasonryModule.default;

        await nextTick();

        if (masonryInstance.value) {
            masonryInstance.value.destroy();
            masonryInstance.value = null;
        }

        masonryInstance.value = new Masonry(grid.value, {
            itemSelector: '.gallery-item',
            columnWidth: '.grid-sizer',
            gutter: 10,
            fitWidth: true,
            transitionDuration: '0.4s',
        });

        // Initial layout
        setTimeout(() => {
            if (masonryInstance.value) {
                masonryInstance.value.layout();
            }
        }, 100);

    } catch (error) {
        console.error('Error loading Masonry:', error);
    }
};

const handleMediaLoad = (item) => {
    item.loaded = true;
    
    // Relayout masonry when media loads
    nextTick(() => {
        if (masonryInstance.value) {
            masonryInstance.value.layout();
        }
    });
};

const loadMore = async () => {
    isLoading.value = true;

    // Create next batch with proper animation setup
    const nextBatch = images.slice(currentIndex, currentIndex + batchSize).map((item, idx) => ({
        ...item,
        height: getRandomHeight(200, 450),
        loaded: false,
        delay: (idx * 0.1).toFixed(2),
        animationIndex: animationCounter++
    }));

    // Add items to visible array
    visibleImages.value.push(...nextBatch);
    currentIndex += batchSize;

    await nextTick();

    // Let masonry handle the new items
    if (masonryInstance.value) {
        const newItems = grid.value.querySelectorAll('.gallery-item:not(.masonry-positioned)');
        newItems.forEach(item => item.classList.add('masonry-positioned'));
        
        if (newItems.length > 0) {
            masonryInstance.value.appended([...newItems]);
            setTimeout(() => {
                masonryInstance.value?.layout();
            }, 50);
        }
    }

    setTimeout(() => {
        isLoading.value = false;
    }, 500);
};

const hasMore = computed(() => currentIndex < images.length);

const initializeGallery = async () => {
    // Reset state
    visibleImages.value = [];
    currentIndex = 0;
    isInitialized.value = false;
    animationCounter = 0;

    // Initialize with first batch
    visibleImages.value = images.slice(0, batchSize).map((item, index) => ({
        ...item,
        height: getRandomHeight(),
        loaded: false,
        delay: (index * 0.1).toFixed(2),
        animationIndex: animationCounter++
    }));

    currentIndex = batchSize;

    await nextTick();
    await loadMasonry();

    isInitialized.value = true;
};

onMounted(async () => {
    await initializeGallery();

    // Handle window resize
    const handleResize = () => {
        if (masonryInstance.value) {
            masonryInstance.value.layout();
        }
    };

    window.addEventListener('resize', handleResize);

    onUnmounted(() => {
        window.removeEventListener('resize', handleResize);
        if (masonryInstance.value) {
            masonryInstance.value.destroy();
        }
    });
});

// Handle route changes
watch(() => route.path, async (newPath, oldPath) => {
    if (newPath !== oldPath) {
        setTimeout(async () => {
            await initializeGallery();
        }, 100);
    }
}, { immediate: false });

onActivated(async () => {
    if (!isInitialized.value) {
        await initializeGallery();
    }
});
</script>

<style scoped>
.gallery-wrapper {
    .gallery-grid {
        margin: 0 auto;
        position: relative;
    }

    .grid-sizer,
    .gallery-item {
        width: calc(25% - 7.5px);
        margin-bottom: 20px;

        @media (max-width: 1200px) {
            width: calc(33.333% - 6.67px);
        }

        @media (max-width: 768px) {
            width: calc(50% - 5px);
        }

        @media (max-width: 480px) {
            width: calc(50% - 5px);
        }
    }

    .gallery-item {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        background: #fff;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        
        /* Initial state - hidden */
        opacity: 0;
        transform: translateY(20px) scale(0.95);
        
        /* Animation trigger */
        animation: masonrySlideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        animation-delay: var(--animation-delay, 0s);

        &:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            z-index: 10;

            .media {
                transform: scale(1.05);
            }
        }

        .media-container {
            position: relative;
            width: 100%;
            height: 250px;
            overflow: hidden;
            background: #f8f9fa;

            .media {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: block;
                opacity: 0;
            }

            .media-loading {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: #f8f9fa;
                display: flex;
                align-items: center;
                justify-content: center;

                .loading-shimmer {
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(
                        90deg,
                        #f8f9fa,
                        #e9ecef,
                        #f8f9fa
                    );
                    background-size: 200% 100%;
                    animation: shimmer 1.5s infinite;
                }
            }
        }

        &.is-loaded {
            .media {
                opacity: 1;
                animation: mediaFadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }
            
            .media-loading {
                opacity: 0;
                pointer-events: none;
            }
        }

        .item-info {
            padding: 0.8rem;
            background: #fff;

            .item-description {
                font-size: 13px;
                color: #666;
                line-height: 1.4;
                margin: 0;
                text-align: center;
                opacity: 0;
                animation: textSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.2s forwards;
            }
        }
    }

    .load-more-container {
        text-align: center;
        margin-top: 3rem;

        .load-more-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #3565ce 0%, #5b7cfa 100%);
            color: #fff;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(53, 101, 206, 0.3);

            &:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 30px rgba(53, 101, 206, 0.4);
            }

            &:active {
                transform: translateY(0);
            }
        }
    }

    .loading-container {
        text-align: center;
        margin: 3rem 0;

        .loading-spinner {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;

            .spinner {
                width: 40px;
                height: 40px;
                border: 3px solid #e1e5e9;
                border-top: 3px solid #3565ce;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            p {
                color: #666;
                font-size: 1rem;
            }
        }
    }
}

/* Keyframe Animations */
@keyframes masonrySlideIn {
    0% {
        opacity: 0;
        transform: translateY(20px) scale(0.95);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes mediaFadeIn {
    0% {
        opacity: 0;
        transform: scale(1.05);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes textSlideIn {
    0% {
        opacity: 0;
        transform: translateY(10px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes shimmer {
    0% {
        background-position: -200% 0;
    }
    100% {
        background-position: 200% 0;
    }
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    .gallery-item {
        animation-duration: 0.2s;
    }
    
    .gallery-item:hover {
        transform: translateY(-2px);
    }
    
    .loading-shimmer {
        animation: none;
    }
}
</style>