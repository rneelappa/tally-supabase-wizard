# Tally Prime XML Structures Guide

## Overview

This guide documents the correct XML structures for extracting data from Tally Prime using the HTTP XML interface. Based on comprehensive research of Tally's hierarchical data architecture, these structures ensure proper data extraction for all major Tally objects.

## Key Findings

### 1. Company Context is Critical
- **All data requests (except companies) require company context**
- Use `<SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>` in STATICVARIABLES
- Companies endpoint works globally without company context

### 2. Divisions = Cost Centres
- Tally doesn't have a native "Division" object
- Use `CostCentre` type for divisions/departments
- Cost Centres represent internal business units for performance tracking

### 3. Hierarchical Data Structure
- Tally uses a strict parent-child hierarchy
- Company → Groups → Ledgers
- Company → Vouchers → Voucher Entries
- Company → Cost Centres

## XML Structures by Data Type

### 1. Companies (Global Request)

```xml
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>List of Companies</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES />
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="List of Companies">
            <TYPE>Company</TYPE>
            <FETCH>NAME,GUID,EMAIL,STATE,PINCODE,PHONE,COMPANYNUMBER,ADDRESS,WEBSITE,MOBILE</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
```

**Response Tags:** `<COMPANY>`

### 2. Cost Centres (Divisions)

```xml
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>List of Cost Centres</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="List of Cost Centres">
            <TYPE>CostCentre</TYPE>
            <FETCH>NAME,GUID,PARENT,CATEGORY,ADDRESS,PHONE,MOBILE,EMAIL</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
```

**Response Tags:** `<COSTCENTRE>`

### 3. Ledgers

```xml
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>List of Ledgers</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="List of Ledgers">
            <TYPE>Ledger</TYPE>
            <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE,ADDRESS,PHONE,MOBILE,EMAIL</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
```

**Response Tags:** `<LEDGER>`

### 4. Groups (Chart of Accounts Structure)

```xml
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>List of Groups</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="List of Groups">
            <TYPE>Group</TYPE>
            <FETCH>NAME,GUID,PARENT</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
```

**Response Tags:** `<GROUP>`

### 5. Vouchers

```xml
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>List of Vouchers</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="List of Vouchers">
            <TYPE>Voucher</TYPE>
            <FETCH>VOUCHERNUMBER,DATE,NARRATION,VOUCHERTYPENAME,REFERENCE,AMOUNT</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
```

**Response Tags:** `<VOUCHER>`, `<LEDGERENTRIES.LIST>`, `<INVENTORYENTRIES.LIST>`

### 6. Voucher Entries

```xml
<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>List of Voucher Entries</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="List of Voucher Entries">
            <TYPE>VoucherEntry</TYPE>
            <FETCH>LEDGERNAME,AMOUNT,NARRATION,ISDEEMEDPOSITIVE</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>
```

**Response Tags:** `<VOUCHERENTRY>`

## Important Static Variables

### Company Context
```xml
<SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
```

### Date Range (for vouchers)
```xml
<SVFROMDATE>{from_date}</SVFROMDATE>  <!-- Format: YYYYMMDD -->
<SVTODATE>{to_date}</SVTODATE>        <!-- Format: YYYYMMDD -->
```

### Current Company (alternative)
```xml
<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
```

## Response Parsing Guidelines

### 1. Companies
- Look for `<COMPANY>` tags within `<COLLECTION>`
- Extract all child elements as key-value pairs

### 2. Cost Centres
- Look for `<COSTCENTRE>` tags within `<COLLECTION>`
- Key fields: NAME, GUID, PARENT, CATEGORY

### 3. Ledgers
- Look for `<LEDGER>` tags within `<COLLECTION>`
- Key fields: NAME, GUID, PARENT, OPENINGBALANCE, CLOSINGBALANCE

### 4. Groups
- Look for `<GROUP>` tags within `<COLLECTION>`
- Key fields: NAME, GUID, PARENT

### 5. Vouchers
- Look for `<VOUCHER>` tags within `<COLLECTION>`
- Each voucher contains:
  - Main voucher details (DATE, VOUCHERNUMBER, etc.)
  - `<LEDGERENTRIES.LIST>` for accounting entries
  - `<INVENTORYENTRIES.LIST>` for stock entries

### 6. Voucher Entries
- Look for `<VOUCHERENTRY>` tags within `<COLLECTION>`
- Key fields: LEDGERNAME, AMOUNT, NARRATION, ISDEEMEDPOSITIVE

## Common Issues and Solutions

### 1. Connection Refused
- Ensure Tally Prime is running
- Check if Tally is listening on port 9000
- Verify Tally is not in Data Entry mode

### 2. Empty Responses
- Check company name spelling (case-sensitive)
- Ensure company exists in Tally
- Verify data exists for the requested type

### 3. XML Parse Errors
- Check for malformed XML in response
- Handle empty responses gracefully
- Validate XML structure before parsing

### 4. Timeout Issues
- Increase timeout for large datasets
- Use date ranges to limit voucher data
- Consider pagination for large collections

## Best Practices

### 1. Error Handling
- Always check response status codes
- Handle connection errors gracefully
- Validate XML responses before parsing

### 2. Performance
- Use date ranges for voucher queries
- Cache company names to avoid repeated lookups
- Implement request timeouts

### 3. Data Validation
- Verify company names before making requests
- Check for required fields in responses
- Handle missing or null values

### 4. Logging
- Log all requests and responses for debugging
- Track performance metrics
- Monitor for connection issues

## Implementation Examples

### Python FastAPI Example
```python
@app.get("/ledgers/{company_name}")
def get_ledgers(company_name: str):
    xml_request = f"""
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Ledgers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES>
            <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
          </STATICVARIABLES>
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Ledgers">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    response = send_tally_request(xml_request)
    # Parse response and return JSON
```

### JavaScript/Node.js Example
```javascript
async function getLedgers(companyName) {
    const xmlRequest = `
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Ledgers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES>
            <SVCOMPANYCONNECT>${companyName}</SVCOMPANYCONNECT>
          </STATICVARIABLES>
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Ledgers">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    `;
    
    const response = await fetch('http://localhost:9000', {
        method: 'POST',
        headers: { 'Content-Type': 'application/xml' },
        body: xmlRequest
    });
    
    return await response.text();
}
```

## Conclusion

These XML structures provide a complete solution for extracting data from Tally Prime. The key is understanding Tally's hierarchical architecture and ensuring proper company context for all requests. With these structures, you can build robust integrations that extract companies, cost centres (divisions), ledgers, groups, vouchers, and voucher entries from Tally Prime. 