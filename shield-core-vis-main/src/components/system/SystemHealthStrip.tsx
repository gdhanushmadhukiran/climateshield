import { cn } from "@/lib/utils";
import { StatusIndicator } from "./StatusIndicator";
import { relativeAge } from "@/lib/risk";
import type { SystemHealth } from "@/types/climate";

/** Infrastructure telemetry strip — not a dashboard card row. */
export function SystemHealthStrip({
  health,
  className,
}: {
  health: SystemHealth;
  className?: string | undefined;
}) {
  return (
    <div
      className={cn(
        "intel-line-top flex w-full flex-wrap items-center gap-x-5 gap-y-2 border-t border-border bg-surface px-4 py-2",
        className,
      )}
      aria-label="System telemetry"
    >
      <span className="label-tech text-muted-foreground/70">TELEMETRY</span>
      <div className="flex flex-1 flex-wrap items-center gap-x-5 gap-y-2">
        {health.services.map((s) => (
          <StatusIndicator
            key={s.id}
            status={s.status}
            label={s.label.toUpperCase()}
            detail={s.detail}
          />
        ))}
      </div>
      <span className="label-tech text-muted-foreground/70" suppressHydrationWarning>
        SYNC {relativeAge(health.lastSyncAt)}
      </span>
      <span className="label-tech">
        HEALTH <span className="num text-risk-low">{health.overallPercent}%</span>
      </span>
    </div>
  );
}
