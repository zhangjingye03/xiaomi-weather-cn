# Xiaomi Weather China for Home Assistant

An unofficial Home Assistant weather integration for Xiaomi Weather's China endpoint. It provides current observations plus hourly and 15-day daily forecasts for Chinese locations.

> **Unofficial project.** This is not affiliated with Xiaomi. It uses the same public mobile-client endpoint used by Xiaomi Weather. The endpoint may change without notice.

## Features

- Config Flow: add a location from **Settings → Devices & services → Add integration**
- Coordinate lookup resolves Xiaomi's district weather station automatically
- Current condition, temperature, feels-like temperature, humidity, pressure, visibility, UV, and wind
- Hourly and daily forecasts
- Polls every 10 minutes; no account or personal API key is required

## Installation with HACS

1. In HACS, open **Custom repositories**.
2. Add this repository as an **Integration**.
3. Download **Xiaomi Weather China** and restart Home Assistant.
4. Add the integration from **Settings → Devices & services**.
5. Enter a name and the latitude/longitude of the desired location.

For a district-level station when Xiaomi's coordinate lookup is too broad, create the location at the desired district's representative coordinates. For example, the verified Haizhu station is `101280108`; Shenzhen Nanshan is `101280604`.

## Data source and privacy

Weather data is requested directly by Home Assistant from `weatherapi.market.xiaomi.com`. No data is proxied through this project. Xiaomi's upstream attribution includes Beijing Meteorological Service, Caiyun, and CNEMC.

## Development

The integration targets Home Assistant 2026.7+. Run Home Assistant's test environment or use a development container before contributing. Do not submit private Xiaomi credentials, Home Assistant access tokens, or location history.

## License

MIT.
