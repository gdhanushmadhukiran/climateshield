import { createContext, useContext, useMemo, useState, useEffect, type ReactNode } from "react";
import type { OperationalMode } from "@/types/climate";

interface OperationalModeContext {
  mode: OperationalMode;
  setMode: (mode: OperationalMode) => void;
  isDegraded: boolean;
}

const Ctx = createContext<OperationalModeContext | null>(null);

export function OperationalModeProvider({
  children,
  initialMode = "LIVE",
}: {
  children: ReactNode;
  initialMode?: OperationalMode;
}) {
  const [mode, setModeState] = useState<OperationalMode>(initialMode);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("climateshield_mode") as OperationalMode | null;
      if (saved === "LIVE" || saved === "DEMO" || saved === "DEGRADED") {
        setModeState(saved);
      }
    } catch {
      // Ignore storage errors
    }
  }, []);

  const setMode = (newMode: OperationalMode) => {
    setModeState(newMode);
    try {
      localStorage.setItem("climateshield_mode", newMode);
    } catch {
      // Ignore storage errors
    }
  };

  const value = useMemo(() => ({ mode, setMode, isDegraded: mode === "DEGRADED" }), [mode]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useOperationalMode(): OperationalModeContext {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useOperationalMode must be used inside OperationalModeProvider");
  return ctx;
}
