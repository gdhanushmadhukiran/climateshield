/**
 * Real-Time Telemetry SSE Subscription Hook
 * Connects to /api/v1/stream/telemetry when in LIVE mode and dynamically
 * invalidates and refreshes React Query caches without page reload.
 */

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useOperationalMode } from "@/hooks/use-operational-mode";
import { climateKeys } from "@/hooks/use-climate-queries";

export function useClimateStream(): void {
  const queryClient = useQueryClient();
  const { mode } = useOperationalMode();

  useEffect(() => {
    // Only subscribe to live telemetry stream when operating in LIVE mode
    if (mode !== "LIVE" && mode !== "DEGRADED") {
      return;
    }

    const sseUrl = "/api/v1/stream/telemetry";
    let eventSource: EventSource | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

    function connect() {
      try {
        eventSource = new EventSource(sseUrl);

        eventSource.addEventListener("river_update", (e) => {
          try {
            const data = JSON.parse(e.data);
            // Invalidate river nodes and ml forecast to trigger fresh React Query render
            queryClient.invalidateQueries({ queryKey: climateKeys.riverNodes });
            queryClient.invalidateQueries({ queryKey: ["river-nodes"] });
            queryClient.invalidateQueries({ queryKey: ["ml-forecast"] });
            queryClient.invalidateQueries({ queryKey: climateKeys.mlForecast("RN-01") });
            // If water breached threshold or rapid rise, also invalidate risk
            if (data.rateOfRiseMPerHour > 0.2 || data.waterLevelM >= data.thresholdM) {
              queryClient.invalidateQueries({ queryKey: climateKeys.cityRisk });
              queryClient.invalidateQueries({ queryKey: climateKeys.zones });
            }
          } catch {
            // Ignore malformed event
          }
        });

        eventSource.addEventListener("sensor_status", () => {
          queryClient.invalidateQueries({ queryKey: climateKeys.riverNodes });
          queryClient.invalidateQueries({ queryKey: climateKeys.systemHealth });
        });

        eventSource.addEventListener("risk_trigger", () => {
          queryClient.invalidateQueries({ queryKey: climateKeys.cityRisk });
          queryClient.invalidateQueries({ queryKey: climateKeys.zones });
        });

        eventSource.addEventListener("ml_forecast_update", () => {
          queryClient.invalidateQueries({ queryKey: ["ml-forecast"] });
          queryClient.invalidateQueries({ queryKey: climateKeys.mlForecast("RN-01") });
          queryClient.invalidateQueries({ queryKey: ["forecast"] });
        });

        eventSource.addEventListener("sensor_anomaly", () => {
          queryClient.invalidateQueries({ queryKey: climateKeys.riverNodes });
          queryClient.invalidateQueries({ queryKey: climateKeys.systemHealth });
          queryClient.invalidateQueries({ queryKey: climateKeys.mlHealth });
          queryClient.invalidateQueries({ queryKey: climateKeys.cityRisk });
        });

        eventSource.addEventListener("ml_status", () => {
          queryClient.invalidateQueries({ queryKey: climateKeys.mlHealth });
        });

        eventSource.onerror = () => {
          if (eventSource) {
            eventSource.close();
            eventSource = null;
          }
          // Retry connection after 5 seconds
          reconnectTimeout = setTimeout(connect, 5000);
        };
      } catch {
        // SSE not supported or network error
      }
    }

    connect();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [mode, queryClient]);
}
