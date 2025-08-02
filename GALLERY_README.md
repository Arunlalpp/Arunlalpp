# Footwear Gallery - Implementation Guide

## Overview
This is a modern, responsive masonry-style gallery built with Nuxt 3 and Vue 3. The gallery features smooth animations, proper image alignment, and lazy loading functionality.

## Features Implemented

### ✅ Fixed Issues
1. **Image Width/Height Alignment**: Fixed misaligned images using consistent aspect ratios (4:5)
2. **Masonry Layout**: Properly configured masonry-layout with consistent gutters and responsive breakpoints
3. **Smooth Animations**: Implemented staggered loading animations with CSS transitions
4. **Responsive Design**: Gallery adapts to different screen sizes (desktop, tablet, mobile)
5. **Loading States**: Added proper loading indicators and states
6. **Media Handling**: Support for both images and videos

### 🎨 Visual Improvements
- Consistent 350px base width for grid items
- 16px gutters between items
- Smooth hover effects with transform and shadow
- Loading animations with fade-in and scale effects
- Professional gradient button styling
- Modal overlay for enlarged viewing

### 📱 Responsive Breakpoints
- **Desktop (1200px+)**: 350px fixed width items
- **Tablet (768px-1199px)**: 50% width items (2 columns)
- **Mobile (480px-767px)**: 50% width items (2 columns)
- **Small Mobile (< 480px)**: 100% width items (1 column)

## File Structure
```
components/
├── Gallery.vue          # Main gallery component
└── ImageModal.vue       # Modal for enlarged images

composables/
└── useGalleryData.js    # Sample data composable

pages/
├── index.vue            # Main gallery page
└── gallery-test.vue     # Test page

assets/scss/
├── main.scss           # Base styles
└── variables.scss      # SCSS variables
```

## How It Works

### 1. Gallery Component (`Gallery.vue`)
- Uses masonry-layout for dynamic grid positioning
- Implements lazy loading with proper media load handling
- Manages loading states and animations
- Handles responsive behavior automatically

### 2. Animation System
- Items start with `opacity: 0` and `transform: translateY(30px) scale(0.95)`
- On load, items transition to `opacity: 1` and `transform: translateY(0) scale(1)`
- Staggered delays for smooth batch loading
- Hover effects with subtle lift and shadow

### 3. Responsive Masonry
- Grid-sizer element defines column width
- Responsive CSS adjusts both grid-sizer and grid-item widths
- Masonry automatically recalculates layout on resize

### 4. Loading Strategy
- Batch loading (6 items per load)
- Images loaded lazily with `loading="lazy"`
- Proper load event handling for layout recalculation
- Loading states prevent multiple simultaneous loads

## Usage

### Basic Implementation
```vue
<template>
  <Gallery />
</template>

<script setup>
import Gallery from '~/components/Gallery.vue';
</script>
```

### Custom Data
Modify `composables/useGalleryData.js` to use your own image data:

```javascript
export const useGalleryData = () => {
  return [
    {
      id: 1,
      image: "your-image-url.jpg",
      title: "Your Image Title",
      alt: "Alt text for accessibility"
    },
    // Add more items...
  ];
};
```

## Running the Project

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

## Dependencies
- `nuxt`: ^4.0.2 - Vue.js framework
- `masonry-layout`: ^4.2.2 - Grid layout engine
- `sass`: ^1.89.2 - CSS preprocessor

## Browser Support
- Modern browsers with CSS Grid and Flexbox support
- Chrome 60+, Firefox 60+, Safari 12+, Edge 79+

## Performance Optimizations
- Lazy loading for images
- Batch loading to prevent overwhelming the browser
- Efficient masonry recalculation only when needed
- CSS transforms for smooth animations (GPU accelerated)
- Minimal re-renders with proper Vue reactivity

## Customization
You can easily customize:
- Grid item sizes by modifying `.grid-sizer` and `.grid-item` widths
- Animation timings in CSS transitions
- Batch size for loading more items
- Color scheme using SCSS variables
- Breakpoints for responsive behavior

The gallery is now fully functional with proper alignment, smooth animations, and responsive design! 🎉