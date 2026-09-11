import { cn } from "@/lib/utils";
import { statusDotClass, statusToneClass } from "@/lib/risk";
import type { ServiceStatus } from "@/types/climate";

const STATUS_GLYPH: Record<ServiceStatus, string> = {
  HEALTHY: "✓",
  ACTIVE: "◆",
  DEGRADED: "!",
  OFFLINE: "×",
};

export function StatusIndicator({
  status,
  label,
  detail,
  className,
}: {
  status: ServiceStatus;
  label?: string | undefined;
  detail?: string | undefined;
  className?: string | undefined;
}) {
  return (
    <span className={cn("inline-flex items-center gap-1.5", className)}>
      <span
        aria-hidden
        className={cn(
          "size-1.5 rounded-full",
          statusDotClass[status],
          status === "ACTIVE" && "pulse-dot",
        )}
      />
      <span className={cn("label-tech", statusToneClass[status])}>
        <span className="sr-only">
          {STATUS_GLYPH[status]} status {status}
          {label ? ` for ${label}` : ""}:{" "}
        </span>
        {label ? `${label} · ` : ""}
        {status}
      </span>
      {detail ? <span className="label-tech text-muted-foreground/70">{detail}</span> : null}
    </span>
  );
}

export function LiveIndicator({
  label = "LIVE",
  className,
  tone = "intel",
}: {
  label?: string | undefined;
  className?: string | undefined;
  tone?: "intel" | "critical" | "muted" | undefined;
}) {
  const dot =
    tone === "critical"
      ? "bg-risk-critical"
      : tone === "muted"
        ? "bg-muted-foreground"
        : "bg-intel";
  const text =
    tone === "critical"
      ? "text-risk-critical"
      : tone === "muted"
        ? "text-muted-foreground"
        : "text-intel";
  return (
    <span className={cn("inline-flex items-center gap-1.5", className)}>
      <span aria-hidden className={cn("size-1.5 rounded-full pulse-dot", dot)} />
      <span className={cn("label-tech", text)}>{label}</span>
    </span>
  );
}

/** Thin animated line signalling an active pipeline / data stream. */
export function DataStreamLine({
  className,
  active = true,
}: {
  className?: string | undefined;
  active?: boolean;
}) {
  return (
    <span
      aria-hidden
      className={cn("block h-px w-full", active ? "data-stream" : "bg-border", className)}
    />
  );
}
