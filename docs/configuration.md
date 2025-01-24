## openpod.toml

The `openpod.toml` file is the configuration file for the OpenPod system. This file is used to configure the system and set up the necessary parameters for the system to function. The `openpod.toml` file is located in the root directory of the OpenPod system.

The `openpod.toml` file contains the following sections:

```toml
# Top-level settings
uuid      = "b2cc95b91e8341f7b7bdfc4fa1ccf4a1"
debug     = false
timezone  = "UTC"
url       = "recursion.space"
api_url   = "api.recursion.space"

[openpod]
repo    = "https://github.com/RecursionSpace/OpenPod"
branch  = "release"
commit  = "fd3c871ce75bb8f6c717c651ff0129d00af836a1"
version = "fd3c871ce75bb8f6c717c651ff0129d00af836a1"

[xbee]
ky = "dd5e4b7d-44f0-4a53-b820-d7c4a66db09a"
op = false

[gpio]
led_io   = 23
led_stat = 17

[hardware]
controller = "BCM2835"
revision   = "abcd"
serial     = "dcba"
model      = "Raspberry Pi Model B Rev 2"
```
