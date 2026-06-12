# Fluidra Local Server for Home Assistant

Home Assistant custom integration for a Fluidra / Swim & Fun / Amitime heat pump through a local bridge server.

This integration is designed for HACS custom repositories. Home Assistant talks only to your local bridge URL, for example:

```text
http://100.97.152.33:8765
```

The bridge server handles Fluidra protocol/auth details outside Home Assistant.

## Features

- Climate entity for the pool heat pump
- Power on/off
- Target temperature
- Preset/mode selection
- Pool temperature sensor
- Air temperature sensor
- Target/min/max setpoint sensors
- No-flow problem binary sensor

## Preset modes

```text
Smart Heating      -> 0
Smart Cooling      -> 1
Smart Auto         -> 2
Boost Heating      -> 3
Silence Heating    -> 4
Boost Cooling      -> 5
Silence Cooling    -> 6
```

## Install with HACS

1. HACS → Integrations → three-dot menu → Custom repositories.
2. Add this repository URL as category `Integration`.
3. Install `Fluidra Local Server`.
4. Restart Home Assistant.
5. Settings → Devices & services → Add integration → `Fluidra Local Server`.
6. Enter your bridge base URL, for example `http://100.97.152.33:8765`.

## Bridge server requirement

The bridge server must expose:

```text
GET /state
GET /capabilities
GET /component/<id>
PUT /power
PUT /temperature
PUT /mode
```

The companion bridge implementation lives in the reverse-engineering/project repo where it was developed.

## Verified components

```text
13 power
14 mode
15 target temperature x10
19 pool temperature x10
28 no-flow status
67 air temperature x10
81 min setpoint
82 max setpoint
```

## Security note

Do not put Fluidra tokens or credentials into Home Assistant. Keep them on the local bridge host. This integration stores only the local bridge URL.
