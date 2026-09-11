/**
 * Climate React Query Hooks
 * Clean data access hooks with stable query keys for all domain models.
 */

import { useQuery, useMutation } from "@tanstack/react-query";
import { climateApi } from "@/services/climate-api";
import { useOperationalMode } from "@/hooks/use-operational-mode";
import { setApiOperationalMode } from "@/services/climate-api";
import type { SimulationRunRequest } from "@/types/climate";
import { useEffect } from "react";

export const climateKeys = {
  city: ["city"] as const,
  cityRisk: ["city-risk"] as const,
  zones: ["zones"] as const,
  zone: (id: string) => ["zone", id] as const,
  assets: ["assets"] as const,
  incidents: ["incidents"] as const,
  alerts: ["alerts"] as const,
  recommendations: ["recommendations"] as const,
  riverNodes: ["river-nodes"] as const,
  dataSources: ["data-sources"] as const,
  forecast: (zoneId: string, horizon?: number) => ["forecast", zoneId, horizon] as const,
  cascade: ["cascade"] as const,
  systemHealth: ["system-health"] as const,
  mlHealth: ["ml-health"] as const,
  mlForecast: (nodeId?: string) => ["ml-forecast", nodeId ?? "RN-01"] as const,
  mlEvaluation: (samples?: number) => ["ml-evaluation", samples ?? 100] as const,
  operationalScenario: ["operational-scenario"] as const,
  simulationScenarios: ["simulation-scenarios"] as const,
  simulationResult: (id: string) => ["simulation-result", id] as const,
  agenticActionPlan: ["agentic-action-plan"] as const,
};

/** Synchronizes OperationalModeContext with the climate API service layer */
export function useSyncOperationalMode(): void {
  const { mode } = useOperationalMode();
  useEffect(() => {
    setApiOperationalMode(mode);
  }, [mode]);
}

export function useCity() {
  return useQuery({
    queryKey: climateKeys.city,
    queryFn: () => climateApi.getCity(),
    staleTime: 60_000,
  });
}

export function useCityRisk() {
  return useQuery({
    queryKey: climateKeys.cityRisk,
    queryFn: () => climateApi.getCityRisk(),
    staleTime: 3000,
    refetchInterval: 6000,
  });
}

export function useZones() {
  return useQuery({
    queryKey: climateKeys.zones,
    queryFn: () => climateApi.getZones(),
    staleTime: 30_000,
  });
}

export function useZone(id: string) {
  return useQuery({
    queryKey: climateKeys.zone(id),
    queryFn: () => climateApi.getZone(id),
    enabled: Boolean(id),
    staleTime: 30_000,
  });
}

export function useAssets() {
  return useQuery({
    queryKey: climateKeys.assets,
    queryFn: () => climateApi.getAssets(),
    staleTime: 60_000,
  });
}

export function useIncidents() {
  return useQuery({
    queryKey: climateKeys.incidents,
    queryFn: () => climateApi.getIncidents(),
    staleTime: 15_000,
  });
}

export function useAlerts() {
  return useQuery({
    queryKey: climateKeys.alerts,
    queryFn: () => climateApi.getAlerts(),
    staleTime: 15_000,
  });
}

export function useRecommendations() {
  return useQuery({
    queryKey: climateKeys.recommendations,
    queryFn: () => climateApi.getRecommendations(),
    staleTime: 30_000,
  });
}

export function useRiverNodes() {
  return useQuery({
    queryKey: climateKeys.riverNodes,
    queryFn: () => climateApi.getRiverNodes(),
    staleTime: 2000,
    refetchInterval: 4000,
  });
}

export function useDataSources() {
  return useQuery({
    queryKey: climateKeys.dataSources,
    queryFn: () => climateApi.getDataSources(),
    staleTime: 60_000,
  });
}

export function useForecast(zoneId = "zone-a", horizon = 12) {
  return useQuery({
    queryKey: climateKeys.forecast(zoneId, horizon),
    queryFn: () => climateApi.getForecast(zoneId),
    staleTime: 60_000,
  });
}

export function useCascade() {
  return useQuery({
    queryKey: climateKeys.cascade,
    queryFn: () => climateApi.getCascade(),
    staleTime: 60_000,
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: climateKeys.systemHealth,
    queryFn: () => climateApi.getSystemHealth(),
    staleTime: 15_000,
  });
}

export function useMlHealth() {
  return useQuery({
    queryKey: climateKeys.mlHealth,
    queryFn: () => climateApi.getMlHealth(),
    staleTime: 3000,
    refetchInterval: 8000,
  });
}

export function useMlForecast(riverNodeId = "RN-01") {
  return useQuery({
    queryKey: climateKeys.mlForecast(riverNodeId),
    queryFn: () => climateApi.getMlForecast(riverNodeId),
    staleTime: 2000,
    refetchInterval: 4000,
  });
}

export function useMlEvaluation(samples = 100) {
  return useQuery({
    queryKey: climateKeys.mlEvaluation(samples),
    queryFn: () => climateApi.getMlEvaluation(samples),
    staleTime: 60_000,
  });
}

export function useOperationalScenario() {
  return useQuery({
    queryKey: climateKeys.operationalScenario,
    queryFn: () => climateApi.getOperationalScenario(),
    staleTime: 60_000,
  });
}

export function useSimulationScenarios() {
  return useQuery({
    queryKey: climateKeys.simulationScenarios,
    queryFn: () => climateApi.getSimulationScenarios(),
    staleTime: 60_000,
  });
}

export function useRunSimulation() {
  return useMutation({
    mutationFn: (req: SimulationRunRequest) => climateApi.runSimulation(req),
  });
}

export function useRunNamedScenario() {
  return useMutation({
    mutationFn: (scenarioName: string) => climateApi.runNamedScenario(scenarioName),
  });
}

export function useSimulationResult(simId: string | null) {
  return useQuery({
    queryKey: climateKeys.simulationResult(simId ?? ""),
    queryFn: () => climateApi.getSimulationResult(simId!),
    enabled: Boolean(simId),
    staleTime: 300_000,
  });
}

export function useAgenticActionPlan() {
  return useQuery({
    queryKey: climateKeys.agenticActionPlan,
    queryFn: () => climateApi.getAgenticActionPlan(),
    staleTime: 2000,
    refetchInterval: 5000,
  });
}
