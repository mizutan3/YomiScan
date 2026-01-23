// src/components/OCRScanner.tsx
import React from 'react';
import { 
  View, 
  Image, 
  ActivityIndicator, 
  Text, 
  ScrollView,
  TouchableOpacity,
  Button
} from 'react-native';
import styles from '../styles/styles';

interface OCRScannerProps {
  image: string | null;
  loading: boolean;
  error: string | null;
  text: string;
  words: string[];
  cropStart: { x: number; y: number };
  cropEnd: { x: number; y: number };
  cropping: boolean;
  handleImageTouchStart: (e: any) => void;
  handleImageTouchMove: (e: any) => void;
  handleImageTouchEnd: () => void;
  renderTextWithClickableWords: () => React.ReactNode;
  pickImage: () => void;
  pickImageFromGallery: () => void;
}

const OCRScanner: React.FC<OCRScannerProps> = ({
  image,
  loading,
  error,
  text,
  words,
  cropStart,
  cropEnd,
  cropping,
  handleImageTouchStart,
  handleImageTouchMove,
  handleImageTouchEnd,
  renderTextWithClickableWords,
  pickImage,
  pickImageFromGallery
}) => {
  return (
    <>
      {image && (
        <View
          style={styles.imageContainer}
          onTouchStart={handleImageTouchStart}
          onTouchMove={handleImageTouchMove}
          onTouchEnd={handleImageTouchEnd}
        >
          <Image
            source={{ uri: image }}
            style={styles.image}
            resizeMode="contain"
          />
          {cropping && (
            <View
              style={[
                styles.cropRectangle,
                {
                  left: Math.min(cropStart.x, cropEnd.x),
                  top: Math.min(cropStart.y, cropEnd.y),
                  width: Math.abs(cropEnd.x - cropStart.x),
                  height: Math.abs(cropEnd.y - cropStart.y),
                },
              ]}
            />
          )}
        </View>
      )}
      {loading && <ActivityIndicator size="large" color="#BB86FC" />}
      {error && <Text style={styles.errorText}>{error}</Text>}

      {image && (
        <>
          <Text style={styles.heading}>Detected Text:</Text>
          <ScrollView style={styles.textContainer}>
            <Text style={styles.text}>
              {renderTextWithClickableWords()}
            </Text>
          </ScrollView>
        </>
      )}
    </>
  );
};

export default OCRScanner;