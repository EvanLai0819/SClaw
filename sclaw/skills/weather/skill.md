---
name: weather
description: Get current weather and forecasts via Open-Meteo API (no API key required). Uses JSON API with city coordinates.
homepage: https://open-meteo.com/en/docs
metadata: {"openclaw":{"emoji":"🌤️","requires":{"bins":["curl","jq"]}}}
---

# Weather Skill (Open-Meteo)

Get current weather conditions and forecasts using Open-Meteo API.

## When to Use

✅ **USE when:**
- "What's the weather in [city]?"
- "Will it rain today/tomorrow?"
- "Temperature in [location]"
- Weather forecast requests
- wttr.in fails or times out

❌ **DON'T use for:**
- Historical weather data
- Severe weather alerts
- Climate analysis

## City Coordinates

You need latitude/longitude for the city. Common cities:

| City | Latitude | Longitude |
|------|----------|-----------|
| Beijing | 39.9042 | 116.4074 |
| Shanghai | 31.2304 | 121.4737 |
| Guangzhou | 23.1291 | 113.2644 |
| Shenzhen | 22.5431 | 114.0579 |
| London | 51.5074 | -0.1278 |
| New York | 40.7128 | -74.0060 |
| Tokyo | 35.6762 | 139.6503 |

## Commands

### Current Weather
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=23.1291&longitude=113.2644&current_weather=true" | jq -r '"Guangzhou: ☁️ " + (.current_weather.temperature|tostring) + "°C, wind: " + (.current_weather.windspeed|tostring) + "km/h"'
```

### Current + Daily Forecast
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=23.1291&longitude=113.2644&current_weather=true&daily=weather_2m_max,weather_2m_min,precipitation_probability_max&timezone=auto" | jq -r '"Current: " + .current_weather.temperature + "°C, Max today: " + .daily.weather_2m_max[0] + "°C, Min: " + .daily.weather_2m_min[0] + "°C"'
```

### 7-Day Forecast
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=39.9042&longitude=116.4074&daily=weather_2m_max,weather_2m_min,precipitation_probability_max&timezone=auto" | jq -r '.daily | to_entries | .[] | "\(.key): Max \(.value.weather_2m_max)°C, Min \(.value.weather_2m_min)°C, Rain: \(.value.precipitation_probability_max)%"'
```

## Weather Codes

Open-Meteo uses WMO codes:
- `0` = Clear sky
- `1-3` = Partly cloudy
- `45-48` = Fog
- `51-55` = Drizzle
- `61-65` = Rain
- `71-77` = Snow
- `80-82` = Rain showers
- `95-99` = Thunderstorm

## Quick Responses

**"What's the weather in Guangzhou?"**
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=23.1291&longitude=113.2644&current_weather=true" | jq -r '"Guangzhou: " + (if .current_weather.weather <= 3 then "☀️" elif .current_weather.weather <= 48 then "🌫️" elif .current_weather.weather <= 65 then "🌧️" else "⛈️" end) + " " + .current_weather.temperature + "°C, wind: " + .current_weather.windspeed + "km/h"'
```

**"Will it rain today?"**
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=23.1291&longitude=113.2644&daily=precipitation_probability_max&timezone=auto" | jq -r 'if .daily.precipitation_probability_max[0] > 50 then "Yes, " + (.daily.precipitation_probability_max[0]|tostring) + "% chance of rain" else "Low chance: " + (.daily.precipitation_probability_max[0]|tostring) + "%" end'
```

## Tips

- **Find coordinates**: Use https://latitudelongitude.org/ to look up any city
- **Units**: Add `&temperature_unit=celsius` or `&temperature_unit=fahrenheit`
- **Timezone**: Use `&timezone=auto` for local time
- **No API key needed** — completely free
- **Rate limit**: Very generous, suitable for production

## Example Output

```json
{
  "latitude": 23.1291,
  "longitude": 113.2644,
  "current_weather": {
    "temperature": 22.5,
    "windspeed": 12.3,
    "weather": 2,
    "time": "2026-03-25T15:00"
  }
}
```
