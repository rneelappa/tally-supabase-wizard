# Supabase Setup Guide for Tally Integration

## Prerequisites
- Supabase project created at: https://ppfwlhfehwelinfprviw.supabase.co
- Service role key (for admin operations)
- Anon key (for public operations)

## Step 1: Create Database Tables

1. **Open Supabase Dashboard**
   - Go to your Supabase project dashboard
   - Navigate to the "SQL Editor" section

2. **Run the Table Creation Script**
   - Copy the contents of `create_supabase_tables.sql`
   - Paste it into the SQL Editor
   - Click "Run" to execute all statements

3. **Verify Tables Created**
   - Go to "Table Editor" in the dashboard
   - You should see the following tables:
     - `tally_companies`
     - `tally_divisions`
     - `tally_ledgers`
     - `tally_groups`
     - `tally_vouchers`
     - `tally_voucher_entries`

## Step 2: Configure API Keys

### For the Tally Wizard Application:
- Use the **service_role key** for admin operations
- This bypasses Row Level Security (RLS) for data import

### For Client Applications:
- Use the **anon key** for public operations
- Users must be authenticated for RLS to work properly

## Step 3: Test Connection

1. **Run the Wizard**
   ```bash
   py -3.11 tally_supabase_wizard.py
   ```

2. **Configure Supabase Settings**
   - Project URL: `https://ppfwlhfehwelinfprviw.supabase.co`
   - API Key: Your service_role key

3. **Test Tally Connection**
   - The wizard will test the Tally connection
   - If successful, it will attempt to sync data

## Step 4: Data Import Process

The wizard will:
1. Connect to Tally and extract data
2. Analyze the data structure
3. Insert data into Supabase tables with:
   - Auto-generated UUID for each record
   - Placeholder user_id (for RLS compliance)
   - Timestamps (created_at, updated_at)

## Troubleshooting

### Common Issues:

1. **404 Errors on Table Creation**
   - Tables must be created manually in Supabase
   - Use the provided SQL script

2. **RLS Policy Violations**
   - Ensure you're using service_role key for admin operations
   - Or authenticate users properly for client operations

3. **Connection Timeouts**
   - Check your Supabase project URL
   - Verify API key is correct
   - Ensure internet connectivity

### Error Messages:

- `"Failed to create table: 404"` → Table doesn't exist, run the SQL script
- `"RLS policy violation"` → Use service_role key or authenticate user
- `"Connection timeout"` → Check network and Supabase URL

## Security Considerations

1. **API Key Management**
   - Never expose service_role key in client applications
   - Use anon key for public operations
   - Rotate keys regularly

2. **Row Level Security**
   - All tables have RLS enabled
   - Users can only access their own data
   - Admin operations bypass RLS with service_role key

3. **Data Validation**
   - Validate data before import
   - Use appropriate data types
   - Handle errors gracefully

## Next Steps

After successful setup:
1. Test data import with sample Tally data
2. Configure user authentication if needed
3. Set up monitoring and logging
4. Implement data validation rules
5. Create backup and recovery procedures 