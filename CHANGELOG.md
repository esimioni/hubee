# Changelog


## [1.0.0] - 2025-03-27

It's been around 2½ years since the last upadatee and I'm using this project at my home with great success, so now I'm confident in releasing a version worth of the `1.0.0` label :)


### Major changes

- Memory footprint - several changes were maded that reduced it significantly  
- Errors are now sent back to the coordinator and printed in the logs  
- Improvements on I2C error handling  
  - The module can now start even if it can't communicate with an I2C sensor  
  - The module will ignore single failures in sensor reading, reporting only if the error persists after 10 minutes  
- Code prepared to work with more models of illuminance sensors, like `VEML7700`


### Changed features

- Update XBee firmware from `1010` to `1014`  
- Several minor fixes and improvements


## [0.9.0] - 2022-10-23

- Initial release