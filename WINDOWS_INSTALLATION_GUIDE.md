# Windows Installation Guide - Tally Supabase Wizard

## 🪟 **Windows Installation Instructions**

This guide will help you install and run the Tally Supabase Wizard on a Windows machine.

## 📋 **Prerequisites**

Before starting, ensure you have:

- **Windows 10/11** (64-bit recommended)
- **Internet connection** for downloading dependencies
- **Administrator privileges** (for installing Python)
- **Tally Prime** running on the machine
- **Supabase project** created with API keys

## 🚀 **Quick Installation (Recommended)**

### **Option 1: One-Click Installation**

1. **Download the project**
   - Copy the entire `TallyTunnels` folder to your Windows machine
   - Place it in a convenient location (e.g., `C:\TallyTunnels`)

2. **Run the installer**
   ```cmd
   # Double-click the batch file
   run_wizard.bat
   ```
   
   **OR** open Command Prompt and run:
   ```cmd
   cd C:\TallyTunnels
   run_wizard.bat
   ```

3. **The script will automatically:**
   - ✅ Check for Python 3.11+
   - ✅ Download and install Python if missing
   - ✅ Install required dependencies
   - ✅ Launch the wizard

### **Option 2: Manual Installation**

If the automatic installation doesn't work, follow these steps:

## 🔧 **Manual Installation Steps**

### **Step 1: Download Project**

1. **Copy the entire project folder** to your Windows machine
   ```
   C:\TallyTunnels\
   ├── tally_supabase_wizard.py
   ├── supabase_manager.py
   ├── tally_supabase_sync.py
   ├── supabase_config_page.py
   ├── dependency_manager.py
   ├── tally_metadata_extractor.py
   ├── requirements.txt
   ├── run_wizard.bat
   ├── README.md
   └── [other files...]
   ```

### **Step 2: Install Python**

1. **Check if Python is installed:**
   ```cmd
   python --version
   ```

2. **If Python is not installed or version < 3.11:**
   - Go to [python.org](https://www.python.org/downloads/)
   - Download Python 3.11.8 or higher
   - **Important:** Check "Add Python to PATH" during installation
   - Run the installer as Administrator

3. **Verify installation:**
   ```cmd
   python --version
   pip --version
   ```

### **Step 3: Install Dependencies**

1. **Open Command Prompt as Administrator**

2. **Navigate to project folder:**
   ```cmd
   cd C:\TallyTunnels
   ```

3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

### **Step 4: Run the Wizard**

```cmd
python tally_supabase_wizard.py
```

## 📁 **Project Structure on Windows**

After copying, your folder structure should look like:

```
C:\TallyTunnels\
├── 📄 README.md
├── 📄 WINDOWS_INSTALLATION_GUIDE.md
├── 📄 PROJECT_SUMMARY.md
├── 📄 SUPABASE_INTEGRATION_README.md
├── 🐍 tally_supabase_wizard.py
├── 🐍 supabase_manager.py
├── 🐍 tally_supabase_sync.py
├── 🐍 supabase_config_page.py
├── 🐍 dependency_manager.py
├── 🐍 tally_metadata_extractor.py
├── 📋 requirements.txt
├── 🪟 run_wizard.bat
├── 🧪 test_supabase_integration.py
├── 🎭 demo_supabase_integration.py
└── 📁 venv\ (created automatically)
```

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. "Python is not recognized"**
```cmd
# Solution: Add Python to PATH manually
setx PATH "%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311"
setx PATH "%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts"
```

#### **2. "pip is not recognized"**
```cmd
# Solution: Install pip
python -m ensurepip --upgrade
```

#### **3. "Permission denied"**
- Run Command Prompt as Administrator
- Or use:
```cmd
pip install --user -r requirements.txt
```

#### **4. "PySide6 installation failed"**
```cmd
# Solution: Install Visual C++ Redistributable
# Download from Microsoft's website
# Then retry:
pip install PySide6
```

#### **5. "Tally connection failed"**
- Ensure Tally Prime is running
- Check if Tally is listening on localhost:9000
- Verify Tally ODBC settings

### **Alternative Installation Methods**

#### **Using Chocolatey (if available):**
```cmd
# Install Python
choco install python

# Install dependencies
pip install -r requirements.txt
```

#### **Using Anaconda (if available):**
```cmd
# Create environment
conda create -n tally-supabase python=3.11

# Activate environment
conda activate tally-supabase

# Install dependencies
pip install -r requirements.txt
```

## 🎯 **Usage Instructions**

### **1. Launch the Wizard**
```cmd
# Method 1: Double-click
run_wizard.bat

# Method 2: Command line
python tally_supabase_wizard.py
```

### **2. Follow the Wizard Steps**

1. **Dependency Check**
   - Click "Check Dependencies"
   - Wait for installation to complete

2. **Welcome Screen**
   - Read the overview
   - Click "Next"

3. **Supabase Configuration**
   - Enter your Supabase project URL
   - Enter your Supabase API key
   - Click "Test Connection"
   - Click "Analyze Tally Data Structure"

4. **Data Synchronization**
   - Review the sync plan
   - Click "Start Data Synchronization"
   - Monitor progress

### **3. Access Your Data**

After synchronization, access your data via:

```cmd
# Example API call
curl "https://your-project.supabase.co/rest/v1/tally_companies" -H "apikey: your-api-key"
```

## 🔒 **Security Considerations**

### **API Key Management**
- Store API keys securely
- Don't share your API keys
- Use environment variables in production

### **Firewall Settings**
- Allow Python to access the internet
- Allow connections to Supabase
- Allow localhost connections for Tally

## 📞 **Support**

### **If you encounter issues:**

1. **Check the logs:**
   ```cmd
   type install_log.txt
   ```

2. **Run tests:**
   ```cmd
   python test_supabase_integration.py
   ```

3. **Run demo:**
   ```cmd
   python demo_supabase_integration.py
   ```

4. **Check Python installation:**
   ```cmd
   python --version
   pip list
   ```

## 🎉 **Success Indicators**

You'll know the installation is successful when:

- ✅ Python 3.11+ is installed
- ✅ All dependencies are installed
- ✅ Wizard launches without errors
- ✅ Can connect to Supabase
- ✅ Can analyze Tally data
- ✅ Can synchronize data successfully

## 📝 **Next Steps**

After successful installation:

1. **Configure Supabase** - Set up your Supabase project
2. **Connect Tally** - Ensure Tally Prime is running
3. **Sync Data** - Use the wizard to synchronize
4. **Access API** - Use Supabase's REST API
5. **Build Applications** - Create apps using your synced data

---

**The Tally Supabase Wizard is now ready to use on your Windows machine!** 🎯 