# Home Assistant Integration for Panasonic UB Series Players


> [!WARNING]
> This is an experimental component. I am not affiliated with Panasonic and this is not an official component from Panasonic. Use at your own risk.

This custom component integrates Panasonic UB-series Blu-ray players (e.g., UB820, UB420, UB9000) into Home Assistant. It provides playback status and elapsed position, plus remote control commands when the player accepts authenticated or unauthenticated control requests.

## Features

* **Media Player Entity**: Standard Home Assistant media player controls, where supported by the player's authentication mode.
* **Two Operation Modes**: Supports standard firmware with authentication and modified firmware that permits unauthenticated control. Stock players still provide unauthenticated status and elapsed-position queries, but generally reject control commands without a player key.
* **Custom Commands**: A dedicated service to send specific remote keys (e.g., `NETFLIX`, `HOME`, `POPUP_MENU`, `RED`, `GREEN`, etc.).
* **Wake-on-LAN**: Supports turning the device on via network (ensure "Remote Start" is enabled in player settings).
* **Real-time Status**: Polls the device for current playback status (Polling interval can be configured).

---

## Installation

### HACS

If this repository is not yet listed in the HACS default store, install it as a custom repository:

1. Open **HACS** in Home Assistant.
2. Open **Integrations** and select the three-dot menu in the upper-right corner.
3. Select **Custom repositories**.
4. Enter `https://github.com/matteoraf/ha-panasonic_ub` as the repository.
5. Select **Integration** as the repository type.
6. Select **Add** or **Download** and wait for the installation to complete.
7. Restart Home Assistant.

After restarting, add the integration from **Settings** > **Devices & Services** > **Add Integration**, then search for **Panasonic UB**.

### Manual

1.  Download the `panasonic_ub` folder from this repository.
2.  Copy the folder into your Home Assistant's `custom_components` directory (e.g., `/config/custom_components/panasonic_ub`).
3.  Restart Home Assistant.

---

## Configuration

1.  Go to **Settings** > **Devices & Services**.
2.  Click **Add Integration** and search for **Panasonic UB**.
3.  Follow the configuration flow:

### Step 1: Connection

* **Host**: Enter the IP address of your Panasonic player. (Make sure that the player and Home Assistant are on the **SAME SUBNET** and you have enabled **Voice Control** in the player settings).

### Step 2: Authentication Mode

You will be asked to choose between **Authenticated** and **Unauthenticated** mode.

* **Authenticated Mode**: Use this if your player is running **stock/official firmware**.
    * Enter the player's 32-character `API Key`.
    * *Note: Obtaining the API key is not easy but **CAN** be done.*

* **Unauthenticated Mode**: Use this for read-only status/elapsed-position access, or if your player is running **modified/enhanced firmware** (often referred to as "region-free" or "jailbroken" firmware).
    * Leave the `API Key` blank.
    * Stock firmware generally allows status queries but rejects remote control commands without authentication.
    * Modified firmware may disable the security checks on the HTTP interface, allowing direct control without a key.

---

## Usage & Entities

### Media Player Entity

The integration creates a standard media player entity, for example: `media_player.panasonic_ub820`.

* **State**: Reports `playing`, `paused`, `idle`, or `off`.
* **Attributes**: Exposes detailed internal status codes (e.g., `TRAY_OPEN`, `MENU`) via the `detailed_status` attribute.

### Services

The integration exposes a specific service to send remote key presses:

**Service**: `panasonic_ub.remote_command`

**Parameters**:

* `entity_id`: The media player entity (e.g., `media_player.panasonic_ub820`).
* `command`: The command string to send.

**Example**:

```yaml
service: panasonic_ub.remote_command
target:
  entity_id: media_player.panasonic_ub820
data:
  command: "NETFLIX"
```
*See `const.py` for a full list of available commands.*

* * * * *

Included Examples
-----------------

This repository includes two helper files to help you set up a beautiful "Virtual Remote" dashboard immediately.

### 1\. `scripts.yaml`

This file contains pre-made scripts for every single command the player supports (Power, Navigation, Apps, Colors, etc.).

**How to use:**

1.  Open the `scripts.yaml` file provided in this repository.

2.  Copy the contents.

3.  Paste them into your Home Assistant's `scripts.yaml` configuration file.

4.  **Important**: Find and replace `media_player.panasonic_ub820` with your actual entity ID if it differs.

5.  Reload Scripts in "Developer Tools" > "YAML".

### 2\. `remote.yaml` (Lovelace Dashboard)

This file provides the YAML configuration for a high-fidelity virtual remote control card for your dashboard.

**Requirements:**

You must install the following frontend cards via HACS:

-   `universal-remote-card`

-   `button-card`


**How to use:**

1.  Create a new Dashboard or add a new View in Lovelace.

2.  Select "Edit Dashboard" > "Add Card" > "Manual".

3.  Copy the content of `remote.yaml`.

4.  Paste it into the card configuration.

5.  This configuration includes:

    -   **Status Display**: A top widget mimicking a VFD display that shows the player's detailed status (e.g., "TRAY OPEN", "PLAYBACK").

    -   **Remote Layout**: A fully mapped button layout matching the physical remote.

* * * * *
