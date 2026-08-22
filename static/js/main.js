document.addEventListener('DOMContentLoaded', function () {
  const flashItems = document.querySelectorAll('.flash');
  flashItems.forEach((item) => {
    setTimeout(() => {
      item.style.opacity = '0';
      item.style.transition = 'opacity 0.5s ease';
    }, 3000);
  });

  const STORAGE_KEY = 'finance_tracker_local_profiles';
  const ACCOUNT_DATA_KEY = 'finance_tracker_account_data';
  const THEME_KEY = 'finance_tracker_theme';
  const ACTIVE_ACCOUNT_KEY = 'finance_tracker_active_account';
  const ACTIVE_PROFILE_STATE_KEY = 'finance_tracker_active_profile_state';
  const themeSelect = document.getElementById('themeSelect');
  const accountSelect = document.getElementById('accountSelect');
  const newAccountBtn = document.getElementById('newAccountBtn');
  const renameAccountBtn = document.getElementById('renameAccountBtn');
  const resetLocalDataBtn = document.getElementById('resetLocalDataBtn');

  const safeParse = (value, fallback) => {
    try {
      return JSON.parse(value) ?? fallback;
    } catch {
      return fallback;
    }
  };

  const fallbackProfiles = [{ id: 'default', name: 'Default profile', createdAt: Date.now(), passwordHash: '' }];

  const hexToBytes = (hex) => {
    const bytes = [];
    for (let i = 0; i < hex.length; i += 2) {
      bytes.push(parseInt(hex.slice(i, i + 2), 16));
    }
    return new Uint8Array(bytes);
  };

  const bytesToHex = (bytes) => {
    return Array.from(bytes).map((byte) => byte.toString(16).padStart(2, '0')).join('');
  };

  const generateSalt = () => {
    if (window.crypto && window.crypto.getRandomValues) {
      return window.crypto.getRandomValues(new Uint8Array(16));
    }
    return new Uint8Array(16).map(() => Math.floor(Math.random() * 256));
  };

  const hashPassword = async (password, saltBytes = null) => {
    const encoder = new TextEncoder();
    const salt = saltBytes || generateSalt();
    const passwordKey = await window.crypto.subtle.importKey(
      'raw',
      encoder.encode(password),
      'PBKDF2',
      false,
      ['deriveBits']
    );
    const derivedBits = await window.crypto.subtle.deriveBits(
      {
        name: 'PBKDF2',
        salt,
        iterations: 120000,
        hash: 'SHA-256',
      },
      passwordKey,
      256
    );
    return `${bytesToHex(salt)}:${bytesToHex(new Uint8Array(derivedBits))}`;
  };

  const verifyPasswordHash = async (password, storedHash) => {
    if (!storedHash || !storedHash.includes(':')) return false;
    const [saltHex, hashHex] = storedHash.split(':');
    if (!saltHex || !hashHex) return false;
    const computedHash = await hashPassword(password, hexToBytes(saltHex));
    return computedHash === storedHash;
  };

  const openIndexedDB = () => {
    return new Promise((resolve, reject) => {
      if (!('indexedDB' in window)) {
        reject(new Error('IndexedDB unavailable'));
        return;
      }

      const request = indexedDB.open('finance_tracker_db', 1);
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('profiles')) {
          db.createObjectStore('profiles', { keyPath: 'id' });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  };

  const saveProfilesToLocal = (profiles) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profiles));
    openIndexedDB().then((db) => {
      const tx = db.transaction('profiles', 'readwrite');
      const store = tx.objectStore('profiles');
      profiles.forEach((profile) => store.put(profile));
    }).catch(() => {});
  };

  const getProfiles = () => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return safeParse(raw, fallbackProfiles);
    }

    const defaultProfile = { id: 'default', name: 'Default profile', createdAt: Date.now(), passwordHash: '' };
    saveProfilesToLocal([defaultProfile]);
    return [defaultProfile];
  };

  const getActiveProfile = () => {
    const profiles = getProfiles();
    const activeId = localStorage.getItem(ACTIVE_ACCOUNT_KEY) || profiles[0]?.id;
    return profiles.find((profile) => profile.id === activeId) || profiles[0];
  };

  const getAccountData = (profileId) => {
    const raw = localStorage.getItem(`${ACCOUNT_DATA_KEY}:${profileId}`);
    if (!raw) {
      return { transactions: [], budgets: {}, goals: [] };
    }
    return safeParse(raw, { transactions: [], budgets: {}, goals: [] });
  };

  const saveAccountData = (profileId, data) => {
    localStorage.setItem(`${ACCOUNT_DATA_KEY}:${profileId}`, JSON.stringify(data));
  };

  const applyTheme = (themeName) => {
    const resolvedTheme = themeName || 'professional-blue';
    document.body.setAttribute('data-theme', resolvedTheme);
    if (themeSelect) {
      themeSelect.value = resolvedTheme;
    }
    localStorage.setItem(THEME_KEY, resolvedTheme);
  };

  const buildAccountOptions = () => {
    const profiles = getProfiles();
    if (!accountSelect) return;
    accountSelect.innerHTML = '';
    profiles.forEach((profile) => {
      const option = document.createElement('option');
      option.value = profile.id;
      option.textContent = profile.name;
      accountSelect.appendChild(option);
    });

    const activeProfileId = localStorage.getItem(ACTIVE_ACCOUNT_KEY) || profiles[0]?.id;
    const selectedId = profiles.some((p) => p.id === activeProfileId) ? activeProfileId : profiles[0]?.id;
    if (selectedId) {
      accountSelect.value = selectedId;
      localStorage.setItem(ACTIVE_ACCOUNT_KEY, selectedId);
    }
  };

  const ensureProfileName = () => {
    const activeProfile = getActiveProfile();
    if (activeProfile) {
      document.title = `${activeProfile.name} | Finance Tracker`;
    }
  };

  const ensureFirstRunHome = () => {
    const profiles = getProfiles();
    const path = window.location.pathname;
    const isHomePath = path === '/home' || path === '/index.html' || path === '/';
    if (!profiles.length && !isHomePath) {
      window.location.href = '/home';
    }
  };

  const createAccount = async (name, password) => {
    const profiles = getProfiles();
    const trimmedName = name.trim();
    if (!trimmedName) return false;
    if (!password || !password.trim()) return false;
    const duplicate = profiles.some((profile) => profile.name.toLowerCase() === trimmedName.toLowerCase());
    if (duplicate) {
      alert('An account with that name already exists.');
      return false;
    }

    const newProfile = {
      id: `profile-${Date.now()}`,
      name: trimmedName,
      createdAt: Date.now(),
      passwordHash: await hashPassword(password.trim()),
    };

    profiles.push(newProfile);
    saveProfilesToLocal(profiles);
    localStorage.setItem(ACTIVE_ACCOUNT_KEY, newProfile.id);
    buildAccountOptions();
    ensureProfileName();
    return true;
  };

  if (themeSelect) {
    themeSelect.addEventListener('change', (event) => {
      applyTheme(event.target.value);
    });
  }

  if (newAccountBtn) {
    newAccountBtn.addEventListener('click', async () => {
      const name = window.prompt('Name for the new local account:', `Account ${Date.now()}`);
      if (!name || !name.trim()) return;
      const password = window.prompt('Set a password for this account:', '');
      if (password === null || !password.trim()) {
        alert('A password is required for each account.');
        return;
      }
      const created = await createAccount(name, password);
      if (created) {
        const activeData = getAccountData(localStorage.getItem(ACTIVE_ACCOUNT_KEY));
        saveAccountData(localStorage.getItem(ACTIVE_ACCOUNT_KEY), activeData);
      }
    });
  }

  if (renameAccountBtn) {
    renameAccountBtn.addEventListener('click', () => {
      const activeProfile = getActiveProfile();
      if (!activeProfile) return;
      const renamed = window.prompt('Rename this account:', activeProfile.name);
      if (!renamed || !renamed.trim()) return;
      const profiles = getProfiles();
      const nextName = renamed.trim();
      const profileIndex = profiles.findIndex((profile) => profile.id === activeProfile.id);
      if (profileIndex >= 0) {
        profiles[profileIndex].name = nextName;
        saveProfilesToLocal(profiles);
        buildAccountOptions();
        ensureProfileName();
      }
    });
  }

  if (resetLocalDataBtn) {
    resetLocalDataBtn.addEventListener('click', () => {
      const confirmed = window.confirm('Reset all local accounts, passwords, and saved finance data for this device?');
      if (!confirmed) return;

      localStorage.clear();
      if ('indexedDB' in window) {
        const databases = ['finance_tracker_db'];
        databases.forEach((databaseName) => {
          const request = indexedDB.deleteDatabase(databaseName);
          request.onerror = () => {};
          request.onsuccess = () => {};
        });
      }
      window.location.href = '/home';
    });
  }

  if (accountSelect) {
    accountSelect.addEventListener('change', (event) => {
      localStorage.setItem(ACTIVE_ACCOUNT_KEY, event.target.value);
      ensureProfileName();
    });
  }

  const persistLocalProfile = () => {
    const activeProfile = getActiveProfile();
    if (!activeProfile) return;
    const profileState = {
      id: activeProfile.id,
      name: activeProfile.name,
      lastUpdated: Date.now(),
      theme: localStorage.getItem(THEME_KEY) || 'professional-blue',
    };
    localStorage.setItem(ACTIVE_PROFILE_STATE_KEY, JSON.stringify(profileState));
  };

  ensureFirstRunHome();
  applyTheme(localStorage.getItem(THEME_KEY) || 'professional-blue');
  buildAccountOptions();
  ensureProfileName();

  document.addEventListener('visibilitychange', persistLocalProfile);
  window.addEventListener('beforeunload', persistLocalProfile);
  setInterval(persistLocalProfile, 10000);
});
