import { useState, useEffect, useMemo } from "react";
import {
  Sparkles,
  Sliders,
  Shield,
  Zap,
  RotateCcw,
  Check,
  AlertTriangle,
  Play,
  Waves,
  CloudRain,
  Activity,
  Building2,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  Cpu,
  ShieldCheck,
  ShieldAlert,
  Loader2,
  CheckCircle2,
  X,
} from "lucide-react";
import {
  useSimulationScenarios,
  useRunSimulation,
  useRunNamedScenario,
} from "@/hooks/use-climate-queries";
import type {
  SimulationRunRequest,
  SimulationRunResponse,
  InterventionRankingItem,
} from "@/types/climate";

interface DigitalTwinLabProps {
  onClose?: () => void;
}

export function DigitalTwinLab({ onClose }: DigitalTwinLabProps) {
  // Predefined scenarios query
  const { data: scenariosData, isLoading: isScenariosLoading } = useSimulationScenarios();
  const runNamedMutation = useRunNamedScenario();
  const runCustomMutation = useRunSimulation();

  // Active scenario state
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>("river_rise_0_5m");
  const [simulationResult, setSimulationResult] = useState<SimulationRunResponse | null>(null);

  // Granular slider & toggle state
  const [riverDelta, setRiverDelta] = useState<number>(0.5);
  const [rainfallPct, setRainfallPct] = useState<number>(0);
  const [hospitalRoadOpen, setHospitalRoadOpen] = useState<boolean>(true);
  const [substationActive, setSubstationActive] = useState<boolean>(true);
  const [pumpStationActive, setPumpStationActive] = useState<boolean>(true);
  const [pumpsDeployed, setPumpsDeployed] = useState<number>(0);
  const [barriersUnits, setBarriersUnits] = useState<number>(0);
  const [sensorStatus, setSensorStatus] = useState<"HEALTHY" | "DEGRADED" | "OFFLINE">("HEALTHY");
  const [responseDelay, setResponseDelay] = useState<number>(0);

  // Staged intervention notification
  const [stagedIntervention, setStagedIntervention] = useState<string | null>(null);
  const [selectedZoneId, setSelectedZoneId] = useState<string>("zone-a");

  // Initial load: run default scenario
  useEffect(() => {
    runNamedMutation.mutate("river_rise_0_5m", {
      onSuccess: (data) => {
        setSimulationResult(data);
      },
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelectScenario = (scenarioId: string) => {
    setSelectedScenarioId(scenarioId);
    setStagedIntervention(null);

    // Sync form controls based on scenario
    if (scenarioId === "river_rise_0_5m") {
      setRiverDelta(0.5);
      setRainfallPct(0);
      setHospitalRoadOpen(true);
      setPumpsDeployed(0);
      setBarriersUnits(0);
      setSensorStatus("HEALTHY");
      setResponseDelay(0);
    } else if (scenarioId === "rainfall_surge_30pct") {
      setRiverDelta(0.15);
      setRainfallPct(30);
      setHospitalRoadOpen(true);
      setPumpsDeployed(0);
      setBarriersUnits(0);
      setSensorStatus("HEALTHY");
      setResponseDelay(0);
    } else if (scenarioId === "hospital_road_blocked") {
      setRiverDelta(0.35);
      setRainfallPct(15);
      setHospitalRoadOpen(false);
      setPumpsDeployed(0);
      setBarriersUnits(0);
      setSensorStatus("HEALTHY");
      setResponseDelay(15);
    } else if (scenarioId === "deploy_2_pumps") {
      setRiverDelta(0.25);
      setRainfallPct(10);
      setHospitalRoadOpen(true);
      setPumpsDeployed(2);
      setBarriersUnits(0);
      setSensorStatus("HEALTHY");
      setResponseDelay(0);
    } else if (scenarioId === "deploy_barriers") {
      setRiverDelta(0.4);
      setRainfallPct(10);
      setHospitalRoadOpen(true);
      setPumpsDeployed(0);
      setBarriersUnits(4);
      setSensorStatus("HEALTHY");
      setResponseDelay(0);
    } else if (scenarioId === "sensor_outage") {
      setRiverDelta(0.3);
      setRainfallPct(10);
      setHospitalRoadOpen(true);
      setPumpsDeployed(0);
      setBarriersUnits(0);
      setSensorStatus("OFFLINE");
      setResponseDelay(0);
    } else if (scenarioId === "do_nothing") {
      setRiverDelta(0.4);
      setRainfallPct(20);
      setHospitalRoadOpen(true);
      setPumpsDeployed(0);
      setBarriersUnits(0);
      setSensorStatus("HEALTHY");
      setResponseDelay(0);
    }

    runNamedMutation.mutate(scenarioId, {
      onSuccess: (data) => {
        setSimulationResult(data);
      },
    });
  };

  const handleRunCustom = () => {
    setSelectedScenarioId("custom");
    setStagedIntervention(null);

    const req: SimulationRunRequest = {
      scenario_id: "custom",
      name: "Custom Parameterized Digital Twin Run",
      environmental: {
        river_level_delta_m: riverDelta,
        rainfall_intensity_pct: rainfallPct,
      },
      infrastructure: {
        hospital_road_available: hospitalRoadOpen,
        substation_operational: substationActive,
        pump_station_operational: pumpStationActive,
        barrier_deployed_km: barriersUnits * 0.125,
      },
      response: {
        pumps_deployed: pumpsDeployed,
        barriers_deployed_units: barriersUnits,
        response_delay_minutes: responseDelay,
      },
      sensor_confidence: {
        sensor_status_overrides: sensorStatus !== "HEALTHY" ? { "SN-UP-01": sensorStatus } : {},
      },
    };

    runCustomMutation.mutate(req, {
      onSuccess: (data) => {
        setSimulationResult(data);
      },
    });
  };

  const handleReset = () => {
    handleSelectScenario("river_rise_0_5m");
  };

  const isExecuting = runNamedMutation.isPending || runCustomMutation.isPending;

  // Selected Zone details
  const currentZone = useMemo(() => {
    if (!simulationResult?.affected_zones) return null;
    return simulationResult.affected_zones.find(
      (z) => z.zone_id.toLowerCase() === selectedZoneId.toLowerCase(),
    );
  }, [simulationResult, selectedZoneId]);

  return (
    <div className="flex-1 min-w-0 bg-[#f4efe4] overflow-y-auto overflow-x-hidden flex flex-col p-6 space-y-6">
      {/* ── TOP HEADER: Digital Twin Lab Header & Controls ── */}
      <div className="bg-[#fcfbf7] rounded-3xl p-6 border border-[#dfd7c4] shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="size-9 rounded-2xl bg-gradient-to-br from-[#0f766e] to-[#115e59] flex items-center justify-center text-white shadow-md">
              <Sparkles className="size-5 text-[#99f6e4]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-editorial text-2xl font-bold text-[#1a2d21]">
                  Resilience What-If Digital Twin
                </h1>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-[#0f766e]/15 text-[#0f766e] border border-[#0f766e]/30">
                  Phase 7 Simulator
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#f3f4f6] text-[#4b5563] border border-[#e5e7eb]">
                  100% In-Memory · Zero DB Mutation
                </span>
              </div>
              <p className="text-xs text-[#716a5b] mt-0.5">
                Counterfactual scenario modeling, compounding hazard simulation, and multi-criteria
                response ranking.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {simulationResult && (
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#f4efe4] border border-[#ded5c2] text-xs font-mono text-[#554e40]">
              <Clock className="size-3.5 text-[#0f766e]" />
              <span>{simulationResult.execution_latency_ms} ms latency</span>
            </div>
          )}

          <button
            onClick={handleReset}
            className="px-3.5 py-2 rounded-xl bg-[#f4efe4] hover:bg-[#e9e1d1] text-[#554e40] font-semibold text-xs flex items-center gap-1.5 transition-colors border border-[#ded5c2] cursor-pointer"
          >
            <RotateCcw className="size-3.5" />
            <span>Reset Baseline</span>
          </button>

          {onClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-[#f4efe4] hover:bg-[#e9e1d1] text-[#554e40] transition-colors border border-[#ded5c2] cursor-pointer"
              title="Close Lab"
            >
              <X className="size-4" />
            </button>
          )}
        </div>
      </div>

      {/* ── PRE-CONFIGURED ONE-CLICK SCENARIOS ── */}
      <div className="bg-[#fcfbf7] rounded-3xl p-5 border border-[#dfd7c4] shadow-xs">
        <div className="flex items-center justify-between mb-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#867e6c] flex items-center gap-1.5">
            <Sliders className="size-3.5 text-[#0f766e]" />
            Pre-Configured Operational Scenarios (7 Scenarios)
          </span>
          <span className="text-[11px] text-[#867e6c]">
            Click any scenario to immediately trigger an in-memory counterfactual evaluation
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5">
          {[
            { id: "river_rise_0_5m", name: "River Rise +0.5m", icon: Waves, tag: "+0.5m" },
            {
              id: "rainfall_surge_30pct",
              name: "Rainfall Surge +30%",
              icon: CloudRain,
              tag: "+30%",
            },
            {
              id: "hospital_road_blocked",
              name: "Hospital Road Blocked",
              icon: AlertTriangle,
              tag: "Cut-Off",
            },
            { id: "deploy_2_pumps", name: "Deploy 2x Pumps", icon: Zap, tag: "10k GPM" },
            { id: "deploy_barriers", name: "Deploy 500m Barriers", icon: ShieldCheck, tag: "500m" },
            { id: "sensor_outage", name: "Sensor Outage", icon: Cpu, tag: "Offline" },
            { id: "do_nothing", name: "Do Nothing", icon: Activity, tag: "Baseline" },
          ].map((sc) => {
            const Icon = sc.icon;
            const isSelected = selectedScenarioId === sc.id;
            return (
              <button
                key={sc.id}
                onClick={() => handleSelectScenario(sc.id)}
                disabled={isExecuting}
                className={`p-3 rounded-2xl text-left transition-all border flex flex-col justify-between min-h-[82px] cursor-pointer ${
                  isSelected
                    ? "bg-[#0f766e] text-white border-[#0d645e] shadow-md ring-2 ring-[#0f766e]/30"
                    : "bg-[#f4efe4] hover:bg-[#eae3d4] text-[#2c3329] border-[#ded5c2]"
                }`}
              >
                <div className="flex items-center justify-between w-full">
                  <Icon className={`size-4 ${isSelected ? "text-[#99f6e4]" : "text-[#0f766e]"}`} />
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.5 rounded-md ${
                      isSelected ? "bg-[#115e59] text-[#99f6e4]" : "bg-[#dfd7c4] text-[#554e40]"
                    }`}
                  >
                    {sc.tag}
                  </span>
                </div>
                <div className="font-bold text-xs mt-2 leading-tight">{sc.name}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── MAIN 3-COLUMN LAB LAYOUT ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* ── LEFT COLUMN: Interactive Parameter Sliders & Modifiers (3 cols) ── */}
        <div className="lg:col-span-3 space-y-4">
          <div className="bg-[#fcfbf7] rounded-3xl p-5 border border-[#dfd7c4] shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#ece4d3] pb-2.5">
              <span className="text-xs font-bold uppercase tracking-wider text-[#1a2d21] flex items-center gap-1.5">
                <Sliders className="size-4 text-[#0f766e]" />
                What-If Controls
              </span>
              <button
                onClick={handleRunCustom}
                disabled={isExecuting}
                className="px-3 py-1.5 rounded-xl bg-[#0f766e] hover:bg-[#115e59] text-white font-bold text-xs flex items-center gap-1 transition-all shadow-xs disabled:opacity-50 cursor-pointer"
              >
                {isExecuting ? (
                  <Loader2 className="size-3.5 animate-spin" />
                ) : (
                  <Play className="size-3.5 fill-current" />
                )}
                <span>Run Custom</span>
              </button>
            </div>

            {/* Environmental Modifiers */}
            <div className="space-y-3">
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-[#867e6c]">
                Environmental Stressors
              </span>

              {/* River Stage Slider */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-[#554e40] font-medium">River Level Delta:</span>
                  <span className="font-mono font-bold text-[#0f766e]">
                    {riverDelta >= 0 ? `+${riverDelta.toFixed(2)}m` : `${riverDelta.toFixed(2)}m`}
                  </span>
                </div>
                <input
                  type="range"
                  min="-0.5"
                  max="2.0"
                  step="0.05"
                  value={riverDelta}
                  onChange={(e) => setRiverDelta(parseFloat(e.target.value))}
                  className="w-full accent-[#0f766e] cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-[#867e6c]">
                  <span>-0.5m (Drought)</span>
                  <span>0.0m (Norm)</span>
                  <span>+2.0m (Severe Crest)</span>
                </div>
              </div>

              {/* Rainfall Intensity Slider */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-[#554e40] font-medium">Rainfall Surge:</span>
                  <span className="font-mono font-bold text-[#0f766e]">
                    {rainfallPct >= 0 ? `+${rainfallPct}%` : `${rainfallPct}%`}
                  </span>
                </div>
                <input
                  type="range"
                  min="-50"
                  max="100"
                  step="5"
                  value={rainfallPct}
                  onChange={(e) => setRainfallPct(parseInt(e.target.value))}
                  className="w-full accent-[#0f766e] cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-[#867e6c]">
                  <span>-50%</span>
                  <span>0% (Norm)</span>
                  <span>+100% (Cloudburst)</span>
                </div>
              </div>
            </div>

            {/* Infrastructure Toggles */}
            <div className="space-y-2.5 pt-2 border-t border-[#ece4d3]">
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-[#867e6c]">
                Critical Infrastructure Availability
              </span>

              <label className="flex items-center justify-between text-xs p-2 rounded-xl bg-[#f4efe4] cursor-pointer">
                <span className="font-medium text-[#2c3329]">Hospital Primary Road:</span>
                <input
                  type="checkbox"
                  checked={hospitalRoadOpen}
                  onChange={(e) => setHospitalRoadOpen(e.target.checked)}
                  className="rounded text-[#0f766e] focus:ring-[#0f766e] size-4"
                />
              </label>

              <label className="flex items-center justify-between text-xs p-2 rounded-xl bg-[#f4efe4] cursor-pointer">
                <span className="font-medium text-[#2c3329]">220kV Substation Active:</span>
                <input
                  type="checkbox"
                  checked={substationActive}
                  onChange={(e) => setSubstationActive(e.target.checked)}
                  className="rounded text-[#0f766e] focus:ring-[#0f766e] size-4"
                />
              </label>

              <label className="flex items-center justify-between text-xs p-2 rounded-xl bg-[#f4efe4] cursor-pointer">
                <span className="font-medium text-[#2c3329]">Municipal Pump Station:</span>
                <input
                  type="checkbox"
                  checked={pumpStationActive}
                  onChange={(e) => setPumpStationActive(e.target.checked)}
                  className="rounded text-[#0f766e] focus:ring-[#0f766e] size-4"
                />
              </label>
            </div>

            {/* Tactical Deployment Modifiers */}
            <div className="space-y-3 pt-2 border-t border-[#ece4d3]">
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-[#867e6c]">
                Tactical Response Countermeasures
              </span>

              {/* Extra Pumps */}
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#554e40] font-medium">Extra High-Capacity Pumps:</span>
                <div className="flex items-center gap-1">
                  {[0, 1, 2, 4].map((num) => (
                    <button
                      key={num}
                      onClick={() => setPumpsDeployed(num)}
                      className={`px-2 py-0.5 rounded-lg font-bold text-[11px] ${
                        pumpsDeployed === num
                          ? "bg-[#0f766e] text-white"
                          : "bg-[#f4efe4] text-[#554e40] hover:bg-[#e9e1d1]"
                      }`}
                    >
                      {num}
                    </button>
                  ))}
                </div>
              </div>

              {/* Flood Barriers */}
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#554e40] font-medium">Modular Barriers (units):</span>
                <div className="flex items-center gap-1">
                  {[0, 2, 4, 8].map((num) => (
                    <button
                      key={num}
                      onClick={() => setBarriersUnits(num)}
                      className={`px-2 py-0.5 rounded-lg font-bold text-[11px] ${
                        barriersUnits === num
                          ? "bg-[#0f766e] text-white"
                          : "bg-[#f4efe4] text-[#554e40] hover:bg-[#e9e1d1]"
                      }`}
                    >
                      {num}
                    </button>
                  ))}
                </div>
              </div>

              {/* Upstream Sensor Health */}
              <div className="space-y-1">
                <span className="text-xs text-[#554e40] font-medium">
                  Upstream Sensor SN-UP-01:
                </span>
                <div className="grid grid-cols-3 gap-1">
                  {(["HEALTHY", "DEGRADED", "OFFLINE"] as const).map((stat) => (
                    <button
                      key={stat}
                      onClick={() => setSensorStatus(stat)}
                      className={`py-1 rounded-lg text-[10px] font-bold text-center ${
                        sensorStatus === stat
                          ? stat === "HEALTHY"
                            ? "bg-[#15803d] text-white"
                            : stat === "DEGRADED"
                              ? "bg-[#b45309] text-white"
                              : "bg-[#b91c1c] text-white"
                          : "bg-[#f4efe4] text-[#554e40] hover:bg-[#e9e1d1]"
                      }`}
                    >
                      {stat}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── CENTER COLUMN: Spatial Map & Affected Assets (5 cols) ── */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-[#fcfbf7] rounded-3xl p-5 border border-[#dfd7c4] shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-[#1a2d21] flex items-center gap-1.5">
                <Waves className="size-4 text-[#0f766e]" />
                Spatial Hazard Envelope & Critical Nodes
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#f4efe4] text-[#554e40] border border-[#ded5c2]">
                Visakhapatnam Corridor
              </span>
            </div>

            {/* Visual SVG Map */}
            <div className="relative w-full h-[280px] rounded-2xl bg-[#142318] border border-[#2b4d36] overflow-hidden p-4 select-none">
              {/* Satellite coastal texture */}
              <div
                className="absolute inset-0 opacity-30 bg-cover bg-center mix-blend-luminosity pointer-events-none"
                style={{
                  backgroundImage: "url('/images/dark_satellite_gis_peninsula_1789059036671.jpg')",
                }}
              />

              {/* SVG Topology & Zones */}
              <svg className="w-full h-full relative z-10" viewBox="0 0 400 240">
                {/* Coastline / Bay */}
                <path
                  d="M 0,220 Q 150,180 250,200 T 400,210 L 400,240 L 0,240 Z"
                  fill="#0c4a6e"
                  opacity="0.4"
                />

                {/* River Upstream to Coast */}
                <path
                  d="M 20,20 C 100,50 160,110 240,140 S 330,190 380,210"
                  fill="none"
                  stroke={riverDelta > 0.4 ? "#38bdf8" : "#0284c7"}
                  strokeWidth={6 + riverDelta * 4}
                  strokeLinecap="round"
                  opacity="0.8"
                />

                {/* Zone A: Old Town Riverbank (Upper Low-Lying) */}
                <g
                  onClick={() => setSelectedZoneId("zone-a")}
                  className="cursor-pointer transition-transform hover:scale-105"
                >
                  <polygon
                    points="30,40 120,30 140,90 50,100"
                    fill={
                      simulationResult?.affected_zones[0]?.simulated_risk &&
                      simulationResult.affected_zones[0].simulated_risk >= 70
                        ? "#dc2626"
                        : "#ea580c"
                    }
                    fillOpacity="0.45"
                    stroke="#f97316"
                    strokeWidth="1.5"
                    strokeDasharray="3 3"
                  />
                  <text
                    x="80"
                    y="70"
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="10"
                    fontWeight="bold"
                  >
                    Zone A: Old Town
                  </text>
                  <text x="80" y="82" textAnchor="middle" fill="#fed7aa" fontSize="8">
                    Risk: {simulationResult?.affected_zones[0]?.simulated_risk ?? 76}
                  </text>
                </g>

                {/* Zone B: Midstream Industrial (Elevated) */}
                <g
                  onClick={() => setSelectedZoneId("zone-b")}
                  className="cursor-pointer transition-transform hover:scale-105"
                >
                  <polygon
                    points="150,80 260,70 270,140 160,140"
                    fill="#eab308"
                    fillOpacity="0.35"
                    stroke="#facc15"
                    strokeWidth="1.5"
                  />
                  <text
                    x="210"
                    y="105"
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="10"
                    fontWeight="bold"
                  >
                    Zone B: Midstream
                  </text>
                  <text x="210" y="117" textAnchor="middle" fill="#fef08a" fontSize="8">
                    Risk: {simulationResult?.affected_zones[1]?.simulated_risk ?? 51}
                  </text>
                </g>

                {/* Zone C: Coastal Port Corridor */}
                <g
                  onClick={() => setSelectedZoneId("zone-c")}
                  className="cursor-pointer transition-transform hover:scale-105"
                >
                  <polygon
                    points="260,150 380,140 370,200 250,190"
                    fill="#10b981"
                    fillOpacity="0.35"
                    stroke="#34d399"
                    strokeWidth="1.5"
                  />
                  <text
                    x="310"
                    y="172"
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="10"
                    fontWeight="bold"
                  >
                    Zone C: Port
                  </text>
                  <text x="310" y="184" textAnchor="middle" fill="#a7f3d0" fontSize="8">
                    Risk: {simulationResult?.affected_zones[2]?.simulated_risk ?? 36}
                  </text>
                </g>

                {/* Critical Hospital Marker */}
                <g transform="translate(110, 85)">
                  <circle
                    r="8"
                    fill={hospitalRoadOpen ? "#22c55e" : "#ef4444"}
                    className={!hospitalRoadOpen ? "animate-ping" : ""}
                    opacity={!hospitalRoadOpen ? "0.75" : "0.9"}
                  />
                  <circle r="7" fill={hospitalRoadOpen ? "#15803d" : "#b91c1c"} />
                  <text
                    x="0"
                    y="3"
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="9"
                    fontWeight="bold"
                  >
                    H
                  </text>
                  <text
                    x="0"
                    y="16"
                    textAnchor="middle"
                    fill="#fef2f2"
                    fontSize="7"
                    fontWeight="bold"
                  >
                    Hospital
                  </text>
                </g>

                {/* Substation Marker */}
                <g transform="translate(230, 75)">
                  <rect
                    x="-6"
                    y="-6"
                    width="12"
                    height="12"
                    rx="2"
                    fill={substationActive ? "#3b82f6" : "#ef4444"}
                  />
                  <text
                    x="0"
                    y="3"
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="8"
                    fontWeight="bold"
                  >
                    ⚡
                  </text>
                  <text x="0" y="15" textAnchor="middle" fill="#e0f2fe" fontSize="7">
                    220kV
                  </text>
                </g>

                {/* Upstream Sensor Node */}
                <g transform="translate(45, 25)">
                  <circle
                    r="6"
                    fill={
                      sensorStatus === "HEALTHY"
                        ? "#10b981"
                        : sensorStatus === "DEGRADED"
                          ? "#f59e0b"
                          : "#ef4444"
                    }
                  />
                  <text x="10" y="4" fill="#ffffff" fontSize="8">
                    SN-UP-01 ({sensorStatus})
                  </text>
                </g>

                {/* Deployed Barriers Indicator */}
                {barriersUnits > 0 && (
                  <path
                    d="M 40,55 Q 80,75 110,95"
                    fill="none"
                    stroke="#38bdf8"
                    strokeWidth="3.5"
                    strokeDasharray="4 2"
                  />
                )}
              </svg>

              {/* Map Legend */}
              <div className="absolute bottom-2 left-2 flex items-center gap-3 bg-[#0f1d13]/85 backdrop-blur-md px-2.5 py-1 rounded-lg border border-[#2b4d36] text-[9px] text-[#cbd5cc]">
                <div className="flex items-center gap-1">
                  <span className="size-2 rounded-full bg-[#ef4444]" />
                  <span>High Risk</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="size-2 rounded-full bg-[#eab308]" />
                  <span>Elevated</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="size-2 rounded-full bg-[#10b981]" />
                  <span>Moderate</span>
                </div>
              </div>
            </div>

            {/* Affected Assets Strip */}
            <div className="mt-3 space-y-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#867e6c]">
                Critical Asset Impacts (Simulated Envelopes)
              </span>
              <div className="grid grid-cols-3 gap-2">
                {simulationResult?.affected_assets?.map((asset) => (
                  <div
                    key={asset.asset_id}
                    className="p-2 rounded-xl bg-[#f4efe4] border border-[#ded5c2] flex flex-col justify-between"
                  >
                    <div className="text-[11px] font-bold text-[#1a2d21] truncate">
                      {asset.name}
                    </div>
                    <div className="flex items-center justify-between text-[9.5px] mt-1 text-[#716a5b]">
                      <span>{asset.category || asset.asset_type || "Infrastructure"}</span>
                      <span
                        className={`font-bold ${
                          (asset.status || asset.simulated_status || "").includes("THREATENED") ||
                          (asset.status || asset.simulated_status || "").includes("SURCHARGE") ||
                          (asset.status || asset.simulated_status || "").includes("TRIPPED") ||
                          (asset.status || asset.simulated_status || "").includes("ISOLATED") ||
                          (asset.status || asset.simulated_status || "").includes("OVERFLOW")
                            ? "text-[#b91c1c]"
                            : "text-[#15803d]"
                        }`}
                      >
                        {asset.status || asset.simulated_status || "OPERATIONAL"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── RIGHT COLUMN: Metric Comparison & Impact Statement (4 cols) ── */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-[#fcfbf7] rounded-3xl p-5 border border-[#dfd7c4] shadow-xs space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[#1a2d21] flex items-center justify-between">
              <span>Modeled Metric Comparison</span>
              <span className="text-[10px] font-semibold text-[#0f766e]">
                Baseline vs Simulated
              </span>
            </span>

            {/* Metric Comparison Cards */}
            <div className="space-y-2">
              {simulationResult?.metrics_comparison?.map((item) => {
                const isWorse = item.absolute_delta > 0;
                const isRiskReduction = item.metric_name?.includes("Residual Risk") ?? false;
                return (
                  <div
                    key={item.metric_name}
                    className="p-2.5 rounded-2xl bg-[#f4efe4] border border-[#ded5c2] flex items-center justify-between"
                  >
                    <div className="min-w-0 pr-2">
                      <div className="text-xs font-semibold text-[#2c3329] truncate">
                        {item.metric_name}
                      </div>
                      <div className="text-[10px] text-[#716a5b] mt-0.5 truncate">
                        {item.interpretation}
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="font-mono font-bold text-xs text-[#1a2d21]">
                        {item.simulated}{" "}
                        <span className="text-[9px] font-normal text-[#867e6c]">
                          {item.unit.split(" ")[0]}
                        </span>
                      </div>
                      <div
                        className={`text-[10px] font-bold flex items-center justify-end gap-0.5 ${
                          isRiskReduction
                            ? "text-[#15803d]"
                            : isWorse
                              ? "text-[#b91c1c]"
                              : "text-[#15803d]"
                        }`}
                      >
                        {item.absolute_delta > 0 ? (
                          <ArrowUpRight className="size-3" />
                        ) : item.absolute_delta < 0 ? (
                          <ArrowDownRight className="size-3" />
                        ) : null}
                        <span>
                          {item.absolute_delta > 0
                            ? `+${item.absolute_delta}`
                            : `${item.absolute_delta}`}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Headline Impact Statement */}
            {simulationResult && (
              <div className="p-3 rounded-2xl bg-[#0f766e]/10 border border-[#0f766e]/30 text-xs text-[#134e4a] leading-relaxed">
                <span className="font-bold">MODELED IMPACT STATEMENT: </span>
                <span>{simulationResult.modeled_impact_statement}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── BOTTOM PANEL: RECOMMENDED INTERVENTION & MULTI-CRITERIA RANKING ── */}
      <div className="bg-[#fcfbf7] rounded-3xl p-6 border border-[#dfd7c4] shadow-xs space-y-4">
        {/* Banner: Best Modeled Option */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-gradient-to-r from-[#115e59] to-[#0f766e] text-white shadow-md">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-full text-[9px] font-extrabold uppercase tracking-wider bg-[#99f6e4] text-[#115e59]">
                BEST MODELED OPTION
              </span>
              <span className="text-xs font-semibold text-[#99f6e4]">
                Multi-Attribute Utility Optimization
              </span>
            </div>
            <div className="font-editorial text-lg font-bold">
              {simulationResult?.best_modeled_option ??
                "Rapid Deployment of 500m Modular Flood Barriers"}
            </div>
            <div className="text-xs text-[#ccfbf1]">
              Safeguards an estimated{" "}
              <span className="font-bold underline">
                {simulationResult?.estimated_population_protected?.toLocaleString() ?? "36,500"}
              </span>{" "}
              residents and {simulationResult?.critical_assets_safeguarded ?? 3} critical
              infrastructure nodes.
            </div>
          </div>

          <button
            onClick={() =>
              setStagedIntervention(
                simulationResult?.best_modeled_option ??
                  "Rapid Deployment of 500m Modular Flood Barriers",
              )
            }
            className="px-4 py-2.5 rounded-xl bg-white hover:bg-[#f0fdf4] text-[#115e59] font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shrink-0 cursor-pointer"
          >
            {stagedIntervention ? (
              <>
                <Check className="size-4 text-[#15803d]" />
                <span>Staged in EOC Console</span>
              </>
            ) : (
              <>
                <Zap className="size-4 text-[#0f766e]" />
                <span>Stage Tactical Package</span>
              </>
            )}
          </button>
        </div>

        {/* 5 Evaluated Intervention Packages Table */}
        <div className="space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#867e6c] flex items-center justify-between">
            <span>Evaluated Countermeasure Packages (Ranked by Multi-Attribute Utility Score)</span>
            <span className="text-[10px] text-[#716a5b]">
              Weights: Risk Reduction (35%) · Pop (25%) · Assets (20%) · Cascade (10%) · ETA (10%)
            </span>
          </span>

          <div className="overflow-x-auto rounded-2xl border border-[#ded5c2]">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#ede5d5] text-[#554e40] font-bold uppercase text-[9.5px]">
                <tr>
                  <th className="p-3">Rank</th>
                  <th className="p-3">Package Name</th>
                  <th className="p-3">Category</th>
                  <th className="p-3 text-right">Simulated Risk Delta</th>
                  <th className="p-3 text-right">Est. Pop Protected</th>
                  <th className="p-3 text-right">Assets</th>
                  <th className="p-3 text-right">ETA</th>
                  <th className="p-3 text-right">Est. Cost</th>
                  <th className="p-3 text-right">Utility Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#ded5c2] bg-[#fcfbf7]">
                {simulationResult?.intervention_ranking?.map((intv) => (
                  <tr
                    key={intv.intervention_id}
                    className={`hover:bg-[#f4efe4] transition-colors ${
                      intv.is_best_modeled_option ? "bg-[#f0fdfa]/80 font-semibold" : ""
                    }`}
                  >
                    <td className="p-3">
                      <span
                        className={`size-6 rounded-full inline-flex items-center justify-center font-mono font-bold text-xs ${
                          intv.rank === 1
                            ? "bg-[#0f766e] text-white"
                            : "bg-[#e5decb] text-[#554e40]"
                        }`}
                      >
                        #{intv.rank}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="font-bold text-[#1a2d21]">{intv.name}</div>
                      <div className="text-[10px] text-[#716a5b]">{intv.description}</div>
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded-md text-[9px] font-bold bg-[#ded5c2] text-[#554e40]">
                        {intv.category}
                      </span>
                    </td>
                    <td className="p-3 text-right font-mono text-[#15803d] font-bold">
                      -{intv.modeled_risk_reduction_points} pts
                    </td>
                    <td className="p-3 text-right font-mono text-[#1a2d21]">
                      {intv.estimated_population_protected.toLocaleString()}
                    </td>
                    <td className="p-3 text-right font-mono text-[#1a2d21]">
                      {intv.critical_assets_safeguarded}
                    </td>
                    <td className="p-3 text-right font-mono text-[#716a5b]">
                      {intv.response_eta_minutes} min
                    </td>
                    <td className="p-3 text-right font-mono text-[#716a5b]">
                      ${intv.estimated_cost_usd.toLocaleString()}
                    </td>
                    <td className="p-3 text-right font-mono font-bold text-[#0f766e]">
                      {intv.multi_attribute_utility_score.toFixed(3)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Operational Assumptions & Safety Disclaimers */}
        <div className="p-4 rounded-2xl bg-[#f4efe4] border border-[#ded5c2] space-y-2 text-[11px] text-[#716a5b]">
          <div className="font-bold text-[#2c3329] uppercase tracking-wider text-[10px] flex items-center gap-1.5">
            <Shield className="size-3.5 text-[#0f766e]" />
            Simulator Assumptions, Limitations & Safety Rules
          </div>
          <ul className="list-disc pl-4 space-y-0.5">
            {simulationResult?.assumptions?.map((assump, idx) => (
              <li key={idx}>{assump}</li>
            ))}
          </ul>
          <div className="text-[10px] text-[#867e6c] font-medium pt-1 border-t border-[#dfd7c4]">
            {simulationResult?.deterministic_safety_note}
          </div>
        </div>
      </div>
    </div>
  );
}
