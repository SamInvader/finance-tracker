import { api, unwrap } from "./api";
import type { Preferences, User } from "../types";

export const authService = {
  register: (payload: object) => unwrap<{ token: string; user: User; preferences: Preferences }>(api.post("/api/auth/register", payload)),
  login: (payload: object) => unwrap<{ token: string; user: User; preferences: Preferences }>(api.post("/api/auth/login", payload)),
  me: () => unwrap<{ user: User; preferences: Preferences }>(api.get("/api/auth/me")),
  updateMe: (payload: object) => unwrap<{ user: User; preferences: Preferences }>(api.patch("/api/auth/me", payload)),
  changePassword: (payload: object) => api.post("/api/auth/change-password", payload),
  logout: () => api.post("/api/auth/logout"),
};
