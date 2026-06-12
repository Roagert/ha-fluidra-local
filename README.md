# Fluidra Local Server for Home Assistant

Home Assistant custom integration for a Fluidra / Swim & Fun / Amitime heat pump through a local bridge server.

This integration is designed for HACS custom repositories. Home Assistant talks only to your local bridge URL, for example:

```text
http://100.97.152.33:8765
```

The bridge server handles Fluidra protocol/auth details outside Home Assistant.

## Optional bridge authentication

Version `0.3.0` adds optional bearer-token support for the local bridge.

1. Start the bridge with an auth token, either through `FLUIDRA_LOCAL_AUTH_TOKEN` or `serve --auth-token`.
2. In Home Assistant, open **Settings → Devices & services → Fluidra Local Server → Configure**.
3. Enter the same token in `auth_token`.

When configured, Home Assistant sends `Authorization: Bearer <token>` to the bridge. Leave `auth_token` blank for an unauthenticated bridge.

## Features

- Climate entity for the pool heat pump
- Climate power on/off
- Dedicated Power switch entity
- Target temperature
- Preset/mode selection
- Pool temperature sensor
- Air temperature sensor
- Target/min/max setpoint sensors
- No Flow Error problem binary sensor (`off` = OK, `on` = error)

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


## Entities

The integration creates:

```text
climate.fluidra_local_heat_pump_pool_heat_pump
switch.fluidra_local_heat_pump_power
sensor.fluidra_local_heat_pump_pool_temperature
sensor.fluidra_local_heat_pump_air_temperature
sensor.fluidra_local_heat_pump_target_temperature
sensor.fluidra_local_heat_pump_minimum_setpoint
sensor.fluidra_local_heat_pump_maximum_setpoint
binary_sensor.fluidra_local_heat_pump_no_flow_error
```

`binary_sensor.fluidra_local_heat_pump_no_flow_error` uses Home Assistant's `problem` device class:

- `off` means normal / no flow error is not active.
- `on` means the heat pump reports a no-flow error.

## Brand assets

The HACS brand assets are included in `brand/` and `custom_components/fluidra_local/brand/`.
They are derived from the public-domain text logo hosted on Wikimedia Commons as `Fluidra_logo.svg`.
Fluidra is a trademark of Fluidra; the logo is used here only to identify the supported integration/device ecosystem.

## Polling and Home Assistant history

This integration is a `local_polling` integration. Home Assistant polls the local Fluidra bridge on a fixed interval and stores normal entity history through Home Assistant's Recorder/history system.

Default behavior:

- Poll interval: **30 seconds**.
- Configurable in the integration options as `scan_interval`.
- Safe range: **10 to 300 seconds**.
- If a temperature, power, flow, or mode value changes at the bridge/backend, the next poll updates the HA entity state.
- If the value has not changed, the HA entity keeps the same value; HA does not create fake state changes just because a poll happened.

The bridge remains the source of truth for the current Fluidra state. The HA coordinator refreshes from the bridge periodically and after HA-originated write commands.
