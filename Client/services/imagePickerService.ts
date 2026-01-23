import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import { Image, Alert } from 'react-native';

export const pickImage = async (
  setImage: (uri: string | null) => void,
  setLoading: (loading: boolean) => void,
  setError: (error: string | null) => void
): Promise<void> => {
  setLoading(true);
  setError(null);

  try {
    const result = await ImagePicker.launchCameraAsync({
      base64: true,
      quality: 1,
      allowsEditing: false,
    });

    if (!result.canceled) {
      const uri = result.assets[0].uri;
      const fileInfo = await FileSystem.getInfoAsync(uri);
      if (!fileInfo.exists) throw new Error("File does not exist.");

      const { width, height } = await new Promise<{ width: number; height: number }>((resolve, reject) => {
        Image.getSize(uri, (w, h) => resolve({ width: w, height: h }), reject);
      });

      console.log(`Image resolution: ${width} x ${height}`);
      console.log(`Image file size: ${fileInfo.size ?? 'unknown'} bytes`);

      const aspectRatio = width / height;
      if (aspectRatio < 1 / 3 || aspectRatio > 3) {
        Alert.alert("Invalid Aspect Ratio", "Image aspect ratio must be between 1:3 and 3:1.");
        return;
      }



      setImage(uri);
    }
  } catch (error) {
    console.error("Error picking image:", error);
    Alert.alert("Error", (error as Error).message || "Failed to capture image");
  } finally {
    setLoading(false);
  }
};

export const pickImageFromGallery = async (
  setImage: (uri: string | null) => void,
  setLoading: (loading: boolean) => void,
  setError: (error: string | null) => void
): Promise<void> => {
  setLoading(true);
  setError(null);

  try {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false,
      quality: 1,
      base64: true,
    });

    if (!result.canceled) {
      const uri = result.assets[0].uri;
      const fileInfo = await FileSystem.getInfoAsync(uri);
      if (!fileInfo.exists) throw new Error("File does not exist.");

      const { width, height } = await new Promise<{ width: number; height: number }>((resolve, reject) => {
        Image.getSize(uri, (w, h) => resolve({ width: w, height: h }), reject);
      });

      console.log(`Image resolution: ${width} x ${height}`);
      console.log(`Image file size: ${fileInfo.size ?? 'unknown'} bytes`);

      const aspectRatio = width / height;
      if (aspectRatio < 1 / 3 || aspectRatio > 3) {
        Alert.alert("Invalid Aspect Ratio", "Image aspect ratio must be between 1:3 and 3:1.");
        return;
      }

      if (fileInfo.size && fileInfo.size > 4 * 1024 * 1024) {
        Alert.alert("File Too Large", "Image exceeds 4MB limit.");
        return;
      }

      setImage(uri);
    }
  } catch (error) {
    console.error("Error picking image from gallery:", error);
    Alert.alert("Error", (error as Error).message || "Failed to select image from gallery");
  } finally {
    setLoading(false);
  }
};
