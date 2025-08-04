# Tally Supabase Wizard

A streamlined desktop application for synchronizing Tally Prime data to Supabase database.

## Overview

Tally Supabase Wizard is a Python-based desktop application that provides a user-friendly wizard interface to:

- Connect to your Supabase database
- Analyze Tally Prime data structure automatically
- Create database tables that match your Tally schema
- Synchronize all Tally metadata to Supabase
- Access your data through Supabase's REST API

## Features

### 🔗 Direct Supabase Integration
- Connect to any Supabase project using API keys
- Test connection and verify credentials
- View existing tables and database structure

### 📊 Automatic Data Analysis
- Analyze Tally Prime data structure in real-time
- Detect all available data types (companies, ledgers, vouchers, etc.)
- Infer field types and create appropriate database schemas
- Generate comprehensive data mapping

### 🗄️ Smart Table Management
- Automatically create tables based on Tally data structure
- Handle schema updates when Tally structure changes
- Maintain data integrity and relationships
- Support for all Tally data types

### 🔄 Data Synchronization
- Full data synchronization from Tally to Supabase
- Incremental updates and change tracking
- Batch processing for large datasets
- Error handling and recovery

### 🎛️ Wizard Interface
- User-friendly configuration wizard
- Real-time connection testing
- Progress tracking and status updates
- Comprehensive logging and error reporting

## Prerequisites

- **Tally Prime**: Running and accessible on localhost:9000
- **Supabase Project**: Created with API keys ready
- **Python 3.11+**: Will be automatically installed if missing

## Installation

### Quick Start

#### Windows
```bash
# Download and run
run_wizard.bat
```

#### macOS/Linux
```bash
# Make executable and run
chmod +x run_wizard.sh
./run_wizard.sh
```

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TallyTunnels
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the wizard**
   ```bash
   python tally_supabase_wizard.py
   ```

## Usage

### 1. Launch the Wizard

The wizard will guide you through the entire setup process:

1. **Dependency Check**: Automatically installs Python and dependencies
2. **Welcome**: Overview of the process
3. **Supabase Configuration**: Connect to your Supabase project
4. **Data Synchronization**: Analyze and sync your Tally data

### 2. Configure Supabase Connection

1. Enter your Supabase project URL
2. Enter your Supabase API key
3. Test the connection
4. Verify existing tables

### 3. Analyze Tally Data

1. Ensure Tally Prime is running on localhost:9000
2. Click "Analyze Tally Data Structure"
3. Review detected data types and field structures
4. Preview the synchronization plan

### 4. Synchronize Data

1. Review the sync plan
2. Confirm data volume and table mappings
3. Start synchronization
4. Monitor progress and completion

## Data Structure

### Tally to Supabase Mapping

| Tally Data | Supabase Table | Description |
|------------|----------------|-------------|
| Companies | `tally_companies` | Company information and details |
| Divisions | `tally_divisions` | Division and branch data |
| Ledgers | `tally_ledgers` | Chart of accounts and ledgers |
| Vouchers | `tally_vouchers` | Transaction vouchers |
| Voucher Entries | `tally_voucher_entries` | Individual voucher entries |

### Field Type Mapping

| Tally Type | Supabase Type | Description |
|------------|---------------|-------------|
| String | `TEXT` | Text data |
| Number | `NUMERIC` | Decimal numbers |
| Integer | `INTEGER` | Whole numbers |
| Date | `TIMESTAMP WITH TIME ZONE` | Date and time |
| Boolean | `BOOLEAN` | True/false values |
| Array/Object | `JSONB` | Complex data structures |

## API Access

Once synchronized, access your Tally data through Supabase's REST API:

### Example API Calls

```bash
# Get all companies
curl "https://your-project.supabase.co/rest/v1/tally_companies" \
  -H "apikey: your-api-key"

# Get ledgers for a specific company
curl "https://your-project.supabase.co/rest/v1/tally_ledgers?company=eq.Your%20Company" \
  -H "apikey: your-api-key"

# Get vouchers with pagination
curl "https://your-project.supabase.co/rest/v1/tally_vouchers?limit=100&offset=0" \
  -H "apikey: your-api-key"
```

### Real-time Subscriptions

```javascript
// Subscribe to real-time updates
const subscription = supabase
  .channel('tally_data')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'tally_ledgers' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
```

## Configuration

### Local Configuration

Configuration is stored in `~/.tally-tunnel/`:

- `config.json` - Main configuration
- `tally_supabase_mapping.json` - Data mapping
- `sync_log.json` - Synchronization history

### Example Configuration

```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_key": "your-api-key-here",
  "company_name": "Your Company",
  "division_name": "Main Division",
  "city_name": "Your City",
  "last_sync": "2024-01-01T00:00:00Z"
}
```

## File Structure

```
TallyTunnels/
├── tally_supabase_wizard.py      # Main wizard application
├── supabase_manager.py           # Core Supabase operations
├── tally_supabase_sync.py        # Tally-Supabase synchronization
├── supabase_config_page.py       # Wizard UI for Supabase config
├── dependency_manager.py         # Dependency installation
├── tally_metadata_extractor.py   # Tally data extraction
├── requirements.txt              # Python dependencies
├── run_wizard.bat               # Windows bootstrapper
├── run_wizard.sh                # macOS/Linux bootstrapper
├── test_supabase_integration.py # Integration tests
├── demo_supabase_integration.py # Demo script
└── README.md                    # This file
```

## Testing

### Run Integration Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
python test_supabase_integration.py
```

### Run Demo

```bash
# Run demonstration
python demo_supabase_integration.py
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify Supabase project URL
   - Check API key permissions
   - Ensure internet connectivity

2. **Table Creation Failed**
   - Check API key has table creation permissions
   - Verify RLS policies
   - Create tables manually in Supabase dashboard

3. **Tally Connection Failed**
   - Ensure Tally Prime is running
   - Check Tally is listening on localhost:9000
   - Verify Tally ODBC settings

4. **Data Sync Errors**
   - Check field type compatibility
   - Verify data integrity
   - Review sync logs for details

### Log Files

- **Application Logs**: Check console output
- **Sync Logs**: `~/.tally-tunnel/sync_log.json`
- **Error Details**: Review exception messages

## Security Considerations

1. **API Key Management**
   - Store API keys securely
   - Use environment variables in production
   - Rotate keys regularly

2. **Data Privacy**
   - Review RLS policies
   - Implement appropriate access controls
   - Consider data encryption

3. **Network Security**
   - Use HTTPS for all connections
   - Verify SSL certificates
   - Monitor network traffic

## Performance

### Optimization Tips

1. **Batch Processing**
   - Large datasets are processed in batches
   - Adjust batch size based on data volume
   - Monitor memory usage

2. **Incremental Sync**
   - Only sync changed data
   - Use timestamps for change detection
   - Implement delta synchronization

3. **Connection Pooling**
   - Reuse database connections
   - Implement connection timeouts
   - Monitor connection health

## Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd TallyTunnels

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_supabase_integration.py

# Run demo
python demo_supabase_integration.py
```

### Code Structure

- **Wizard Pages**: Each wizard step is a separate class
- **Threading**: Background operations use QThread
- **Error Handling**: Comprehensive exception handling
- **Logging**: Detailed logging for debugging

## Support

For issues and questions:

1. **Check Documentation**: Review this README
2. **Run Tests**: Use the test scripts
3. **Review Logs**: Check error messages
4. **Contact Support**: Reach out for assistance

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Changelog

### Version 1.0.0
- Initial release
- Supabase integration
- Tally data synchronization
- Wizard interface
- Automatic dependency management 