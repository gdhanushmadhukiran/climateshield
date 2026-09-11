import { AlertTriangle, CloudOff, Database, Inbox, Loader2, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import { clockTime } from "@/lib/risk";
import type { ReactNode } from "react";

function StateFrame({
  icon,
  title,
  children,
  tone = "muted",
  className,
  actions,
}: {
  icon: ReactNode;
  title: string;
  children?: ReactNode | undefined;
  tone?: "muted" | "intel" | "warning" | "critical" | undefined;
  className?: string | undefined;
  actions?: ReactNode | undefined;
}) {
  const toneRing = {
    muted: "border-border",
    intel: "border-intel/40",
    warning: "border-risk-moderate/45",
    critical: "border-risk-critical/50",
  }[tone];
  const toneText = {
    muted: "text-muted-foreground",
    intel: "text-intel",
    warning: "text-risk-moderate",
    critical: "text-risk-critical",
  }[tone];
  return (
    <div
      role="status"
      className={cn(
        "flex items-start gap-3 border bg-surface/60 px-4 py-3.5 text-sm",
        toneRing,
        className,
      )}
    >
      <span className={cn("mt-0.5 shrink-0", toneText)} aria-hidden>
        {icon}
      </span>
      <div className="min-w-0 flex-1">
        <p className={cn("label-tech", toneText)}>{title}</p>
        {children ? (
          <div className="mt-1.5 text-[13px] text-muted-foreground">{children}</div>
        ) : null}
        {actions ? <div className="mt-3 flex gap-2">{actions}</div> : null}
      </div>
    </div>
  );
}

export function LoadingState({
  label = "Acquiring data",
  className,
}: {
  label?: string | undefined;
  className?: string | undefined;
}) {
  return (
    <StateFrame
      tone="intel"
      className={className}
      icon={<Loader2 className="size-4 animate-spin" />}
      title={label.toUpperCase()}
    >
      Requesting the latest validated observation from the intelligence layer.
    </StateFrame>
  );
}

export function ErrorState({
  message = "The intelligence layer returned an error.",
  onRetry,
  className,
}: {
  message?: string | undefined;
  onRetry?: (() => void) | undefined;
  className?: string | undefined;
}) {
  return (
    <StateFrame
      tone="critical"
      className={className}
      icon={<ShieldAlert className="size-4" />}
      title="REQUEST FAILED"
      actions={
        onRetry ? (
          <button
            type="button"
            onClick={onRetry}
            className="border border-border-strong px-2.5 py-1 text-[11px] tracking-wide uppercase hover:border-intel hover:text-intel"
          >
            Retry
          </button>
        ) : undefined
      }
    >
      {message}
    </StateFrame>
  );
}

export function EmptyState({
  title = "No records",
  message = "Nothing matches the current operational filter.",
  className,
}: {
  title?: string | undefined;
  message?: string | undefined;
  className?: string | undefined;
}) {
  return (
    <StateFrame
      className={className}
      icon={<Inbox className="size-4" />}
      title={title.toUpperCase()}
    >
      {message}
    </StateFrame>
  );
}

export function OfflineState({ className }: { className?: string | undefined }) {
  return (
    <StateFrame
      tone="critical"
      className={className}
      icon={<CloudOff className="size-4" />}
      title="CONNECTION LOST"
    >
      ClimateShield cannot reach the risk engine. Displaying the last cached assessment only — do
      not issue alerts from this view.
    </StateFrame>
  );
}

export function DegradedState({
  reason = "Live rainfall API unavailable.",
  fallback = "Using last validated observation.",
  lastValidAt,
  className,
}: {
  reason?: string | undefined;
  fallback?: string | undefined;
  lastValidAt?: string | undefined;
  className?: string | undefined;
}) {
  return (
    <StateFrame
      tone="warning"
      className={className}
      icon={<AlertTriangle className="size-4" />}
      title="⚠ DEGRADED INTELLIGENCE"
    >
      <p>{reason}</p>
      <p>{fallback}</p>
      {lastValidAt ? (
        <p className="mt-1.5 label-tech text-muted-foreground/70" suppressHydrationWarning>
          LAST VALID UPDATE {clockTime(lastValidAt)}
        </p>
      ) : null}
    </StateFrame>
  );
}

export function LowConfidenceState({
  confidence,
  message = "Limited environmental data in this area.",
  className,
}: {
  confidence: number;
  message?: string | undefined;
  className?: string | undefined;
}) {
  return (
    <StateFrame
      tone="warning"
      className={className}
      icon={<Database className="size-4" />}
      title={`LOW CONFIDENCE · ${confidence}%`}
    >
      {message} Treat this assessment as indicative; confirm with field observation before acting.
    </StateFrame>
  );
}

export function StaleDataState({
  lastValidAt,
  className,
}: {
  lastValidAt: string;
  className?: string | undefined;
}) {
  return (
    <StateFrame
      tone="warning"
      className={className}
      icon={<AlertTriangle className="size-4" />}
      title="STALE OBSERVATION"
    >
      No new packet received. Last valid update{" "}
      <span suppressHydrationWarning>{clockTime(lastValidAt)}</span>.
    </StateFrame>
  );
}
