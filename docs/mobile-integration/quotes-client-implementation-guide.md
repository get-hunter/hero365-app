# Quotes Client Implementation Guide

## Overview

This guide provides comprehensive documentation for implementing quote management functionality in the Hero365 mobile application. Quotes are formal, binding offers that differ from estimates in their legal implications and business rules.

## Business Context for Quotes

### Quote vs Estimate Key Differences

| Aspect | Quote | Estimate |
|--------|-------|----------|
| **Binding Nature** | Legally binding when accepted | Non-binding, preliminary |
| **Pricing Precision** | Exact, fixed pricing | Approximate, subject to change |
| **Validity Period** | Required, typically 30-90 days | Optional |
| **Terms & Conditions** | Must include binding language | General terms acceptable |
| **Client Expectation** | Ready to proceed | Budget planning |
| **Revision Process** | Requires new quote | Can be updated |

## Authentication & Permissions

### Required Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Business-Context: <business_id>
```

### Required Permissions
- **View Quotes**: `view_projects`
- **Create/Edit Quotes**: `edit_projects` 
- **Delete Quotes**: `delete_projects`

---

## Quote Creation

### 1. Create New Quote

**Endpoint**: `POST /api/v1/estimates`

**Quote-Specific Requirements**:
- `document_type` must be set to `"quote"`
- `valid_until` is strongly recommended (required for professional quotes)
- More detailed line item descriptions expected
- Binding terms and conditions should be included

**Request Body**:
```json
{
  "document_type": "quote",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Kitchen Renovation - Firm Quote",
  "description": "Complete kitchen renovation with premium finishes. This quote constitutes a firm offer.",
  "line_items": [
    {
      "description": "Premium kitchen cabinet installation with soft-close hinges",
      "quantity": 1,
      "unit_price": 8500.00,
      "unit": "complete_set",
      "category": "Cabinetry",
      "notes": "Includes delivery, installation, and hardware"
    },
    {
      "description": "Quartz countertop fabrication and installation",
      "quantity": 45,
      "unit_price": 85.00,
      "unit": "sqft",
      "category": "Countertops",
      "notes": "Includes edge finishing and cutouts"
    },
    {
      "description": "Professional project management and coordination",
      "quantity": 1,
      "unit_price": 1200.00,
      "unit": "project",
      "category": "Management"
    }
  ],
  "currency": "USD",
  "tax_rate": 8.75,
  "overall_discount_type": "percentage",
  "overall_discount_value": 5.0,
  "valid_until": "2024-04-15T23:59:59Z",
  "terms": {
    "payment_terms": "50% deposit required upon acceptance, balance due upon completion",
    "validity_period": 45,
    "warranty_terms": "2-year warranty on all workmanship",
    "terms_and_conditions": "This quote constitutes a binding offer upon acceptance. Price includes all materials and labor as specified."
  },
  "template_id": "quote_template_premium"
}
```

**Success Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "business_id": "550e8400-e29b-41d4-a716-446655440005",
  "estimate_number": "QUO-000001",
  "document_type": "quote",
  "document_type_display": "Quote",
  "status": "draft",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Kitchen Renovation - Firm Quote",
  "line_items": [...],
  "total_amount": 13087.50,
  "tax_amount": 1087.50,
  "valid_until": "2024-04-15T23:59:59Z",
  "created_at": "2024-02-01T10:00:00Z",
  "financial_summary": {
    "subtotal": 12425.00,
    "discount_amount": 621.25,
    "tax_amount": 1087.50,
    "total_amount": 13087.50
  }
}
```

### 2. Create Quote from Template

**Endpoint**: `POST /api/v1/estimates/from-template`

**Request Body**:
```json
{
  "template_id": "quote_template_renovation",
  "document_type": "quote",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Home Renovation Quote",
  "template_variables": {
    "client_name": "John Smith",
    "project_address": "123 Main St, Anytown",
    "completion_timeline": "6-8 weeks",
    "quote_valid_days": "45"
  },
  "valid_until": "2024-04-15T23:59:59Z"
}
```

### 3. Convert Estimate to Quote

**Endpoint**: `POST /api/v1/estimates/{estimate_id}/convert-to-quote`

**Request Body**:
```json
{
  "title": "Updated Kitchen Renovation - Firm Quote",
  "valid_until": "2024-04-15T23:59:59Z",
  "terms": {
    "payment_terms": "50% deposit required upon acceptance",
    "terms_and_conditions": "This quote constitutes a binding offer upon acceptance."
  },
  "notes": "Converted from preliminary estimate after scope finalization"
}
```

**Response**: Creates a new quote document with QUO- prefix

---

## Quote Editing

### 1. Update Quote (Draft Only)

**Endpoint**: `PUT /api/v1/estimates/{quote_id}`

**Important**: Quotes can only be edited while in `draft` status

**Request Body**:
```json
{
  "title": "Updated Kitchen Renovation Quote",
  "description": "Complete kitchen renovation with updated specifications",
  "line_items": [
    {
      "description": "Premium kitchen cabinet installation - Updated specs",
      "quantity": 1,
      "unit_price": 9000.00,
      "unit": "complete_set",
      "category": "Cabinetry",
      "notes": "Upgraded to premium soft-close hardware"
    }
  ],
  "valid_until": "2024-05-01T23:59:59Z",
  "terms": {
    "payment_terms": "60% deposit required upon acceptance, balance due upon completion"
  }
}
```

### 2. Update Quote Status

**Endpoint**: `PATCH /api/v1/estimates/{quote_id}/status`

**Status Transitions for Quotes**:
- `draft` → `sent` (Send to client)
- `sent` → `viewed` (Client viewed quote)
- `viewed` → `approved` (Client accepted quote)
- `viewed` → `rejected` (Client declined quote)
- `viewed` → `expired` (Quote expired)

**Request Body**:
```json
{
  "status": "sent",
  "notes": "Quote sent to client via email on 2024-02-01"
}
```

### 3. Revise Rejected/Expired Quote

**Endpoint**: `POST /api/v1/estimates/{quote_id}/revise`

**Request Body**:
```json
{
  "title": "Revised Kitchen Renovation Quote",
  "line_items": [
    {
      "description": "Standard kitchen cabinet installation",
      "quantity": 1,
      "unit_price": 7500.00,
      "unit": "complete_set",
      "category": "Cabinetry"
    }
  ],
  "valid_until": "2024-05-15T23:59:59Z",
  "revision_notes": "Reduced cabinet cost based on client feedback"
}
```

**Response**: Creates a new quote with updated pricing and terms

---

## Quote Deletion

### 1. Delete Draft Quote

**Endpoint**: `DELETE /api/v1/estimates/{quote_id}`

**Important**: Only draft quotes can be deleted

**Response**: `200 OK`
```json
{
  "message": "Quote deleted successfully",
  "quote_id": "550e8400-e29b-41d4-a716-446655440004",
  "success": true
}
```

### 2. Cancel Sent Quote

**Endpoint**: `PATCH /api/v1/estimates/{quote_id}/status`

**Request Body**:
```json
{
  "status": "cancelled",
  "notes": "Quote cancelled at client request"
}
```

**Note**: Sent quotes cannot be deleted, only cancelled

---

## Quote Validation Rules

### Client-Side Validation

```typescript
interface QuoteValidation {
  // Required fields for quotes
  document_type: "quote" // Must be explicitly set
  valid_until: Date      // Required for quotes
  contact_id: string     // Required
  title: string          // Required, min 1 char
  line_items: array      // Required, min 1 item
  
  // Recommended fields
  terms: {
    payment_terms: string
    terms_and_conditions: string // Should include binding language
  }
  
  // Business rules
  valid_until_minimum_days: 7    // Quotes should be valid for at least 7 days
  detailed_descriptions: true    // Line items should have detailed descriptions
}
```

### Validation Examples

```swift
// iOS Swift validation example
func validateQuote(_ quote: QuoteModel) -> [ValidationError] {
    var errors: [ValidationError] = []
    
    // Document type validation
    guard quote.documentType == .quote else {
        errors.append(.invalidDocumentType)
        return errors
    }
    
    // Valid until validation
    guard let validUntil = quote.validUntil else {
        errors.append(.missingValidUntil)
        return errors
    }
    
    let minimumValidDays = 7
    let minimumDate = Calendar.current.date(byAdding: .day, value: minimumValidDays, to: Date())!
    guard validUntil >= minimumDate else {
        errors.append(.validUntilTooSoon)
        return errors
    }
    
    // Line items validation
    guard !quote.lineItems.isEmpty else {
        errors.append(.missingLineItems)
        return errors
    }
    
    // Detailed descriptions validation
    for item in quote.lineItems {
        guard item.description.count >= 10 else {
            errors.append(.lineItemDescriptionTooShort(itemId: item.id))
        }
    }
    
    // Terms validation
    if let terms = quote.terms?.termsAndConditions {
        let bindingKeywords = ["binding", "offer", "acceptance", "commitment"]
        let hasBindingLanguage = bindingKeywords.contains { keyword in
            terms.lowercased().contains(keyword)
        }
        
        if !hasBindingLanguage {
            errors.append(.missingBindingLanguage)
        }
    }
    
    return errors
}
```

---

## Mobile UI Implementation

### 1. Quote Creation Flow

```swift
struct QuoteCreationView: View {
    @State private var quote = QuoteModel()
    @State private var validationErrors: [ValidationError] = []
    
    var body: some View {
        NavigationView {
            Form {
                Section("Quote Details") {
                    TextField("Quote Title", text: $quote.title)
                    TextEditor(text: $quote.description)
                    
                    DatePicker("Valid Until", 
                              selection: $quote.validUntil,
                              in: Date()...,
                              displayedComponents: .date)
                }
                
                Section("Line Items") {
                    ForEach(quote.lineItems.indices, id: \.self) { index in
                        QuoteLineItemRow(item: $quote.lineItems[index])
                    }
                    
                    Button("Add Item") {
                        quote.lineItems.append(QuoteLineItem())
                    }
                }
                
                Section("Terms & Conditions") {
                    TextField("Payment Terms", text: $quote.terms.paymentTerms)
                    TextEditor(text: $quote.terms.termsAndConditions)
                        .placeholder("Include binding language for quotes")
                }
                
                Section("Quote Summary") {
                    QuoteFinancialSummary(quote: quote)
                }
            }
            .navigationTitle("Create Quote")
            .navigationBarItems(
                leading: Button("Cancel") { /* dismiss */ },
                trailing: Button("Create") { createQuote() }
                    .disabled(!isValidQuote())
            )
        }
    }
    
    private func createQuote() {
        // Validate quote
        validationErrors = validateQuote(quote)
        guard validationErrors.isEmpty else { return }
        
        // Call API
        QuoteService.shared.createQuote(quote) { result in
            switch result {
            case .success(let createdQuote):
                // Handle success
                break
            case .failure(let error):
                // Handle error
                break
            }
        }
    }
}
```

### 2. Quote List with Visual Distinctions

```swift
struct QuoteListView: View {
    @State private var quotes: [QuoteModel] = []
    
    var body: some View {
        List(quotes) { quote in
            QuoteRowView(quote: quote)
        }
        .navigationTitle("Quotes")
        .onAppear { loadQuotes() }
    }
}

struct QuoteRowView: View {
    let quote: QuoteModel
    
    var body: some View {
        HStack {
            // Quote indicator
            RoundedRectangle(cornerRadius: 4)
                .fill(Color.green)
                .frame(width: 4, height: 60)
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(quote.estimateNumber)
                        .font(.headline)
                        .foregroundColor(.green)
                    
                    Spacer()
                    
                    QuoteStatusBadge(status: quote.status)
                }
                
                Text(quote.title)
                    .font(.subheadline)
                    .lineLimit(2)
                
                HStack {
                    Text("Valid until: \(quote.validUntil, formatter: dateFormatter)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text(quote.totalAmount, format: .currency(code: quote.currency))
                        .font(.headline)
                        .foregroundColor(.primary)
                }
            }
            
            Spacer()
            
            // Quote icon
            Image(systemName: "doc.text.fill")
                .foregroundColor(.green)
        }
        .padding(.vertical, 4)
    }
}
```

### 3. Quote Status Management

```swift
struct QuoteStatusBadge: View {
    let status: QuoteStatus
    
    var body: some View {
        Text(status.displayName)
            .font(.caption)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(backgroundColor)
            .foregroundColor(textColor)
            .cornerRadius(8)
    }
    
    private var backgroundColor: Color {
        switch status {
        case .draft: return .gray.opacity(0.2)
        case .sent: return .blue.opacity(0.2)
        case .viewed: return .orange.opacity(0.2)
        case .approved: return .green.opacity(0.2)
        case .rejected: return .red.opacity(0.2)
        case .expired: return .yellow.opacity(0.2)
        case .cancelled: return .gray.opacity(0.3)
        }
    }
    
    private var textColor: Color {
        switch status {
        case .draft: return .gray
        case .sent: return .blue
        case .viewed: return .orange
        case .approved: return .green
        case .rejected: return .red
        case .expired: return .yellow
        case .cancelled: return .gray
        }
    }
}
```

---

## API Service Implementation

### 1. Quote Service Class

```swift
class QuoteService: ObservableObject {
    static let shared = QuoteService()
    private let apiClient = APIClient.shared
    
    // Create new quote
    func createQuote(_ quote: QuoteModel, completion: @escaping (Result<QuoteModel, APIError>) -> Void) {
        let endpoint = "/api/v1/estimates"
        
        var request = quote.toCreateRequest()
        request.documentType = "quote"
        
        apiClient.post(endpoint, body: request) { (result: Result<QuoteResponse, APIError>) in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    completion(.success(QuoteModel(from: response)))
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        }
    }
    
    // Update quote
    func updateQuote(_ quote: QuoteModel, completion: @escaping (Result<QuoteModel, APIError>) -> Void) {
        let endpoint = "/api/v1/estimates/\(quote.id)"
        
        let request = quote.toUpdateRequest()
        
        apiClient.put(endpoint, body: request) { (result: Result<QuoteResponse, APIError>) in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    completion(.success(QuoteModel(from: response)))
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        }
    }
    
    // Delete quote
    func deleteQuote(_ quoteId: String, completion: @escaping (Result<Void, APIError>) -> Void) {
        let endpoint = "/api/v1/estimates/\(quoteId)"
        
        apiClient.delete(endpoint) { (result: Result<EmptyResponse, APIError>) in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    completion(.success(()))
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        }
    }
    
    // Update quote status
    func updateQuoteStatus(_ quoteId: String, status: QuoteStatus, notes: String? = nil, completion: @escaping (Result<QuoteModel, APIError>) -> Void) {
        let endpoint = "/api/v1/estimates/\(quoteId)/status"
        
        let request = StatusUpdateRequest(status: status.rawValue, notes: notes)
        
        apiClient.patch(endpoint, body: request) { (result: Result<QuoteResponse, APIError>) in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    completion(.success(QuoteModel(from: response)))
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        }
    }
    
    // Get quotes with filtering
    func getQuotes(documentType: DocumentType = .quote, status: QuoteStatus? = nil, completion: @escaping (Result<[QuoteModel], APIError>) -> Void) {
        var endpoint = "/api/v1/estimates?document_type=quote"
        
        if let status = status {
            endpoint += "&status=\(status.rawValue)"
        }
        
        apiClient.get(endpoint) { (result: Result<QuoteListResponse, APIError>) in
            DispatchQueue.main.async {
                switch result {
                case .success(let response):
                    let quotes = response.estimates.map { QuoteModel(from: $0) }
                    completion(.success(quotes))
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        }
    }
}
```

### 2. Error Handling

```swift
enum QuoteError: LocalizedError {
    case invalidDocumentType
    case missingValidUntil
    case validUntilTooSoon
    case missingLineItems
    case lineItemDescriptionTooShort(itemId: String)
    case missingBindingLanguage
    case cannotEditSentQuote
    case cannotDeleteSentQuote
    case quoteExpired
    
    var errorDescription: String? {
        switch self {
        case .invalidDocumentType:
            return "Document type must be 'quote'"
        case .missingValidUntil:
            return "Quotes must have a valid until date"
        case .validUntilTooSoon:
            return "Quote must be valid for at least 7 days"
        case .missingLineItems:
            return "Quote must have at least one line item"
        case .lineItemDescriptionTooShort:
            return "Line item descriptions should be detailed (minimum 10 characters)"
        case .missingBindingLanguage:
            return "Quote terms should include binding language"
        case .cannotEditSentQuote:
            return "Cannot edit quote after it has been sent"
        case .cannotDeleteSentQuote:
            return "Cannot delete quote after it has been sent"
        case .quoteExpired:
            return "This quote has expired"
        }
    }
}
```

---

## Testing Guidelines

### 1. Unit Tests

```swift
class QuoteServiceTests: XCTestCase {
    var quoteService: QuoteService!
    var mockAPIClient: MockAPIClient!
    
    override func setUp() {
        super.setUp()
        mockAPIClient = MockAPIClient()
        quoteService = QuoteService()
        // Inject mock client
    }
    
    func testCreateQuote_Success() {
        // Given
        let quote = QuoteModel.mockQuote()
        let expectedResponse = QuoteResponse.mockResponse()
        mockAPIClient.mockPostResponse = .success(expectedResponse)
        
        let expectation = XCTestExpectation(description: "Create quote")
        
        // When
        quoteService.createQuote(quote) { result in
            // Then
            switch result {
            case .success(let createdQuote):
                XCTAssertEqual(createdQuote.documentType, .quote)
                XCTAssertEqual(createdQuote.estimateNumber, "QUO-000001")
                expectation.fulfill()
            case .failure:
                XCTFail("Expected success")
            }
        }
        
        wait(for: [expectation], timeout: 1.0)
    }
    
    func testDeleteQuote_DraftStatus_Success() {
        // Given
        let quoteId = "test-quote-id"
        mockAPIClient.mockDeleteResponse = .success(EmptyResponse())
        
        let expectation = XCTestExpectation(description: "Delete quote")
        
        // When
        quoteService.deleteQuote(quoteId) { result in
            // Then
            switch result {
            case .success:
                expectation.fulfill()
            case .failure:
                XCTFail("Expected success")
            }
        }
        
        wait(for: [expectation], timeout: 1.0)
    }
    
    func testValidateQuote_MissingValidUntil_ReturnsError() {
        // Given
        var quote = QuoteModel.mockQuote()
        quote.validUntil = nil
        
        // When
        let errors = validateQuote(quote)
        
        // Then
        XCTAssertTrue(errors.contains(.missingValidUntil))
    }
}
```

### 2. Integration Tests

```swift
class QuoteIntegrationTests: XCTestCase {
    func testQuoteWorkflow_CreateEditDelete() async throws {
        // Create quote
        let quote = try await QuoteService.shared.createQuote(QuoteModel.mockQuote())
        XCTAssertEqual(quote.documentType, .quote)
        XCTAssertEqual(quote.status, .draft)
        
        // Edit quote
        var updatedQuote = quote
        updatedQuote.title = "Updated Quote Title"
        let editedQuote = try await QuoteService.shared.updateQuote(updatedQuote)
        XCTAssertEqual(editedQuote.title, "Updated Quote Title")
        
        // Delete quote
        try await QuoteService.shared.deleteQuote(quote.id)
        
        // Verify deletion
        do {
            _ = try await QuoteService.shared.getQuote(quote.id)
            XCTFail("Expected quote to be deleted")
        } catch APIError.notFound {
            // Expected
        }
    }
}
```

---

## Performance Optimization

### 1. Caching Strategy

```swift
class QuoteCacheManager {
    private var quotesCache: [String: QuoteModel] = [:]
    private let cacheQueue = DispatchQueue(label: "quotes.cache", attributes: .concurrent)
    
    func cacheQuote(_ quote: QuoteModel) {
        cacheQueue.async(flags: .barrier) {
            self.quotesCache[quote.id] = quote
        }
    }
    
    func getCachedQuote(_ id: String) -> QuoteModel? {
        return cacheQueue.sync {
            return quotesCache[id]
        }
    }
    
    func clearCache() {
        cacheQueue.async(flags: .barrier) {
            self.quotesCache.removeAll()
        }
    }
}
```

### 2. Offline Support

```swift
class OfflineQuoteManager {
    private let userDefaults = UserDefaults.standard
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()
    
    func saveDraftQuoteOffline(_ quote: QuoteModel) {
        guard quote.status == .draft else { return }
        
        do {
            let data = try encoder.encode(quote)
            userDefaults.set(data, forKey: "offline_quote_\(quote.id)")
        } catch {
            print("Failed to save offline quote: \(error)")
        }
    }
    
    func getOfflineDraftQuotes() -> [QuoteModel] {
        let keys = userDefaults.dictionaryRepresentation().keys
        let quoteKeys = keys.filter { $0.starts(with: "offline_quote_") }
        
        return quoteKeys.compactMap { key in
            guard let data = userDefaults.data(forKey: key) else { return nil }
            return try? decoder.decode(QuoteModel.self, from: data)
        }
    }
    
    func syncOfflineQuotes() async {
        let offlineQuotes = getOfflineDraftQuotes()
        
        for quote in offlineQuotes {
            do {
                _ = try await QuoteService.shared.createQuote(quote)
                // Remove from offline storage after successful sync
                userDefaults.removeObject(forKey: "offline_quote_\(quote.id)")
            } catch {
                print("Failed to sync offline quote: \(error)")
            }
        }
    }
}
```

---

## Security Considerations

### 1. Data Validation

```swift
extension QuoteModel {
    func sanitizeForAPI() -> QuoteModel {
        var sanitized = self
        
        // Sanitize strings
        sanitized.title = title.trimmingCharacters(in: .whitespacesAndNewlines)
        sanitized.description = description?.trimmingCharacters(in: .whitespacesAndNewlines)
        
        // Validate financial values
        sanitized.lineItems = lineItems.map { item in
            var sanitizedItem = item
            sanitizedItem.quantity = max(0, item.quantity)
            sanitizedItem.unitPrice = max(0, item.unitPrice)
            return sanitizedItem
        }
        
        return sanitized
    }
}
```

### 2. Business Context Validation

```swift
func validateBusinessContext(for quote: QuoteModel) -> Bool {
    guard let currentBusinessId = AuthManager.shared.currentBusinessId else {
        return false
    }
    
    return quote.businessId == currentBusinessId
}
```

---

## Common Questions & Troubleshooting

### Q: Why can't I edit my quote?
**A**: Quotes can only be edited while in `draft` status. Once sent, you need to create a revision.

### Q: What's the difference between cancelling and deleting a quote?
**A**: 
- **Delete**: Permanently removes draft quotes
- **Cancel**: Marks sent quotes as cancelled (preserves audit trail)

### Q: Why does my quote need a valid until date?
**A**: Quotes are binding offers and must have expiration dates for legal clarity.

### Q: How do I handle quote revisions?
**A**: Use the revision endpoint to create a new quote based on the original with updated terms.

### Q: Can I convert a quote back to an estimate?
**A**: No, quotes cannot be converted back to estimates. Create a new estimate if needed.

This guide provides comprehensive implementation details for quote management in your Hero365 mobile application. Focus on the validation rules and visual distinctions to help users understand they're working with binding documents. 