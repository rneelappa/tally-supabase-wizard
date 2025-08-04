# Tally Tunnel Wizard - Supabase Integration

This document describes the Supabase integration features that replace the Cloudflare tunnel functionality with direct database synchronization.

## Overview

The Supabase integration allows you to:
- Connect directly to your Supabase database
- Analyze Tally Prime data structure automatically
- Create database tables that match your Tally data
- Synchronize all Tally metadata to Supabase
- Access your Tally data through Supabase's REST API

## Features

### 🔗 Direct Supabase Connection
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

## Configuration

### Supabase Setup

1. **Create a Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Note your project URL and API keys

2. **Configure API Access**
   - Use the `anon` key for public access
   - Use the `service_role` key for admin operations
   - Enable Row Level Security (RLS) as needed

3. **Database Permissions**
   - Ensure your API key has permission to create tables
   - Grant necessary permissions for data operations

### Project Configuration

```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_key": "your-api-key-here",
  "company_name": "Your Company",
  "division_name": "Main Division",
  "city_name": "Your City"
}
```

## Usage

### 1. Launch the Wizard

```bash
# Activate virtual environment
source venv/bin/activate

# Run the wizard
python tally_tunnel_wizard.py
```

### 2. Configure Supabase Connection

1. **Enter Supabase Details**
   - Project URL: `https://your-project.supabase.co`
   - API Key: Your Supabase API key

2. **Test Connection**
   - Click "Test Connection" to verify credentials
   - Check existing tables in your database

### 3. Analyze Tally Data

1. **Start Analysis**
   - Click "Analyze Tally Data Structure"
   - The system will connect to Tally Prime (localhost:9000)
   - Analyze all available data types

2. **Review Results**
   - View detected data structures
   - Check field types and relationships
   - Review estimated record counts

### 4. Synchronize Data

1. **Preview Sync Plan**
   - Review tables to be created/updated
   - Check estimated data volume
   - Verify field mappings

2. **Start Synchronization**
   - Click "Start Data Synchronization"
   - Monitor progress in real-time
   - Review completion status

## Data Structure

### Tally Data Types

The system automatically maps Tally data to Supabase tables:

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

Once synchronized, you can access your Tally data through Supabase's REST API:

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

## File Structure

```
TallyTunnels/
├── supabase_manager.py          # Core Supabase operations
├── tally_supabase_sync.py       # Tally-Supabase synchronization
├── supabase_config_page.py      # Wizard UI for Supabase config
├── test_supabase_integration.py # Integration tests
├── demo_supabase_integration.py # Demo script
└── SUPABASE_INTEGRATION_README.md
```

## Configuration Files

### Local Configuration
- **Location**: `~/.tally-tunnel/`
- **Files**:
  - `config.json` - Main configuration
  - `tally_supabase_mapping.json` - Data mapping
  - `sync_log.json` - Synchronization history

### Example Configuration

```json
{
  "supabase_url": "https://ppfwlhfehwelinfprviw.supabase.co",
  "supabase_key": "sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA",
  "company_name": "Demo Company",
  "division_name": "Main Division",
  "subdivision_name": "",
  "city_name": "Demo City",
  "last_sync": "2024-01-01T00:00:00Z"
}
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

## Future Enhancements

### Planned Features

1. **Real-time Sync**
   - Continuous data synchronization
   - Change detection and propagation
   - Event-driven updates

2. **Advanced Analytics**
   - Data visualization
   - Custom reporting
   - Business intelligence integration

3. **Multi-tenant Support**
   - Multiple company support
   - Role-based access control
   - Data isolation

4. **Backup and Recovery**
   - Automated backups
   - Point-in-time recovery
   - Disaster recovery procedures

## Support

For issues and questions:

1. **Check Documentation**: Review this README
2. **Run Tests**: Use the test scripts
3. **Review Logs**: Check error messages
4. **Contact Support**: Reach out for assistance

## License

This integration is part of the Tally Tunnel Wizard project and follows the same licensing terms. 