## 🐳 AI Companion Bot for Termux
A personal AI companion that runs on Termux (Android) and sends periodic notifications with thoughtful messages using the GROQ API.

![image](https://github.com/user-attachments/assets/6c2f58dc-e310-49aa-89ee-47fdd1660be7)


### Prerequisites

* Termux installed on Android
* Termux:API add-on installed
* Python 3.x
* GROQ API key

### Installation

#### Install required packages:

```bash
pkg install python termux-api
pip install requests
```

####  Clone the repository:

```bash
git clone https://github.com/PrashantBtkl/little_big_dreams
cd little_big_dreams
```

#### Set up your GROQ API key:

```bash
export GROQ_API_KEY="your-api-key-here"
```

### Configuration
Edit the script to customize:
```
MASTER_NAME: Your name for personalized interactions
System prompt: Modify the AI's personality and behavior
Response formatting: Adjust words per line in notifications
```

Usage
Run manually:
```bash
python little_big_dreams.py
```
Set up as a CRON job:
```bash
crontab -e
# Add line to run at desired interval:
# */30 * * * * cd /path/to/script && python little_big_dreams.py
```
