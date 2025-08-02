<template>
    <div class="page-container">
        <header class="page-header">
            <h1>Footwear Gallery</h1>
            <p>A modern masonry-style gallery with smooth animations</p>
        </header>
        
        <Gallery />
    </div>
</template>

<script setup>
import Gallery from '~/components/Gallery.vue';

// Set page meta
useHead({
    title: 'Footwear Gallery - Test Page',
    meta: [
        { name: 'description', content: 'Modern footwear gallery with masonry layout and smooth animations' }
    ]
});
</script>

<style lang="scss" scoped>
.page-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
    text-align: center;
    padding: 3rem 1rem 1rem;
    
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #333;
        margin: 0 0 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        
        @media (max-width: 768px) {
            font-size: 2rem;
        }
    }
    
    p {
        font-size: 1.1rem;
        color: #666;
        margin: 0;
        max-width: 600px;
        margin: 0 auto;
    }
}
</style>