// src/services/syncService.ts
import { API_BASE_URL } from './api';
import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';

const DEVICE_ID_KEY = "device_id";

async function generateDeviceId(): Promise<string> {
  const randomString = `${Math.random()}-${Date.now()}`;
  return await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, randomString);
}

export async function getDeviceId(): Promise<string> {
  let stored = await SecureStore.getItemAsync(DEVICE_ID_KEY);
  if (!stored) {
    stored = await generateDeviceId();
    await SecureStore.setItemAsync(DEVICE_ID_KEY, stored);
  }
  return stored;
}

export async function initializeServerDictionaries(): Promise<void> {
  const deviceId = await getDeviceId();

  const res = await fetch(`${API_BASE_URL}/dictionaries/init`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ device_id: deviceId }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error("Failed to initialize server dictionaries: " + error);
  }
}

export const uploadDictionaryState = async (dictionaries: string[], order: string[]) => {
  const deviceId = await getDeviceId();

  const res = await fetch(`${API_BASE_URL}/sync/dictionaries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      device_id: deviceId,
      dictionaries,
      order,
    }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error("Failed to sync dictionary state: " + error);
  }

  return await res.json();
};

export const fetchDictionaryState = async () => {
  const deviceId = await getDeviceId();

  const res = await fetch(`${API_BASE_URL}/sync/dictionaries?device_id=${deviceId}`);
  if (!res.ok) {
    const error = await res.text();
    throw new Error("Failed to fetch dictionary state: " + error);
  }

  return await res.json();
};
