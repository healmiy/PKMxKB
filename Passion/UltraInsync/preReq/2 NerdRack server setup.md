---
ID: scn_ca064d2f
Class: Scene
Act: 1
cssclasses:
  - cornell-border
  - cornell-left
  - cornell-livepreview
  - wide-page
operonId: vlv34iw
operonProjectStage: Default.Working
priority: Zero
assignees:
  - "[[Healmiy]]"
description: have an always on device as central node for Vertex Proxy, Headscale, Syncthing etc
datetimeCreated: 2026-07-05T01:45:31
timestamp: 2026-07-10T14:53:31
stakeholder:
  - "[[AGENTS|aigents]]"
Status: Working
type:
  - asset
progress: 0
directSubtaskCount: 1
directDoneSubtaskCount: 0
directOpenSubtaskCount: 1
treeDescendantCount: 1
treeDoneDescendantCount: 0
treeOpenDescendantCount: 1
trackers:
  - 2026-07-05T01:58:27/2026-07-05T02:05:54
timeSpent: 0 hours 7 minutes
totalDuration: 2
tags:
  - decks
dg-publish: true
canvas:
  - "[[3a1. SyncThings Setup.canvas]]"
3a1. SyncThings Setup: []
Chapter: 3a1. SyncThings Setup
---

## Must have:
- [x] [[Syncthing]] - act as central node, especially for mobile devices
```
sudo apt-get update
sudo apt-get install syncthing

systemctl cat syncthing@.service
sudo systemctl daemon-reload
sudo systemctl enable syncthing@healmiy
sudo systemctl start syncthing@healmiy

sudo systemctl status syncthing@healmiy
```

- [x] Cloudflare 
```
sudo apt-get update && sudo apt-get install cloudflared
sudo reboot
cloudflared --version
```

- [x] Tailscale
```
curl -fsSL https://tailscale.com/install.sh  && sudo tailscale up
sudo tailscale set --ssh
```

- [x] UFW
```
sudo ufw allow 2525/tcp              # SSH
sudo ufw allow 41641/udp             # Tailscale WireGuard
sudo ufw allow 22420/tcp             # Syncthing sync
sudo ufw allow 22420/udp             # Syncthing sync
sudo ufw allow in on tailscale0      # All Tailscale traffic
```

```
sudo ufw default deny incoming
sudo ufw default allow outgoing

ip link show

sudo ufw show added      # or below line if ufw is not yet activated
sudo ufw status numbered
sudo ufw app list
```

## SSH Hardening
Created drop-in config at `/etc/ssh/sshd_config.d/hardened.conf`:
```
Port 2525
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
AllowUsers healmiy
X11Forwarding no
```
Validated with sshd -t and restarted sshd. Confirmed listening on port 2525 (IPv4 + IPv6), port 22 no longer open.
### on M2AirMie
```
mkdir -p ~/.ssh
touch ~/.ssh/config
chmod 600 ~/.ssh/config
```
paste 👇 
![[NerdRack#Give IDEAi SSH key to control server]]
- [ ] Give Aigents (IDEAi), access to NerdRack server via SSH key Authentication (just use `ssh adsvise`)
	- [x] M2AirMie
	- [ ] [[AiM1]]
- [x] Fast Note Sync
	- [x] AiM1
	- [x] EmiPhone
	- [x] iPadM3mi

![[4 Sync-thing PKMxKB folder to all devices#Devices]]