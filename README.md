# SMA SpeedWire Integration for Home Assistant  

Custom integration for Home Assistant to connect SMA inverters via SpeedWire protocol

## Installation
Note: Restart is always required after installation.

## Setup
After installation, you should find **SMA SpeedWire** under the Configuration -> Integrations -> Add integration.

Enter IP and password (default password is '0000') of inverter on integration setup.

## Features
Provides 3 entities
- Energy production total in kWh
- Energy production today in kWh
- Power production now in kW

## Debugging
Add the following to `configuration.yml` to show debugging logs. Please make sure to include debug logs when filing an issue.

See [logger intergration docs](https://www.home-assistant.io/integrations/logger/) for more information to configure logging.

```yml
logger:
  default: warning
  logs:
    custom_components.sma_sppedwire: debug
```

## Credits
Inspired from [SMAInverter](https://github.com/Rincewind76/SMAInverter).
