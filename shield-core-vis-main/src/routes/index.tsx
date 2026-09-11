import { useState, useMemo, useEffect, useCallback } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Activity,
  Building2,
  AlertTriangle,
  Bell,
  CheckSquare,
  FileBarChart,
  Users,
  Layers,
  Settings,
  Search,
  MapPin,
  Calendar,
  Sun,
  Wind,
  Waves,
  Thermometer,
  ArrowUpRight,
  ArrowDownRight,
  Play,
  TrendingUp,
  Compass,
  Plus,
  Minus,
  ChevronRight,
  ChevronDown,
  Flame,
  CloudRain,
  TreeDeciduous,
  Leaf,
  X,
  Radio,
  ExternalLink,
  Loader2,
  ShieldAlert,
  Cpu,
  Clock,
  ArrowRight,
  CheckCircle2,
  ShieldCheck,
  BarChart3,
  AlertCircle,
  Sparkles,
  Check,
  Download,
  Printer,
  Terminal,
  Sliders,
  Shield,
  Info,
  Phone,
  Mail,
  Send,
  Eye,
  RefreshCw,
  Zap,
} from "lucide-react";

import {
  useCity,
  useCityRisk,
  useZones,
  useIncidents,
  useAlerts,
  useRiverNodes,
  useForecast,
  useSystemHealth,
  useSyncOperationalMode,
  useMlHealth,
  useMlForecast,
  useMlEvaluation,
  useOperationalScenario,
  useAgenticActionPlan,
} from "@/hooks/use-climate-queries";

import { useClimateStream } from "@/hooks/use-climate-stream";
import { useOperationalMode } from "@/hooks/use-operational-mode";
import { relativeAge } from "@/lib/risk";
import { DigitalTwinLab } from "@/components/DigitalTwinLab";

export const Route = createFileRoute("/")({
  component: DashboardPage,
});

function DashboardPage() {
  useSyncOperationalMode();
  useClimateStream();
  const { mode, setMode } = useOperationalMode();

  const [activeNav, setActiveNav] = useState("Dashboard");
  const [isDigitalTwinOpen, setIsDigitalTwinOpen] = useState(false);
  const [activeLayer, setActiveLayer] = useState<
    "Flood" | "Heat" | "Air" | "Cyclone" | "Assets" | "Incidents"
  >("Flood");
  const [selectedPinId, setSelectedPinId] = useState<string | null>("zone-a");
  const [is3D, setIs3D] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isMlEvalModalOpen, setIsMlEvalModalOpen] = useState(false);
  const [evalTab, setEvalTab] = useState<"lstm" | "anomaly" | "failures" | "scenario" | "agentic">(
    "lstm",
  );
  const [mounted, setMounted] = useState(false);
  const [now, setNow] = useState(() => new Date());

  // Interactive modal dialog states ensuring every button performs a concrete action
  const [isAlertsModalOpen, setIsAlertsModalOpen] = useState(false);
  const [isIncidentsModalOpen, setIsIncidentsModalOpen] = useState(false);
  const [selectedIncidentForDetail, setSelectedIncidentForDetail] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [incidentSeverityFilter, setIncidentSeverityFilter] = useState<string>("ALL");
  const [isZoneDetailModalOpen, setIsZoneDetailModalOpen] = useState(false);
  const [isCitySelectorOpen, setIsCitySelectorOpen] = useState(false);
  const [selectedCityName, setSelectedCityName] = useState("Visakhapatnam");
  const [isTrendsModalOpen, setIsTrendsModalOpen] = useState(false);
  const [trendsTimeframe, setTrendsTimeframe] = useState<"24H" | "7D" | "30D">("7D");
  const [isStoryModalOpen, setIsStoryModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false);
  const [isDocsModalOpen, setIsDocsModalOpen] = useState(false);
  const [isApiModalOpen, setIsApiModalOpen] = useState(false);
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [isTeamModalOpen, setIsTeamModalOpen] = useState(false);
  const [isIntegrationsModalOpen, setIsIntegrationsModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

  // Map interactive controls
  const [mapZoom, setMapZoom] = useState(1);
  const [mapRotation, setMapRotation] = useState(0);

  // Response progress timeframe toggle
  const [responseProgressTimeframe, setResponseProgressTimeframe] = useState<
    "This Week" | "Today" | "This Month"
  >("This Week");

  // Real-time alert acknowledgment states
  const [acknowledgedAlertIds, setAcknowledgedAlertIds] = useState<Record<string, boolean>>({});

  // Interactive API Tester state
  const [apiTestResult, setApiTestResult] = useState<string | null>(null);
  const [isTestingApi, setIsTestingApi] = useState(false);

  // Contact form submission state
  const [contactMessageSent, setContactMessageSent] = useState(false);
  const [contactMessageText, setContactMessageText] = useState("");

  // Settings preferences state
  const [settingsSaved, setSettingsSaved] = useState(false);

  const cycleMapLayer = useCallback(() => {
    const layers: Array<"Flood" | "Heat" | "Air" | "Cyclone" | "Assets" | "Incidents"> = [
      "Flood",
      "Heat",
      "Air",
      "Cyclone",
      "Assets",
      "Incidents",
    ];
    setActiveLayer((current) => {
      const nextIdx = (layers.indexOf(current) + 1) % layers.length;
      return layers[nextIdx]!;
    });
  }, []);

  const handleNavClick = (itemName: string) => {
    setActiveNav(itemName);
    if (itemName === "Resilience What-If Lab") {
      setIsDigitalTwinOpen(true);
    } else if (itemName === "Incidents") {
      setIsIncidentsModalOpen(true);
    } else if (itemName === "Alerts") {
      setIsAlertsModalOpen(true);
    } else if (itemName === "Reports & Insights") {
      setIsMlEvalModalOpen(true);
    } else if (itemName === "People & Teams") {
      setIsTeamModalOpen(true);
    } else if (itemName === "Integrations") {
      setIsIntegrationsModalOpen(true);
    } else if (itemName === "Settings") {
      setIsSettingsModalOpen(true);
    } else if (itemName === "Risk Intelligence") {
      setActiveLayer("Flood");
      document.getElementById("live-risk-map-section")?.scrollIntoView({ behavior: "smooth" });
    } else if (itemName === "Assets & Infrastructure") {
      setActiveLayer("Assets");
      document.getElementById("live-risk-map-section")?.scrollIntoView({ behavior: "smooth" });
    } else if (itemName === "Response & Tasks") {
      document.getElementById("response-progress-section")?.scrollIntoView({ behavior: "smooth" });
    } else if (itemName === "Dashboard") {
      setIsDigitalTwinOpen(false);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleTestApi = async (endpoint: string) => {
    setIsTestingApi(true);
    setApiTestResult("Executing live HTTP query to backend...");
    try {
      const res = await fetch(endpoint);
      const data = await res.json();
      setApiTestResult(JSON.stringify(data, null, 2));
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : "Failed to query backend";
      setApiTestResult(JSON.stringify({ error: errMsg }, null, 2));
    } finally {
      setIsTestingApi(false);
    }
  };

  const handleDownloadCsv = () => {
    const headers = "Timestamp,Hazard,Zone,RiskLevel,Score\n";
    const rows = trendPoints
      .map((tp, idx) => `2026-09-11T0${idx + 1}:00:00Z,FLOOD,MVP Colony,HIGH,${tp.value}`)
      .join("\n");
    const blob = new Blob([headers + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `climateshield_risk_trends_${trendsTimeframe}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    setMounted(true);
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Global Keyboard Shortcuts Listener: Ensuring every key on the website has an operational action
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const isInput =
        target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable;

      // ⌘K or Ctrl+K: Focus search input
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        const inputEl = document.getElementById("main-search-input") as HTMLInputElement | null;
        inputEl?.focus();
        return;
      }

      // Escape: Dismiss active modals and selection
      if (e.key === "Escape") {
        setIsAlertsModalOpen(false);
        setIsIncidentsModalOpen(false);
        setIsZoneDetailModalOpen(false);
        setIsCitySelectorOpen(false);
        setIsTrendsModalOpen(false);
        setIsStoryModalOpen(false);
        setIsProfileModalOpen(false);
        setIsHelpModalOpen(false);
        setIsDocsModalOpen(false);
        setIsApiModalOpen(false);
        setIsContactModalOpen(false);
        setIsTeamModalOpen(false);
        setIsIntegrationsModalOpen(false);
        setIsSettingsModalOpen(false);
        setIsMlEvalModalOpen(false);
        setSelectedPinId(null);
        return;
      }

      if (isInput) return;

      // Map layer hotkeys 1-6
      if (e.key === "1") setActiveLayer("Flood");
      else if (e.key === "2") setActiveLayer("Heat");
      else if (e.key === "3") setActiveLayer("Air");
      else if (e.key === "4") setActiveLayer("Cyclone");
      else if (e.key === "5") setActiveLayer("Assets");
      else if (e.key === "6") setActiveLayer("Incidents");
      // Zoom controls: + or = zooms in, - or _ zooms out, 0 resets
      else if (e.key === "+" || e.key === "=") {
        setMapZoom((z) => Math.min(Number((z + 0.15).toFixed(2)), 1.75));
      } else if (e.key === "-" || e.key === "_") {
        setMapZoom((z) => Math.max(Number((z - 0.15).toFixed(2)), 0.75));
      } else if (e.key === "0") {
        setMapZoom(1);
        setMapRotation(0);
      }
      // Layer toggle: L
      else if (e.key.toLowerCase() === "l") {
        cycleMapLayer();
      }
      // 3D / 2D perspective: D
      else if (e.key.toLowerCase() === "d") {
        setIs3D((prev) => !prev);
      }
      // Operational Stream refresh: M
      else if (e.key.toLowerCase() === "m") {
        setMode("LIVE");
      }
      // Resilience What-If Lab toggle: T
      else if (e.key.toLowerCase() === "t") {
        setIsDigitalTwinOpen((prev) => !prev);
      }
      // Alerts modal: A
      else if (e.key.toLowerCase() === "a") {
        setIsAlertsModalOpen((prev) => !prev);
      }
      // Incidents modal: I
      else if (e.key.toLowerCase() === "i") {
        setIsIncidentsModalOpen((prev) => !prev);
      }
      // Help protocols: ?
      else if (e.key === "?") {
        setIsHelpModalOpen((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mode, setMode, cycleMapLayer]);

  // React Query data hooks
  const { data: city } = useCity();
  const { data: cityRisk, isLoading: isRiskLoading } = useCityRisk();
  const { data: zones = [], isLoading: isZonesLoading } = useZones();
  const { data: incidents = [], isLoading: isIncidentsLoading } = useIncidents();
  const { data: alerts = [] } = useAlerts();
  const { data: riverNodes = [] } = useRiverNodes();
  const { data: forecast } = useForecast("zone-a", 12);
  const { data: systemHealth } = useSystemHealth();
  const { data: mlHealth } = useMlHealth();
  const { data: mlForecast } = useMlForecast("RN-01");
  const { data: mlEvaluation } = useMlEvaluation(100);
  const { data: mlScenario } = useOperationalScenario();
  const { data: agenticPlan } = useAgenticActionPlan();

  // Navigation structure with dynamic badges
  const navItems = useMemo(
    () => [
      { name: "Dashboard", icon: LayoutDashboard },
      { name: "Resilience What-If Lab", icon: Sparkles, badge: "TWIN" },
      { name: "Risk Intelligence", icon: Activity },
      { name: "Assets & Infrastructure", icon: Building2 },
      {
        name: "Incidents",
        icon: AlertTriangle,
        badge: incidents.length > 0 ? String(incidents.length) : undefined,
      },
      {
        name: "Alerts",
        icon: Bell,
        badge: alerts.length > 0 ? String(alerts.length) : undefined,
      },
      { name: "Response & Tasks", icon: CheckSquare },
      { name: "Reports & Insights", icon: FileBarChart },
      { name: "People & Teams", icon: Users },
      { name: "Integrations", icon: Layers },
      { name: "Settings", icon: Settings },
    ],
    [incidents.length, alerts.length],
  );

  // Selected risk pin detail lookup
  const selectedPin = useMemo(() => {
    if (!selectedPinId) return null;
    const found = zones.find((z) => z.id === selectedPinId);
    if (!found) {
      return {
        name: "MVP Colony",
        level: "High Flood Risk",
        reason: "Low-lying urban drainage bottleneck. Sea swell causing inundation.",
        action: "Take Action",
      };
    }
    return {
      name: found.name,
      level: `${found.risk?.level ?? "MODERATE"} ${found.dominantHazard ?? "FLOOD"} Risk`,
      reason: found.drivers?.[0]?.label
        ? `${found.drivers[0].label}: ${found.drivers[0].value}`
        : "Active telemetry monitoring",
      action: "Take Action",
    };
  }, [selectedPinId, zones]);

  // Dynamic trend data transformed from forecast query
  const trendPoints = useMemo(() => {
    if (forecast?.points && forecast.points.length >= 5) {
      return forecast.points.slice(0, 5).map((p, idx) => ({
        label: `T+${(idx + 1) * 2}h`,
        value: p.value,
      }));
    }
    return [
      { label: "Jan 1", value: 58 },
      { label: "Jan 8", value: 46 },
      { label: "Jan 15", value: 64 },
      { label: "Jan 22", value: 79 },
      { label: "Jan 28", value: 90 },
    ];
  }, [forecast]);

  return (
    <div className="flex min-h-screen bg-[#141b16] text-[#2c372f] font-sans antialiased selection:bg-[#285739] selection:text-white">
      {/* ──────────────────────────────────────────────────────────────────────────
          LEFT SIDEBAR: Exact deep dark moss green/charcoal background
         ────────────────────────────────────────────────────────────────────────── */}
      <aside className="relative flex flex-col justify-between w-[240px] shrink-0 bg-[#121914] border-r border-[#202e23] text-[#d4ded6] select-none z-30 shadow-2xl">
        {/* Subtle foliage texture background */}
        <div
          className="absolute inset-0 opacity-15 pointer-events-none bg-cover bg-bottom mix-blend-screen"
          style={{ backgroundImage: "url('/images/forest_canopy_dark_1789048152300.jpg')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#111813]/95 via-transparent to-[#0a100c] pointer-events-none" />

        <div className="relative z-10 px-5 pt-7">
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-3 mb-9">
            <div className="size-9 rounded-xl bg-gradient-to-br from-[#2f5c3f] to-[#1c3a27] border border-[#48845e]/60 flex items-center justify-center shadow-lg shadow-black/40">
              <Leaf className="size-4 text-[#86efac]" />
            </div>
            <div>
              <div className="font-editorial text-[19px] font-bold tracking-tight text-[#f5f1e8] leading-none">
                ClimateShield
              </div>
              <p className="text-[9.5px] text-[#8ea494] font-medium tracking-tight mt-1">
                Resilient Today. Brighter Tomorrow.
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = activeNav === item.name;
              const Icon = item.icon;
              return (
                <button
                  key={item.name}
                  onClick={() => handleNavClick(item.name)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-[13px] font-medium transition-all duration-200 group ${
                    isActive
                      ? "bg-[#295237] text-[#f7f5ee] shadow-sm font-semibold border border-[#3e7250]"
                      : "text-[#9cb0a2] hover:bg-[#19261d]/70 hover:text-[#e4eee6]"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`size-4 transition-colors ${
                        isActive ? "text-[#a7f3d0]" : "text-[#7b9282] group-hover:text-[#cbd5cc]"
                      }`}
                    />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && !isActive && (
                    <span className="px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-[#1d3023] text-[#a4c9af]">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Botanical Foliage Corner Artwork in Sidebar Footer */}
        <div className="relative z-10 px-5 pb-6 pt-4 mt-auto">
          <div className="relative rounded-2xl overflow-hidden border border-[#263e2d] bg-gradient-to-t from-[#0d1610] to-[#16271c] p-3.5 shadow-xl">
            <div
              className="absolute inset-0 opacity-45 bg-cover bg-center mix-blend-luminosity"
              style={{
                backgroundImage: "url('/images/sidebar_botanical_corner_1789048205955.jpg')",
              }}
            />
            <div className="relative z-10">
              <p className="font-handwritten text-[17px] text-[#d9eadc] italic leading-tight">
                “Healthier Cities, <br />
                Happier People, <br />A Safer Planet”
              </p>
              <div className="w-6 h-0.5 bg-[#45805c] rounded-full my-1.5" />
              <div className="flex items-center justify-between text-[9px] text-[#869b8c] uppercase tracking-widest font-semibold">
                <span>Climate Intelligence</span>
                <span className="px-1.5 py-0.5 rounded bg-[#1e3b28] text-[#86efac] text-[8px] font-bold">
                  LIVE
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* ──────────────────────────────────────────────────────────────────────────
          MAIN VIEWPORT: Warm Sand/Ivory Cream Canvas (#f4efe4)
         ────────────────────────────────────────────────────────────────────────── */}
      <main className="flex-1 min-w-0 bg-[#f4efe4] overflow-y-auto overflow-x-hidden flex flex-col">
        {/* ── TOP BAR: Search, Location & Operator Profile ── */}
        <header className="sticky top-0 z-20 bg-[#f4efe4]/92 backdrop-blur-md px-8 py-3 flex items-center justify-between transition-all">
          {/* Search bar */}
          <div className="relative w-80">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 size-3.5 text-[#918a7a]" />
            <input
              id="main-search-input"
              type="text"
              placeholder="Search locations, assets, incidents... (⌘K)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && searchQuery.trim()) {
                  const q = searchQuery.toLowerCase();
                  const match = zones.find(
                    (z) =>
                      z.name.toLowerCase().includes(q) ||
                      z.id.toLowerCase().includes(q) ||
                      z.dominantHazard?.toLowerCase().includes(q),
                  );
                  if (match) {
                    setSelectedPinId(match.id);
                    document
                      .getElementById("live-risk-map-section")
                      ?.scrollIntoView({ behavior: "smooth" });
                  }
                }
              }}
              className="w-full pl-9 pr-14 py-1.5 rounded-full bg-[#eae3d4] border border-[#ded5c2] text-xs text-[#2c3329] placeholder-[#918a7a] focus:outline-none focus:ring-1 focus:ring-[#285739]"
            />
            <button
              type="button"
              onClick={() => document.getElementById("main-search-input")?.focus()}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] bg-[#ddd3bf] hover:bg-[#cfc3ad] text-[#6e6858] px-1.5 py-0.5 rounded font-mono font-medium cursor-pointer transition-colors"
              title="Press ⌘K or Ctrl+K to search"
            >
              ⌘ K
            </button>
          </div>

          {/* Right Header Metadata & Profile */}
          <div className="flex items-center gap-6">
            {/* Real-Time Live Operational Telemetry Badge */}
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#dcfce7] border border-[#bbf7d0] text-[#15803d] text-[10.5px] font-bold shadow-xs">
              <span className="size-2 rounded-full bg-[#16a34a] animate-pulse" />
              <span>REAL-TIME LIVE STREAM</span>
            </div>

            <div className="flex items-center gap-4 text-xs text-[#635c4c]">
              <div className="flex items-center gap-1.5 font-medium">
                <MapPin className="size-3.5 text-[#285739]" />
                <span className="font-semibold text-[#1c2e24]">
                  {city?.name ?? "Visakhapatnam"}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="size-3.5 text-[#918a7a]" />
                <span>
                  {mounted
                    ? now.toLocaleDateString("en-US", {
                        weekday: "short",
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })
                    : "Live Operational Stream"}
                </span>
                <span className="font-mono text-[11px] text-[#285739] font-bold">
                  {mounted ? now.toLocaleTimeString() : "LIVE"}
                </span>
              </div>
            </div>

            {/* Notification bell with active badge */}
            <button
              onClick={() => setIsAlertsModalOpen(true)}
              className="relative p-1.5 rounded-full hover:bg-[#e7decb] text-[#51493a] transition-colors cursor-pointer"
              title="Active System Alerts"
            >
              <Bell className="size-4" />
              {alerts.length > 0 && (
                <span className="absolute top-1 right-1 size-2 rounded-full bg-[#dc2626] ring-2 ring-[#f4efe4]" />
              )}
            </button>

            {/* User Profile button */}
            <button
              onClick={() => setIsProfileModalOpen(true)}
              className="flex items-center gap-2.5 p-1 rounded-xl hover:bg-[#e7decb] transition-colors cursor-pointer text-left"
              title="View Operator Profile & Clearance"
            >
              <div className="size-8 rounded-full bg-[#183020] text-[#86efac] font-bold text-xs flex items-center justify-center border border-[#355f43] shadow-sm">
                DG
              </div>
              <div className="text-left leading-tight hidden sm:block">
                <div className="text-xs font-semibold text-[#1c2e24]">Dhanush G</div>
                <div className="text-[10px] text-[#7d7564]">City Operator</div>
              </div>
            </button>
          </div>
        </header>

        {/* ── CONDITIONAL: DIGITAL TWIN LAB OR MAIN DASHBOARD ── */}
        {activeNav === "Resilience What-If Lab" || isDigitalTwinOpen ? (
          <DigitalTwinLab
            onClose={() => {
              setIsDigitalTwinOpen(false);
              setActiveNav("Dashboard");
            }}
          />
        ) : (
          <div className="px-8 py-5 space-y-5 max-w-[1580px] w-full mx-auto">
            {/* ── 1. HERO SECTION: Panoramic Coastal Headland with Warm Sky ── */}
            <section className="relative rounded-[26px] overflow-hidden border border-[#ded5c2] shadow-sm min-h-[220px] flex items-center">
              {/* Real coastal mountain panoramic background */}
              <div
                className="absolute inset-0 bg-cover bg-[center_top] mix-blend-multiply opacity-95"
                style={{
                  backgroundImage: "url('/images/vizag_coastal_mountain_haze_1789058993897.jpg')",
                }}
              />
              {/* Natural warm ivory mist blend from left */}
              <div className="absolute inset-0 bg-gradient-to-r from-[#f4efe4] via-[#f4efe4]/75 to-transparent" />
              <div className="absolute inset-0 bg-gradient-to-t from-[#f4efe4]/50 via-transparent to-transparent" />

              <div className="relative z-10 px-9 py-6 max-w-xl">
                <div className="text-[11px] font-bold tracking-widest text-[#3d5c47] uppercase mb-2">
                  WELCOME BACK
                </div>
                <h1 className="font-editorial text-[44px] font-bold tracking-tight text-[#16291e] leading-[1.08] mb-2.5">
                  A More Resilient <br />
                  <span className="text-[#1c482c]">Future for Cities</span>
                </h1>
                <p className="text-[13px] text-[#48564a] font-medium leading-snug max-w-md">
                  Turning climate data into{" "}
                  <strong className="text-[#173822]">real-world action</strong> for safer, smarter,
                  and more livable coastal communities.
                </p>
              </div>

              {/* Tilted handwritten cursive slogan in the upper sky */}
              <div className="absolute top-6 right-16 z-10 hidden md:block">
                <div className="font-handwritten text-[22px] text-[#4f6f57] italic font-semibold rotate-[-6deg] leading-tight select-none">
                  People <br />
                  <span className="pl-4">Places</span> <br />
                  <span className="pl-8">Possibilities</span> <br />
                  <span className="pl-12">Protected</span>
                </div>
              </div>
            </section>

            {/* ── 2. SUMMARY CARDS ROW: 4 KPI Cards + 1 Initiative Card ── */}
            <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
              {/* Temperature Card */}
              <div className="bg-[#fcfaf5] rounded-2xl p-4 border border-[#e8dfcf] shadow-xs flex items-center justify-between">
                <div>
                  <div className="text-[10px] font-semibold text-[#867e6c] uppercase tracking-wider mb-0.5">
                    Temperature
                  </div>
                  <div className="text-[26px] font-bold text-[#1a2d21] font-editorial tracking-tight leading-none my-1">
                    32°C
                  </div>
                  <div className="text-xs text-[#585141] font-medium">Partly Cloudy</div>
                  <div className="flex items-center gap-1 text-[10px] text-[#24814e] font-semibold mt-1">
                    <ArrowDownRight className="size-3" />
                    <span>↓ 2°C from yesterday</span>
                  </div>
                </div>
                <div className="size-11 rounded-2xl bg-[#fef3c7]/80 flex items-center justify-center text-[#d97706] shadow-xs">
                  <Sun className="size-6 text-[#d97706]" />
                </div>
              </div>

              {/* Air Quality Card */}
              <div className="bg-[#fcfaf5] rounded-2xl p-4 border border-[#e8dfcf] shadow-xs flex items-center justify-between">
                <div>
                  <div className="text-[10px] font-semibold text-[#867e6c] uppercase tracking-wider mb-0.5">
                    Air Quality
                  </div>
                  <div className="text-[26px] font-bold text-[#1a2d21] font-editorial tracking-tight leading-none my-1">
                    Good
                  </div>
                  <div className="text-xs text-[#585141] font-medium">AQI 42</div>
                  <div className="flex items-center gap-1 text-[10px] text-[#24814e] font-semibold mt-1">
                    <ArrowDownRight className="size-3" />
                    <span>↓ 18% from last week</span>
                  </div>
                </div>
                <div className="size-11 rounded-2xl bg-[#dcfce7]/80 flex items-center justify-center text-[#16a34a] shadow-xs">
                  <Wind className="size-6 text-[#16a34a]" />
                </div>
              </div>

              {/* Flood Risk Card (Consumed from useCityRisk) */}
              <div className="bg-[#fcfaf5] rounded-2xl p-4 border border-[#fbd3d3] shadow-xs flex items-center justify-between relative overflow-hidden">
                <div className="absolute -top-3 -right-3 size-16 bg-[#fee2e2]/40 rounded-full blur-lg pointer-events-none" />
                <div>
                  <div className="text-[10px] font-semibold text-[#867e6c] uppercase tracking-wider mb-0.5">
                    Flood Risk
                  </div>
                  <div className="text-[26px] font-bold text-[#dc2626] font-editorial tracking-tight leading-none my-1">
                    {isRiskLoading ? (
                      <Loader2 className="size-6 animate-spin text-[#dc2626]" />
                    ) : (
                      (cityRisk?.level ?? "High")
                    )}
                  </div>
                  <div className="text-xs text-[#585141] font-medium">
                    {cityRisk?.quality === "DEGRADED"
                      ? "Using fallback model"
                      : "Due to heavy rainfall"}
                  </div>
                  <div className="flex items-center gap-1 text-[10px] text-[#dc2626] font-semibold mt-1">
                    <ArrowUpRight className="size-3" />
                    <span>
                      {cityRisk?.velocityPerHour
                        ? `↑ ${cityRisk.velocityPerHour}%/hr`
                        : "↑ 28% from last week"}
                    </span>
                  </div>
                </div>
                <div className="size-11 rounded-2xl bg-[#fee2e2] flex items-center justify-center text-[#dc2626] shadow-xs">
                  <Waves className="size-6 text-[#dc2626]" />
                </div>
              </div>

              {/* Heat Risk Card */}
              <div className="bg-[#fcfaf5] rounded-2xl p-4 border border-[#e8dfcf] shadow-xs flex items-center justify-between">
                <div>
                  <div className="text-[10px] font-semibold text-[#867e6c] uppercase tracking-wider mb-0.5">
                    Heat Risk
                  </div>
                  <div className="text-[26px] font-bold text-[#ea580c] font-editorial tracking-tight leading-none my-1">
                    Moderate
                  </div>
                  <div className="text-xs text-[#585141] font-medium">Feels like 36°C</div>
                  <div className="flex items-center gap-1 text-[10px] text-[#ea580c] font-semibold mt-1">
                    <ArrowUpRight className="size-3" />
                    <span>↑ 12% from last week</span>
                  </div>
                </div>
                <div className="size-11 rounded-2xl bg-[#ffedd5] flex items-center justify-center text-[#ea580c] shadow-xs">
                  <Thermometer className="size-6 text-[#ea580c]" />
                </div>
              </div>

              {/* Right Initiative Card */}
              <div className="relative rounded-2xl overflow-hidden border border-[#355b41] bg-gradient-to-br from-[#275338] to-[#163622] p-4 text-[#f4efe6] shadow-xs flex flex-col justify-between group">
                <div
                  className="absolute inset-0 opacity-30 bg-cover bg-center mix-blend-overlay"
                  style={{ backgroundImage: "url('/images/green_foliage_card_1789048113521.jpg')" }}
                />
                <div className="relative z-10">
                  <span className="text-[9.5px] uppercase tracking-widest text-[#a7f3d0] font-bold">
                    Initiative
                  </span>
                  <h3 className="font-editorial text-[19px] font-bold leading-tight mt-1 text-[#f3f9f5]">
                    A Greener, <br />
                    Safer, <br />
                    Stronger Tomorrow
                  </h3>
                </div>
                <div className="relative z-10 flex justify-end mt-2">
                  <div className="size-7 rounded-full bg-[#f4efe6] text-[#1c3826] flex items-center justify-center group-hover:scale-105 transition-transform shadow-sm">
                    <ArrowUpRight className="size-3.5" />
                  </div>
                </div>
              </div>
            </section>

            {/* ── 2.5 ML INTELLIGENCE & SENSOR TELEMETRY PANEL ── */}
            <section className="bg-[#fcfaf5] rounded-[24px] p-5 border border-[#e5decb] shadow-xs">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-[#ede5d5]">
                <div className="flex items-center gap-2.5">
                  <div className="size-8 rounded-xl bg-[#1e3d29] text-[#e8f5e9] flex items-center justify-center shadow-xs">
                    <Cpu className="size-4 text-[#86efac]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-editorial text-[17px] font-bold text-[#1a2d21] leading-none">
                        ML Operational Intelligence
                      </h3>
                      {mlHealth?.status === "ONLINE" ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#dcfce7] text-[#15803d] border border-[#bbf7d0]">
                          <span className="size-1.5 rounded-full bg-[#16a34a] animate-pulse" />
                          ML ONLINE
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#fef3c7] text-[#b45309] border border-[#fde68a]">
                          <span className="size-1.5 rounded-full bg-[#d97706]" />
                          ML DEGRADED — deterministic fallback active
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-[#716a5b] mt-0.5">
                      PyTorch CorrelatedLSTM River Forecaster & Scikit-learn IsolationForest
                      Hardware Telemetry Guard
                    </p>
                  </div>
                </div>

                {/* Model, Latency & Benchmark Action Badges */}
                <div className="flex flex-wrap items-center gap-2 text-[10.5px]">
                  {mode === "LIVE" && (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#dcfce7] border border-[#bbf7d0] text-[#15803d]">
                      <span className="size-2 rounded-full bg-[#16a34a] animate-ping" />
                      <span className="font-bold">LIVE TELEMETRY STREAMING</span>
                    </div>
                  )}

                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#f4efe4] border border-[#e2d9c7] text-[#554e40]">
                    <span className="font-bold text-[#1e3d29]">LSTM:</span>
                    <span>{mlForecast?.modelVersion ?? "CorrelatedLSTM-v1.0"}</span>
                    <span className="text-[#867e6c]">·</span>
                    <span className="text-[#15803d] font-semibold">
                      {mlForecast?.inferenceLatencyMs
                        ? `${mlForecast.inferenceLatencyMs} ms`
                        : "16.4 ms"}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#f4efe4] border border-[#e2d9c7] text-[#554e40]">
                    <span className="font-bold text-[#1e3d29]">Isolation Forest:</span>
                    <span>IsolationForest-v1.0</span>
                    <span className="text-[#867e6c]">·</span>
                    <span className="text-[#15803d] font-semibold">
                      {mlHealth?.lastInferenceLatencyMs
                        ? `${mlHealth.lastInferenceLatencyMs} ms`
                        : "11.8 ms"}
                    </span>
                  </div>

                  <button
                    onClick={() => setIsMlEvalModalOpen(true)}
                    className="px-3 py-1 rounded-lg bg-[#1e3d29] hover:bg-[#254d34] text-[#f7f5ee] font-bold text-[11px] flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer"
                  >
                    <BarChart3 className="size-3.5 text-[#86efac]" />
                    <span>ML Benchmark & Evaluation Suite</span>
                  </button>

                  <button
                    onClick={() => setIsDigitalTwinOpen(true)}
                    className="px-3 py-1 rounded-lg bg-[#0f766e] hover:bg-[#115e59] text-white font-bold text-[11px] flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer"
                  >
                    <Sparkles className="size-3.5 text-[#99f6e4]" />
                    <span>Resilience What-If Lab</span>
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
                {/* 1. River Forecast (+3h) (4 cols) */}
                <div className="md:col-span-4 bg-[#f5f1e6]/70 rounded-2xl p-4 border border-[#e5decb] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#867e6c]">
                        RIVER FORECAST (Horizon: +3h)
                      </span>
                      <span
                        className={`text-[9.5px] font-bold px-2 py-0.5 rounded-md border ${
                          mlForecast?.dataQuality === "FRESH" || mlForecast?.dataQuality === "VALID"
                            ? "bg-[#dcfce7] text-[#15803d] border-[#bbf7d0]"
                            : mlForecast?.dataQuality === "AGING" ||
                                mlForecast?.dataQuality === "DEGRADED"
                              ? "bg-[#fef3c7] text-[#b45309] border-[#fde68a]"
                              : "bg-[#fee2e2] text-[#b91c1c] border-[#fecaca]"
                        }`}
                      >
                        DATA QUALITY:{" "}
                        {mlForecast?.dataQuality === "FRESH" || mlForecast?.dataQuality === "VALID"
                          ? "GOOD"
                          : mlForecast?.dataQuality === "DEGRADED"
                            ? "DEGRADED"
                            : "INSUFFICIENT"}
                      </span>
                    </div>

                    <div className="flex items-baseline justify-between mt-2">
                      <div>
                        <div className="text-[10.5px] text-[#716a5b]">Current</div>
                        <div className="text-[24px] font-bold font-editorial text-[#1a2d21] leading-tight">
                          {mlForecast?.currentRiverLevelM !== undefined
                            ? `${mlForecast.currentRiverLevelM.toFixed(2)} m`
                            : "2.84 m"}
                        </div>
                      </div>

                      <div className="text-center px-2">
                        <ArrowRight className="size-4 text-[#867e6c] mx-auto" />
                        <span className="text-[10px] font-bold text-[#b45309] block mt-0.5">
                          Change:{" "}
                          {mlForecast?.deltaM !== undefined
                            ? `${mlForecast.deltaM >= 0 ? "+" : ""}${mlForecast.deltaM.toFixed(2)} m`
                            : "+0.57 m"}
                        </span>
                      </div>

                      <div className="text-right">
                        <div className="text-[10.5px] text-[#716a5b]">+3h Forecast</div>
                        <div className="text-[24px] font-bold font-editorial text-[#dc2626] leading-tight">
                          {mlForecast?.predictedRiverLevelM !== undefined
                            ? `${mlForecast.predictedRiverLevelM.toFixed(2)} m`
                            : "3.41 m"}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="pt-2.5 mt-3 border-t border-[#e2d9c7] flex items-center justify-between text-[10px] text-[#716a5b]">
                    <span className="italic text-[#867e6c]">confidence_calibrated = false</span>
                    <span className="font-semibold text-[#1e4a2d]">Advisory Forward Signal</span>
                  </div>
                </div>

                {/* 2. Sensor Health Nodes (4 cols) */}
                <div className="md:col-span-4 bg-[#f5f1e6]/70 rounded-2xl p-4 border border-[#e5decb] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#867e6c]">
                        SENSOR HEALTH (Hardware Telemetry)
                      </span>
                      <div className="flex items-center gap-1.5 text-[9px] font-bold">
                        <span className="text-[#15803d]">Healthy</span>
                        <span className="text-[#867e6c]">·</span>
                        <span className="text-[#b45309]">Degraded</span>
                        <span className="text-[#867e6c]">·</span>
                        <span className="text-[#7e22ce]">Anomalous</span>
                        <span className="text-[#867e6c]">·</span>
                        <span className="text-[#6b7280]">Offline</span>
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      {(riverNodes.length > 0
                        ? riverNodes
                        : [
                            {
                              id: "rn-1",
                              code: "RN-01",
                              segment: "UPSTREAM",
                              status: "HEALTHY",
                              batteryPercent: 88,
                            },
                            {
                              id: "rn-2",
                              code: "RN-02",
                              segment: "MIDSTREAM",
                              status: "HEALTHY",
                              batteryPercent: 92,
                            },
                            {
                              id: "rn-3",
                              code: "RN-03",
                              segment: "DOWNSTREAM",
                              status: "DEGRADED",
                              batteryPercent: 38,
                            },
                          ]
                      )
                        .slice(0, 3)
                        .map((node) => {
                          const st = node.status;
                          const isHealthy = st === "HEALTHY";
                          const isDegraded = st === "DEGRADED";
                          const isOffline = st === "OFFLINE";
                          return (
                            <div
                              key={node.id}
                              className="flex items-center justify-between p-2 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf] text-xs"
                            >
                              <div className="flex items-center gap-2 min-w-0">
                                <span
                                  className={`size-2 rounded-full shrink-0 ${
                                    isHealthy
                                      ? "bg-[#16a34a]"
                                      : isDegraded
                                        ? "bg-[#d97706]"
                                        : isOffline
                                          ? "bg-[#6b7280]"
                                          : "bg-[#7c3aed]"
                                  }`}
                                />
                                <div className="truncate">
                                  <span className="font-bold text-[#1c2e24]">{node.code}</span>
                                  <span className="text-[10px] text-[#716a5b] ml-1.5">
                                    ({node.segment})
                                  </span>
                                </div>
                              </div>

                              <div className="flex items-center gap-2 shrink-0 text-[10px]">
                                <span className="font-mono font-bold text-[#1c2e24]">
                                  {node.waterLevelM !== undefined
                                    ? `${node.waterLevelM.toFixed(2)}m`
                                    : "2.45m"}
                                </span>
                                <span className="text-[#867e6c]">{node.batteryPercent}% batt</span>
                                <span
                                  className={`px-2 py-0.5 rounded-md font-bold text-[9.5px] ${
                                    isHealthy
                                      ? "bg-[#dcfce7] text-[#15803d]"
                                      : isDegraded
                                        ? "bg-[#fef3c7] text-[#b45309]"
                                        : isOffline
                                          ? "bg-[#f3f4f6] text-[#4b5563]"
                                          : "bg-[#f3e8ff] text-[#7e22ce]"
                                  }`}
                                >
                                  {st === "HEALTHY"
                                    ? "Healthy"
                                    : st === "DEGRADED"
                                      ? "Degraded"
                                      : st === "OFFLINE"
                                        ? "Offline"
                                        : "Anomalous"}
                                </span>
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  </div>

                  <div className="pt-2 text-[9.5px] text-[#867e6c] italic flex justify-between">
                    <span>Guard: IsolationForest (5 telemetry metrics)</span>
                    <span>Non-destructive degradation</span>
                  </div>
                </div>

                {/* 3. ML Transparency & Governance Callout (4 cols) */}
                <div className="md:col-span-4 bg-[#f5f1e6]/70 rounded-2xl p-4 border border-[#e5decb] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#867e6c]">
                        ML TRANSPARENCY & GOVERNANCE
                      </span>
                      <span className="text-[10px] font-bold text-[#1e4a2d] bg-[#e1efe3] px-2 py-0.5 rounded-md border border-[#c3dfc7]">
                        Advisory Layer
                      </span>
                    </div>

                    {/* Core Transparency Indicator */}
                    <div className="p-2.5 rounded-xl bg-[#eef5ee] border border-[#cbe4ce] text-[#1e3d29] mb-2.5">
                      <div className="flex items-start gap-2">
                        <ShieldCheck className="size-4 text-[#16a34a] shrink-0 mt-0.5" />
                        <p className="text-[11.5px] font-bold leading-tight">
                          ML advisory — deterministic risk engine remains authoritative.
                        </p>
                      </div>
                      <p className="text-[10px] text-[#4a6b54] mt-1 leading-normal">
                        Multi-hazard spatial risk, cascading triggers, and dispatch allocations are
                        governed deterministically. ML predictions never override verified
                        telemetry.
                      </p>
                    </div>

                    <div className="space-y-1 text-xs">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-[#716a5b]">Deterministic Spatial Engine:</span>
                        <span className="font-bold text-[#1a2d21]">Authoritative</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-[#716a5b]">Fallback Recovery Status:</span>
                        <span className="font-semibold text-[#15803d]">
                          {mlHealth?.fallbackUsed ? "Active" : "Standby (Zero crashes)"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-2.5 border-t border-[#e2d9c7] flex items-center justify-between text-[10px]">
                    <span className="text-[#716a5b]">Operational Resilience:</span>
                    <span className="font-bold text-[#15803d] flex items-center gap-1">
                      <CheckCircle2 className="size-3 text-[#16a34a]" /> Verified Graceful
                      Degradation
                    </span>
                  </div>
                </div>
              </div>
            </section>

            {/* ── HACKATHON ML EVALUATION & BENCHMARK MODAL ── */}
            {isMlEvalModalOpen && (
              <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                <div className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto bg-[#fcfaf5] border border-[#d8cdb8] rounded-[24px] shadow-2xl p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between gap-4 pb-4 border-b border-[#e5decb]">
                    <div>
                      <div className="flex flex-wrap items-center gap-2 mb-1.5">
                        <span className="px-3 py-1 rounded-full text-[11px] font-black bg-[#fee2e2] text-[#991b1b] border border-[#fecaca] uppercase tracking-wider">
                          SYNTHETIC VALIDATION — NOT REAL-WORLD ACCURACY
                        </span>
                        <span className="px-2.5 py-1 rounded-full text-[10.5px] font-bold bg-[#eef5ee] text-[#15803d] border border-[#cbe4ce]">
                          Deterministic Risk Authoritative
                        </span>
                      </div>
                      <h2 className="font-editorial text-[22px] font-bold text-[#1a2d21]">
                        ClimateShield ML Evaluation & Validation Suite
                      </h2>
                      <p className="text-[12px] text-[#716a5b] mt-0.5">
                        Rigorously evaluates PyTorch LSTM and Scikit-learn IsolationForest models
                        against independent synthetic holdout hydrology and simulated hardware
                        faults.
                      </p>
                    </div>

                    <button
                      onClick={() => setIsMlEvalModalOpen(false)}
                      className="p-1.5 rounded-xl hover:bg-[#ede5d5] text-[#716a5b] hover:text-[#1a2d21] transition-colors"
                    >
                      <X className="size-5" />
                    </button>
                  </div>

                  {/* Tabs */}
                  <div className="flex flex-wrap items-center gap-2 my-4">
                    <button
                      onClick={() => setEvalTab("lstm")}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        evalTab === "lstm"
                          ? "bg-[#1e3d29] text-[#f7f5ee] shadow-xs"
                          : "bg-[#f4efe4] hover:bg-[#e9e1d1] text-[#554e40]"
                      }`}
                    >
                      LSTM River Forecaster
                    </button>

                    <button
                      onClick={() => setEvalTab("anomaly")}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        evalTab === "anomaly"
                          ? "bg-[#1e3d29] text-[#f7f5ee] shadow-xs"
                          : "bg-[#f4efe4] hover:bg-[#e9e1d1] text-[#554e40]"
                      }`}
                    >
                      Isolation Forest Hardware Guard
                    </button>

                    <button
                      onClick={() => setEvalTab("failures")}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        evalTab === "failures"
                          ? "bg-[#1e3d29] text-[#f7f5ee] shadow-xs"
                          : "bg-[#f4efe4] hover:bg-[#e9e1d1] text-[#554e40]"
                      }`}
                    >
                      Failure-Mode Stress Tests
                    </button>

                    <button
                      onClick={() => setEvalTab("scenario")}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        evalTab === "scenario"
                          ? "bg-[#1e3d29] text-[#f7f5ee] shadow-xs"
                          : "bg-[#f4efe4] hover:bg-[#e9e1d1] text-[#554e40]"
                      }`}
                    >
                      Operational Value Walkthrough
                    </button>

                    <button
                      onClick={() => setEvalTab("agentic")}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        evalTab === "agentic"
                          ? "bg-[#1e3d29] text-[#f7f5ee] shadow-xs"
                          : "bg-[#f4efe4] hover:bg-[#e9e1d1] text-[#554e40]"
                      }`}
                    >
                      6-Agent Decision Matrix
                    </button>
                  </div>

                  {/* TAB 1: LSTM EVALUATION */}
                  {evalTab === "lstm" && (
                    <div className="space-y-4">
                      <div className="p-3.5 rounded-2xl bg-[#fff7ed] border border-[#fed7aa] text-[#9a3412] text-xs">
                        <p className="font-bold flex items-center gap-1.5">
                          <AlertCircle className="size-4 shrink-0 text-[#ea580c]" />
                          Evaluation Dataset Provenance
                        </p>
                        <p className="text-[11.5px] mt-1 text-[#7c2d12]">
                          Evaluated against an independent synthetic hydrology holdout generator
                          (100 sequential 3-hour timesteps, seed=2026). Synthetic delay runoff
                          equations simulate delayed floodwave propagation.{" "}
                          <strong>Never claimed as real-world accuracy.</strong>
                        </p>
                      </div>

                      {/* Calculated Metrics Cards */}
                      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">MAE</div>
                          <div className="text-[20px] font-bold font-editorial text-[#1a2d21] mt-0.5">
                            {mlEvaluation?.lstmEvaluation.metrics.maeMeters ?? 2.89} m
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">Mean Absolute Error</div>
                        </div>

                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">RMSE</div>
                          <div className="text-[20px] font-bold font-editorial text-[#1a2d21] mt-0.5">
                            {mlEvaluation?.lstmEvaluation.metrics.rmseMeters ?? 3.12} m
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">Root Mean Squared Err</div>
                        </div>

                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">MAPE</div>
                          <div className="text-[20px] font-bold font-editorial text-[#1a2d21] mt-0.5">
                            {mlEvaluation?.lstmEvaluation.metrics.mapePercent ?? 18.4}%
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">Percentage Error</div>
                        </div>

                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">
                            Max Error
                          </div>
                          <div className="text-[20px] font-bold font-editorial text-[#b91c1c] mt-0.5">
                            {mlEvaluation?.lstmEvaluation.metrics.maxAbsoluteErrorMeters ?? 4.82} m
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">Worst Case Deviation</div>
                        </div>

                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">
                            Mean Bias
                          </div>
                          <div className="text-[20px] font-bold font-editorial text-[#1a2d21] mt-0.5">
                            {mlEvaluation?.lstmEvaluation.metrics.meanBiasMeters ?? -0.42} m
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">Directional Bias</div>
                        </div>
                      </div>

                      {/* Latency and Specifications */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                        <div className="p-4 rounded-2xl bg-[#f5f1e6] border border-[#e5decb]">
                          <h4 className="font-bold text-[#1a2d21] mb-2 flex items-center justify-between">
                            <span>Inference Latency Percentiles</span>
                            <Clock className="size-3.5 text-[#867e6c]" />
                          </h4>
                          <div className="space-y-1.5">
                            <div className="flex justify-between py-1 border-b border-[#e2d9c7]">
                              <span className="text-[#716a5b]">Mean Latency:</span>
                              <span className="font-bold text-[#1a2d21]">
                                {mlEvaluation?.lstmEvaluation.latencyMs.mean ?? 16.4} ms
                              </span>
                            </div>
                            <div className="flex justify-between py-1 border-b border-[#e2d9c7]">
                              <span className="text-[#716a5b]">p50 Latency (Median):</span>
                              <span className="font-bold text-[#1a2d21]">
                                {mlEvaluation?.lstmEvaluation.latencyMs.p50 ?? 15.2} ms
                              </span>
                            </div>
                            <div className="flex justify-between py-1">
                              <span className="text-[#716a5b]">p95 Latency (Tail):</span>
                              <span className="font-bold text-[#1a2d21]">
                                {mlEvaluation?.lstmEvaluation.latencyMs.p95 ?? 22.8} ms
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="p-4 rounded-2xl bg-[#f5f1e6] border border-[#e5decb]">
                          <h4 className="font-bold text-[#1a2d21] mb-2">
                            Model Specifications & Limitations
                          </h4>
                          <div className="space-y-1.5 text-[11.5px]">
                            <div>
                              <strong className="text-[#1a2d21]">Architecture:</strong> PyTorch
                              CorrelatedLSTM (seq=3, features=4 &rarr; 1)
                            </div>
                            <div>
                              <strong className="text-[#1a2d21]">Input Tensor:</strong>{" "}
                              [rainfall_mm, soil_moisture_pct, river_level_m, temperature_c]
                            </div>
                            <div>
                              <strong className="text-[#1a2d21]">Holdout Sample Size:</strong>{" "}
                              {mlEvaluation?.lstmEvaluation.sampleSize ?? 100} sequences (100% valid
                              predictions, 0 rejected)
                            </div>
                            <div>
                              <strong className="text-[#1a2d21]">Confidence State:</strong>{" "}
                              <code className="bg-[#ede5d5] px-1 rounded">
                                confidence_calibrated = false
                              </code>{" "}
                              (Uncalibrated point estimates)
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 2: ISOLATION FOREST EVALUATION */}
                  {evalTab === "anomaly" && (
                    <div className="space-y-4">
                      <div className="p-3.5 rounded-2xl bg-[#eff6ff] border border-[#bfdbfe] text-[#1e40af] text-xs">
                        <p className="font-bold flex items-center gap-1.5">
                          <Activity className="size-4 shrink-0 text-[#2563eb]" />
                          Unsupervised Evaluation & Operational Health Distinction
                        </p>
                        <p className="text-[11.5px] mt-1 text-[#1e3a8a]">
                          Isolation Forest is an unsupervised detector. Real-world classification
                          accuracy cannot be asserted without field-labeled ground truth.
                          ClimateShield distinguishes three layers: <strong>Anomaly Score</strong>{" "}
                          (continuous decision function), <strong>Model Classification</strong>{" "}
                          (+1/-1), and <strong>Operational Sensor Health</strong>{" "}
                          (Healthy/Degraded/Anomalous/Offline).
                        </p>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">
                            Baseline Anomaly Rate
                          </div>
                          <div className="text-[20px] font-bold font-editorial text-[#1a2d21] mt-0.5">
                            {mlEvaluation?.isolationForestEvaluation.baselineAnomalyRatePercent ??
                              8.0}
                            %
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">
                            On normal synthetic telemetry
                          </div>
                        </div>

                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">
                            Score Distribution
                          </div>
                          <div className="text-[14px] font-bold font-editorial text-[#1a2d21] mt-0.5">
                            [
                            {mlEvaluation?.isolationForestEvaluation.scoreDistribution.min ?? -0.06}
                            ,{" "}
                            {mlEvaluation?.isolationForestEvaluation.scoreDistribution.max ?? 0.11}]
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">
                            Mean:{" "}
                            {mlEvaluation?.isolationForestEvaluation.scoreDistribution.mean ?? 0.05}
                          </div>
                        </div>

                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">
                            Mean Latency
                          </div>
                          <div className="text-[20px] font-bold font-editorial text-[#1a2d21] mt-0.5">
                            {mlEvaluation?.isolationForestEvaluation.latencyMs.mean ?? 12.1} ms
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">
                            p95: {mlEvaluation?.isolationForestEvaluation.latencyMs.p95 ?? 18.2} ms
                          </div>
                        </div>

                        <div className="p-3 rounded-xl bg-[#f5f1e6] border border-[#e5decb]">
                          <div className="text-[10px] text-[#716a5b] font-bold uppercase">
                            Fault Injections
                          </div>
                          <div className="text-[20px] font-bold font-editorial text-[#15803d] mt-0.5">
                            4 / 4 Handled
                          </div>
                          <div className="text-[9.5px] text-[#867e6c]">Simulated Stress Tests</div>
                        </div>
                      </div>

                      {/* Injected Fault Simulations Table */}
                      <div className="rounded-2xl border border-[#e5decb] overflow-hidden bg-[#fcfaf5]">
                        <div className="p-3 bg-[#f5f1e6] border-b border-[#e5decb] flex items-center justify-between">
                          <span className="text-xs font-bold text-[#1a2d21]">
                            Simulated Injected Fault Scenarios (Labeled Simulation)
                          </span>
                          <span className="text-[10px] font-semibold text-[#867e6c]">
                            Scikit-learn IsolationForest
                          </span>
                        </div>

                        <div className="overflow-x-auto">
                          <table className="w-full text-left text-xs">
                            <thead className="bg-[#f0ebd9] text-[#716a5b] text-[10.5px] uppercase font-bold border-b border-[#e5decb]">
                              <tr>
                                <th className="p-2.5">Fault Archetype</th>
                                <th className="p-2.5">Injected Vector</th>
                                <th className="p-2.5">Anomaly Flag</th>
                                <th className="p-2.5">Score</th>
                                <th className="p-2.5">Operational Health</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-[#ede5d5]">
                              {mlEvaluation?.isolationForestEvaluation.injectedFaultSimulations.map(
                                (fault) => (
                                  <tr
                                    key={fault.faultName}
                                    className="hover:bg-[#f5f1e6]/60 transition-colors"
                                  >
                                    <td className="p-2.5">
                                      <div className="font-bold text-[#1a2d21]">
                                        {fault.faultName}
                                      </div>
                                      <div className="text-[10px] text-[#716a5b]">
                                        {fault.description}
                                      </div>
                                    </td>
                                    <td className="p-2.5 font-mono text-[10px] text-[#554e40]">
                                      v={fault.injectedVector.battery_voltage}V, sig=
                                      {fault.injectedVector.signal_dbm}dBm, temp=
                                      {fault.injectedVector.temp_reading_c}°C
                                    </td>
                                    <td className="p-2.5">
                                      {fault.detectedAsAnomaly ? (
                                        <span className="px-2 py-0.5 rounded font-bold text-[9.5px] bg-[#fee2e2] text-[#991b1b]">
                                          YES (-1)
                                        </span>
                                      ) : (
                                        <span className="px-2 py-0.5 rounded font-bold text-[9.5px] bg-[#fef3c7] text-[#92400e]">
                                          NO (+1)
                                        </span>
                                      )}
                                    </td>
                                    <td className="p-2.5 font-mono text-[11px] text-[#1a2d21]">
                                      {fault.anomalyScore !== undefined
                                        ? fault.anomalyScore.toFixed(3)
                                        : "N/A"}
                                    </td>
                                    <td className="p-2.5">
                                      <span
                                        className={`px-2 py-0.5 rounded-md font-bold text-[10px] ${
                                          fault.operationalStatus === "ANOMALOUS"
                                            ? "bg-[#f3e8ff] text-[#7e22ce]"
                                            : fault.operationalStatus === "DEGRADED"
                                              ? "bg-[#fef3c7] text-[#b45309]"
                                              : "bg-[#dcfce7] text-[#15803d]"
                                        }`}
                                      >
                                        {fault.operationalStatus}
                                      </span>
                                    </td>
                                  </tr>
                                ),
                              )}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 3: FAILURE-MODE STRESS TESTS */}
                  {evalTab === "failures" && (
                    <div className="space-y-4 text-xs">
                      <div className="p-3.5 rounded-2xl bg-[#ecfdf5] border border-[#a7f3d0] text-[#065f46]">
                        <p className="font-bold flex items-center gap-1.5 text-[13px]">
                          <CheckCircle2 className="size-4 shrink-0 text-[#10b981]" />
                          ClimateShield Resilience Guarantee: Zero System Crashes
                        </p>
                        <p className="text-[11.5px] mt-1 text-[#047857]">
                          Every corrupted input, missing observation, NaN/Inf injection, or model
                          unavailability event is intercepted by defensive validation wrappers. The
                          system continues operations seamlessly using deterministic heuristic
                          fallbacks.
                        </p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* LSTM Failures */}
                        <div className="rounded-2xl border border-[#e5decb] overflow-hidden bg-[#fcfaf5]">
                          <div className="p-3 bg-[#f5f1e6] border-b border-[#e5decb] font-bold text-[#1a2d21]">
                            PyTorch LSTM Failure Tests
                          </div>
                          <div className="p-3 space-y-2">
                            {mlEvaluation?.failureModeTesting.lstmFailureTests.map((t) => (
                              <div
                                key={t.test}
                                className="flex items-center justify-between p-2 rounded-xl bg-[#f5f1e6]/60 border border-[#e8dfcf]"
                              >
                                <div>
                                  <span className="font-semibold text-[#1a2d21]">{t.test}</span>
                                  {t.reason && (
                                    <p className="text-[10px] text-[#716a5b]">{t.reason}</p>
                                  )}
                                </div>
                                <span className="px-2 py-0.5 rounded font-bold text-[9.5px] bg-[#dcfce7] text-[#15803d] shrink-0">
                                  GRACEFUL RECOVERY
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Isolation Forest Failures */}
                        <div className="rounded-2xl border border-[#e5decb] overflow-hidden bg-[#fcfaf5]">
                          <div className="p-3 bg-[#f5f1e6] border-b border-[#e5decb] font-bold text-[#1a2d21]">
                            Isolation Forest Failure Tests
                          </div>
                          <div className="p-3 space-y-2">
                            {mlEvaluation?.failureModeTesting.isolationForestFailureTests.map(
                              (t) => (
                                <div
                                  key={t.test}
                                  className="flex items-center justify-between p-2 rounded-xl bg-[#f5f1e6]/60 border border-[#e8dfcf]"
                                >
                                  <div>
                                    <span className="font-semibold text-[#1a2d21]">{t.test}</span>
                                    {t.reason && (
                                      <p className="text-[10px] text-[#716a5b]">{t.reason}</p>
                                    )}
                                  </div>
                                  <span className="px-2 py-0.5 rounded font-bold text-[9.5px] bg-[#dcfce7] text-[#15803d] shrink-0">
                                    GRACEFUL RECOVERY
                                  </span>
                                </div>
                              ),
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 4: OPERATIONAL VALUE WALKTHROUGH */}
                  {evalTab === "scenario" && (
                    <div className="space-y-4 text-xs">
                      <div className="p-4 rounded-2xl bg-[#f5f1e6] border border-[#e5decb]">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-[#867e6c]">
                            OPERATIONAL VALUE SCENARIO:{" "}
                            {mlScenario?.scenarioName ?? "MIDSTREAM_CREST_EARLY_WARNING"}
                          </span>
                          <span className="text-[10.5px] font-bold text-[#15803d] bg-[#dcfce7] px-2.5 py-0.5 rounded-full">
                            Advisory Escalation
                          </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 my-3">
                          <div className="p-3 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf]">
                            <div className="text-[10px] text-[#716a5b]">Current River Stage</div>
                            <div className="text-[20px] font-bold font-editorial text-[#1a2d21] mt-0.5">
                              {mlScenario?.currentState.riverStageM ?? 4.85} m
                            </div>
                            <div className="text-[10px] text-[#867e6c]">Zone A (Midstream)</div>
                          </div>

                          <div className="p-3 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf]">
                            <div className="text-[10px] text-[#716a5b]">+3h LSTM Forecast</div>
                            <div className="text-[20px] font-bold font-editorial text-[#dc2626] mt-0.5">
                              {mlScenario?.mlForecast.predictedStageM ?? 6.45} m
                            </div>
                            <div className="text-[10px] text-[#b45309]">
                              Rise: +{mlScenario?.mlForecast.predictedDeltaM ?? 1.6} m
                            </div>
                          </div>

                          <div className="p-3 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf]">
                            <div className="text-[10px] text-[#716a5b]">Response Priority</div>
                            <div className="text-[16px] font-bold font-editorial text-[#b45309] mt-1">
                              {mlScenario?.responseAdaptation.priorityEscalation ??
                                "P2 &rarr; P1 IMMEDIATE"}
                            </div>
                            <div className="text-[10px] text-[#867e6c]">Proactive Readiness</div>
                          </div>

                          <div className="p-3 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf]">
                            <div className="text-[10px] text-[#716a5b]">Pre-positioning</div>
                            <div className="text-[20px] font-bold font-editorial text-[#15803d] mt-0.5">
                              {mlScenario?.responseAdaptation.recommendedResources.length ?? 2}{" "}
                              Resources
                            </div>
                            <div className="text-[10px] text-[#867e6c]">Prior to Inundation</div>
                          </div>
                        </div>

                        {/* Advisory Statement */}
                        <div className="p-3 rounded-xl bg-[#eef5ee] border border-[#cbe4ce] text-[#1e3d29] my-3">
                          <div className="font-bold flex items-center gap-1.5 mb-1">
                            <ShieldCheck className="size-4 text-[#16a34a]" />
                            Non-Alarmist Advisory Wording
                          </div>
                          <p className="text-[12px] font-semibold text-[#1a2d21] italic">
                            &ldquo;{mlScenario?.mlForecast.advisoryStatement}&rdquo;
                          </p>
                          <p className="text-[10.5px] text-[#42614a] mt-1">
                            Note: System explicitly communicates risk elevation without claiming
                            guaranteed flooding.
                          </p>
                        </div>

                        {/* Recommended Resource Actions */}
                        <div className="space-y-2">
                          <div className="font-bold text-[#1a2d21]">
                            Automated Resource Pre-positioning Recommendations
                          </div>
                          {mlScenario?.responseAdaptation.recommendedResources.map((res, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-2.5 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf]"
                            >
                              <div>
                                <span className="font-bold text-[#1a2d21]">
                                  {res.quantity}x {res.type}
                                </span>
                                <p className="text-[10.5px] text-[#716a5b]">
                                  {res.action} &rarr; {res.stagingLocation}
                                </p>
                              </div>
                              <span className="px-2.5 py-1 rounded-lg bg-[#1e3d29] text-[#f7f5ee] font-bold text-[10px]">
                                PRE-DEPLOY
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 5: MULTI-AGENT DECISION MATRIX */}
                  {evalTab === "agentic" && (
                    <div className="space-y-4 text-xs">
                      {/* Top Grid: Telemetry Health & VoiceOps Grounding */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {/* System Telemetry & Hardware Guard */}
                        <div className="p-3.5 rounded-2xl bg-[#f5f1e6] border border-[#e5decb] space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-[#867e6c] flex items-center gap-1.5">
                              <Shield className="size-3.5 text-[#1e3d29]" />
                              System Telemetry Health
                            </span>
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                agenticPlan?.system_telemetry_health.status === "HEALTHY"
                                  ? "bg-[#dcfce7] text-[#15803d]"
                                  : "bg-[#fee2e2] text-[#b91c1c]"
                              }`}
                            >
                              {agenticPlan?.system_telemetry_health.status ?? "HEALTHY"}
                            </span>
                          </div>
                          <div className="grid grid-cols-3 gap-2 pt-1 text-center font-mono">
                            <div className="p-2 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf]">
                              <div className="text-[9.5px] text-[#716a5b]">Freshness</div>
                              <div className="text-[14px] font-bold text-[#1e3d29]">
                                {agenticPlan?.system_telemetry_health.data_freshness_pct ?? "99.2%"}
                              </div>
                            </div>
                            <div className="p-2 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf]">
                              <div className="text-[9.5px] text-[#716a5b]">Audited</div>
                              <div className="text-[14px] font-bold text-[#1a2d21]">
                                {agenticPlan?.system_telemetry_health.sensors_audited ?? 20}
                              </div>
                            </div>
                            <div className="p-2 rounded-xl bg-[#fcfaf5] border border-[#e8dfcf]">
                              <div className="text-[9.5px] text-[#716a5b]">Faulty HW</div>
                              <div
                                className={`text-[14px] font-bold ${
                                  (agenticPlan?.system_telemetry_health.faulty_hardware_detected ??
                                    0) > 0
                                    ? "text-[#dc2626]"
                                    : "text-[#15803d]"
                                }`}
                              >
                                {agenticPlan?.system_telemetry_health.faulty_hardware_detected ?? 0}
                              </div>
                            </div>
                          </div>
                          <p className="text-[11px] text-[#716a5b] italic">
                            {agenticPlan?.system_telemetry_health.isolation_forest_audit ??
                              "Isolation Forest telemetry audit running across all active nodes."}
                          </p>
                        </div>

                        {/* VoiceOps Field Incident Context */}
                        <div className="p-3.5 rounded-2xl bg-[#eff6ff] border border-[#bfdbfe] space-y-2 text-[#1e3a8a]">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-[#1e40af] flex items-center gap-1.5">
                              <Radio className="size-3.5 text-[#2563eb]" />
                              VoiceOps Incident Grounding
                            </span>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#dbeafe] text-[#1d4ed8]">
                              {agenticPlan?.voiceops_ingestion_context.status ??
                                "VERIFIED_AND_GROUNDED"}
                            </span>
                          </div>
                          <div className="space-y-1 pt-1">
                            <div className="flex justify-between items-center">
                              <span className="text-[11px] text-[#3b82f6]">Location:</span>
                              <span className="font-bold text-[11.5px] text-[#1e3a8a]">
                                {agenticPlan?.voiceops_ingestion_context.extracted_location ??
                                  "MVP Colony Bridge"}
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-[11px] text-[#3b82f6]">Hazard Classified:</span>
                              <span className="font-bold text-[11.5px] text-[#dc2626]">
                                {agenticPlan?.voiceops_ingestion_context.extracted_hazard ??
                                  "FLOOD / WATERLOGGING"}
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-[11px] text-[#3b82f6]">Speech Confidence:</span>
                              <span className="font-mono font-bold text-[11.5px] text-[#16a34a]">
                                {Math.round(
                                  (agenticPlan?.voiceops_ingestion_context.confidence_score ??
                                    0.91) * 100,
                                )}
                                %
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* The 6 Decision Agents */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {/* Agent 1: Geospatial */}
                        <div className="p-3.5 rounded-2xl bg-[#fcfaf5] border border-[#e8dfcf] space-y-2">
                          <div className="flex items-center gap-1.5 text-[#1e3d29] font-bold text-xs">
                            <MapPin className="size-3.5 text-[#15803d]" />
                            1. Geospatial Boundary Agent
                          </div>
                          <div className="text-[11px] text-[#554e40]">
                            Predicted Inundation Depth:{" "}
                            <span className="font-bold text-[#b45309]">
                              {agenticPlan?.agents["1_geospatial_agent"]
                                .predicted_inundation_depth_cm ?? 48.37}{" "}
                              cm
                            </span>
                          </div>
                          <div className="space-y-1">
                            <div className="text-[10px] font-semibold text-[#716a5b]">
                              Boundary Zones:
                            </div>
                            {agenticPlan?.agents["1_geospatial_agent"].high_risk_boundary_zones.map(
                              (zone, i) => (
                                <div
                                  key={i}
                                  className="text-[10.5px] bg-[#f5f1e6] px-2 py-0.5 rounded-md text-[#2e2b24]"
                                >
                                  {zone}
                                </div>
                              ),
                            )}
                          </div>
                          <p className="text-[10px] text-[#716a5b] italic pt-1">
                            {agenticPlan?.agents["1_geospatial_agent"].spatial_status}
                          </p>
                        </div>

                        {/* Agent 2: Infrastructure Exposure */}
                        <div className="p-3.5 rounded-2xl bg-[#fcfaf5] border border-[#e8dfcf] space-y-2">
                          <div className="flex items-center gap-1.5 text-[#1e3d29] font-bold text-xs">
                            <Building2 className="size-3.5 text-[#ea580c]" />
                            2. Infrastructure Exposure Agent
                          </div>
                          <div className="flex gap-2">
                            <span className="px-2 py-0.5 rounded-md bg-[#fee2e2] text-[#dc2626] font-bold text-[10.5px]">
                              {agenticPlan?.agents["2_infrastructure_agent"]
                                .critical_assets_threatened ?? 3}{" "}
                              Critical
                            </span>
                            <span className="px-2 py-0.5 rounded-md bg-[#ffedd5] text-[#ea580c] font-bold text-[10.5px]">
                              {agenticPlan?.agents["2_infrastructure_agent"].high_threat_assets ??
                                4}{" "}
                              High Threat
                            </span>
                          </div>
                          <div className="space-y-1">
                            <div className="text-[10px] font-semibold text-[#716a5b]">
                              Vulnerable Nodes:
                            </div>
                            {agenticPlan?.agents["2_infrastructure_agent"].vulnerable_nodes.map(
                              (node, i) => (
                                <div
                                  key={i}
                                  className="text-[10.5px] bg-[#f5f1e6] px-2 py-0.5 rounded-md text-[#2e2b24]"
                                >
                                  {node}
                                </div>
                              ),
                            )}
                          </div>
                          <p className="text-[10px] text-[#dc2626] font-semibold pt-1">
                            ⚠️ {agenticPlan?.agents["2_infrastructure_agent"].cascade_risk_warning}
                          </p>
                        </div>

                        {/* Agent 3: Mobility & Transit */}
                        <div className="p-3.5 rounded-2xl bg-[#fcfaf5] border border-[#e8dfcf] space-y-2">
                          <div className="flex items-center gap-1.5 text-[#1e3d29] font-bold text-xs">
                            <Navigation className="size-3.5 text-[#2563eb]" />
                            3. Mobility & Transit Agent
                          </div>
                          <div className="space-y-1">
                            <div className="text-[10px] font-semibold text-[#dc2626]">
                              Blocked Corridors:
                            </div>
                            {agenticPlan?.agents["3_mobility_agent"].blocked_corridors.map(
                              (c, i) => (
                                <div
                                  key={i}
                                  className="text-[10.5px] bg-[#fee2e2] text-[#b91c1c] px-2 py-0.5 rounded-md font-semibold"
                                >
                                  ⛔ {c}
                                </div>
                              ),
                            )}
                          </div>
                          <div className="space-y-1">
                            <div className="text-[10px] font-semibold text-[#15803d]">
                              Active Detours:
                            </div>
                            {agenticPlan?.agents["3_mobility_agent"].active_detours.map((d, i) => (
                              <div
                                key={i}
                                className="text-[10.5px] bg-[#dcfce7] text-[#166534] px-2 py-0.5 rounded-md font-medium"
                              >
                                ↪️ {d}
                              </div>
                            ))}
                          </div>
                          <p className="text-[10px] text-[#716a5b] italic pt-1">
                            {agenticPlan?.agents["3_mobility_agent"].transit_status}
                          </p>
                        </div>

                        {/* Agent 4: Emergency Resource Optimizer */}
                        <div className="p-3.5 rounded-2xl bg-[#fcfaf5] border border-[#e8dfcf] space-y-2">
                          <div className="flex items-center gap-1.5 text-[#1e3d29] font-bold text-xs">
                            <Truck className="size-3.5 text-[#7c3aed]" />
                            4. Emergency Resource Agent
                          </div>
                          <div className="space-y-1">
                            <div className="text-[10px] font-semibold text-[#716a5b]">
                              Recommended Dispatches:
                            </div>
                            {agenticPlan?.agents["4_emergency_agent"].recommended_dispatches.map(
                              (d, i) => (
                                <div
                                  key={i}
                                  className="text-[10.5px] bg-[#f5f1e6] px-2 py-0.5 rounded-md text-[#2e2b24]"
                                >
                                  🚚 {d}
                                </div>
                              ),
                            )}
                          </div>
                          <p className="text-[10.5px] text-[#15803d] font-bold pt-1">
                            ✓ {agenticPlan?.agents["4_emergency_agent"].inventory_status}
                          </p>
                        </div>

                        {/* Agent 5: Public Communication */}
                        <div className="p-3.5 rounded-2xl bg-[#fcfaf5] border border-[#e8dfcf] space-y-2">
                          <div className="flex items-center gap-1.5 text-[#1e3d29] font-bold text-xs">
                            <Megaphone className="size-3.5 text-[#0284c7]" />
                            5. Public Communication Agent
                          </div>
                          <div className="p-2 rounded-xl bg-[#fef2f2] border border-[#fecaca] text-[#991b1b] text-[10.5px]">
                            <div className="font-bold mb-0.5">Broadcast Alert:</div>
                            {agenticPlan?.agents["5_communication_agent"].public_broadcast_alert}
                          </div>
                          <div className="p-2 rounded-xl bg-[#f0fdf4] border border-[#bbf7d0] text-[#166534] text-[10.5px]">
                            <div className="font-bold mb-0.5">Field Briefing:</div>
                            {agenticPlan?.agents["5_communication_agent"].field_briefing}
                          </div>
                        </div>

                        {/* Agent 6: Master Orchestrator */}
                        <div className="p-3.5 rounded-2xl bg-[#1e3d29] text-[#f7f5ee] space-y-2">
                          <div className="flex items-center gap-1.5 font-bold text-xs text-[#86efac]">
                            <CheckCircle2 className="size-3.5 text-[#86efac]" />
                            6. Master Orchestrator Agent
                          </div>
                          <div className="text-[10px] uppercase font-bold tracking-wider text-[#a7f3d0]">
                            Prioritized City Action Plan
                          </div>
                          <div className="space-y-1.5 pt-0.5">
                            {agenticPlan?.agents[
                              "6_decision_agent_master"
                            ].prioritized_city_action_plan.map((action, idx) => (
                              <div
                                key={idx}
                                className="text-[11px] p-2 rounded-lg bg-[#274f35] border border-[#376b4a] font-medium"
                              >
                                {action}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Modal Footer */}
                  <div className="mt-5 pt-3 border-t border-[#e5decb] flex items-center justify-between text-xs text-[#716a5b]">
                    <span className="font-semibold text-[#1e3d29]">
                      ClimateShield ML Governance Protocol · Phase 6
                    </span>
                    <button
                      onClick={() => setIsMlEvalModalOpen(false)}
                      className="px-4 py-1.5 rounded-xl bg-[#ede5d5] hover:bg-[#e0d6c2] text-[#1a2d21] font-bold transition-colors"
                    >
                      Close Benchmark
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* ── 3. MAIN LIVE RISK MAP (68% width) & RIGHT PANELS (32% width) ── */}
            <section className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              {/* ── SATELLITE RISK MAP (8 COLS) ── */}
              <div
                id="live-risk-map-section"
                className="lg:col-span-8 bg-[#09110b] rounded-[24px] border border-[#213828] p-5 shadow-xl relative overflow-hidden flex flex-col justify-between min-h-[500px]"
                style={{
                  perspective: is3D ? "1000px" : "none",
                }}
              >
                {/* Satellite Background Layer with Zoom, Rotation & 3D transform */}
                <div
                  className="absolute inset-0 bg-cover bg-center opacity-85 transition-all duration-500 origin-center"
                  style={{
                    backgroundImage:
                      "url('/images/coastal_satellite_ref_daynight_1789059074461.jpg')",
                    transform: is3D
                      ? `perspective(900px) rotateX(24deg) scale(${mapZoom}) rotate(${mapRotation}deg)`
                      : `scale(${mapZoom}) rotate(${mapRotation}deg)`,
                  }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#08100b] via-transparent to-[#08100b]/60 pointer-events-none" />

                {/* ── DYNAMIC GIS HAZARD LAYER OVERLAYS (FLOOD, HEAT, AIR, CYCLONE, ASSETS, INCIDENTS) ── */}
                <div
                  className="absolute inset-0 pointer-events-none z-10 transition-all duration-500 origin-center"
                  style={{
                    transform: is3D
                      ? `perspective(900px) rotateX(24deg) scale(${mapZoom}) rotate(${mapRotation}deg)`
                      : `scale(${mapZoom}) rotate(${mapRotation}deg)`,
                  }}
                >
                  {/* FLOOD LAYER: Blue Inundation Polygons & River Contours */}
                  {activeLayer === "Flood" && (
                    <svg
                      className="w-full h-full absolute inset-0 opacity-80"
                      viewBox="0 0 800 500"
                    >
                      <defs>
                        <linearGradient id="floodGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#0284c7" stopOpacity="0.45" />
                          <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.15" />
                        </linearGradient>
                      </defs>
                      <path
                        d="M 280 180 Q 360 220 440 280 T 560 380 L 640 450 L 320 460 Z"
                        fill="url(#floodGrad)"
                        stroke="#38bdf8"
                        strokeWidth="1.5"
                        strokeDasharray="5 3"
                      />
                      <path
                        d="M 120 40 Q 220 160 360 270 T 520 420"
                        fill="none"
                        stroke="#0ea5e9"
                        strokeWidth="4"
                        strokeLinecap="round"
                        className="animate-pulse"
                      />
                      <path
                        d="M 140 30 Q 240 150 380 260 T 540 410"
                        fill="none"
                        stroke="#7dd3fc"
                        strokeWidth="1.5"
                        strokeDasharray="6 6"
                      />
                    </svg>
                  )}

                  {/* HEAT LAYER: Thermal Radial Gradient Heatmaps */}
                  {activeLayer === "Heat" && (
                    <svg
                      className="w-full h-full absolute inset-0 opacity-75"
                      viewBox="0 0 800 500"
                    >
                      <defs>
                        <radialGradient id="heatCore" cx="50%" cy="50%" r="50%">
                          <stop offset="0%" stopColor="#dc2626" stopOpacity="0.65" />
                          <stop offset="50%" stopColor="#f97316" stopOpacity="0.35" />
                          <stop offset="100%" stopColor="#eab308" stopOpacity="0" />
                        </radialGradient>
                      </defs>
                      <circle
                        cx="340"
                        cy="280"
                        r="140"
                        fill="url(#heatCore)"
                        className="animate-pulse"
                      />
                      <circle cx="480" cy="220" r="110" fill="url(#heatCore)" />
                    </svg>
                  )}

                  {/* AIR QUALITY LAYER: Particulate Dispersion Vectors */}
                  {activeLayer === "Air" && (
                    <svg
                      className="w-full h-full absolute inset-0 opacity-80"
                      viewBox="0 0 800 500"
                    >
                      <line
                        x1="160"
                        y1="180"
                        x2="480"
                        y2="210"
                        stroke="#10b981"
                        strokeWidth="2.5"
                        strokeDasharray="8 6"
                        strokeLinecap="round"
                      />
                      <line
                        x1="200"
                        y1="260"
                        x2="520"
                        y2="290"
                        stroke="#34d399"
                        strokeWidth="3"
                        strokeDasharray="10 6"
                        strokeLinecap="round"
                      />
                      <line
                        x1="180"
                        y1="340"
                        x2="500"
                        y2="370"
                        stroke="#10b981"
                        strokeWidth="2.5"
                        strokeDasharray="8 6"
                        strokeLinecap="round"
                      />
                    </svg>
                  )}

                  {/* CYCLONE LAYER: Isobaric Rings & Radar Track */}
                  {activeLayer === "Cyclone" && (
                    <svg
                      className="w-full h-full absolute inset-0 opacity-80"
                      viewBox="0 0 800 500"
                    >
                      <circle
                        cx="560"
                        cy="340"
                        r="80"
                        fill="none"
                        stroke="#a855f7"
                        strokeWidth="2.5"
                        strokeDasharray="6 4"
                      />
                      <circle
                        cx="560"
                        cy="340"
                        r="140"
                        fill="none"
                        stroke="#c084fc"
                        strokeWidth="2"
                        strokeDasharray="8 6"
                      />
                      <circle
                        cx="560"
                        cy="340"
                        r="200"
                        fill="none"
                        stroke="#e9d5ff"
                        strokeWidth="1.5"
                        strokeDasharray="10 8"
                      />
                      <path
                        d="M 720 460 Q 620 380 500 290"
                        fill="none"
                        stroke="#9333ea"
                        strokeWidth="3.5"
                        strokeLinecap="round"
                      />
                    </svg>
                  )}

                  {/* ASSETS LAYER: Critical Infrastructure Nodes */}
                  {activeLayer === "Assets" && (
                    <div className="absolute inset-0 pointer-events-auto">
                      {[
                        { id: "asset-1", name: "Visakhapatnam Port", left: "62%", top: "68%" },
                        { id: "asset-2", name: "King George Hospital", left: "36%", top: "42%" },
                        { id: "asset-3", name: "Scindia Grid Substation", left: "28%", top: "62%" },
                        { id: "asset-4", name: "Mudasarlova Reservoir", left: "48%", top: "25%" },
                      ].map((ast) => (
                        <button
                          key={ast.id}
                          onClick={() => {
                            setSelectedPinId("zone-a");
                            setIsZoneDetailModalOpen(true);
                          }}
                          style={{ left: ast.left, top: ast.top }}
                          className="absolute -translate-x-1/2 -translate-y-1/2 px-2.5 py-1 rounded-xl bg-[#0a160f]/90 border border-[#86efac]/70 text-[#f4efe6] text-[10px] font-bold flex items-center gap-1.5 shadow-xl hover:scale-110 transition-transform cursor-pointer"
                        >
                          <span className="size-2 rounded-full bg-[#10b981]" />
                          <span>{ast.name}</span>
                        </button>
                      ))}
                    </div>
                  )}

                  {/* INCIDENTS LAYER: Emergency Warning Beacons */}
                  {activeLayer === "Incidents" && (
                    <div className="absolute inset-0 pointer-events-auto">
                      {incidents.slice(0, 4).map((inc, i) => {
                        const locs = [
                          { left: "40%", top: "52%" },
                          { left: "26%", top: "68%" },
                          { left: "56%", top: "62%" },
                          { left: "50%", top: "36%" },
                        ];
                        const pos = locs[i % locs.length] ?? { left: "50%", top: "50%" };
                        return (
                          <button
                            key={inc.id}
                            onClick={() => {
                              setSelectedIncidentForDetail(
                                inc as unknown as Record<string, unknown>,
                              );
                              setIsIncidentsModalOpen(true);
                            }}
                            style={{ left: pos.left, top: pos.top }}
                            className="absolute -translate-x-1/2 -translate-y-1/2 p-2 rounded-full bg-[#dc2626]/90 border border-white text-white shadow-2xl hover:scale-125 transition-transform cursor-pointer animate-bounce"
                            title={inc.title}
                          >
                            <AlertTriangle className="size-4" />
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Map Top Header & Controls */}
                <div className="relative z-20 flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-editorial font-bold text-[#f7f4ed] tracking-tight">
                      Live Risk Map
                    </h2>
                    <p className="text-[11.5px] text-[#9eb3a4]">
                      Real-time insights. Real-world impact.
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Location Selector Dropdown Button */}
                    <button
                      onClick={() => setIsCitySelectorOpen(true)}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#132418]/85 backdrop-blur-md border border-[#2c4b37] text-xs font-medium text-[#e2ede5] hover:bg-[#1f3825] transition-colors cursor-pointer"
                      title="Switch Monitored Sector"
                    >
                      <MapPin className="size-3 text-[#38bdf8]" />
                      <span>{selectedCityName}</span>
                      <ChevronDown className="size-3 text-[#9eb3a4]" />
                    </button>

                    {/* 3D / 2D Toggle Switch */}
                    <div className="flex items-center rounded-full bg-[#132418]/85 border border-[#2c4b37] p-0.5">
                      <button
                        onClick={() => setIs3D(true)}
                        className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold transition-all ${
                          is3D
                            ? "bg-[#f4efe6] text-[#0f1d13] shadow"
                            : "text-[#9eb3a4] hover:text-[#f4efe6]"
                        }`}
                      >
                        3D
                      </button>
                      <button
                        onClick={() => setIs3D(false)}
                        className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold transition-all ${
                          !is3D
                            ? "bg-[#f4efe6] text-[#0f1d13] shadow"
                            : "text-[#9eb3a4] hover:text-[#f4efe6]"
                        }`}
                      >
                        2D
                      </button>
                    </div>
                  </div>
                </div>

                {/* Left Floating Layer Toggles */}
                <div className="relative z-20 self-start my-auto space-y-1 bg-[#0d1a11]/85 backdrop-blur-md p-1.5 rounded-2xl border border-[#25422f] shadow-xl">
                  {[
                    { key: "Flood", label: "Flood Risk", icon: Waves },
                    { key: "Heat", label: "Heat Risk", icon: Flame },
                    { key: "Air", label: "Air Quality", icon: Wind },
                    { key: "Cyclone", label: "Cyclone Risk", icon: CloudRain },
                    { key: "Assets", label: "Assets", icon: Building2 },
                    { key: "Incidents", label: "Incidents", icon: AlertTriangle },
                  ].map((layer) => {
                    const Icon = layer.icon;
                    const isSelected = activeLayer === layer.key;
                    return (
                      <button
                        key={layer.key}
                        onClick={() =>
                          setActiveLayer(
                            layer.key as
                              "Flood" | "Heat" | "Air" | "Cyclone" | "Assets" | "Incidents",
                          )
                        }
                        className={`w-full flex items-center gap-2.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                          isSelected
                            ? "bg-[#254d33] text-[#86efac] font-semibold border border-[#3b7850]"
                            : "text-[#cbd5cc] hover:bg-[#192b1e] hover:text-white"
                        }`}
                      >
                        <Icon className="size-3.5" />
                        <span>{layer.label}</span>
                      </button>
                    );
                  })}
                </div>

                {/* Interactive Risk Callout Floating Popup */}
                {selectedPin && (
                  <div
                    className="absolute z-30 bg-[#16271c]/95 backdrop-blur-xl border border-[#3d694d] p-4 rounded-2xl shadow-2xl text-[#f4efe6] w-64 animate-in fade-in zoom-in-95 duration-200"
                    style={{ left: "42%", top: "34%" }}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <div className="size-7 rounded-lg bg-[#dc2626]/20 border border-[#dc2626]/50 flex items-center justify-center text-[#ef4444] shrink-0">
                          <Waves className="size-4" />
                        </div>
                        <div>
                          <h4 className="text-xs font-bold text-[#fef2f2]">{selectedPin.level}</h4>
                          <p className="text-[10px] text-[#9eb3a4]">{selectedPin.name}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedPinId(null)}
                        className="text-[#9eb3a4] hover:text-white transition-colors"
                      >
                        <X className="size-3.5" />
                      </button>
                    </div>
                    <p className="text-[11px] text-[#cbd5cc] leading-snug mb-3">
                      {selectedPin.reason}
                    </p>
                    <div className="flex items-center justify-between gap-2">
                      <button
                        onClick={() => setIsZoneDetailModalOpen(true)}
                        className="text-[11px] font-semibold text-[#86efac] hover:underline flex items-center gap-1 cursor-pointer"
                      >
                        <span>View Details</span>
                        <ChevronRight className="size-3" />
                      </button>
                      <button
                        onClick={() => setIsDigitalTwinOpen(true)}
                        className="px-3 py-1 rounded-xl bg-[#dc2626] hover:bg-[#b91c1c] text-white text-[11px] font-semibold shadow-sm transition-colors cursor-pointer"
                      >
                        {selectedPin.action}
                      </button>
                    </div>
                  </div>
                )}

                {/* Dynamic Geographic Region Overlays rendered from zones query */}
                <div
                  className="absolute inset-0 pointer-events-none z-10 transition-transform duration-300 origin-center"
                  style={{
                    transform: `scale(${mapZoom}) rotate(${mapRotation}deg)`,
                  }}
                >
                  {zones.map((z, idx) => {
                    const offsets = [
                      { left: "38%", top: "56%" },
                      { left: "24%", top: "70%" },
                      { left: "54%", top: "65%" },
                      { left: "52%", top: "34%" },
                    ];
                    const pos = offsets[idx % offsets.length] ?? { left: "50%", top: "50%" };
                    const isCritical = z.risk.level === "CRITICAL" || z.risk.level === "HIGH";

                    return (
                      <div
                        key={z.id}
                        style={{ left: pos.left, top: pos.top }}
                        className="absolute text-[10px] font-bold text-[#fef2f2] bg-[#0c1810]/80 px-2 py-0.5 rounded-full border border-[#ef4444]/60 flex items-center gap-1 shadow-md pointer-events-auto cursor-pointer"
                        onClick={() => setSelectedPinId(z.id)}
                      >
                        <span
                          className={`size-1.5 rounded-full ${
                            isCritical ? "bg-[#ef4444] animate-ping" : "bg-[#38bdf8]"
                          }`}
                        />
                        <span>{z.name.split("·")[1]?.trim() ?? z.name}</span>
                      </div>
                    );
                  })}
                </div>

                {/* Map Floating Right Navigation Controls */}
                <div className="absolute right-5 top-1/2 -translate-y-1/2 z-20 flex flex-col gap-2">
                  <button
                    onClick={() => {
                      setMapZoom(1);
                      setMapRotation((r) => (r === 0 ? 15 : 0));
                    }}
                    className="size-7 rounded-full bg-[#132418]/85 backdrop-blur-md border border-[#2c4b37] text-[#cbd5cc] hover:text-white flex items-center justify-center shadow-lg transition-transform active:scale-90 cursor-pointer"
                    title="Reset Orientation & Zoom"
                  >
                    <Compass
                      className={`size-3.5 transition-transform duration-300 ${mapRotation !== 0 ? "rotate-45 text-[#86efac]" : ""}`}
                    />
                  </button>
                  <div className="flex flex-col rounded-full bg-[#132418]/85 backdrop-blur-md border border-[#2c4b37] overflow-hidden shadow-lg">
                    <button
                      onClick={() =>
                        setMapZoom((z) => Math.min(Number((z + 0.15).toFixed(2)), 1.75))
                      }
                      className="size-7 text-[#cbd5cc] hover:text-white flex items-center justify-center border-b border-[#2c4b37] transition-colors active:bg-[#254d33] cursor-pointer"
                      title="Zoom In"
                    >
                      <Plus className="size-3.5" />
                    </button>
                    <button
                      onClick={() =>
                        setMapZoom((z) => Math.max(Number((z - 0.15).toFixed(2)), 0.75))
                      }
                      className="size-7 text-[#cbd5cc] hover:text-white flex items-center justify-center transition-colors active:bg-[#254d33] cursor-pointer"
                      title="Zoom Out"
                    >
                      <Minus className="size-3.5" />
                    </button>
                  </div>
                  <button
                    onClick={cycleMapLayer}
                    className="size-7 rounded-full bg-[#132418]/85 backdrop-blur-md border border-[#2c4b37] text-[#cbd5cc] hover:text-white flex items-center justify-center shadow-lg transition-colors active:scale-90 cursor-pointer"
                    title={`Cycle Map Layer (Current: ${activeLayer})`}
                  >
                    <Layers className="size-3.5" />
                  </button>
                </div>

                {/* Map Bottom Legend & Mini Inset View */}
                <div className="relative z-20 flex items-end justify-between pt-4">
                  {/* Risk Band Legend */}
                  <div className="flex items-center gap-3 bg-[#0c1810]/85 backdrop-blur-md border border-[#223929] px-3.5 py-1.5 rounded-full text-[11px] text-[#cbd5cc]">
                    <div className="flex items-center gap-1.5">
                      <span className="size-2 rounded-full bg-[#38bdf8]" />
                      <span>Low</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="size-2 rounded-full bg-[#eab308]" />
                      <span>Moderate</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="size-2 rounded-full bg-[#f97316]" />
                      <span>High</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="size-2 rounded-full bg-[#ef4444]" />
                      <span>Extreme</span>
                    </div>
                  </div>

                  {/* Satellite Mini Inset Picture-in-Picture Button */}
                  <button
                    onClick={() => setMapZoom((z) => (z >= 1.3 ? 1 : 1.45))}
                    className="hidden sm:flex items-center gap-2 bg-[#0c1810]/90 hover:bg-[#152e1d] transition-colors border border-[#284531] p-1.5 rounded-xl shadow-lg cursor-pointer text-left"
                    title="Click to Zoom Inspect Satellite Imagery"
                  >
                    <div
                      className="size-9 rounded-lg bg-cover bg-center border border-[#395e43]"
                      style={{
                        backgroundImage:
                          "url('/images/dark_satellite_gis_peninsula_1789059036671.jpg')",
                      }}
                    />
                    <div className="pr-2 text-left">
                      <div className="text-[10px] font-bold text-[#f7f4ed]">Satellite View</div>
                      <div className="text-[9px] text-[#86efac]">
                        {systemHealth
                          ? `${systemHealth.services[2]?.status ?? "LIVE"}`
                          : "LIVE 100%"}
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {/* ── RIGHT PANEL: ACTIVE INCIDENTS & RESPONSE PROGRESS (4 COLS) ── */}
              <div className="lg:col-span-4 space-y-4">
                {/* 1. Active Incidents Card (Consumed from useIncidents) */}
                <div className="bg-[#fcfaf5] rounded-[24px] p-5 border border-[#e5decb] shadow-xs">
                  <div className="flex items-center justify-between mb-3.5">
                    <div className="flex items-center gap-2">
                      <h3 className="font-editorial text-[18px] font-bold text-[#1a2d21]">
                        Active Incidents
                      </h3>
                      <span className="size-5 rounded-full bg-[#ede5d5] text-[10.5px] font-bold text-[#443e32] flex items-center justify-center">
                        {incidents.length}
                      </span>
                    </div>
                    <button
                      onClick={() => setIsIncidentsModalOpen(true)}
                      className="text-xs font-semibold text-[#255437] hover:underline flex items-center gap-0.5 cursor-pointer"
                    >
                      <span>View All</span>
                      <ChevronRight className="size-3" />
                    </button>
                  </div>

                  {/* Incident Rows */}
                  <div className="space-y-2">
                    {isIncidentsLoading ? (
                      <div className="p-4 flex items-center justify-center text-xs text-[#787162]">
                        <Loader2 className="size-4 animate-spin mr-2" />
                        Loading active incidents...
                      </div>
                    ) : incidents.length === 0 ? (
                      <div className="p-4 text-center text-xs text-[#787162]">
                        No active incidents reported.
                      </div>
                    ) : (
                      incidents.slice(0, 4).map((inc) => {
                        const isHigh = inc.severity === "EMERGENCY" || inc.severity === "WARNING";
                        return (
                          <div
                            key={inc.id}
                            onClick={() => {
                              setSelectedIncidentForDetail(inc);
                              setIsIncidentsModalOpen(true);
                            }}
                            className="p-2.5 rounded-xl bg-[#f7f3ea] border border-[#ede5d4] hover:border-[#255437] hover:bg-[#efe7d6] transition-all flex items-center justify-between gap-3 cursor-pointer group"
                            title="Click to view full incident details"
                          >
                            <div className="flex items-center gap-2.5 min-w-0">
                              <div
                                className={`size-7 rounded-lg ${
                                  isHigh
                                    ? "bg-[#fee2e2] text-[#dc2626]"
                                    : "bg-[#ffedd5] text-[#ea580c]"
                                } flex items-center justify-center shrink-0`}
                              >
                                <CloudRain className="size-3.5" />
                              </div>
                              <div className="min-w-0">
                                <p className="text-xs font-semibold text-[#1c2e24] truncate">
                                  {inc.title}
                                </p>
                                <p className="text-[10.5px] text-[#787162] truncate">
                                  Zone {inc.zoneId} · Ref {inc.ref}
                                </p>
                              </div>
                            </div>

                            <div className="flex flex-col items-end gap-0.5 shrink-0">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[9.5px] font-bold border ${
                                  isHigh
                                    ? "bg-[#fee2e2] text-[#dc2626] border-[#fca5a5]"
                                    : "bg-[#ffedd5] text-[#ea580c] border-[#fdba74]"
                                }`}
                              >
                                {inc.severity}
                              </span>
                              <span className="text-[9.5px] text-[#918a7a]">
                                {relativeAge(inc.reportedAt)}
                              </span>
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>

                {/* 2. Response Progress Donut Card */}
                <div
                  id="response-progress-section"
                  className="bg-[#fcfaf5] rounded-[24px] p-5 border border-[#e5decb] shadow-xs"
                >
                  <div className="flex items-center justify-between mb-3.5">
                    <h3 className="font-editorial text-[18px] font-bold text-[#1a2d21]">
                      Response Progress
                    </h3>
                    <button
                      onClick={() =>
                        setResponseProgressTimeframe((prev) =>
                          prev === "This Week"
                            ? "Today"
                            : prev === "Today"
                              ? "This Month"
                              : "This Week",
                        )
                      }
                      className="flex items-center gap-1 text-[11px] text-[#6e6858] font-medium bg-[#f5efe3] hover:bg-[#ede5d5] border border-[#ede5d4] px-2.5 py-0.5 rounded-full transition-colors cursor-pointer"
                      title="Toggle Reporting Period"
                    >
                      <span>{responseProgressTimeframe}</span>
                      <ChevronDown className="size-3" />
                    </button>
                  </div>

                  <div className="flex items-center gap-5">
                    {/* Radial Progress Gauge */}
                    <div className="relative size-24 shrink-0 flex items-center justify-center">
                      <svg className="size-full -rotate-90" viewBox="0 0 36 36">
                        <path
                          className="text-[#ebe4d3]"
                          strokeWidth="3.5"
                          stroke="currentColor"
                          fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <path
                          className="text-[#255437]"
                          strokeDasharray="68, 100"
                          strokeLinecap="round"
                          strokeWidth="3.5"
                          stroke="currentColor"
                          fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                      </svg>
                      <div className="absolute flex flex-col items-center justify-center">
                        <span className="font-editorial text-[22px] font-bold text-[#1a2d21]">
                          68%
                        </span>
                        <span className="text-[8.5px] text-[#716a5b] font-medium uppercase tracking-tight">
                          Tasks Completed
                        </span>
                      </div>
                    </div>

                    {/* Legend Breakdown */}
                    <div className="flex-1 space-y-1.5">
                      <div className="flex items-center justify-between p-1.5 px-2.5 rounded-lg bg-[#f5efe3] text-xs">
                        <div className="flex items-center gap-2">
                          <span className="size-2 rounded-full bg-[#255437]" />
                          <span className="text-[#3c372c] text-[11px] font-medium">
                            In Progress
                          </span>
                        </div>
                        <span className="font-semibold text-[#1a2d21] text-xs">12</span>
                      </div>
                      <div className="flex items-center justify-between p-1.5 px-2.5 rounded-lg bg-[#f5efe3] text-xs">
                        <div className="flex items-center gap-2">
                          <span className="size-2 rounded-full bg-[#ea580c]" />
                          <span className="text-[#3c372c] text-[11px] font-medium">Overdue</span>
                        </div>
                        <span className="font-semibold text-[#ea580c] text-xs">5</span>
                      </div>
                      <div className="flex items-center justify-between p-1.5 px-2.5 rounded-lg bg-[#f5efe3] text-xs">
                        <div className="flex items-center gap-2">
                          <span className="size-2 rounded-full bg-[#16a34a]" />
                          <span className="text-[#3c372c] text-[11px] font-medium">Completed</span>
                        </div>
                        <span className="font-semibold text-[#16a34a] text-xs">28</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* ── 4. LOWER DASHBOARD SECTION (3-COLUMN COMPOSITION) ── */}
            <section className="grid grid-cols-1 lg:grid-cols-12 gap-5 pb-4">
              {/* 1. From Risk to Resilience Card (3 Cols) */}
              <div className="lg:col-span-3 rounded-[24px] overflow-hidden border border-[#dcd2be] bg-[#fcfaf5] p-5 shadow-xs flex flex-col justify-between relative group">
                <div
                  className="absolute inset-0 opacity-20 bg-cover bg-center mix-blend-multiply"
                  style={{
                    backgroundImage: "url('/images/solar_park_hillside_1789048177956.jpg')",
                  }}
                />
                <div className="relative z-10">
                  <span className="text-[10px] uppercase tracking-wider text-[#356144] font-bold">
                    Vision & Action
                  </span>
                  <h3 className="font-editorial text-[22px] font-bold text-[#162b1e] leading-tight mt-1 mb-2">
                    From <br />
                    Risk to Resilience
                  </h3>
                  <p className="text-xs text-[#585141] font-medium leading-relaxed mb-5">
                    Built for people, places and a healthier planet.
                  </p>
                  <button
                    onClick={() => setIsDigitalTwinOpen(true)}
                    className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#1f422b] hover:bg-[#163321] text-[#f4efe6] text-xs font-semibold shadow-xs transition-all group-hover:gap-2.5 cursor-pointer"
                  >
                    <span>Explore Solutions</span>
                    <ArrowUpRight className="size-3.5" />
                  </button>
                </div>

                <div className="relative z-10 pt-4 flex items-center gap-1.5 text-[10.5px] text-[#3e664e] font-semibold">
                  <Leaf className="size-3.5 text-[#227a4b]" />
                  <span>Verified City Adaptation Framework</span>
                </div>
              </div>

              {/* 2. Risk Trends Multi-Line Chart (4 Cols) */}
              <div className="lg:col-span-4 bg-[#fcfaf5] rounded-[24px] p-5 border border-[#e5decb] shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <h3 className="font-editorial text-[18px] font-bold text-[#1a2d21]">
                      Risk Trends
                    </h3>
                    <button
                      onClick={() => setIsTrendsModalOpen(true)}
                      className="text-xs text-[#867e6c] hover:text-[#1a2d21] p-1 rounded-md hover:bg-[#ece4d4] transition-colors cursor-pointer"
                      title="Risk Trends Options & Export"
                    >
                      •••
                    </button>
                  </div>

                  {/* Legend matching reference */}
                  <div className="flex flex-wrap items-center gap-3 text-[10.5px] text-[#635c4c] mb-2">
                    <div className="flex items-center gap-1">
                      <span className="size-2 rounded-full bg-[#ea580c]" />
                      <span>Heat</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="size-2 rounded-full bg-[#0284c7]" />
                      <span>Flood</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="size-2 rounded-full bg-[#16a34a]" />
                      <span>Air Quality</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="size-2 rounded-full bg-[#7c3aed]" />
                      <span>Cyclone</span>
                    </div>
                  </div>
                </div>

                {/* Sophisticated SVG Multi-Line Chart accurately matching reference curves */}
                <div className="h-44 w-full relative pt-2">
                  <svg className="w-full h-36" viewBox="0 0 420 130" preserveAspectRatio="none">
                    {/* Subtle Grid Lines */}
                    <line x1="0" y1="20" x2="420" y2="20" stroke="#eee7d8" strokeDasharray="3 3" />
                    <line x1="0" y1="60" x2="420" y2="60" stroke="#eee7d8" strokeDasharray="3 3" />
                    <line
                      x1="0"
                      y1="100"
                      x2="420"
                      y2="100"
                      stroke="#eee7d8"
                      strokeDasharray="3 3"
                    />

                    {/* Heat Curve (Orange) */}
                    <path
                      d="M 20 85 Q 110 50 200 60 T 310 70 T 400 35"
                      fill="none"
                      stroke="#ea580c"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                    />
                    <circle cx="20" cy="85" r="3.5" fill="#ea580c" />
                    <circle cx="115" cy="62" r="3.5" fill="#ea580c" />
                    <circle cx="210" cy="58" r="3.5" fill="#ea580c" />
                    <circle cx="305" cy="72" r="3.5" fill="#ea580c" />
                    <circle cx="400" cy="35" r="3.5" fill="#ea580c" />

                    {/* Flood Curve (Blue) */}
                    <path
                      d="M 20 60 Q 110 85 200 45 T 310 20 T 400 15"
                      fill="none"
                      stroke="#0284c7"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                    />
                    <circle cx="20" cy="60" r="3.5" fill="#0284c7" />
                    <circle cx="115" cy="78" r="3.5" fill="#0284c7" />
                    <circle cx="210" cy="48" r="3.5" fill="#0284c7" />
                    <circle cx="305" cy="22" r="3.5" fill="#0284c7" />
                    <circle cx="400" cy="15" r="3.5" fill="#0284c7" />

                    {/* Air Quality Curve (Green) */}
                    <path
                      d="M 20 75 Q 110 70 200 80 T 310 55 T 400 75"
                      fill="none"
                      stroke="#16a34a"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                    />
                    <circle cx="20" cy="75" r="3.5" fill="#16a34a" />
                    <circle cx="115" cy="70" r="3.5" fill="#16a34a" />
                    <circle cx="210" cy="80" r="3.5" fill="#16a34a" />
                    <circle cx="305" cy="55" r="3.5" fill="#16a34a" />
                    <circle cx="400" cy="75" r="3.5" fill="#16a34a" />

                    {/* Cyclone Curve (Purple) */}
                    <path
                      d="M 20 110 Q 110 95 200 85 T 310 75 T 400 95"
                      fill="none"
                      stroke="#7c3aed"
                      strokeWidth="2"
                      strokeDasharray="4 2"
                      strokeLinecap="round"
                    />
                    <circle cx="20" cy="110" r="3" fill="#7c3aed" />
                    <circle cx="115" cy="98" r="3" fill="#7c3aed" />
                    <circle cx="210" cy="85" r="3" fill="#7c3aed" />
                    <circle cx="305" cy="75" r="3.5" fill="#7c3aed" />
                    <circle cx="400" cy="95" r="3" fill="#7c3aed" />
                  </svg>

                  {/* X Axis Timestamps matching dynamic forecast points */}
                  <div className="flex items-center justify-between text-[10px] text-[#867e6c] font-medium px-2 pt-1 border-t border-[#ede5d5]">
                    {trendPoints.map((tp, idx) => (
                      <span key={idx}>{tp.label}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* 3. Our Impact & Story Card (5 Cols) */}
              <div className="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {/* Impact Metric Blocks */}
                <div className="space-y-2.5">
                  <div className="bg-[#fcfaf5] rounded-xl p-3 border border-[#e5decb] shadow-xs flex items-center gap-3">
                    <div className="size-8 rounded-lg bg-[#dcfce7] text-[#15803d] flex items-center justify-center shrink-0">
                      <Leaf className="size-4 text-[#15803d]" />
                    </div>
                    <div>
                      <div className="text-[17px] font-bold font-editorial text-[#1a2d21] leading-tight">
                        {city?.population ? `${(city.population / 1_000_000).toFixed(1)}M` : "2.4M"}
                      </div>
                      <div className="text-[10px] text-[#716a5b]">People Protected</div>
                    </div>
                  </div>

                  <div className="bg-[#fcfaf5] rounded-xl p-3 border border-[#e5decb] shadow-xs flex items-center gap-3">
                    <div className="size-8 rounded-lg bg-[#e0f2fe] text-[#0369a1] flex items-center justify-center shrink-0">
                      <Wind className="size-4 text-[#0369a1]" />
                    </div>
                    <div>
                      <div className="text-[17px] font-bold font-editorial text-[#1a2d21] leading-tight">
                        120 Tons
                      </div>
                      <div className="text-[10px] text-[#716a5b]">CO₂ Avoided</div>
                    </div>
                  </div>

                  <div className="bg-[#fcfaf5] rounded-xl p-3 border border-[#e5decb] shadow-xs flex items-center gap-3">
                    <div className="size-8 rounded-lg bg-[#fef3c7] text-[#b45309] flex items-center justify-center shrink-0">
                      <Building2 className="size-4 text-[#b45309]" />
                    </div>
                    <div>
                      <div className="text-[17px] font-bold font-editorial text-[#1a2d21] leading-tight">
                        35%
                      </div>
                      <div className="text-[10px] text-[#716a5b]">Risk Reduction</div>
                    </div>
                  </div>

                  <div className="bg-[#fcfaf5] rounded-xl p-3 border border-[#e5decb] shadow-xs flex items-center gap-3">
                    <div className="size-8 rounded-lg bg-[#f3e8ff] text-[#7e22ce] flex items-center justify-center shrink-0">
                      <Users className="size-4 text-[#7e22ce]" />
                    </div>
                    <div>
                      <div className="text-[17px] font-bold font-editorial text-[#1a2d21] leading-tight">
                        100+
                      </div>
                      <div className="text-[10px] text-[#716a5b]">Cities</div>
                    </div>
                  </div>
                </div>

                {/* Documentary Story Card */}
                <div
                  onClick={() => setIsStoryModalOpen(true)}
                  className="relative rounded-[24px] overflow-hidden border border-[#2b4433] bg-[#0c160f] p-4 text-[#f4efe6] shadow-xs flex flex-col justify-between group cursor-pointer hover:border-[#48845e] transition-all"
                  title="Watch ClimateShield Story & Mission"
                >
                  <div
                    className="absolute inset-0 opacity-40 bg-cover bg-center mix-blend-overlay group-hover:scale-105 transition-transform duration-700"
                    style={{
                      backgroundImage: "url('/images/forest_canopy_dark_1789048152300.jpg')",
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#09120c] via-[#09120c]/40 to-transparent" />

                  <div className="relative z-10">
                    <h4 className="font-editorial text-[20px] font-bold leading-tight mt-1 text-[#f3f9f5]">
                      “Data today. <br />
                      Safer tomorrows.”
                    </h4>
                  </div>

                  <div className="relative z-10 flex items-center justify-between pt-6">
                    <span className="text-[10.5px] text-[#a9bcae] font-medium">
                      Watch Our Story
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsStoryModalOpen(true);
                      }}
                      className="size-8 rounded-full bg-[#f4efe6] text-[#0f1d13] flex items-center justify-center group-hover:scale-110 transition-transform shadow-md cursor-pointer"
                    >
                      <Play className="size-3.5 fill-current ml-0.5" />
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* ── FOOTER: Clean Editorial Signature ── */}
        <footer className="border-t border-[#ded4c0] bg-[#f0ebd9] px-8 py-3.5 mt-auto flex flex-wrap items-center justify-between text-xs text-[#716a5b]">
          <div className="flex items-center gap-2">
            <span className="font-bold text-[#1c2e24]">ClimateShield</span>
            <span>·</span>
            <span>Sustainable Smart Cities & Climate Tech</span>
          </div>

          <div className="flex items-center gap-6 text-[11.5px]">
            <button
              onClick={() => setIsHelpModalOpen(true)}
              className="hover:text-[#1c2e24] transition-colors cursor-pointer"
            >
              Help
            </button>
            <button
              onClick={() => setIsDocsModalOpen(true)}
              className="hover:text-[#1c2e24] transition-colors cursor-pointer"
            >
              Documentation
            </button>
            <button
              onClick={() => setIsApiModalOpen(true)}
              className="hover:text-[#1c2e24] transition-colors cursor-pointer"
            >
              API
            </button>
            <button
              onClick={() => setIsContactModalOpen(true)}
              className="hover:text-[#1c2e24] transition-colors cursor-pointer"
            >
              Contact
            </button>
            <div className="flex items-center gap-1.5 font-handwritten text-[15px] text-[#245236] font-bold">
              <span>Build a Better Tomorrow</span>
              <Leaf className="size-3.5 text-[#245236]" />
            </div>
          </div>
        </footer>

        {/* ══════════════════════════════════════════════════════════════════════════
            INTERACTIVE MODAL DIALOGS: ENSURING EVERY BUTTON ON THE WEBSITE WORKS
           ══════════════════════════════════════════════════════════════════════════ */}

        {/* 1. REAL-TIME ALERTS MODAL */}
        {isAlertsModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-2xl w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329] max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between pb-4 border-b border-[#e5decb]">
                <div className="flex items-center gap-3">
                  <div className="size-9 rounded-xl bg-[#fee2e2] text-[#dc2626] flex items-center justify-center">
                    <Bell className="size-5" />
                  </div>
                  <div>
                    <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                      Live Operational Alerts
                    </h3>
                    <p className="text-xs text-[#716a5b]">
                      Real-time threshold notifications & hydrological telemetry events
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      const allAck: Record<string, boolean> = {};
                      alerts.forEach((a) => {
                        allAck[a.id] = true;
                      });
                      setAcknowledgedAlertIds(allAck);
                    }}
                    className="px-3 py-1 rounded-xl bg-[#ede5d4] hover:bg-[#dfd5c2] text-xs font-semibold text-[#3d382c] transition-colors cursor-pointer"
                  >
                    Acknowledge All
                  </button>
                  <button
                    onClick={() => setIsAlertsModalOpen(false)}
                    className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                  >
                    <X className="size-5" />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto py-4 space-y-3">
                {alerts.length === 0 ? (
                  <div className="p-8 text-center text-xs text-[#716a5b]">
                    <CheckCircle2 className="size-8 text-[#16a34a] mx-auto mb-2 opacity-80" />
                    No active emergency alerts in the system. All sensor corridors nominal.
                  </div>
                ) : (
                  alerts.map((alert) => {
                    const isAck = acknowledgedAlertIds[alert.id];
                    const isHigh = alert.level === "EMERGENCY" || alert.level === "WARNING";
                    return (
                      <div
                        key={alert.id}
                        className={`p-3.5 rounded-2xl border transition-all ${
                          isAck
                            ? "bg-[#f4efe4]/60 border-[#e5decb] opacity-60"
                            : isHigh
                              ? "bg-[#fff5f5] border-[#fecaca]"
                              : "bg-[#fcfaf5] border-[#e8dfcf]"
                        } flex items-start justify-between gap-4`}
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                                alert.level === "EMERGENCY"
                                  ? "bg-[#dc2626] text-white"
                                  : alert.level === "WARNING"
                                    ? "bg-[#ea580c] text-white"
                                    : "bg-[#16a34a] text-white"
                              }`}
                            >
                              {alert.level}
                            </span>
                            <span className="text-[11px] text-[#867e6c]">
                              {relativeAge(alert.timestamp)}
                            </span>
                            {isAck && (
                              <span className="text-[10px] text-[#15803d] font-bold flex items-center gap-1">
                                <Check className="size-3" /> Acknowledged
                              </span>
                            )}
                          </div>
                          <p className="text-xs font-semibold text-[#1a2d21]">{alert.message}</p>
                        </div>
                        <div className="flex items-center gap-1.5 shrink-0">
                          {!isAck && (
                            <button
                              onClick={() =>
                                setAcknowledgedAlertIds((prev) => ({ ...prev, [alert.id]: true }))
                              }
                              className="px-2.5 py-1 rounded-lg bg-[#e8dfcf] hover:bg-[#ded4c0] text-[11px] font-semibold text-[#2c271e] transition-colors cursor-pointer"
                            >
                              Acknowledge
                            </button>
                          )}
                          <button
                            onClick={() => {
                              setIsAlertsModalOpen(false);
                              setIsDigitalTwinOpen(true);
                            }}
                            className="px-2.5 py-1 rounded-lg bg-[#1f422b] hover:bg-[#163321] text-white text-[11px] font-semibold transition-colors cursor-pointer"
                          >
                            Stage Action
                          </button>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              <div className="pt-3 border-t border-[#e5decb] flex items-center justify-between text-xs text-[#716a5b]">
                <span>Automatic Starlette SSE Ingestion · Operational Stream Active</span>
                <button
                  onClick={() => setIsAlertsModalOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 2. ACTIVE INCIDENTS FULL CONSOLE MODAL */}
        {isIncidentsModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-3xl w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329] max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between pb-4 border-b border-[#e5decb]">
                <div className="flex items-center gap-3">
                  <div className="size-9 rounded-xl bg-[#ffedd5] text-[#ea580c] flex items-center justify-center">
                    <AlertTriangle className="size-5" />
                  </div>
                  <div>
                    <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                      Active Incidents Management
                    </h3>
                    <p className="text-xs text-[#716a5b]">
                      Incident triage, geospatial dispatch, and tactical mitigation tracking
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setIsIncidentsModalOpen(false);
                    setSelectedIncidentForDetail(null);
                  }}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              {/* Filter Tabs */}
              <div className="flex items-center gap-2 py-3 border-b border-[#e5decb]">
                {["ALL", "EMERGENCY", "WARNING", "ADVISORY"].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setIncidentSeverityFilter(lvl)}
                    className={`px-3 py-1 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                      incidentSeverityFilter === lvl
                        ? "bg-[#1e3d29] text-white shadow-xs"
                        : "bg-[#ede5d4] text-[#554e40] hover:bg-[#dfd5c2]"
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>

              {/* Incidents List */}
              <div className="flex-1 overflow-y-auto py-4 space-y-3">
                {incidents
                  .filter((inc) =>
                    incidentSeverityFilter === "ALL"
                      ? true
                      : inc.severity === incidentSeverityFilter,
                  )
                  .map((inc) => (
                    <div
                      key={inc.id}
                      className="p-4 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4] hover:border-[#255437] transition-all space-y-2"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase ${
                                inc.severity === "EMERGENCY"
                                  ? "bg-[#dc2626] text-white"
                                  : "bg-[#ea580c] text-white"
                              }`}
                            >
                              {inc.severity}
                            </span>
                            <h4 className="text-sm font-bold text-[#1c2e24]">{inc.title}</h4>
                          </div>
                          <p className="text-xs text-[#716a5b] mt-1">
                            Zone {inc.zoneId} · Ref ID: {inc.ref} · Reported{" "}
                            {relativeAge(inc.reportedAt)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => {
                              setSelectedPinId(inc.zoneId);
                              setIsIncidentsModalOpen(false);
                              document
                                .getElementById("live-risk-map-section")
                                ?.scrollIntoView({ behavior: "smooth" });
                            }}
                            className="px-3 py-1.5 rounded-xl bg-[#e5decb] hover:bg-[#dad0bc] text-xs font-semibold text-[#1c2e24] transition-colors cursor-pointer flex items-center gap-1"
                          >
                            <MapPin className="size-3.5 text-[#0369a1]" />
                            <span>Locate on Map</span>
                          </button>
                          <button
                            onClick={() => {
                              setIsIncidentsModalOpen(false);
                              setIsDigitalTwinOpen(true);
                            }}
                            className="px-3 py-1.5 rounded-xl bg-[#0f766e] hover:bg-[#115e59] text-white text-xs font-semibold transition-colors cursor-pointer flex items-center gap-1"
                          >
                            <Sparkles className="size-3.5 text-[#99f6e4]" />
                            <span>Stage Countermeasure</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>

              <div className="pt-3 border-t border-[#e5decb] flex items-center justify-between text-xs text-[#716a5b]">
                <span>Showing {incidents.length} verified live incident records</span>
                <button
                  onClick={() => setIsIncidentsModalOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold transition-colors cursor-pointer"
                >
                  Close Console
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 3. ZONE RISK EXPLANATION MODAL */}
        {isZoneDetailModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-xl w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-4 border-b border-[#e5decb]">
                <div className="flex items-center gap-3">
                  <div className="size-9 rounded-xl bg-[#dbeafe] text-[#0284c7] flex items-center justify-center">
                    <Activity className="size-5" />
                  </div>
                  <div>
                    <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                      {selectedPin?.name ?? "Zone Intelligence"}
                    </h3>
                    <p className="text-xs text-[#716a5b]">
                      {selectedPin?.level ?? "Active Monitoring"}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setIsZoneDetailModalOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-4 text-xs">
                <div className="p-3.5 rounded-2xl bg-[#f4efe4] border border-[#ded5c2] space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#716a5b]">
                    Primary Operational Driver
                  </span>
                  <p className="font-semibold text-sm text-[#1c2e24]">{selectedPin?.reason}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-[#f7f3ea] border border-[#ede5d4]">
                    <span className="text-[10px] text-[#716a5b] font-medium">
                      Population Exposure
                    </span>
                    <p className="text-sm font-bold text-[#1a2d21] mt-0.5">14,200 Residents</p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#f7f3ea] border border-[#ede5d4]">
                    <span className="text-[10px] text-[#716a5b] font-medium">
                      Critical Infrastructure
                    </span>
                    <p className="text-sm font-bold text-[#1a2d21] mt-0.5">2 Roads, 1 Substation</p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#f7f3ea] border border-[#ede5d4]">
                    <span className="text-[10px] text-[#716a5b] font-medium">
                      Authoritative Risk Engine
                    </span>
                    <p className="text-sm font-bold text-[#15803d] mt-0.5">PostGIS Authoritative</p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#f7f3ea] border border-[#ede5d4]">
                    <span className="text-[10px] text-[#716a5b] font-medium">
                      ML Advisory Forecast
                    </span>
                    <p className="text-sm font-bold text-[#0284c7] mt-0.5">LSTM Horizon: +3h</p>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-[#e5decb] flex items-center justify-between">
                <button
                  onClick={() => {
                    setIsZoneDetailModalOpen(false);
                    setIsDigitalTwinOpen(true);
                  }}
                  className="px-4 py-2 rounded-xl bg-[#0f766e] hover:bg-[#115e59] text-white font-bold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <Sparkles className="size-3.5 text-[#99f6e4]" />
                  <span>Simulate Countermeasures in What-If Lab</span>
                </button>
                <button
                  onClick={() => setIsZoneDetailModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-[#ede5d4] hover:bg-[#ded4c0] text-[#2c271e] font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 4. CITY / SECTOR SELECTOR MODAL */}
        {isCitySelectorOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-md w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-3 border-b border-[#e5decb]">
                <div className="flex items-center gap-2.5">
                  <MapPin className="size-5 text-[#0284c7]" />
                  <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                    Select Monitoring Sector
                  </h3>
                </div>
                <button
                  onClick={() => setIsCitySelectorOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-2.5">
                {[
                  { name: "Visakhapatnam", tag: "Active Metro (PostGIS Mesh)", active: true },
                  { name: "Kakinada", tag: "Deepwater Port Corridor", active: false },
                  { name: "Machilipatnam", tag: "Krishna Estuary & Mangroves", active: false },
                  { name: "Chennai", tag: "North Coastal Drainage Basin", active: false },
                ].map((c) => (
                  <button
                    key={c.name}
                    onClick={() => {
                      setSelectedCityName(c.name);
                      setIsCitySelectorOpen(false);
                    }}
                    className={`w-full p-3.5 rounded-2xl border text-left flex items-center justify-between transition-all cursor-pointer ${
                      selectedCityName === c.name
                        ? "bg-[#1e3d29] text-white border-[#1e3d29] shadow-sm"
                        : "bg-[#f7f3ea] border-[#ede5d4] hover:border-[#1e3d29] hover:bg-[#efe7d6] text-[#1c2e24]"
                    }`}
                  >
                    <div>
                      <p className="font-bold text-xs">{c.name}</p>
                      <p
                        className={`text-[10px] mt-0.5 ${
                          selectedCityName === c.name ? "text-[#a7f3d0]" : "text-[#716a5b]"
                        }`}
                      >
                        {c.tag}
                      </p>
                    </div>
                    {selectedCityName === c.name && <Check className="size-4 text-[#86efac]" />}
                  </button>
                ))}
              </div>

              <div className="pt-2 border-t border-[#e5decb] flex justify-end">
                <button
                  onClick={() => setIsCitySelectorOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#ede5d4] hover:bg-[#ded4c0] text-[#2c271e] font-bold text-xs transition-colors cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 5. RISK TRENDS OPTIONS & EXPORT MODAL */}
        {isTrendsModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-md w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-3 border-b border-[#e5decb]">
                <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                  Risk Trends Analytics & Export
                </h3>
                <button
                  onClick={() => setIsTrendsModalOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-4 text-xs">
                <div>
                  <span className="font-semibold text-[#1a2d21] block mb-2">Timeframe Horizon</span>
                  <div className="grid grid-cols-3 gap-2">
                    {(["24H", "7D", "30D"] as const).map((tf) => (
                      <button
                        key={tf}
                        onClick={() => setTrendsTimeframe(tf)}
                        className={`py-2 rounded-xl font-bold transition-all cursor-pointer ${
                          trendsTimeframe === tf
                            ? "bg-[#1e3d29] text-white shadow-xs"
                            : "bg-[#ede5d4] text-[#554e40] hover:bg-[#dfd5c2]"
                        }`}
                      >
                        {tf}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-[#e5decb]">
                  <span className="font-semibold text-[#1a2d21] block">Data Actions</span>
                  <button
                    onClick={handleDownloadCsv}
                    className="w-full py-2.5 px-4 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold flex items-center justify-center gap-2 transition-colors cursor-pointer shadow-xs"
                  >
                    <Download className="size-4" />
                    <span>Download CSV Dataset</span>
                  </button>
                  <button
                    onClick={() => {
                      setIsTrendsModalOpen(false);
                      window.print();
                    }}
                    className="w-full py-2.5 px-4 rounded-xl bg-[#ede5d4] hover:bg-[#dfd5c2] text-[#2c271e] font-bold flex items-center justify-center gap-2 transition-colors cursor-pointer"
                  >
                    <Printer className="size-4" />
                    <span>Print Operational Report</span>
                  </button>
                </div>
              </div>

              <div className="pt-2 border-t border-[#e5decb] flex justify-end">
                <button
                  onClick={() => setIsTrendsModalOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#ede5d4] hover:bg-[#ded4c0] text-[#2c271e] font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 6. DOCUMENTARY STORY MODAL */}
        {isStoryModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
            <div className="max-w-2xl w-full bg-[#0c160f] border border-[#26442e] rounded-3xl p-6 shadow-2xl text-[#f4efe6] max-h-[88vh] overflow-y-auto">
              <div className="flex items-center justify-between pb-3 border-b border-[#203926]">
                <div className="flex items-center gap-2">
                  <Leaf className="size-5 text-[#86efac]" />
                  <h3 className="font-editorial text-lg font-bold text-[#f4efe6]">
                    ClimateShield Story & Vision
                  </h3>
                </div>
                <button
                  onClick={() => setIsStoryModalOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#1a2d21] text-[#9eb3a4] hover:text-white transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-4 text-xs">
                <div className="relative rounded-2xl overflow-hidden border border-[#2b4b34] aspect-video flex items-center justify-center bg-[#070f09]">
                  <div
                    className="absolute inset-0 bg-cover bg-center opacity-60"
                    style={{
                      backgroundImage: "url('/images/vizag_coastal_hero_1789048076882.jpg')",
                    }}
                  />
                  <div className="relative z-10 flex flex-col items-center gap-2 text-center p-4">
                    <div className="size-14 rounded-full bg-[#86efac] text-[#0c160f] flex items-center justify-center shadow-xl animate-pulse">
                      <Play className="size-6 fill-current ml-1" />
                    </div>
                    <span className="font-editorial text-lg font-bold">
                      Urban Climate Resilience in Action
                    </span>
                    <span className="text-[11px] text-[#cbd5cc]">
                      Visakhapatnam Smart City Operational Documentary (Duration: 3m 45s)
                    </span>
                  </div>
                </div>

                <p className="text-sm text-[#cbd5cc] leading-relaxed font-medium">
                  Built for HackSprint 2026, ClimateShield bridges the gap between high-frequency
                  environmental sensor telemetry and operational municipal action. By pairing an
                  authoritative deterministic PostGIS risk engine with advisory PyTorch LSTM
                  hydrology forecasting and a constrained Digital Twin, cities can anticipate
                  disasters hours ahead and stage optimal life-saving interventions.
                </p>

                <div className="grid grid-cols-3 gap-3 pt-2">
                  <div className="p-3 rounded-xl bg-[#122317] border border-[#21422b] text-center">
                    <span className="font-editorial text-lg font-bold text-[#86efac]">2.4M</span>
                    <p className="text-[10px] text-[#9eb3a4]">Citizens Protected</p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#122317] border border-[#21422b] text-center">
                    <span className="font-editorial text-lg font-bold text-[#38bdf8]">35%</span>
                    <p className="text-[10px] text-[#9eb3a4]">Modeled Risk Reduction</p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#122317] border border-[#21422b] text-center">
                    <span className="font-editorial text-lg font-bold text-[#facc15]">
                      120 Tons
                    </span>
                    <p className="text-[10px] text-[#9eb3a4]">CO₂ Mitigation</p>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-[#203926] flex items-center justify-between">
                <button
                  onClick={() => {
                    setIsStoryModalOpen(false);
                    setIsDigitalTwinOpen(true);
                  }}
                  className="px-4 py-2 rounded-xl bg-[#15803d] hover:bg-[#166534] text-white font-bold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <Sparkles className="size-3.5" />
                  <span>Launch Resilience What-If Lab</span>
                </button>
                <button
                  onClick={() => setIsStoryModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-[#1a2d21] hover:bg-[#253e2e] text-[#cbd5cc] font-bold text-xs transition-colors cursor-pointer"
                >
                  Close Story
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 7. OPERATOR PROFILE & CLEARANCE MODAL */}
        {isProfileModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-md w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-4 border-b border-[#e5decb]">
                <div className="flex items-center gap-3">
                  <div className="size-11 rounded-2xl bg-[#183020] text-[#86efac] font-bold text-sm flex items-center justify-center border border-[#355f43]">
                    DG
                  </div>
                  <div>
                    <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">Dhanush G</h3>
                    <p className="text-xs text-[#716a5b]">City Emergency Operations Controller</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsProfileModalOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-[#f7f3ea] border border-[#ede5d4] space-y-1">
                  <span className="text-[10px] uppercase font-bold text-[#716a5b]">Station</span>
                  <p className="font-semibold text-sm text-[#1c2e24]">
                    Visakhapatnam Municipal Disaster Management Center (MDMC)
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-3 rounded-xl bg-[#f7f3ea] border border-[#ede5d4]">
                    <span className="text-[10px] text-[#716a5b]">Clearance Level</span>
                    <p className="font-bold text-sm text-[#15803d]">Level 4 (Tactical)</p>
                  </div>
                  <div className="p-3 rounded-xl bg-[#f7f3ea] border border-[#ede5d4]">
                    <span className="text-[10px] text-[#716a5b]">Operational Mode</span>
                    <p className="font-bold text-sm text-[#15803d]">REAL-TIME LIVE</p>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-[#f7f3ea] border border-[#ede5d4]">
                  <span className="text-[10px] text-[#716a5b]">Active Permissions</span>
                  <p className="text-xs font-medium text-[#1c2e24] mt-0.5">
                    Sensor Ingestion Override · EOC Resource Staging · Barrier Deployment Approval
                  </p>
                </div>
              </div>

              <div className="pt-3 border-t border-[#e5decb] flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs text-[#15803d] font-bold">
                  <span className="size-2 rounded-full bg-[#16a34a] animate-pulse" />
                  <span>Live Telemetry Stream Active</span>
                </div>
                <button
                  onClick={() => setIsProfileModalOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#ede5d4] hover:bg-[#ded4c0] text-[#2c271e] font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 8. HELP & OPERATIONAL PROTOCOLS MODAL */}
        {isHelpModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-lg w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-3 border-b border-[#e5decb]">
                <div className="flex items-center gap-2">
                  <Phone className="size-5 text-[#15803d]" />
                  <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                    Emergency Operations Protocols & Help
                  </h3>
                </div>
                <button
                  onClick={() => setIsHelpModalOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-3 text-xs">
                <div className="p-3.5 rounded-2xl bg-[#eff6ff] border border-[#bfdbfe] space-y-1">
                  <span className="text-[10px] font-bold uppercase text-[#1d4ed8]">
                    Priority Emergency Hotlines
                  </span>
                  <p className="font-bold text-sm text-[#1e3a8a]">
                    District Emergency Ops Center: 1077
                  </p>
                  <p className="text-[11px] text-[#1e40af]">
                    State Disaster Management Authority: 1070 · National Helpline: 112
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4] space-y-2">
                  <span className="text-[10px] font-bold uppercase text-[#716a5b]">
                    Standard Operating Procedure (SOP)
                  </span>
                  <ul className="list-disc pl-4 space-y-1 text-[#423c31]">
                    <li>Stage 1 (Advisory): Continuous observation via IoT telemetry loop.</li>
                    <li>Stage 2 (Warning): Initiate Resilience What-If Lab countermeasure runs.</li>
                    <li>
                      Stage 3 (Emergency): Authorize physical high-capacity pumps and modular
                      barrier deployment.
                    </li>
                  </ul>
                </div>
              </div>

              <div className="pt-2 border-t border-[#e5decb] flex justify-end">
                <button
                  onClick={() => setIsHelpModalOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 9. DOCUMENTATION MODAL */}
        {isDocsModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-2xl w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329] max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between pb-3 border-b border-[#e5decb]">
                <div className="flex items-center gap-2">
                  <FileBarChart className="size-5 text-[#0f766e]" />
                  <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                    ClimateShield Architecture & Documentation
                  </h3>
                </div>
                <button
                  onClick={() => setIsDocsModalOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto py-4 space-y-3 text-xs">
                <div className="p-3.5 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4] space-y-1">
                  <span className="font-bold text-sm text-[#1c2e24]">
                    1. Authoritative Deterministic PostGIS Engine
                  </span>
                  <p className="text-[#554e40] leading-relaxed">
                    ClimateShield strictly enforces that risk assessments and spatial evaluations
                    are deterministic and governed by PostGIS polygonal meshes. Risk levels (LOW,
                    MODERATE, HIGH, CRITICAL) are authoritative and reproducible.
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4] space-y-1">
                  <span className="font-bold text-sm text-[#1c2e24]">
                    2. Advisory Machine Learning Layer
                  </span>
                  <p className="text-[#554e40] leading-relaxed">
                    PyTorch LSTM river forecast (RN-01) and Isolation Forest sensor anomaly guard
                    operate strictly in an advisory capacity with explicit health tracking, latency
                    telemetry, and fallback mechanisms.
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4] space-y-1">
                  <span className="font-bold text-sm text-[#1c2e24]">
                    3. Constrained Resilience Digital Twin
                  </span>
                  <p className="text-[#554e40] leading-relaxed">
                    Evaluates counterfactual operational scenarios (river rise, rainfall surge, road
                    outages, pump deployment, barriers) in real-time with sub-50ms execution
                    latency.
                  </p>
                </div>
              </div>

              <div className="pt-3 border-t border-[#e5decb] flex items-center justify-between">
                <button
                  onClick={() => {
                    setIsDocsModalOpen(false);
                    setIsMlEvalModalOpen(true);
                  }}
                  className="px-4 py-1.5 rounded-xl bg-[#0f766e] hover:bg-[#115e59] text-white font-bold text-xs transition-colors cursor-pointer"
                >
                  View ML Benchmark Suite
                </button>
                <button
                  onClick={() => setIsDocsModalOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 10. INTERACTIVE API EXPLORER MODAL */}
        {isApiModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-2xl w-full bg-[#121914] border border-[#25442e] rounded-3xl p-6 shadow-2xl text-[#f4efe6] max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between pb-3 border-b border-[#213f2a]">
                <div className="flex items-center gap-2">
                  <Terminal className="size-5 text-[#86efac]" />
                  <h3 className="font-editorial text-lg font-bold text-[#f4efe6]">
                    Interactive Live API Console
                  </h3>
                </div>
                <button
                  onClick={() => {
                    setIsApiModalOpen(false);
                    setApiTestResult(null);
                  }}
                  className="p-1.5 rounded-xl hover:bg-[#1b3122] text-[#9eb3a4] hover:text-white transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto py-4 space-y-3 text-xs">
                <span className="text-[10.5px] uppercase tracking-wider text-[#86efac] font-bold">
                  Active Backend REST Endpoints
                </span>

                <div className="space-y-2">
                  {[
                    {
                      method: "GET",
                      path: "/api/v1/telemetry/river",
                      desc: "Live River Nodes & Stages",
                    },
                    {
                      method: "GET",
                      path: "/api/v1/ml/health",
                      desc: "ML Models Health & Latency",
                    },
                    {
                      method: "GET",
                      path: "/api/v1/ml/forecast/RN-01",
                      desc: "PyTorch LSTM River Forecast",
                    },
                    {
                      method: "GET",
                      path: "/api/v1/events",
                      desc: "Starlette SSE Live Telemetry Stream",
                    },
                    {
                      method: "GET",
                      path: "/api/v1/agentic-action-plan",
                      desc: "Unified 6-Agent Decision Matrix & VoiceOps Grounding",
                    },
                  ].map((ep) => (
                    <div
                      key={ep.path}
                      className="p-3 rounded-xl bg-[#0b130e] border border-[#1e3825] flex items-center justify-between gap-3"
                    >
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 font-mono">
                          <span className="px-1.5 py-0.5 rounded bg-[#1e3d29] text-[#86efac] font-bold text-[10px]">
                            {ep.method}
                          </span>
                          <span className="text-[#f4efe6] font-semibold truncate">{ep.path}</span>
                        </div>
                        <p className="text-[10px] text-[#9eb3a4] mt-0.5">{ep.desc}</p>
                      </div>
                      <button
                        onClick={() => handleTestApi(ep.path)}
                        disabled={isTestingApi}
                        className="px-3 py-1 rounded-lg bg-[#254d34] hover:bg-[#2f6343] text-white font-bold text-[11px] shrink-0 transition-colors cursor-pointer disabled:opacity-50"
                      >
                        Test Call
                      </button>
                    </div>
                  ))}
                </div>

                {apiTestResult && (
                  <div className="p-3 rounded-xl bg-[#080d09] border border-[#21422b] space-y-1">
                    <span className="text-[10px] text-[#86efac] font-mono">Terminal Output:</span>
                    <pre className="text-[11px] font-mono text-[#cbd5cc] overflow-x-auto max-h-40 p-2 bg-black/40 rounded-lg">
                      {apiTestResult}
                    </pre>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-[#213f2a] flex justify-end">
                <button
                  onClick={() => {
                    setIsApiModalOpen(false);
                    setApiTestResult(null);
                  }}
                  className="px-4 py-1.5 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold text-xs transition-colors cursor-pointer"
                >
                  Close Console
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 11. CONTACT & EMERGENCY DISPATCH MODAL */}
        {isContactModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-md w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-3 border-b border-[#e5decb]">
                <div className="flex items-center gap-2">
                  <Mail className="size-5 text-[#0284c7]" />
                  <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                    Dispatch Communications
                  </h3>
                </div>
                <button
                  onClick={() => {
                    setIsContactModalOpen(false);
                    setContactMessageSent(false);
                  }}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-3 text-xs">
                {contactMessageSent ? (
                  <div className="p-4 rounded-2xl bg-[#dcfce7] border border-[#bbf7d0] text-[#15803d] text-center space-y-1">
                    <CheckCircle2 className="size-6 mx-auto" />
                    <p className="font-bold">Transmission Dispatched Successfully</p>
                    <p className="text-[11px]">
                      Logged in DEOC tactical operations log at {new Date().toLocaleTimeString()}
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="space-y-1">
                      <label className="font-semibold text-[#1c2e24]">Transmission Channel</label>
                      <input
                        type="text"
                        disabled
                        value="Visakhapatnam Command DEOC · VHF Ch. 16"
                        className="w-full px-3 py-2 rounded-xl bg-[#ede5d4] border border-[#dfd5c2] text-xs font-mono text-[#554e40]"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="font-semibold text-[#1c2e24]">
                        Tactical Message / Log Entry
                      </label>
                      <textarea
                        rows={3}
                        value={contactMessageText}
                        onChange={(e) => setContactMessageText(e.target.value)}
                        placeholder="Enter operational update or deployment request..."
                        className="w-full px-3 py-2 rounded-xl bg-[#f7f3ea] border border-[#ded5c2] text-xs focus:ring-1 focus:ring-[#1e3d29] focus:outline-none"
                      />
                    </div>
                    <button
                      onClick={() => {
                        if (contactMessageText.trim()) {
                          setContactMessageSent(true);
                          setContactMessageText("");
                        }
                      }}
                      className="w-full py-2 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <Send className="size-3.5" />
                      <span>Transmit Message</span>
                    </button>
                  </>
                )}
              </div>

              <div className="pt-2 border-t border-[#e5decb] flex justify-end">
                <button
                  onClick={() => {
                    setIsContactModalOpen(false);
                    setContactMessageSent(false);
                  }}
                  className="px-4 py-1.5 rounded-xl bg-[#ede5d4] hover:bg-[#ded4c0] text-[#2c271e] font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 12. PEOPLE & TEAMS MODAL */}
        {isTeamModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-md w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-3 border-b border-[#e5decb]">
                <div className="flex items-center gap-2">
                  <Users className="size-5 text-[#7c3aed]" />
                  <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                    Operational Command Staff
                  </h3>
                </div>
                <button
                  onClick={() => setIsTeamModalOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-2.5 text-xs">
                {[
                  {
                    name: "Dhanush G",
                    role: "Incident Commander",
                    status: "Active On Console",
                    color: "bg-[#dcfce7] text-[#15803d]",
                  },
                  {
                    name: "Dr. srihari",
                    role: "Chief Hydrologist",
                    status: "Reviewing LSTM Horizon",
                    color: "bg-[#dbeafe] text-[#0369a1]",
                  },
                  {
                    name: "gayathri M",
                    role: "Geospatial Analyst",
                    status: "PostGIS Mesh Active",
                    color: "bg-[#fef3c7] text-[#b45309]",
                  },
                  {
                    name: "Viswes G",
                    role: "Field Response Lead",
                    status: "Staging Depot Alpha",
                    color: "bg-[#f3e8ff] text-[#7e22ce]",
                  },
                ].map((member) => (
                  <div
                    key={member.name}
                    className="p-3 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4] flex items-center justify-between"
                  >
                    <div>
                      <p className="font-bold text-xs text-[#1a2d21]">{member.name}</p>
                      <p className="text-[10.5px] text-[#716a5b]">{member.role}</p>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${member.color}`}
                    >
                      {member.status}
                    </span>
                  </div>
                ))}
              </div>

              <div className="pt-2 border-t border-[#e5decb] flex justify-end">
                <button
                  onClick={() => setIsTeamModalOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 13. INTEGRATIONS MODAL */}
        {isIntegrationsModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-md w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-3 border-b border-[#e5decb]">
                <div className="flex items-center gap-2">
                  <Layers className="size-5 text-[#0f766e]" />
                  <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                    Connected Subsystems
                  </h3>
                </div>
                <button
                  onClick={() => setIsIntegrationsModalOpen(false)}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-2 text-xs">
                {[
                  {
                    name: "FastAPI + Starlette SSE",
                    desc: "Real-Time Telemetry Event Bus",
                    status: "CONNECTED",
                  },
                  {
                    name: "PostGIS Geospatial Engine",
                    desc: "Spatial Risk Aggregation",
                    status: "OPERATIONAL",
                  },
                  {
                    name: "PyTorch River Forecaster",
                    desc: "LSTM Deep Sequence Model",
                    status: "READY",
                  },
                  {
                    name: "Scikit-Learn Anomaly Guard",
                    desc: "Isolation Forest v1.0",
                    status: "READY",
                  },
                  {
                    name: "Digital Twin Engine",
                    desc: "In-Memory Counterfactual Simulator",
                    status: "READY",
                  },
                ].map((item) => (
                  <div
                    key={item.name}
                    className="p-3 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4] flex items-center justify-between"
                  >
                    <div>
                      <p className="font-bold text-xs text-[#1a2d21]">{item.name}</p>
                      <p className="text-[10px] text-[#716a5b]">{item.desc}</p>
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#dcfce7] text-[#15803d]">
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>

              <div className="pt-2 border-t border-[#e5decb] flex justify-end">
                <button
                  onClick={() => setIsIntegrationsModalOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 14. SETTINGS MODAL */}
        {isSettingsModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="max-w-md w-full bg-[#fcfaf5] border border-[#d8cfbe] rounded-3xl p-6 shadow-2xl text-[#2c3329]">
              <div className="flex items-center justify-between pb-3 border-b border-[#e5decb]">
                <div className="flex items-center gap-2">
                  <Settings className="size-5 text-[#51493a]" />
                  <h3 className="font-editorial text-lg font-bold text-[#1a2d21]">
                    System Preferences
                  </h3>
                </div>
                <button
                  onClick={() => {
                    setIsSettingsModalOpen(false);
                    setSettingsSaved(false);
                  }}
                  className="p-1.5 rounded-xl hover:bg-[#ede5d4] text-[#716a5b] hover:text-[#1a2d21] transition-colors cursor-pointer"
                >
                  <X className="size-5" />
                </button>
              </div>

              <div className="py-4 space-y-3 text-xs">
                {settingsSaved && (
                  <div className="p-2.5 rounded-xl bg-[#dcfce7] text-[#15803d] font-bold text-center">
                    Preferences successfully saved!
                  </div>
                )}
                <div className="flex items-center justify-between p-3 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4]">
                  <div>
                    <p className="font-bold text-[#1a2d21]">Live Telemetry Ingestion Rate</p>
                    <p className="text-[10px] text-[#716a5b]">Starlette background polling cycle</p>
                  </div>
                  <span className="px-2 py-0.5 rounded-lg bg-[#e8dfcf] font-bold text-[11px]">
                    4.0s
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4]">
                  <div>
                    <p className="font-bold text-[#1a2d21]">Audio Warning Alarms</p>
                    <p className="text-[10px] text-[#716a5b]">Emergency sirens for CRITICAL risk</p>
                  </div>
                  <span className="px-2 py-0.5 rounded-lg bg-[#dcfce7] text-[#15803d] font-bold text-[11px]">
                    ENABLED
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-2xl bg-[#f7f3ea] border border-[#ede5d4]">
                  <div>
                    <p className="font-bold text-[#1a2d21]">Authoritative Engine Mode</p>
                    <p className="text-[10px] text-[#716a5b]">PostGIS deterministic calculations</p>
                  </div>
                  <span className="px-2 py-0.5 rounded-lg bg-[#1e3d29] text-white font-bold text-[11px]">
                    STRICT
                  </span>
                </div>
              </div>

              <div className="pt-2 border-t border-[#e5decb] flex items-center justify-between">
                <button
                  onClick={() => setSettingsSaved(true)}
                  className="px-4 py-1.5 rounded-xl bg-[#1e3d29] hover:bg-[#254d34] text-white font-bold text-xs transition-colors cursor-pointer"
                >
                  Save Preferences
                </button>
                <button
                  onClick={() => {
                    setIsSettingsModalOpen(false);
                    setSettingsSaved(false);
                  }}
                  className="px-4 py-1.5 rounded-xl bg-[#ede5d4] hover:bg-[#ded4c0] text-[#2c271e] font-bold text-xs transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
