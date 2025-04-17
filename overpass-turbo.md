# search layer is negative
```bash
[out:json][timeout:300];

relation["route"="subway"]["network"="Delhi Metro"];
way(r);
way._["layer"~"^(-1|-2|-3|-4|-5|-6|-7|-8|-9)$"];

out geom;
```