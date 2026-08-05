# CarbonatiX — API Schema

Request/response parameter documentation for each endpoint per RFC 001 & RFC 002.

---

## 1. Auth (`/auth`)

### `POST /auth/register` — Create new account

**Request:**

|Param|Type|Description|
|-|-|-|
|`email`|string (email)|required, unique|
|`password`|string|required, min 8 chars, must contain letters+numbers+symbols|

**Response `201`:**

```json
{
  "user": { "id": "usr_123", "email": "user@company.com" },
  "token": "jwt-token"
}
```

---

### `POST /auth/login` — Login

**Request:**

|Param|Type|Description|
|-|-|-|
|`email`|string (email)|required|
|`password`|string|required|

**Response `200`:**

```json
{
  "user": { "id": "usr_123", "email": "user@company.com" },
  "token": "jwt-token"
}
```

---

## 2. Company (`/company`)

> All requests require header `Authorization: Bearer <jwt>`

### `GET /company` — Get company data

**Response `200`:**

```json
{
  "company": {
    "id": "cmp_123",
    "name": "Demo Smelter",
    "technology": "RKEF",
    "period_cap_tco2e": 480000.0,
    "site_spec": {
      "ef_captive_pltu": 0.98,
      "dryer_thermal_efficiency": 0.82,
      "sec_eaf_kwh_per_t_alloy": 3200.0,
      "alloy_nickel_grade": 0.12,
      "kiln_thermal_efficiency": 0.74
    }
  }
}
```

---

### `PUT /company` — Update company data

**Request (all fields optional):**

|Param|Type|Description|
|-|-|-|
|`name`|string|optional|
|`technology`|string|optional|
|`period_cap_tco2e`|float|optional|
|`site_spec`|object|optional, see sub-fields below|

**site_spec sub-fields:**

|Param|Type|Description|
|-|-|-|
|`ef_captive_pltu`|float|emission factor captive PLTU|
|`dryer_thermal_efficiency`|float|dryer thermal efficiency|
|`sec_eaf_kwh_per_t_alloy`|float|EAF specific energy consumption (kWh/t alloy)|
|`alloy_nickel_grade`|float|nickel alloy grade|
|`kiln_thermal_efficiency`|float|kiln thermal efficiency|

**Response `200`:** Returns the same company object as `GET /company`.

---

## 3. Twin Model (`/twin`)

> All requests require header `Authorization: Bearer <jwt>`

### `POST /twin/model` — Upload GLB model

**Request:** `multipart/form-data`

|Param|Type|Description|
|-|-|-|
|`file`|file (.glb)|required|

**Response `201`:**

```json
{
  "twin_model": {
    "id": "twin_123",
    "file_id": "file_glb_123",
    "parts": [
      { "mesh_ref": "mesh_ore_stockpile", "label": "Ore Stockpile" }
    ]
  }
}
```

---

### `GET /twin/nodes` — Get node authoring state

**Response `200`:**

```json
{
  "twin_model_id": "twin_123",
  "nodes": [
    {
      "node_id": "node_ore_1",
      "label": "Ore Stockpile A",
      "mesh_ref": "mesh_ore_stockpile",
      "process_type": "ORE_STOCKPILE"
    }
  ]
}
```

---

### `PUT /twin/nodes` — Replace entire node list

**Request:**

|Param|Type|Description|
|-|-|-|
|`nodes`|array|required, list of node objects|

**Node object:**

|Param|Type|Description|
|-|-|-|
|`node_id`|string|required|
|`label`|string|required|
|`mesh_ref`|string|required|
|`process_type`|string|required, e.g. `ORE_STOCKPILE`, `ROTARY_DRYER`, `ROTARY_KILN`, `EAF`, `CAPTIVE_POWER`|

**Response `200`:** Returns the same object as `GET /twin/nodes`.

---

### `GET /twin/gaps` — Check model gaps

**Response `200`:**

```json
{
  "unbound_required_process_types": ["CAPTIVE_POWER"],
  "orphan_fields": [
    {
      "field_name": "dryer_thermal_efficiency",
      "owning_process_type": "ROTARY_DRYER",
      "document_id": "doc_123"
    }
  ],
  "ambiguous_fields": [
    {
      "field_name": "reductant_biocoke_pct",
      "owning_process_type": "ROTARY_KILN",
      "candidate_node_ids": ["node_kiln_1", "node_kiln_2"]
    }
  ]
}
```

---

## 4. Documents (`/documents`)

> All requests require header `Authorization: Bearer <jwt>`

### `POST /documents` — Upload documents

**Request:** `multipart/form-data`

|Param|Type|Description|
|-|-|-|
|`files[]`|file(s)|required, PDF/image/XLSX|

**Response `201`:**

```json
{
  "documents": [
    { "document_id": "doc_123", "status": "processed" }
  ],
  "candidates": [
    {
      "candidate_id": "cand_123",
      "field_name": "wet_ore_input_tons",
      "value": 42000.0,
      "confidence": 0.93,
      "owning_process_type": "ORE_STOCKPILE",
      "routing_status": "routed",
      "target_node_id": "node_ore_1",
      "accepted": false
    }
  ]
}
```

---

## 5. Emissions (`/emissions`)

> All requests require header `Authorization: Bearer <jwt>`
> This route is stateless — no database writes.

### `POST /emissions` — Calculate emissions

**Request:**

|Param|Type|Description|
|-|-|-|
|`wet_ore_input_tons`|float|wet ore tonnage|
|`moisture_content_pct`|float|fraction [0,1], e.g. 0.32 for 32%|
|`nickel_grade_pct`|float|fraction [0,1]|
|`reductant_biocoke_pct`|float|fraction [0,1]|
|`sec_eaf_kwh_per_t_alloy`|float|EAF specific energy|
|`power_mix_captive_coal`|float|fraction [0,1], must sum = 1.0|
|`power_mix_hydro_grid`|float|fraction [0,1], must sum = 1.0|
|`ef_captive_pltu`|float|emission factor|
|`dryer_thermal_efficiency`|float|thermal efficiency|

**Response `200`:**

```json
{
  "emission_result": {
    "nickel_output_tons": 514.08,
    "alloy_output_tons": 4284.0,
    "dryer_emissions": 100.0,
    "kiln_heat_emissions": 200.0,
    "kiln_reductant_emissions": 300.0,
    "eaf_emissions": 400.0,
    "scope_1": 600.0,
    "scope_2": 400.0,
    "total_emissions": 1000.0,
    "intensity_per_tonne_ni": 1.945,
    "dry_ore_tons": 28560.0,
    "dryer_coal_tons": 50.0,
    "kiln_coal_tons": 60.0,
    "reductant_tons": 70.0,
    "eaf_mwh": 80.0
  }
}
```

> Note: `intensity_per_tonne_ni` may be `null` when nickel output is 0.

---

## 6. Runs (`/runs`)

> All requests require header `Authorization: Bearer <jwt>`

### `POST /runs` — Commit calculation snapshot

**Request:**

|Param|Type|Description|
|-|-|-|
|`input_snapshot`|object|required, same fields as `POST /emissions` request|

**Response `201`:**

```json
{
  "run": {
    "id": "run_123",
    "input_snapshot": {},
    "emission_result": {},
    "compliance": {
      "period_cap_tco2e": 480000.0,
      "status": "deficit",
      "position_tco2e": 45000.0,
      "value_idr": 1584000000.0
    },
    "forecast_snapshot": {
      "nickel": { "price_usd_per_ton": 15400.0 },
      "carbon": { "limit_price_idr": 35200.0 }
    },
    "created_at": "2026-08-04T08:00:00Z"
  }
}
```

> Note: This route writes an immutable snapshot. Stored forecast values are from commit time.

---

### `GET /runs/{id}` — Get committed run

**Response `200`:** Same shape as `POST /runs` response.

---

## 7. Forecasts (`/forecasts`)

> All requests require header `Authorization: Bearer <jwt>`

### `GET /forecasts` — Get price projections

**Query params:**

|Param|Type|Description|
|-|-|-|
|`horizon_days`|int|required, 7–30, default 14|

**Response `200`:**

```json
{
  "horizon_days": 14,
  "nickel_forecast": {
    "currency": "USD",
    "points": [
      {
        "date": "2026-08-05",
        "price_usd_per_ton": 15400.0,
        "lower_usd_per_ton": 14900.0,
        "upper_usd_per_ton": 15900.0
      }
    ],
    "stale": false
  },
  "carbon_forecast": {
    "currency": "IDR",
    "points": [
      {
        "date": "2026-08-05",
        "limit_price_idr": 42000.0,
        "lower_limit_price_idr": 39000.0,
        "upper_limit_price_idr": 46000.0
      }
    ],
    "stale": false
  }
}
```

---

## 8. Recommendations SSE (`/runs/{id}/recommendation`)

> Requires header `Authorization: Bearer <jwt>`
> Media type: `text/event-stream`

### `GET /runs/{id}/recommendation` — Stream recommendation

**Events:**

|Event|Status|Description|
|-|-|-|
|`stage`|`running` \| `complete` \| `failed`|Progress stage|
|`recommendation`|—|Final recommendation|
|`error`|—|Error if advisor fails|
|`done`|—|Stream complete|

**Example stream:**

```
event: stage
data: {"stage":"retrieve","status":"running"}

event: stage
data: {"stage":"retrieve","status":"complete"}

event: recommendation
data: {"text":"...","citations":[{"article":"Perpres 98/2021 Pasal 3"}],"confidence":0.84}

event: done
data: {"run_id":"run_123"}
```

---

## 9. Error Contract

All error responses follow this format:

```json
{
  "error": {
    "code": "validation_error",
    "message": "moisture_content_pct must be between 0 and 1",
    "field": "moisture_content_pct",
    "details": { "owner_process_type": "ORE_STOCKPILE" }
  }
}
```

|Field|Type|Description|
|-|-|-|
|`code`|string|machine-readable error code|
|`message`|string|human-readable message|
|`field`|string\|null|optional, for field-level validation|
|`details`|object\|null|optional, additional context|

**Status code conventions:**

|Code|Description|
|-|-|
|`200`|Successful read or computation|
|`201`|Successfully created resource|
|`400`|Malformed request shape|
|`401`|Missing or invalid token|
|`403`|Authenticated but not authorized|
|`404`|Resource not found within caller scope|
|`409`|Conflict with current state|
|`413`|File too large|
|`415`|Unsupported file type|
|`422`|Semantically invalid input|
|`503`|Dependency unavailable|

---

## 10. Auth Header

All protected routes require:

```
Authorization: Bearer <jwt>
```

JWT is issued and verified by FastAPI. JWT payload:

|Claim|Description|
|-|-|
|`sub`|user_id|
|`company_id`|company data scope|
|`email`|user email|
|`exp`|expiry timestamp|
