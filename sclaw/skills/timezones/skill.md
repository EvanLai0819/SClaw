---
name: get-time
description: Get current time in a specific city or timezone
triggers:
  - time
  - current time
  - what time
  - time in
  - timezone
---

# Time Zone Lookup

This skill provides the current time in major cities around the world.

## Parameters

- **city**: City name (e.g., 'New York', 'Tokyo', 'London', 'Paris')

## Supported Cities

### North America
- New York, Los Angeles, San Francisco, Chicago, Toronto, Vancouver, Mexico City

### Europe
- London, Paris, Berlin, Moscow, Amsterdam, Istanbul

### Asia
- Tokyo, Beijing, Shanghai, Dubai, Mumbai, Singapore, Hong Kong, Seoul, Bangkok

### Australia
- Sydney

## Usage Examples

```
What time is it in Tokyo?
```

```
Get the current time in London
```

```
Time in New York
```

```
What's the time in Paris right now?
```

## Output Format

Returns time in format: `HH:MM:SS TZ (Day, Month D)`

Example: `14:30:45 JST (Thursday, March 20)`

## Notes

- Supports major cities worldwide
- If city is not recognized, suggests available options
- Uses accurate timezone data
- Time is real-time based on current moment
