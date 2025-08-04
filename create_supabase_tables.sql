-- Create Supabase tables for Tally data synchronization
-- Run this script in your Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tally Companies Table
CREATE TABLE IF NOT EXISTS tally_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company_name TEXT,
    company_path TEXT,
    company_address TEXT,
    company_phone TEXT,
    company_email TEXT,
    company_website TEXT,
    company_tax_number TEXT,
    company_registration_number TEXT,
    company_financial_year_start DATE,
    company_financial_year_end DATE,
    company_currency TEXT,
    company_language TEXT,
    company_timezone TEXT,
    company_created_date TIMESTAMP WITH TIME ZONE,
    company_modified_date TIMESTAMP WITH TIME ZONE,
    company_status TEXT,
    company_type TEXT,
    company_industry TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 2. Tally Divisions Table
CREATE TABLE IF NOT EXISTS tally_divisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company_name TEXT,
    division_name TEXT,
    division_path TEXT,
    division_address TEXT,
    division_phone TEXT,
    division_email TEXT,
    division_website TEXT,
    division_tax_number TEXT,
    division_registration_number TEXT,
    division_financial_year_start DATE,
    division_financial_year_end DATE,
    division_currency TEXT,
    division_language TEXT,
    division_timezone TEXT,
    division_created_date TIMESTAMP WITH TIME ZONE,
    division_modified_date TIMESTAMP WITH TIME ZONE,
    division_status TEXT,
    division_type TEXT,
    division_industry TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 3. Tally Groups Table
CREATE TABLE IF NOT EXISTS tally_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company_name TEXT,
    division_name TEXT,
    group_name TEXT,
    group_path TEXT,
    group_parent TEXT,
    group_category TEXT,
    group_type TEXT,
    group_nature TEXT,
    group_reserved TEXT,
    group_used_in TEXT,
    group_created_date TIMESTAMP WITH TIME ZONE,
    group_modified_date TIMESTAMP WITH TIME ZONE,
    group_status TEXT,
    group_description TEXT,
    group_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 4. Tally Ledgers Table
CREATE TABLE IF NOT EXISTS tally_ledgers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company_name TEXT,
    division_name TEXT,
    ledger_name TEXT,
    ledger_path TEXT,
    ledger_parent TEXT,
    ledger_group TEXT,
    ledger_category TEXT,
    ledger_type TEXT,
    ledger_nature TEXT,
    ledger_reserved TEXT,
    ledger_used_in TEXT,
    ledger_created_date TIMESTAMP WITH TIME ZONE,
    ledger_modified_date TIMESTAMP WITH TIME ZONE,
    ledger_status TEXT,
    ledger_description TEXT,
    ledger_notes TEXT,
    ledger_address TEXT,
    ledger_phone TEXT,
    ledger_email TEXT,
    ledger_website TEXT,
    ledger_tax_number TEXT,
    ledger_registration_number TEXT,
    ledger_currency TEXT,
    ledger_opening_balance NUMERIC(15,2),
    ledger_current_balance NUMERIC(15,2),
    ledger_closing_balance NUMERIC(15,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 5. Tally Vouchers Table
CREATE TABLE IF NOT EXISTS tally_vouchers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company_name TEXT,
    division_name TEXT,
    voucher_number TEXT,
    voucher_date DATE,
    voucher_type TEXT,
    voucher_narration TEXT,
    voucher_party_ledger_name TEXT,
    voucher_amount NUMERIC(15,2),
    voucher_currency TEXT,
    voucher_exchange_rate NUMERIC(10,4),
    voucher_base_amount NUMERIC(15,2),
    voucher_created_date TIMESTAMP WITH TIME ZONE,
    voucher_modified_date TIMESTAMP WITH TIME ZONE,
    voucher_status TEXT,
    voucher_notes TEXT,
    voucher_reference TEXT,
    voucher_cheque_number TEXT,
    voucher_cheque_date DATE,
    voucher_bank_name TEXT,
    voucher_branch_name TEXT,
    voucher_ifsc_code TEXT,
    voucher_account_number TEXT,
    voucher_transaction_type TEXT,
    voucher_payment_mode TEXT,
    voucher_tax_amount NUMERIC(15,2),
    voucher_discount_amount NUMERIC(15,2),
    voucher_total_amount NUMERIC(15,2),
    voucher_rounding_amount NUMERIC(15,2),
    voucher_final_amount NUMERIC(15,2),
    voucher_ledger_entries JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- 6. Tally Voucher Entries Table
CREATE TABLE IF NOT EXISTS tally_voucher_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company_name TEXT,
    division_name TEXT,
    voucher_number TEXT,
    voucher_date DATE,
    voucher_type TEXT,
    ledger_name TEXT,
    ledger_path TEXT,
    ledger_group TEXT,
    ledger_category TEXT,
    ledger_type TEXT,
    ledger_nature TEXT,
    amount NUMERIC(15,2),
    currency TEXT,
    exchange_rate NUMERIC(10,4),
    base_amount NUMERIC(15,2),
    narration TEXT,
    party_ledger_name TEXT,
    party_ledger_path TEXT,
    party_ledger_group TEXT,
    party_ledger_category TEXT,
    party_ledger_type TEXT,
    party_ledger_nature TEXT,
    bill_allocation TEXT,
    cost_center_allocation TEXT,
    tax_amount NUMERIC(15,2),
    discount_amount NUMERIC(15,2),
    total_amount NUMERIC(15,2),
    rounding_amount NUMERIC(15,2),
    final_amount NUMERIC(15,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security (RLS) on all tables
ALTER TABLE tally_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE tally_divisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tally_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE tally_ledgers ENABLE ROW LEVEL SECURITY;
ALTER TABLE tally_vouchers ENABLE ROW LEVEL SECURITY;
ALTER TABLE tally_voucher_entries ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for all tables
-- Users can only view and modify their own data
CREATE POLICY "Users can view own companies" ON tally_companies
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own divisions" ON tally_divisions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own groups" ON tally_groups
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own ledgers" ON tally_ledgers
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own vouchers" ON tally_vouchers
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own voucher entries" ON tally_voucher_entries
    FOR ALL USING (auth.uid() = user_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tally_companies_user_id ON tally_companies(user_id);
CREATE INDEX IF NOT EXISTS idx_tally_companies_company_name ON tally_companies(company_name);

CREATE INDEX IF NOT EXISTS idx_tally_divisions_user_id ON tally_divisions(user_id);
CREATE INDEX IF NOT EXISTS idx_tally_divisions_company_name ON tally_divisions(company_name);
CREATE INDEX IF NOT EXISTS idx_tally_divisions_division_name ON tally_divisions(division_name);

CREATE INDEX IF NOT EXISTS idx_tally_groups_user_id ON tally_groups(user_id);
CREATE INDEX IF NOT EXISTS idx_tally_groups_company_name ON tally_groups(company_name);
CREATE INDEX IF NOT EXISTS idx_tally_groups_group_name ON tally_groups(group_name);

CREATE INDEX IF NOT EXISTS idx_tally_ledgers_user_id ON tally_ledgers(user_id);
CREATE INDEX IF NOT EXISTS idx_tally_ledgers_company_name ON tally_ledgers(company_name);
CREATE INDEX IF NOT EXISTS idx_tally_ledgers_ledger_name ON tally_ledgers(ledger_name);

CREATE INDEX IF NOT EXISTS idx_tally_vouchers_user_id ON tally_vouchers(user_id);
CREATE INDEX IF NOT EXISTS idx_tally_vouchers_company_name ON tally_vouchers(company_name);
CREATE INDEX IF NOT EXISTS idx_tally_vouchers_voucher_number ON tally_vouchers(voucher_number);
CREATE INDEX IF NOT EXISTS idx_tally_vouchers_voucher_date ON tally_vouchers(voucher_date);

CREATE INDEX IF NOT EXISTS idx_tally_voucher_entries_user_id ON tally_voucher_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_tally_voucher_entries_company_name ON tally_voucher_entries(company_name);
CREATE INDEX IF NOT EXISTS idx_tally_voucher_entries_voucher_number ON tally_voucher_entries(voucher_number);
CREATE INDEX IF NOT EXISTS idx_tally_voucher_entries_ledger_name ON tally_voucher_entries(ledger_name);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_tally_companies_updated_at BEFORE UPDATE ON tally_companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tally_divisions_updated_at BEFORE UPDATE ON tally_divisions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tally_groups_updated_at BEFORE UPDATE ON tally_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tally_ledgers_updated_at BEFORE UPDATE ON tally_ledgers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tally_vouchers_updated_at BEFORE UPDATE ON tally_vouchers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tally_voucher_entries_updated_at BEFORE UPDATE ON tally_voucher_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated; 