# CarbonatiX ERP — API Params Schema

Dokumentasi parameter request untuk setiap endpoint, melengkapi mapping Streamlit ↔ FastAPI.

\---

## 1\. Users (`/api/v1/users`)

### `POST /users` — Register user baru

|Param|Tipe|Keterangan|
|-|-|-|
|`username`|string|wajib, unik|
|`email`|string|wajib, unik|
|`password`|string|wajib|
|`full\_name`|string|wajib|
|`role`|enum|`admin` \| `superadmin` \| `operator` \| `viewer`|
|`facility\_id`|string|wajib|
|`phone\_number`|string|opsional|

### `PUT /users/{id}` — Update user

|Param|Tipe|Keterangan|
|-|-|-|
|`full\_name`|string|opsional|
|`email`|string|opsional|
|`phone\_number`|string|opsional|
|`role`|enum|opsional|
|`facility\_id`|string|opsional|
|`is\_active`|boolean|opsional|

### `PUT /users/{id}` — Approval (superadmin only)

|Param|Tipe|Keterangan|
|-|-|-|
|`status`|enum|`pending` \| `approved` \| `rejected`|
|`approved\_by`|string|user\_id superadmin|
|`approved\_at`|datetime|timestamp approval|

### `GET /users` — Query params (list/filter)

|Param|Tipe|Keterangan|
|-|-|-|
|`role`|enum|filter opsional|
|`facility\_id`|string|filter opsional|
|`status`|enum|filter opsional|
|`search`|string|cari nama/email|
|`page`|int|default 1|
|`page\_size`|int|default 20|

\---

## 2\. Node Data — RKEF Process (`/api/v1/nodes`)

### `POST /nodes` — Buat node baru

|Param|Tipe|Keterangan|
|-|-|-|
|`node\_id`|string|wajib, unik|
|`node\_name`|string|wajib|
|`facility\_id`|string|wajib|
|`line`|string|mis. "RKEF Line 4"|
|`latitude`|float|wajib|
|`longitude`|float|wajib|
|`node\_type`|enum|`furnace` \| `converter` \| `casting` \| dst|
|`status`|enum|`active` \| `idle` \| `maintenance`|

### `PUT /nodes/{id}` — Update node

|Param|Tipe|Keterangan|
|-|-|-|
|`node\_name`|string|opsional|
|`latitude`|float|opsional|
|`longitude`|float|opsional|
|`status`|enum|opsional|
|`node\_type`|enum|opsional|

### `POST /nodes/{id}/parameters` — Input parameter node

|Param|Tipe|Keterangan|
|-|-|-|
|`timestamp`|datetime|wajib|
|`electrode\_load`|float|—|
|`tap\_temperature`|float|—|
|`power\_draw`|float|—|
|`hourly\_emissions`|float|—|
|`ptbae\_pu\_cap\_contribution`|float|—|
|`ore\_input\_vol`|float|—|
|`avg\_moisture`|float|—|
|`nickel\_grade`|float|—|
|`total\_power\_draw`|float|—|
|`scope\_process`|float|Scope 1|
|`scope\_grid`|float|Scope 2|
|`current\_intensity`|float|tCO2/tNi|

### `GET /nodes` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`facility\_id`|string|filter opsional|
|`status`|enum|filter opsional|
|`node\_type`|enum|filter opsional|
|`page`|int|default 1|
|`page\_size`|int|default 20|

### `GET /nodes/{id}/parameters` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`date\_from`|date|opsional|
|`date\_to`|date|opsional|
|`granularity`|enum|`raw` \| `hourly` \| `daily`|

### Grouping tampilan UI (referensi widget)

**Selected Node Inspector**

```
latitude, longitude, node\_id, node\_name, status,
electrode\_load, tap\_temperature, power\_draw,
hourly\_emissions, ptbae\_pu\_cap\_contribution
```

**Global Site Informatics**

```
ore\_input\_vol, avg\_moisture, nickel\_grade,
total\_power\_draw, scope\_process, scope\_grid,
current\_intensity
```

\---

## 3\. Document Upload \& Extraction (`/api/v1/documents`)

### `POST /documents` — Upload dokumen

|Param|Tipe|Keterangan|
|-|-|-|
|`file`|multipart/file|wajib|
|`document\_type`|enum|`spe\_grk` \| `srn\_ppi` \| `lcam` \| `invoice` \| `permit` \| `other`|
|`facility\_id`|string|wajib|
|`uploaded\_by`|string|user\_id|
|`tags`|array\[string]|opsional|

### `POST /documents/{id}/extract` — Jalankan ekstraksi

|Param|Tipe|Keterangan|
|-|-|-|
|`extraction\_mode`|enum|`auto` \| `manual`|
|`extract\_fields`|array\[string]|opsional, field spesifik yang mau diekstrak|

### `GET /documents/{id}/extracted-data` — Response fields

|Field|Tipe|Keterangan|
|-|-|-|
|`document\_id`|string|—|
|`extracted\_at`|datetime|—|
|`confidence\_score`|float|0–1|
|`fields`|object|key-value hasil ekstraksi|
|`raw\_text`|string|teks mentah hasil OCR/parsing|
|`status`|enum|`success` \| `partial` \| `failed`|

### `GET /documents` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`facility\_id`|string|filter opsional|
|`document\_type`|enum|filter opsional|
|`status`|enum|filter opsional|
|`date\_from`|date|opsional|
|`date\_to`|date|opsional|
|`page`|int|default 1|
|`page\_size`|int|default 20|

\---

## 4\. 3D Scan (`/api/v1/scans`)

### `POST /scans` — Upload scan

|Param|Tipe|Keterangan|
|-|-|-|
|`file`|multipart/file|`.glb` \| `.obj` \| `.ply`|
|`facility\_id`|string|wajib|
|`node\_id`|string|opsional|
|`scan\_name`|string|wajib|
|`captured\_at`|datetime|opsional|
|`captured\_by`|string|user\_id|

### `GET /scans` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`facility\_id`|string|filter opsional|
|`node\_id`|string|filter opsional|
|`date\_from`|date|opsional|
|`date\_to`|date|opsional|
|`page`|int|default 1|
|`page\_size`|int|default 20|

### `GET /scans/{id}/file` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`format`|enum|`glb` \| `obj` \| `ply` (jika tersedia multi-format)|

### `DELETE /scans/{id}`

Tidak ada body — cukup path param `id`.

\---

## 5\. Models (`/api/v1/models`)

### `GET /models` — Query params

|Param|Tipe|Keterangan|
|-|-|-|
|`facility\_id`|string|filter opsional|
|`model\_type`|enum|`emission\\\_prediction` \| `what\\\_if\\\_simulation` \| dst|
|`status`|enum|filter opsional|

### `POST /models/simulate` — AI What-If Engine

|Param|Tipe|Keterangan|
|-|-|-|
|`facility\_id`|string|wajib|
|`shift\_coal\_to\_hydro\_pct`|int (0–100)|—|
|`production\_capacity\_overdrive\_pct`|int (50–150)|—|
|`ore\_quality\_moisture\_ni\_grade\_pct`|int (0–100)|—|
|`inject\_bio\_coke\_reductant`|boolean|—|



