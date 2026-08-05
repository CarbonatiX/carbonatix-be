# CarbonatiX ERP — API Params Schema

Dokumentasi parameter request untuk setiap endpoint, melengkapi mapping Streamlit ↔ FastAPI.

---

## 1. Users (`/api/v1/users`)

### `POST /users` — Register user baru

|Param|Tipe|Keterangan|
|-|-|-|
|`username`|string|wajib, unik|
|`email`|string|wajib, unik|
|`password`|string|wajib|
|`full_name`|string|wajib|
|`role`|enum|`operator` | `viewer`|
|`facility_id`|string|wajib|
|`phone_number`|string|opsional|

### `PUT /users/{id}` — Update user

|Param|Tipe|Keterangan|
|-|-|-|
|`full_name`|string|opsional|
|`email`|string|opsional|
|`phone_number`|string|opsional|
|`role`|enum|opsional|
|`facility_id`|string|opsional|
|`is_active`|boolean|opsional|

### `PUT /users/{id}` — Approval (superadmin only)

|Param|Tipe|Keterangan|
|-|-|-|
|`status`|enum|`pending` | `approved` | `rejected`|
|`approved_by`|string|user_id operator|
|`approved_at`|datetime|timestamp approval|

### `GET /users` — Query params (list/filter)

|Param|Tipe|Keterangan|
|-|-|-|
|`role`|enum|filter opsional|
|`facility_id`|string|filter opsional|
|`status`|enum|filter opsional|
|`search`|string|cari nama/email|
|`page`|int|default 1|
|`page_size`|int|default 20|

---

## 2. Node Data — RKEF Process (`/api/v1/nodes`)

### `POST /nodes` — Buat node baru

|Param|Tipe|Keterangan|
|-|-|-|
|`node_id`|string|wajib, unik|
|`node_name`|string|wajib|
|`facility_id`|string|wajib|
|`line`|string|mis. "RKEF Line 4"|
|`latitude`|float|wajib|
|`longitude`|float|wajib|
|`node_type`|enum|`furnace` | `converter` | `casting` | dst|
|`status`|enum|`active` | `idle` | `maintenance`|

### `PUT /nodes/{id}` — Update node

|Param|Tipe|Keterangan|
|-|-|-|
|`node_name`|string|opsional|
|`latitude`|float|opsional|
|`longitude`|float|opsional|
|`status`|enum|opsional|
|`node_type`|enum|opsional|

### `POST /nodes/{id}/parameters` — Input parameter node

|Param|Tipe|Keterangan|
|-|-|-|
|`timestamp`|datetime|wajib|
|`electrode_load`|float|—|
|`tap_temperature`|float|—|
|`power_draw`|float|—|
|`hourly_emissions`|float|—|
|`ptbae_pu_cap_contribution`|float|—|
|`ore_input_vol`|float|—|
|`avg_moisture`|float|—|
|`nickel_grade`|float|—|
|`total_power_draw`|float|—|
|`scope_process`|float|Scope 1|
|`scope_grid`|float|Scope 2|
|`current_intensity`|float|tCO2/tNi|

### `GET /nodes` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`facility_id`|string|filter opsional|
|`status`|enum|filter opsional|
|`node_type`|enum|filter opsional|
|`page`|int|default 1|
|`page_size`|int|default 20|

### `GET /nodes/{id}/parameters` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`date_from`|date|opsional|
|`date_to`|date|opsional|
|`granularity`|enum|`raw` | `hourly` | `daily`|

### Grouping tampilan UI (referensi widget)

**Selected Node Inspector**

```
latitude, longitude, node_id, node_name, status,
electrode_load, tap_temperature, power_draw,
hourly_emissions, ptbae_pu_cap_contribution
```

**Global Site Informatics**

```
ore_input_vol, avg_moisture, nickel_grade,
total_power_draw, scope_process, scope_grid,
current_intensity
```

---

## 3. Document Upload \& Extraction (`/api/v1/documents`)

### `POST /documents` — Upload dokumen

|Param|Tipe|Keterangan|
|-|-|-|
|`file`|multipart/file|wajib|
|`document_type`|enum|`spe_grk` \| `srn_ppi` \| `lcam` \| `invoice` \| `permit` \| `other`|
|`facility_id`|string|wajib|
|`uploaded_by`|string|user_id|
|`tags`|array[string]|opsional|

### `POST /documents/{id}/extract` — Jalankan ekstraksi

|Param|Tipe|Keterangan|
|-|-|-|
|`extraction_mode`|enum|`auto` | `manual`|
|`extract_fields`|array[string]|opsional, field spesifik yang mau diekstrak|

### `GET /documents/{id}/extracted-data` — Response fields

|Field|Tipe|Keterangan|
|-|-|-|
|`document_id`|string|—|
|`extracted_at`|datetime|—|
|`confidence_score`|float|0–1|
|`fields`|object|key-value hasil ekstraksi|
|`raw_text`|string|teks mentah hasil OCR/parsing|
|`status`|enum|`success` | `partial` | `failed`|

### `GET /documents` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`facility_id`|string|filter opsional|
|`document_type`|enum|filter opsional|
|`status`|enum|filter opsional|
|`date_from`|date|opsional|
|`date_to`|date|opsional|
|`page`|int|default 1|
|`page_size`|int|default 20|

---

## 4. 3D Scan (`/api/v1/scans`)

### `POST /scans` — Upload scan

|Param|Tipe|Keterangan|
|-|-|-|
|`file`|multipart/file|`.glb` | `.obj` | `.ply`|
|`facility_id`|string|wajib|
|`node_id`|string|opsional|
|`scan_name`|string|wajib|
|`captured_at`|datetime|opsional|
|`captured_by`|string|user_id|

### `GET /scans` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`facility_id`|string|filter opsional|
|`node_id`|string|filter opsional|
|`date_from`|date|opsional|
|`date_to`|date|opsional|
|`page`|int|default 1|
|`page_size`|int|default 20|

### `GET /scans/{id}/file` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`format`|enum|`glb` | `obj` | `ply` (jika tersedia multi-format)|

### `DELETE /scans/{id}`

Tidak ada body — cukup path param `id`.

---

## 5. Models (`/api/v1/models`)

### `GET /models` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`facility_id`|string|filter opsional|
|`model_type`|enum|`emission_prediction` | `what_if_simulation` | dst|
|`status`|enum|filter opsional|

### `POST /models/simulate` — AI What-If Engine

|Param|Tipe|Keterangan|
|-|-|-|
|`facility_id`|string|wajib|
|`shift_coal_to_hydro_pct`|int (0–100)|—|
|`production_capacity_overdrive_pct`|int (50–150)|—|
|`ore_quality_moisture_ni_grade_pct`|int (0–100)|—|
|`inject_bio_coke_reductant`|boolean|—|



