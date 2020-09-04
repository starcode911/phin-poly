
# pHin Smart Water Monitor node server

Make your pool chemical information available in the ISY

(c) 2020 starcode911

MIT license.


## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes, Polyglot will reboot your ISY, you can watch the status in the main polyglot log.
4. Once your ISY is back up open the Admin Console.
5. Configure the node server per configuration section below.

### Node Settings
The settings for this node are:

#### Short Poll
   * How often to poll the pHin service for current water data. pHin only updates every x minutes

#### Long Poll


#### Token
	* Your Token, needed to authorize connection to the pHin API.


## Requirements

1. Polyglot V2
2. This has only been tested with ISY 5.2.0 so it is not guaranteed to work with any other version.

# Upgrading

The nodeserver keeps track of the version number and when a profile rebuild is necessary.  The profile/version.txt will contain the profile_version which is updated in server.json when the profile should be rebuilt.

# Release Notes

- 0.1.0 09/04/2020
   - Initial version published to github 
