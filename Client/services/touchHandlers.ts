// src/services/touchHandlers.ts
import { Dimensions } from 'react-native';
import { processCroppedImage } from './ocrServices';
import { Image } from 'react-native';

const { width: screenWidth, height: screenHeight } = Dimensions.get("window");

export const handleImageTouchStart = (
  e: any,
  image: string | null,
  setCropStart: (point: { x: number; y: number }) => void,
  setCropEnd: (point: { x: number; y: number }) => void,
  setCropping: (cropping: boolean) => void
) => {
  if (!image) return;
  const { locationX, locationY } = e.nativeEvent;
  setCropStart({ x: locationX, y: locationY });
  setCropEnd({ x: locationX, y: locationY });
  setCropping(true);
};

export const handleImageTouchMove = (
  e: any,
  cropping: boolean,
  image: string | null,
  setCropEnd: (point: { x: number; y: number }) => void
) => {
  if (!cropping || !image) return;
  
  const { locationX, locationY } = e.nativeEvent;
  
  // Get the dimensions of the image container
  const containerWidth = screenWidth * 0.9;
  const containerHeight = screenHeight * 0.4;
  
  // Constrain the coordinates to stay within the image container
  const constrainedX = Math.max(0, Math.min(locationX, containerWidth));
  const constrainedY = Math.max(0, Math.min(locationY, containerHeight));
  
  setCropEnd({ 
    x: constrainedX,
    y: constrainedY 
  });
};

export const handleImageTouchEnd = async (
  cropping: boolean,
  image: string | null,
  cropStart: { x: number; y: number },
  cropEnd: { x: number; y: number },
  setCropping: (cropping: boolean) => void,
  setCropStart: (point: { x: number; y: number }) => void,
  setCropEnd: (point: { x: number; y: number }) => void,
  isVertical: boolean,
  isFastMode: boolean,
  setText: (text: string) => void,
  setWords: (words: string[]) => void,
  setLoading: (loading: boolean) => void,
  setError: (error: string | null) => void
) => {
  if (!cropping || !image) return;
  setCropping(false);
  
  try {
    // Get the actual image dimensions
    const { width: imgWidth, height: imgHeight } = await new Promise<{width: number, height: number}>((resolve, reject) => {
      Image.getSize(image, (width, height) => {
        resolve({width, height});
      }, reject);
    });

    // Calculate the displayed image dimensions and scaling factors
    const containerWidth = screenWidth * 0.9;
    const containerHeight = screenHeight * 0.4;
    
    // Calculate the actual image aspect ratio
    const imgAspect = imgWidth / imgHeight;
    const containerAspect = containerWidth / containerHeight;
    
    let scaleX, scaleY;
    let offsetX = 0, offsetY = 0;
    
    // Calculate scaling based on how the image is fitted in the container
    if (imgAspect > containerAspect) {
      // Image is wider than container - fit to width
      scaleX = scaleY = imgWidth / containerWidth;
      offsetY = (containerHeight - (imgHeight / scaleX)) / 2;
    } else {
      // Image is taller than container - fit to height
      scaleX = scaleY = imgHeight / containerHeight;
      offsetX = (containerWidth - (imgWidth / scaleY)) / 2;
    }
    
    // Adjust crop coordinates to account for any offset and scaling
    const adjustedStartX = (Math.max(0, Math.min(cropStart.x, containerWidth)) - offsetX) * scaleX;
    const adjustedStartY = (Math.max(0, Math.min(cropStart.y, containerHeight)) - offsetY) * scaleY;
    const adjustedEndX = (Math.max(0, Math.min(cropEnd.x, containerWidth)) - offsetX) * scaleX;
    const adjustedEndY = (Math.max(0, Math.min(cropEnd.y, containerHeight)) - offsetY) * scaleY;
    
    // Calculate relative positions within the original image
    const left = Math.max(0, Math.min(adjustedStartX, adjustedEndX)) / imgWidth;
    const top = Math.max(0, Math.min(adjustedStartY, adjustedEndY)) / imgHeight;
    const width = Math.min(1, Math.abs(adjustedEndX - adjustedStartX) / imgWidth);
    const height = Math.min(1, Math.abs(adjustedEndY - adjustedStartY) / imgHeight);
    
    if (width > 0.05 || height > 0.05) { // Перевірка чи площа виділенної області більша ніж 5% від розміру зображення
      await processCroppedImage(
        image,
        left,
        top,
        width,
        height,
        isVertical,
        isFastMode,
        setText,
        setWords,
        setLoading,
        setError
      );
    }
  } catch (error) { // Помилка якщо площа менша ніж 5% зображення
    console.error("Error calculating crop coordinates:", error); 
    setError("Failed to process crop selection");
  } finally {
    // Reset crop markers
    setCropStart({ x: 0, y: 0 });
    setCropEnd({ x: 0, y: 0 });
  }
};