import { createContext, useContext, useState, type ReactNode } from "react";
import type { User } from "../types";
import * as api from "../services/api";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  login: (employeeCode: string, password: string, staySignedIn: boolean) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function loadStoredUser(): User | null {
  const raw = localStorage.getItem("bp_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(loadStoredUser());

  async function login(employeeCode: string, password: string, staySignedIn: boolean) {
    const { access_token, user: loggedInUser } = await api.login(employeeCode, password, staySignedIn);
    localStorage.setItem("bp_token", access_token);
    localStorage.setItem("bp_user", JSON.stringify(loggedInUser));
    setUser(loggedInUser);
    return loggedInUser;
  }

  function logout() {
    localStorage.removeItem("bp_token");
    localStorage.removeItem("bp_user");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
