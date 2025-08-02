<template>
    <div class="gallery-wrapper">
        <ClientOnly>
            <div ref="grid" class="gallery-grid">
                <div class="grid-sizer"></div>
                <div v-for="(item, index) in visibleImages" :key="item.id + '-' + index" class="gallery-item" :class="[
                    { 'is-loading': !item.loaded, 'is-loaded': item.loaded },
                    item.sizeType ? `size-${item.sizeType}` : ''
                ]" :style="{
                    '--animation-delay': `${item.delay || 0}s`,
                    '--item-height': item.height ? `${item.height}px` : 'auto'
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
            transitionDuration: '0.6s',
            stagger: 30,
            resize: true,
        });

        // Add entrance animations for existing items
        const items = grid.value.querySelectorAll('.gallery-item');
        items.forEach((item, index) => {
            item.style.setProperty('--animation-delay', `${index * 0.1}s`);
        });

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
    
    // Add a slight delay for smoother animation
    setTimeout(() => {
        if (masonryInstance.value) {
            masonryInstance.value.layout();
        }
    }, 50);
};

const loadMore = async () => {
    isLoading.value = true;

    // Create next batch with staggered animation delays
    const nextBatch = images.slice(currentIndex, currentIndex + batchSize).map((item, idx) => ({
        ...item,
        height: getRandomHeight(200, 450),
        loaded: false,
        delay: (idx * 0.15).toFixed(2), // Increased stagger time for smoother effect
    }));

    // Add items to visible array
    visibleImages.value.push(...nextBatch);
    currentIndex += batchSize;

    await nextTick();

    // Get newly added items and apply entrance animations
    const allItems = grid.value.querySelectorAll('.gallery-item');
    const newItems = Array.from(allItems).slice(-nextBatch.length);
    
    // Apply masonry to new items
    if (masonryInstance.value && newItems.length > 0) {
        // Temporarily hide new items for smoother entrance
        newItems.forEach((el, idx) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px) scale(0.9)';
        });

        masonryInstance.value.appended(newItems);
        
        // Layout and then animate in
        setTimeout(() => {
            masonryInstance.value?.layout();
            
            // Animate new items in with stagger
            newItems.forEach((el, idx) => {
                setTimeout(() => {
                    el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0) scale(1)';
                }, idx * 100); // 100ms stagger between items
            });
        }, 50);
    }

    setTimeout(() => {
        isLoading.value = false;
    }, 800); // Increased to match animation duration
};

const hasMore = computed(() => currentIndex < images.length);

const initializeGallery = async () => {
    // Reset state
    visibleImages.value = [];
    currentIndex = 0;
    isInitialized.value = false;

    // Initialize with first batch
    visibleImages.value = images.slice(0, batchSize).map((item, index) => ({
        ...item,
        height: getRandomHeight(),
        loaded: false,
        delay: (index * 0.1).toFixed(2) // Initial stagger
    }));

    currentIndex = batchSize;

    await nextTick();
    await loadMasonry();

    isInitialized.value = true;
};

onMounted(async () => {
    await initializeGallery();

    // Handle window resize with debounce
    let resizeTimeout;
    const handleResize = () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (masonryInstance.value) {
                masonryInstance.value.layout();
            }
        }, 100);
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    onUnmounted(() => {
        window.removeEventListener('resize', handleResize);
        if (masonryInstance.value) {
            masonryInstance.value.destroy();
        }
    });
});

// Handle route changes to reinitialize gallery
watch(() => route.path, async (newPath, oldPath) => {
    if (newPath !== oldPath) {
        setTimeout(async () => {
            await initializeGallery();
        }, 100);
    }
}, { immediate: false });

// Force reinitialize when component becomes visible
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
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(0);
        opacity: 0;
        animation: masonryFadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        animation-delay: var(--animation-delay, 0s);

        &.is-loading {
            .media-container .media {
                opacity: 0;
            }
        }

        &.is-loaded {
            .media-container .media {
                opacity: 1;
                animation: mediaFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }
            
            .media-loading {
                opacity: 0;
                pointer-events: none;
            }
        }

        &:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            z-index: 10;

            .media {
                transform: scale(1.05);
            }
        }

        .media-container {
            position: relative;
            width: 100%;
            height: var(--item-height, 250px);
            overflow: hidden;
            background: #f8f9fa;

            .media {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                display: block;
                opacity: 0;
            }

            .media-loading {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #f8f9fa;
                transition: opacity 0.3s ease;

                .loading-shimmer {
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(
                        90deg,
                        transparent,
                        rgba(255, 255, 255, 0.4),
                        transparent
                    );
                    background-size: 200% 100%;
                    animation: shimmer 1.5s infinite;
                }
            }
        }

        .item-info {
            padding: 0.8rem;
            background: #fff;
            transform: translateY(0);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);

            .item-description {
                font-size: 13px;
                color: #666;
                line-height: 1.4;
                margin: 0;
                text-align: center;
                opacity: 0;
                animation: textFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s forwards;
            }
        }
    }

    .load-more-container {
        text-align: center;
        margin-top: 3rem;
        opacity: 0;
        animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.3s forwards;

        .load-more-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1.2rem 2.5rem;
            background: linear-gradient(135deg, #3565ce 0%, #5b7cfa 100%);
            color: #fff;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 20px rgba(53, 101, 206, 0.3);
            position: relative;
            overflow: hidden;

            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(255, 255, 255, 0.2),
                    transparent
                );
                transition: left 0.5s ease;
            }

            &:hover {
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 8px 30px rgba(53, 101, 206, 0.4);

                &::before {
                    left: 100%;
                }
            }

            &:active {
                transform: translateY(-1px) scale(1.02);
            }
        }
    }

    .loading-container {
        text-align: center;
        margin: 3rem 0;
        opacity: 0;
        animation: fadeIn 0.3s ease forwards;

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
                animation: pulse 2s ease-in-out infinite;
            }
        }
    }
}

/* Keyframe Animations */
@keyframes masonryFadeIn {
    0% {
        opacity: 0;
        transform: translateY(30px) scale(0.9);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes mediaFadeIn {
    0% {
        opacity: 0;
        transform: scale(1.1);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes textFadeIn {
    0% {
        opacity: 0;
        transform: translateY(10px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInUp {
    0% {
        opacity: 0;
        transform: translateY(20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    0% {
        opacity: 0;
    }
    100% {
        opacity: 1;
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

@keyframes pulse {
    0%, 100% {
        opacity: 0.6;
    }
    50% {
        opacity: 1;
    }
}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
    .gallery-item {
        animation-duration: 0.3s;
    }
    
    .gallery-item:hover {
        transform: translateY(-2px);
    }
    
    .media {
        transition-duration: 0.2s;
    }
    
    .loading-shimmer {
        animation: none;
    }
}
</style>