---
layout: default
title: Deployment
parent: Install & config
nav_order: 3
---

## Deployment

To deploy the platform, run:

```bash
./compose.sh up -d
```

After running the deployment command, check whether the `init` service has exited with a code 0 (indicating success). If it did not, restart the service. This issue can occur due to timing problems, often because the required SQL tables have not been created yet.
