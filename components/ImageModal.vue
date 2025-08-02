<template>
    <div class="modal-overlay" @click="closeModal" @keydown.esc="closeModal">
        <div class="modal-container" @click.stop>
            <button class="close-button" @click="closeModal" aria-label="Close modal">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            
            <div class="modal-content">
                <div class="media-wrapper">
                    <template v-if="item.video">
                        <video 
                            :src="item.video" 
                            controls 
                            autoplay 
                            muted 
                            loop 
                            playsinline 
                            class="modal-media"
                        />
                    </template>
                    <template v-else>
                        <img 
                            :src="item.image" 
                            :alt="item.alt || item.title" 
                            class="modal-media"
                        />
                    </template>
                </div>
                
                <div class="modal-info">
                    <h3 class="modal-title">{{ item.title }}</h3>
                    <p v-if="item.alt" class="modal-description">{{ item.alt }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    item: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['close']);

const closeModal = () => {
    emit('close');
};

// Handle escape key
onMounted(() => {
    document.addEventListener('keydown', handleKeydown);
    document.body.style.overflow = 'hidden';
});

onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown);
    document.body.style.overflow = '';
});

const handleKeydown = (event) => {
    if (event.key === 'Escape') {
        closeModal();
    }
};
</script>

<style lang="scss" scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 2rem;
    backdrop-filter: blur(4px);
    animation: fadeIn 0.3s ease-out;
}

.modal-container {
    position: relative;
    max-width: 90vw;
    max-height: 90vh;
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    animation: slideIn 0.3s ease-out;
    
    @media (max-width: 768px) {
        max-width: 95vw;
        max-height: 95vh;
        margin: 1rem;
    }
}

.close-button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 10;
    transition: all 0.2s ease;
    
    &:hover {
        background: rgba(0, 0, 0, 0.9);
        transform: scale(1.1);
    }
}

.modal-content {
    display: flex;
    flex-direction: column;
    max-height: 90vh;
}

.media-wrapper {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;
    min-height: 300px;
}

.modal-media {
    max-width: 100%;
    max-height: 70vh;
    object-fit: contain;
    display: block;
    
    @media (max-width: 768px) {
        max-height: 60vh;
    }
}

.modal-info {
    padding: 1.5rem;
    background: #fff;
    border-top: 1px solid #e5e5e5;
}

.modal-title {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #333;
    line-height: 1.4;
}

.modal-description {
    margin: 0;
    font-size: 0.95rem;
    color: #666;
    line-height: 1.5;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(20px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
</style>