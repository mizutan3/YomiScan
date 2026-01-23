import { Animated } from 'react-native';

export const toggleSidebar = (
  isSidebarVisible: boolean,
  setIsSidebarVisible: (visible: boolean) => void,
  sidebarAnimation: Animated.Value
): void => {
  Animated.timing(sidebarAnimation, {
    toValue: isSidebarVisible ? -300 : 0,
    duration: 300,
    useNativeDriver: true,
  }).start();
  setIsSidebarVisible(!isSidebarVisible);
};

export const closeSidebar = (
  setIsSidebarVisible: (visible: boolean) => void,
  sidebarAnimation: Animated.Value
): void => {
  Animated.timing(sidebarAnimation, {
    toValue: -300,
    duration: 300,
    useNativeDriver: true,
  }).start();
  setIsSidebarVisible(false);
};