# Climate Sentinel

Build the foundational frontend and visual design system for an elite climate-risk intelligence platform named:

╔══════════════════════════════════════╗

        CLIMATESHIELD

PREDICT. SIMULATE. DECIDE. PROTECT.

╚══════════════════════════════════════╝

IMPORTANT:

This is a hackathon-grade climate resilience command platform.

The visual experience must immediately communicate:

"THIS SYSTEM UNDERSTANDS WHAT IS HAPPENING,

WHERE IT IS HAPPENING,

WHAT WILL HAPPEN NEXT,

WHAT WILL BE AFFECTED,

AND WHAT SHOULD BE DONE."

Do NOT build a generic SaaS dashboard.

Do NOT build a generic weather application.

Do NOT build a generic GIS application.

Do NOT build a collection of disconnected analytics pages.

Build the visual foundation of a:

CLIMATE OPERATIONS + RISK INTELLIGENCE CENTER.

The product should feel like a combination of:

- emergency operations center

- geospatial intelligence platform

- AI decision-support system

- climate command center

- mission-control interface

- premium enterprise software

It should look credible enough that a municipal disaster-management officer could imagine using it.

========================================================

CORE PRODUCT STORY

========================================================

Everything in the interface must support this chain:

SENSE

↓

VALIDATE

↓

PREDICT

↓

MAP RISK

↓

EXPLAIN

↓

UNDERSTAND CASCADE

↓

OPTIMIZE RESPONSE

↓

SIMULATE

↓

ALERT

↓

ACT

↓

LEARN

This chain should influence the entire information architecture.

The application must visually communicate that ClimateShield converts:

ENVIRONMENTAL DATA

into

CLIMATE RISK

into

EXPOSURE

into

DECISION

into

ACTION.

========================================================

VISUAL IDENTITY

========================================================

Create a cinematic but professional dark interface.

NOT cyberpunk.

NOT gaming UI.

NOT flashy.

NOT excessive glassmorphism.

Think:

"Bloomberg Terminal meets modern disaster-response command center meets advanced geospatial intelligence."

The interface should feel:

- serious

- intelligent

- high-trust

- operational

- technically advanced

- calm under pressure

- data-dense

- precise

The design must have a strong visual hierarchy.

========================================================

COLOR SYSTEM

========================================================

BASE:

#070A0E

#0B0F14

#10151C

Panels:

#111820

#141B23

Borders:

subtle cool-gray borders.

Primary text:

#F5F7FA

Secondary text:

#8B96A5

DATA / INTELLIGENCE:

Cyan / electric blue

Use this for:

- active data

- AI intelligence

- sensor telemetry

- selected elements

- system connections

- live indicators

RISK:

LOW → green

MODERATE → yellow

HIGH → orange

CRITICAL → red

IMPORTANT:

Never flood the UI with red.

Red must communicate genuine operational urgency.

========================================================

SIGNATURE VISUAL ELEMENT

========================================================

Create a subtle "LIVE CLIMATE INTELLIGENCE" visual language.

Use small animated indicators:

● LIVE

DATA STREAM

MODEL ACTIVE

SENSOR ONLINE

FORECAST RUNNING

Do NOT animate everything.

Animations should communicate system activity.

Example:

LIVE CLIMATE INTELLIGENCE

●

Last synchronized

02:14 ago

========================================================

TYPOGRAPHY

========================================================

Use:

Inter / Geist

Strong numerical typography.

Technical labels can use uppercase.

Example:

OVERALL CLIMATE RISK

82

/100

CRITICAL

Use compact typography for metadata.

Avoid oversized marketing typography.

This is an operational command system.

========================================================

APPLICATION FRAME

========================================================

Build a professional desktop-first command-center frame.

Structure:

┌────────────────────────────────────────────────────────────┐

│ CLIMATESHIELD DEMO CITY ● LIVE INTELLIGENCE USER │

├──────────────┬─────────────────────────────────────────────┤

│ │ │

│ NAVIGATION │ │

│ │ MAIN OPERATIONS │

│ │ │

│ │ │

│ │ │

│ │ │

│ │ │

│ │ │

├──────────────┴─────────────────────────────────────────────┤

│ SYSTEM HEALTH | DATA | SENSOR NETWORK | MODEL | ALERTS │

└────────────────────────────────────────────────────────────┘

========================================================

SIDEBAR

========================================================

Top:

CLIMATESHIELD

Small label:

CLIMATE INTELLIGENCE PLATFORM

Navigation:

COMMAND CENTER

RISK MAP

FORECAST

CASCADE

RESPONSE OPTIMIZER

DIGITAL TWIN

INCIDENTS

ASSETS

ANALYTICS

Divider

SYSTEM

DATA SOURCES

ALERT CENTER

SYSTEM HEALTH

SETTINGS

At bottom:

OPERATIONAL MODE

● LIVE

Allow modes:

LIVE

DEMO

DEGRADED

The active navigation item should have a subtle cyan intelligence indicator.

Do NOT use giant pill-shaped navigation.

========================================================

TOP COMMAND BAR

========================================================

Build a high-quality command bar.

Left:

LOCATION

Demo City

▼

Middle:

● LIVE CLIMATE INTELLIGENCE

Last sync:

2 min ago

Right:

System Health

● 98%

Alerts

03

Search

Operator

========================================================

COMMAND BAR BEHAVIOR

========================================================

Location selector should visually suggest that ClimateShield can operate across:

CITY

ZONE

ASSET

Do not implement complex functionality yet.

Prepare the UI for future API integration.

========================================================

GLOBAL OPERATIONAL STATUS STRIP

========================================================

At the bottom or top of the main workspace create a compact system telemetry strip.

Example:

WEATHER

● HEALTHY

GIS

● HEALTHY

IoT

● HEALTHY

RISK ENGINE

● ACTIVE

ALERT SERVICE

● HEALTHY

DATABASE

● HEALTHY

This should look like infrastructure telemetry rather than ordinary dashboard cards.

========================================================

RISK LANGUAGE

========================================================

Create a unified risk vocabulary.

Risk:

0–29

LOW

30–59

MODERATE

60–79

HIGH

80–100

CRITICAL

Every risk object should be capable of showing:

RISK SCORE

CONFIDENCE

DATA FRESHNESS

RISK VELOCITY

Example:

87 / 100

CRITICAL

93% CONFIDENCE

+14 / HR

2 MIN AGO

These must be visually distinct.

========================================================

CORE REUSABLE COMPONENTS

========================================================

Create a professional component library.

Components:

MetricCard

RiskMetric

RiskBadge

SeverityBadge

ConfidenceIndicator

DataFreshnessIndicator

RiskVelocityIndicator

StatusIndicator

LiveIndicator

Panel

PanelHeader

SectionHeader

PageHeader

CommandBar

DataTable

AlertCard

IncidentCard

AssetCard

ZoneCard

ActionCard

Timeline

ForecastChart

RiskChart

MapContainer

MapLayerControl

SystemHealthStrip

LoadingState

ErrorState

EmptyState

OfflineState

DegradedState

LowConfidenceState

========================================================

MAP FOUNDATION

========================================================

Create a reusable MapContainer.

The map must eventually support:

Risk Zones

Population Exposure

Critical Infrastructure

Incidents

IoT Sensors

River Monitoring Nodes

Forecast Layers

Historical Flood Areas

Heat Risk

Road Exposure

For now use a polished dark geospatial map implementation or structured map placeholder.

DO NOT create a fake 3D city.

DO NOT create photorealistic buildings.

The map should be analytical.

Prepare the component to consume:

GeoJSON

coordinates

risk polygons

asset markers

sensor markers

incident markers

========================================================

GEO-INTELLIGENCE VISUAL LANGUAGE

========================================================

Create visual conventions for:

ZONE

ASSET

INCIDENT

SENSOR

RIVER NODE

HAZARD

Each should have its own recognizable icon and interaction state.

Example:

Zone:

polygon

Asset:

infrastructure marker

Incident:

warning marker

Sensor:

telemetry node

River:

connected sensor chain

========================================================

RIVER SYSTEM FOUNDATION

========================================================

ClimateShield will eventually contain a real-time river monitoring chain.

Preserve this architecture visually:

UPSTREAM

↓

MIDSTREAM

↓

DOWNSTREAM

↓

LOCAL RISK ZONES

Sensor data will eventually flow:

ESP32

-

Water Level Sensor

-

Rainfall Sensor

-

GPS

↓

LoRa

↓

Gateway

↓

MQTT

↓

FastAPI

↓

PostgreSQL/PostGIS

↓

ClimateShield Risk Engine

↓

Alerts / Decision Support

Do not build the hardware backend yet.

Only create reusable visual concepts for:

SensorNode

RiverNode

TelemetryStatus

RiverFlowConnection

These will be connected to real backend data later.

========================================================

DATA CONFIDENCE

========================================================

Make uncertainty a first-class design element.

ClimateShield should never visually imply:

"AI IS ALWAYS CORRECT."

Create components for:

HIGH CONFIDENCE

MEDIUM CONFIDENCE

LOW CONFIDENCE

STALE DATA

DEGRADED DATA

Example:

RISK

87

CONFIDENCE

93%

DATA

FRESH

Another example:

RISK

74

CONFIDENCE

51%

WARNING:

Limited environmental data.

This should look professional rather than alarming.

========================================================

DEGRADED MODE

========================================================

Create a system-wide degraded mode.

Example:

┌──────────────────────────────────────────────┐

│ ⚠ DEGRADED INTELLIGENCE │

│ │

│ Live rainfall API unavailable. │

│ Using last validated observation. │

│ │

│ Last valid update: 12:41 PM │

└──────────────────────────────────────────────┘

The interface must never simply break when data is unavailable.

The hackathon specifically expects consideration of:

sensor failure

API failure

stale data

duplicate events

failed alerts

incorrect AI assessment

large event spikes

Prepare visual states for all of these.

========================================================

DEMO DATA MODEL

========================================================

Create realistic prototype entities.

CITY:

Demo City

ZONES:

Zone A

Zone B

Zone C

Zone D

ASSETS:

District Hospital

Emergency Response Center

Main Bridge

Water Treatment Facility

Power Substation

Primary School

HAZARDS:

Flood

Extreme Rainfall

Heat

SENSOR NODES:

Upstream Node

Midstream Node

Downstream Node

INCIDENTS:

Flooding

Road Waterlogging

Drainage Stress

Extreme Heat

Do NOT use lorem ipsum.

========================================================

FRONTEND ARCHITECTURE

========================================================

Use:

TypeScript

React

Component-based architecture.

Create clean folders:

src/

components/

components/ui/

components/climate/

components/geospatial/

components/risk/

components/operations/

components/system/

pages/

services/

types/

lib/

hooks/

Prepare API abstraction.

Do NOT tightly couple UI components to mock data.

========================================================

TYPED DATA CONTRACTS

========================================================

Create interfaces/types for:

RiskZone

RiskScore

RiskDriver

Forecast

CascadeNode

CascadeEdge

Asset

Incident

Recommendation

SimulationScenario

SimulationResult

Alert

DataSource

SensorNode

RiverNode

SystemHealth

========================================================

ROUTING

========================================================

Create routes:

/overview

/risk-map

/forecast

/cascade

/response-optimizer

/digital-twin

/incidents

/assets

/analytics

/data-sources

/alerts

/settings

Every route must load correctly.

Do not fully implement those modules yet.

Only create their structural page shells using the same design system.

========================================================

GLOBAL UX PRINCIPLE

========================================================

The interface must constantly answer:

WHERE?

WHEN?

WHY?

WHO / WHAT IS EXPOSED?

WHAT SHOULD WE DO?

WHAT HAPPENS IF WE DO IT?

These questions should become the DNA of the product.

========================================================

VISUAL DETAILS

========================================================

Use:

- subtle 1px borders

- restrained shadows

- compact spacing

- high-density information layout

- clean data tables

- professional iconography

- small status indicators

- subtle hover states

- smooth page transitions

Avoid:

- huge cards

- excessive empty space

- giant gradients

- excessive rounded rectangles

- decorative illustrations

- stock images

- unnecessary 3D

- excessive glowing effects

- fake AI chat bubbles

========================================================

SIGNATURE CLIMATESHIELD ELEMENT

========================================================

Create a subtle recurring visual motif:

a thin cyan "intelligence line"

This can appear in:

- active navigation

- live data

- selected map zones

- system telemetry

- model activity

- data pipelines

It should become part of the brand identity.

Use it sparingly.

========================================================

ACCESSIBILITY

========================================================

Implement:

- strong contrast

- keyboard navigation

- focus states

- semantic buttons

- accessible labels

- tooltips

- risk label + color + icon

Never communicate severity using color alone.

========================================================

RESPONSIVE

========================================================

Desktop-first.

Tablet:

collapsible sidebar.

Mobile:

compact navigation

stacked intelligence panels

horizontal metric scrolling

usable map

Do not simply shrink the desktop layout.

========================================================

MOST IMPORTANT REQUIREMENT

========================================================

This first build is NOT supposed to contain every feature.

It establishes the DNA of ClimateShield.

The final result should make a judge think:

"This is an actual climate operations platform."

NOT:

"This is another hackathon dashboard."

Build the foundation with enough visual quality that subsequent prompts can add:

Risk Intelligence

Forecasting

Cascade Analysis

Response Optimization

Digital Twin

Incident Operations

IoT River Monitoring

Analytics

without changing the design language.

========================================================

STOP CONDITION

========================================================

After completing this prompt:

DO NOT automatically build the full Command Center functionality.

DO NOT build the Forecast engine.

DO NOT build the Cascade engine.

DO NOT build the Digital Twin.

DO NOT build backend logic.

DO NOT invent AI models.

DO NOT add unnecessary features.

Complete only:

1. Design system

2. Application shell

3. Navigation

4. Command bar

5. System telemetry foundation

6. Risk visual language

7. Reusable components

8. Map foundation

9. River-system visual foundation

10. Data confidence states

11. Degraded-mode states

12. Routing

13. Typed frontend contracts

14. Demo/live/degraded mode foundation

Then STOP.

The next prompt will build the actual CLIMATESHIELD COMMAND CENTER.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/6dd89803-4c6f-4548-b13a-d9d3c059af3b).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
