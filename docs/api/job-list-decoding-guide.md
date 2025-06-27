# Job List Decoding Guide for App Client

This guide provides detailed instructions for the mobile app client on how to properly decode and handle job list responses from the Hero365 API.

## API Endpoint

```
GET /api/v1/jobs/list
```

## Response Structure

### Paginated Response Format
```json
{
  "jobs": [JobListResponse],
  "total": 150,
  "skip": 0,
  "limit": 100,
  "has_more": true
}
```

### JobListResponse Schema
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "contact_id": "550e8400-e29b-41d4-a716-446655440002",
  "contact": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "display_name": "John Doe (Acme Corp)",
    "company_name": "Acme Corp",
    "email": "john@acme.com",
    "phone": "+1-555-0123",
    "mobile_phone": "+1-555-0124",
    "primary_contact_method": "john@acme.com"
  },
  "job_number": "JOB-000001",
  "title": "HVAC Maintenance Service",
  "job_type": "maintenance",
  "status": "scheduled",
  "priority": "medium",
  "scheduled_start": "2024-01-15T09:00:00Z",
  "scheduled_end": "2024-01-15T12:00:00Z",
  "assigned_to": ["user123", "user456"],
  "estimated_revenue": "280.00",
  "is_overdue": false,
  "is_emergency": false,
  "created_date": "2024-01-10T10:30:00Z",
  "last_modified": "2024-01-14T16:45:00Z",
  "status_display": "Scheduled",
  "priority_display": "Medium",
  "type_display": "Maintenance"
}
```

## Swift/iOS Decoding

### 1. Define Data Models

```swift
import Foundation

// MARK: - Job List Response Models

struct JobListPaginatedResponse: Codable {
    let jobs: [JobListResponse]
    let total: Int
    let skip: Int
    let limit: Int
    let hasMore: Bool
    
    enum CodingKeys: String, CodingKey {
        case jobs, total, skip, limit
        case hasMore = "has_more"
    }
}

struct JobListResponse: Codable, Identifiable {
    let id: UUID
    let contactId: UUID?
    let contact: JobContact?
    let jobNumber: String
    let title: String
    let jobType: JobType
    let status: JobStatus
    let priority: JobPriority
    let scheduledStart: Date?
    let scheduledEnd: Date?
    let assignedTo: [String]
    let estimatedRevenue: Decimal
    let isOverdue: Bool
    let isEmergency: Bool
    let createdDate: Date?
    let lastModified: Date?
    let statusDisplay: String
    let priorityDisplay: String
    let typeDisplay: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case contactId = "contact_id"
        case contact
        case jobNumber = "job_number"
        case title
        case jobType = "job_type"
        case status, priority
        case scheduledStart = "scheduled_start"
        case scheduledEnd = "scheduled_end"
        case assignedTo = "assigned_to"
        case estimatedRevenue = "estimated_revenue"
        case isOverdue = "is_overdue"
        case isEmergency = "is_emergency"
        case createdDate = "created_date"
        case lastModified = "last_modified"
        case statusDisplay = "status_display"
        case priorityDisplay = "priority_display"
        case typeDisplay = "type_display"
    }
}

struct JobContact: Codable, Identifiable {
    let id: UUID
    let displayName: String
    let companyName: String?
    let email: String?
    let phone: String?
    let mobilePhone: String?
    let primaryContactMethod: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
        case companyName = "company_name"
        case email, phone
        case mobilePhone = "mobile_phone"
        case primaryContactMethod = "primary_contact_method"
    }
}

// MARK: - Enums

enum JobType: String, Codable, CaseIterable {
    case service = "service"
    case project = "project"
    case maintenance = "maintenance"
    case installation = "installation"
    case repair = "repair"
    case inspection = "inspection"
    case consultation = "consultation"
    case quote = "quote"
    case followUp = "follow_up"
    case emergency = "emergency"
    
    var displayName: String {
        switch self {
        case .service: return "Service"
        case .project: return "Project"
        case .maintenance: return "Maintenance"
        case .installation: return "Installation"
        case .repair: return "Repair"
        case .inspection: return "Inspection"
        case .consultation: return "Consultation"
        case .quote: return "Quote"
        case .followUp: return "Follow Up"
        case .emergency: return "Emergency"
        }
    }
}

enum JobStatus: String, Codable, CaseIterable {
    case draft = "draft"
    case quoted = "quoted"
    case scheduled = "scheduled"
    case inProgress = "in_progress"
    case onHold = "on_hold"
    case completed = "completed"
    case cancelled = "cancelled"
    case invoiced = "invoiced"
    case paid = "paid"
    
    var displayName: String {
        switch self {
        case .draft: return "Draft"
        case .quoted: return "Quoted"
        case .scheduled: return "Scheduled"
        case .inProgress: return "In Progress"
        case .onHold: return "On Hold"
        case .completed: return "Completed"
        case .cancelled: return "Cancelled"
        case .invoiced: return "Invoiced"
        case .paid: return "Paid"
        }
    }
}

enum JobPriority: String, Codable, CaseIterable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case urgent = "urgent"
    case emergency = "emergency"
    
    var displayName: String {
        switch self {
        case .low: return "Low"
        case .medium: return "Medium"
        case .high: return "High"
        case .urgent: return "Urgent"
        case .emergency: return "Emergency"
        }
    }
}
```

### 2. Custom Decoder for Dates and Decimals

```swift
extension JobListResponse {
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        // Basic fields
        id = try container.decode(UUID.self, forKey: .id)
        contactId = try container.decodeIfPresent(UUID.self, forKey: .contactId)
        contact = try container.decodeIfPresent(JobContact.self, forKey: .contact)
        jobNumber = try container.decode(String.self, forKey: .jobNumber)
        title = try container.decode(String.self, forKey: .title)
        
        // Enums with fallback
        jobType = try container.decodeIfPresent(JobType.self, forKey: .jobType) ?? .service
        status = try container.decodeIfPresent(JobStatus.self, forKey: .status) ?? .draft
        priority = try container.decodeIfPresent(JobPriority.self, forKey: .priority) ?? .medium
        
        // Arrays
        assignedTo = try container.decodeIfPresent([String].self, forKey: .assignedTo) ?? []
        
        // Booleans
        isOverdue = try container.decodeIfPresent(Bool.self, forKey: .isOverdue) ?? false
        isEmergency = try container.decodeIfPresent(Bool.self, forKey: .isEmergency) ?? false
        
        // Display strings
        statusDisplay = try container.decode(String.self, forKey: .statusDisplay)
        priorityDisplay = try container.decode(String.self, forKey: .priorityDisplay)
        typeDisplay = try container.decode(String.self, forKey: .typeDisplay)
        
        // Dates (ISO 8601 format)
        let dateFormatter = ISO8601DateFormatter()
        
        if let scheduledStartString = try container.decodeIfPresent(String.self, forKey: .scheduledStart) {
            scheduledStart = dateFormatter.date(from: scheduledStartString)
        } else {
            scheduledStart = nil
        }
        
        if let scheduledEndString = try container.decodeIfPresent(String.self, forKey: .scheduledEnd) {
            scheduledEnd = dateFormatter.date(from: scheduledEndString)
        } else {
            scheduledEnd = nil
        }
        
        if let createdDateString = try container.decodeIfPresent(String.self, forKey: .createdDate) {
            createdDate = dateFormatter.date(from: createdDateString)
        } else {
            createdDate = nil
        }
        
        if let lastModifiedString = try container.decodeIfPresent(String.self, forKey: .lastModified) {
            lastModified = dateFormatter.date(from: lastModifiedString)
        } else {
            lastModified = nil
        }
        
        // Decimal handling
        if let revenueString = try container.decodeIfPresent(String.self, forKey: .estimatedRevenue) {
            estimatedRevenue = Decimal(string: revenueString) ?? Decimal.zero
        } else {
            estimatedRevenue = Decimal.zero
        }
    }
}
```

### 3. API Service Implementation

```swift
class JobService: ObservableObject {
    private let baseURL = "https://your-api-domain.com/api/v1"
    private let session = URLSession.shared
    
    func fetchJobs(skip: Int = 0, limit: Int = 100) async throws -> JobListPaginatedResponse {
        var urlComponents = URLComponents(string: "\(baseURL)/jobs/list")!
        urlComponents.queryItems = [
            URLQueryItem(name: "skip", value: String(skip)),
            URLQueryItem(name: "limit", value: String(limit))
        ]
        
        guard let url = urlComponents.url else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        do {
            let decoder = JSONDecoder()
            return try decoder.decode(JobListPaginatedResponse.self, from: data)
        } catch {
            print("Decoding error: \(error)")
            throw APIError.decodingError(error)
        }
    }
}

enum APIError: Error {
    case invalidURL
    case invalidResponse
    case serverError(Int)
    case decodingError(Error)
}
```

### 4. Usage Example

```swift
class JobListViewModel: ObservableObject {
    @Published var jobs: [JobListResponse] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let jobService = JobService()
    
    func loadJobs() async {
        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }
        
        do {
            let response = try await jobService.fetchJobs()
            await MainActor.run {
                self.jobs = response.jobs
                self.isLoading = false
            }
        } catch {
            await MainActor.run {
                self.errorMessage = "Failed to load jobs: \(error.localizedDescription)"
                self.isLoading = false
            }
        }
    }
}
```

## Android/Kotlin Decoding

### 1. Data Classes

```kotlin
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import java.math.BigDecimal
import java.time.Instant
import java.util.*

@Serializable
data class JobListPaginatedResponse(
    val jobs: List<JobListResponse>,
    val total: Int,
    val skip: Int,
    val limit: Int,
    @SerialName("has_more") val hasMore: Boolean
)

@Serializable
data class JobListResponse(
    val id: String,
    @SerialName("contact_id") val contactId: String? = null,
    val contact: JobContact? = null,
    @SerialName("job_number") val jobNumber: String,
    val title: String,
    @SerialName("job_type") val jobType: JobType,
    val status: JobStatus,
    val priority: JobPriority,
    @SerialName("scheduled_start") val scheduledStart: String? = null,
    @SerialName("scheduled_end") val scheduledEnd: String? = null,
    @SerialName("assigned_to") val assignedTo: List<String> = emptyList(),
    @SerialName("estimated_revenue") val estimatedRevenue: String,
    @SerialName("is_overdue") val isOverdue: Boolean = false,
    @SerialName("is_emergency") val isEmergency: Boolean = false,
    @SerialName("created_date") val createdDate: String? = null,
    @SerialName("last_modified") val lastModified: String? = null,
    @SerialName("status_display") val statusDisplay: String,
    @SerialName("priority_display") val priorityDisplay: String,
    @SerialName("type_display") val typeDisplay: String
) {
    // Helper methods to convert string dates to Instant
    fun getScheduledStartInstant(): Instant? = scheduledStart?.let { Instant.parse(it) }
    fun getScheduledEndInstant(): Instant? = scheduledEnd?.let { Instant.parse(it) }
    fun getCreatedDateInstant(): Instant? = createdDate?.let { Instant.parse(it) }
    fun getLastModifiedInstant(): Instant? = lastModified?.let { Instant.parse(it) }
    
    // Helper method to convert string to BigDecimal
    fun getEstimatedRevenueDecimal(): BigDecimal = BigDecimal(estimatedRevenue)
}

@Serializable
data class JobContact(
    val id: String,
    @SerialName("display_name") val displayName: String,
    @SerialName("company_name") val companyName: String? = null,
    val email: String? = null,
    val phone: String? = null,
    @SerialName("mobile_phone") val mobilePhone: String? = null,
    @SerialName("primary_contact_method") val primaryContactMethod: String
)

@Serializable
enum class JobType(val value: String) {
    @SerialName("service") SERVICE("service"),
    @SerialName("project") PROJECT("project"),
    @SerialName("maintenance") MAINTENANCE("maintenance"),
    @SerialName("installation") INSTALLATION("installation"),
    @SerialName("repair") REPAIR("repair"),
    @SerialName("inspection") INSPECTION("inspection"),
    @SerialName("consultation") CONSULTATION("consultation"),
    @SerialName("quote") QUOTE("quote"),
    @SerialName("follow_up") FOLLOW_UP("follow_up"),
    @SerialName("emergency") EMERGENCY("emergency");
    
    val displayName: String
        get() = when (this) {
            SERVICE -> "Service"
            PROJECT -> "Project"
            MAINTENANCE -> "Maintenance"
            INSTALLATION -> "Installation"
            REPAIR -> "Repair"
            INSPECTION -> "Inspection"
            CONSULTATION -> "Consultation"
            QUOTE -> "Quote"
            FOLLOW_UP -> "Follow Up"
            EMERGENCY -> "Emergency"
        }
}

@Serializable
enum class JobStatus(val value: String) {
    @SerialName("draft") DRAFT("draft"),
    @SerialName("quoted") QUOTED("quoted"),
    @SerialName("scheduled") SCHEDULED("scheduled"),
    @SerialName("in_progress") IN_PROGRESS("in_progress"),
    @SerialName("on_hold") ON_HOLD("on_hold"),
    @SerialName("completed") COMPLETED("completed"),
    @SerialName("cancelled") CANCELLED("cancelled"),
    @SerialName("invoiced") INVOICED("invoiced"),
    @SerialName("paid") PAID("paid");
    
    val displayName: String
        get() = when (this) {
            DRAFT -> "Draft"
            QUOTED -> "Quoted"
            SCHEDULED -> "Scheduled"
            IN_PROGRESS -> "In Progress"
            ON_HOLD -> "On Hold"
            COMPLETED -> "Completed"
            CANCELLED -> "Cancelled"
            INVOICED -> "Invoiced"
            PAID -> "Paid"
        }
}

@Serializable
enum class JobPriority(val value: String) {
    @SerialName("low") LOW("low"),
    @SerialName("medium") MEDIUM("medium"),
    @SerialName("high") HIGH("high"),
    @SerialName("urgent") URGENT("urgent"),
    @SerialName("emergency") EMERGENCY("emergency");
    
    val displayName: String
        get() = when (this) {
            LOW -> "Low"
            MEDIUM -> "Medium"
            HIGH -> "High"
            URGENT -> "Urgent"
            EMERGENCY -> "Emergency"
        }
}
```

### 2. API Service Implementation

```kotlin
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import java.io.IOException

class JobService(private val baseUrl: String, private val authToken: String) {
    private val client = OkHttpClient()
    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
    }
    
    suspend fun fetchJobs(skip: Int = 0, limit: Int = 100): Result<JobListPaginatedResponse> {
        return try {
            val url = "$baseUrl/api/v1/jobs/list?skip=$skip&limit=$limit"
            val request = Request.Builder()
                .url(url)
                .addHeader("Authorization", "Bearer $authToken")
                .addHeader("Content-Type", "application/json")
                .build()
            
            val response: Response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val body = response.body?.string() ?: ""
                val jobResponse = json.decodeFromString<JobListPaginatedResponse>(body)
                Result.success(jobResponse)
            } else {
                Result.failure(IOException("Server error: ${response.code}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

## Key Handling Points

### 1. Nullable Fields
- `contact_id` and `contact` can be null
- All datetime fields can be null
- Handle gracefully with default values

### 2. Date Format
- All dates are in ISO 8601 format: `"2024-01-15T09:00:00Z"`
- Use proper date parsers (`ISO8601DateFormatter` for iOS, `Instant.parse()` for Android)

### 3. Decimal Precision
- `estimated_revenue` comes as string to preserve decimal precision
- Convert to appropriate decimal type in your platform

### 4. Enum Validation
- API provides fallback values for invalid enums
- Always use `decodeIfPresent` with default values

### 5. Array Fields
- `assigned_to` is always an array, but can be empty
- Handle empty arrays gracefully

### 6. Display Fields
- Use `status_display`, `priority_display`, `type_display` for UI
- These are pre-formatted for user display

## Error Handling

Always implement proper error handling for:
- Network failures
- JSON parsing errors
- Invalid enum values
- Missing required fields
- Server errors (4xx, 5xx responses)

This structure ensures robust handling of job list data while maintaining type safety and proper validation across your mobile applications. 