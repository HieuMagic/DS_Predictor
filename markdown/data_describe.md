# Mô tả Dữ Liệu - DS_Predictor

## 📊 Tổng Quan Dataset

### Thông tin cơ bản
- **Số lượng mẫu**: 14,585 xe
- **Số lượng đặc trưng**: 71 features (70 features + 1 target)
- **Biến mục tiêu**: `price_million` (Giá xe tính bằng triệu VNĐ)
- **Loại bài toán**: Regression (Dự đoán giá xe)
- **Nguồn dữ liệu**: 
  - Chotot.com: 4,928 mẫu ban đầu
  - Bonbanh.com: 10,000 mẫu ban đầu
  - Sau xử lý outliers và missing values: 14,585 mẫu

---

## 📂 Nguồn Dữ Liệu Gốc

### 1. Dataset Chotot (`raw_chotot_car_features.csv`)
**Đặc điểm:**
- Nguồn: Web scraping từ Chotot.com
- Số mẫu: 4,928 xe
- Số features: 21 cột
- Tình trạng: Nhiều missing values (17%-100%), dữ liệu chưa chuẩn hóa

**Các trường dữ liệu quan trọng:**
- `price`: Giá xe (format: "320.000.000 đ")
- `Hãng`, `Dòng xe`: Thông tin hãng và model xe
- `Số Km đã đi`: Số km đã đi (có giá trị placeholder 999999)
- `Năm sản xuất`: Năm sản xuất xe
- `Hộp số`: Loại hộp số (Tự động/Số sàn/Bán tự động)
- `Nhiên liệu`: Loại nhiên liệu (Xăng/Dầu/Điện/Hybrid)
- `Kiểu dáng`: Kiểu dáng xe (SUV, Sedan, Hatchback, etc.)
- `Số chỗ`: Số chỗ ngồi
- `Xuất xứ`: Quốc gia xuất xứ
- `Tình trạng`: Tình trạng xe (Đã sử dụng/Mới)
- `location`: Địa chỉ bán xe

**Các trường bị loại bỏ:**
- `seller` (100% missing)
- `Còn hạn đăng kiểm` (58% missing)
- `Số đời chủ` (57% missing)
- `Có phụ kiện đi kèm` (68% missing)
- `Chính sách bảo hành`, `Trọng lượng`, `Trọng tải` (không liên quan)

### 2. Dataset Bonbanh (`raw_bonbanh_car_features.csv`)
**Đặc điểm:**
- Nguồn: Web scraping từ Bonbanh.com
- Số mẫu: 10,000 xe
- Số features: 15 cột
- Tình trạng: Dữ liệu sạch hơn, hầu như không có missing values (chỉ 0.15% ở location)

**Các trường dữ liệu quan trọng:**
- `title`: Tên xe (format: "Xe Toyota Fortuner Legender 2.4L 4x2 AT 2025")
  - Cần extract `brand` và `model` từ title
- `price`: Giá xe (format: "1 Tỷ 679 Triệu", "498 Triệu")
- `Năm sản xuất`: Năm sản xuất xe
- `Tình trạng`: Xe mới/Xe đã dùng
- `Số Km đã đi`: Format "6,900 Km", xe mới là "-"
- `Xuất xứ`: Nhập khẩu/Trong nước
- `Kiểu dáng`: Kiểu dáng xe
- `Động cơ`: Chứa nhiên liệu và dung tích (ví dụ: "Xăng 2.0 L")
- `Hộp số`: Số tự động/Số tay
- `Số chỗ ngồi`: Format "5 chỗ", "7 chỗ"
- `location`: Địa chỉ chi tiết

**Các trường bị loại bỏ:**
- `Dẫn động`: Không có ở Chotot
- `Màu ngoại thất`, `Màu nội thất`: Ít ảnh hưởng giá
- `Số cửa`: Không quan trọng
- `Dung tích động cơ`: Khó fill chính xác

---

## 🔄 Quy Trình Xử Lý Dữ Liệu

### Phase I: Đánh Giá Dữ Liệu Thô
- Khám phá cấu trúc dữ liệu từ 2 nguồn
- Đánh giá missing values
- Xác định các trường dữ liệu cần giữ lại và loại bỏ

### Phase II: Chuẩn Hóa Dữ Liệu (normalize_interim.csv)

#### 2.1 Parse Price → `price_million`
- **Chotot**: "320.000.000 đ" → 320
- **Bonbanh**: "1 Tỷ 679 Triệu" → 1,679
- **Loại**: Float (triệu VNĐ)

#### 2.2 Parse Odometer → `km`
- **Chotot**: Xử lý placeholder 999999 → NaN
- **Bonbanh**: "6,900 Km" → 6900, "-" → 0 (xe mới)
- **Loại**: Float (km)

#### 2.3 Parse Year → `year`
- Validate range: 1980-2025
- **Loại**: Float (năm)

#### 2.4 Extract Brand & Model
**Chotot**: Đã có sẵn cột `Hãng` và `Dòng xe`

**Bonbanh**: Extract từ title bằng regex
- Bỏ từ "Xe" ở đầu
- Tách brand từ danh sách 60+ hãng xe
- Loại bỏ các thành phần không phải model (transmission, drivetrain, engine)
- Phần còn lại là model

#### 2.5 Extract Engine → `engine`, `engine_missing`
- **Chotot**: Không có dữ liệu → engine=0, engine_missing=1
- **Bonbanh**: Extract từ cột "Động cơ" ("Xăng 2.0 L" → 2.0)
- **Loại**: Float (lít), Binary (missing indicator)

#### 2.6 Chuẩn Hóa Categorical Variables

| Variable         | Mapping                                                           | Result                   |
|------------------|-------------------------------------------------------------------|--------------------------|
| **transmission** | Tự động/Số tự động → AT<br>Số sàn/Số tay → MT<br>Bán tự động → AT | AT/MT                    |
| **fuel_type**    | Xăng/Dầu/Điện/Hybrid                                              | Xăng/Dầu/Điện/Hybrid     |
| **body_type**    | Giữ nguyên, chuẩn hóa sau                                         | SUV/Sedan/Hatchback/etc. |
| **origin**       | Việt Nam → Trong nước<br>Khác → Nhập khẩu                         | Trong nước/Nhập khẩu     |
| **condition**    | Đã sử dụng/Xe đã dùng → Cũ<br>Mới/Xe mới → Mới                    | Mới/Cũ                   |

#### 2.7 Parse Seats → `seats`
- Extract số từ chuỗi: "5 chỗ" → 5
- **Loại**: Float (số chỗ ngồi)

#### 2.8 Extract City → `city`
- Parse từ location để lấy tỉnh/thành phố
- Chuẩn hóa HCM, Hà Nội
- Fallback: "Khác" hoặc "unknow"

#### 2.9 Chuẩn hóa `seller_id`
- **Chotot**: Đã có sẵn (có ~3.8% missing)
- **Bonbanh**: Đã có sẵn (int64)
- **Xử lý**: Convert sang string, fill missing bằng "0"
- **Mục đích**: Dùng để phát hiện duplicates (cùng seller, cùng xe)
- **Lưu ý**: Sẽ bị xóa sau khi loại duplicates, không dùng cho modeling

#### 2.10 Merge Datasets
- Merge 2 datasets với 16 cột chuẩn hóa (bao gồm seller_id)
- Thêm cột `source` để trace nguồn gốc
- **Output**: `normalize_interim.csv` (14,928 rows)

#### 2.11 Create Early Features
- Tạo `age` = CURRENT_YEAR - year (2025 - year)
- Tạo `km_per_year` = km / age (với age > 0)
- **Mục đích**: Dùng cho việc loại bỏ duplicates và phát hiện outliers

#### 2.12 Loại Bỏ Duplicates
- **Phương pháp**: Dựa trên các cột: seller_id, brand, model, year, km, price_million, transmission, fuel_type, body_type, city
- **Giữ lại**: First occurrence của mỗi nhóm duplicate
- **Kết quả**: Giảm từ 14,928 → 14,585 rows (loại bỏ ~343 duplicates)

### Phase III: Xử Lý Outliers (outlier_interim.csv)

#### 3.1 Phương pháp
- Sử dụng IQR (Interquartile Range) kết hợp Domain Knowledge
- Không loại bỏ xe siêu sang có giá hợp lý

#### 3.2 Ngưỡng Outliers

| Biến              | Ngưỡng Thấp | Ngưỡng Cao      | Số lượng bị loại |
|-------------------|-------------|-----------------|------------------|
| **price_million** | 50 triệu    | Không giới hạn* | ~200 xe          |
| **km**            | 0 km        | 500,000 km      | ~100 xe          |
| **year**          | 1995        | 2025            | ~40 xe           |

*Loại bỏ thủ công 2 xe có giá bất thường (Ford Escape 40 tỷ, Acura ILX 50 tỷ)

#### 3.3 Kết quả
- **Trước**: 14,928 rows
- **Sau**: 14,585 rows
- **Loại bỏ**: 343 outliers (2.3%)

### Phase IV: Xử Lý Missing Values (fill_interim.csv)

#### 4.1 Missing Values trước xử lý

| Cột              | Missing | %       | Chiến lược                   |
|------------------|---------|---------|------------------------------|
| **origin**       | 1,021   | 7.00%   | Lookup từ brand              |
| **seats**        | 843     | 5.78%   | Lookup từ body_type          |
| **body_type**    | 736     | 5.05%   | Mode theo model              |
| **km**           | 229     | 1.57%   | Xe mới→0, xe cũ→median       |
| **transmission** | 16      | 0.11%   | Mode theo (brand, model)     |
| **year**         | 8       | 0.05%   | Median theo (brand, model)   |

#### 4.2 Chiến lược Imputation

**a) body_type**: Mode theo `model`
- Mỗi model thường chỉ có 1 kiểu thân xe phổ biến
- Fallback: "Kiểu dáng khác"

**b) seats**: Lookup từ `body_type`
```
SUV/MPV/Van → 7 chỗ
Sedan/Hatchback/Crossover → 5 chỗ
Coupe/Convertible → 4 chỗ
Pickup → 5 chỗ
```

**c) transmission**: Mode theo `(brand, model)`
- Fallback: AT (phổ biến hơn)

**d) origin**: Lookup từ `brand`
- Các hãng có nhà máy lắp ráp tại VN: Toyota, Honda, Mazda, Ford, Hyundai, Kia, Mitsubishi, Suzuki, Isuzu, Thaco, VinFast → "Trong nước"
- Còn lại → "Nhập khẩu"

**e) km**: Theo `condition`
- Xe "Mới" → 0 km
- Xe "Cũ" → median theo (brand, model, year)

**f) year**: Median theo `(brand, model)`

#### 4.3 Kết quả
- **Sau imputation**: 0% missing values
- **Dataset**: 14,585 rows × 15 cols (clean)

### Phase V: Feature Engineering (feature_interim.csv)

#### 5.1 Tạo Features Mới

**a) `age`**: Tuổi xe (năm)
```python
age = CURRENT_YEAR - year  # 2025 - year
```
- **Ý nghĩa**: Xe càng cũ thì giá càng giảm
- **Loại**: Integer (năm)

**b) `km_per_year`**: Số km trung bình mỗi năm
```python
km_per_year = km / age  # Xe mới (age=0) → 0
```
- **Ý nghĩa**: Mức độ sử dụng xe (km/năm cao → xe dùng nhiều)
- **Loại**: Float (km/năm)

**c) `is_luxury`**: Xe sang hay không
```python
LUXURY_BRANDS = ['Mercedes Benz', 'BMW', 'Lexus', 'Porsche', 
                 'Jaguar', 'Volvo', 'Bentley', 'Rolls Royce', 
                 'Maserati', 'Ferrari', 'Lamborghini', 'Genesis']
is_luxury = 1 if brand in LUXURY_BRANDS else 0
```
- **Ý nghĩa**: Xe sang thường có giá cao hơn
- **Loại**: Binary (0/1)
- **Phân bố**: ~18.7% xe sang trong dataset (2,723 xe)

**d) `usage`**: Mức độ sử dụng xe dựa trên km_per_year
```python
def classify_usage(km_per_year):
    if km_per_year < 10000:
        return 'low'
    elif km_per_year <= 20000:
        return 'medium'
    else:
        return 'high'

usage = df['km_per_year'].apply(classify_usage)
```
- **Ý nghĩa**: Phân loại mức độ sử dụng xe theo số km trung bình mỗi năm
- **Loại**: Categorical (low/medium/high)
- **Phân bố**: 
  - Low (<10,000 km/năm): 53.8% (7,067 xe)
  - Medium (10,000-20,000 km/năm): 36.0% (5,193 xe)
  - High (>20,000 km/năm): 10.1% (1,463 xe)

#### 5.2 Xóa Features Cũ
- Xóa cột `year` (thay bằng `age`) để tránh đa cộng tuyến
- Xóa cột `seller_id` (chỉ dùng để phát hiện duplicates, không có giá trị dự đoán)

### Phase VI: Encoding (encoding_interim.csv)

#### 6.1 One-Hot Encoding

**a) `transmission` → `transmission_binary`**
- AT (Tự động) → 1
- MT (Số sàn) → 0

**b) `usage` → `usage_*` (3 features)**
- `usage_low`: Sử dụng ít (<10,000 km/năm)
- `usage_medium`: Sử dụng trung bình (10,000-20,000 km/năm)
- `usage_high`: Sử dụng nhiều (>20,000 km/năm)

**c) `fuel_type` → `fuel_*` (4 features)**
- `fuel_gasoline`: Xăng
- `fuel_diesel`: Dầu
- `fuel_electric`: Điện
- `fuel_hybrid`: Hybrid

**d) `origin` → `inland_binary`**
- Trong nước → 1
- Nhập khẩu → 0

**e) `condition` → `new_binary`**
- Mới → 1
- Cũ → 0

**f) `source` → `bobanh_binary`**
- Bonbanh → 1
- Chotot → 0

**g) `body_type` → `body_type_*` (10 features)**
Chuẩn hóa trước khi one-hot:
```
SUV/Crossover → suv
Sedan → sedan
Hatchback → hatchback
Van/Minivan → minivan
Pickup → pickup
Coupe → coupe
Convertible/Mui trần → convertible
Truck → truck
Wagon → wagon
Khác → other
```

Features: `body_type_convertible`, `body_type_coupe`, `body_type_hatchback`, `body_type_minivan`, `body_type_other`, `body_type_pickup`, `body_type_sedan`, `body_type_suv`, `body_type_truck`, `body_type_wagon`

#### 6.2 Group Rare Values + One-Hot

**h) `city` → `city_*` (19 features)**
- **Threshold**: 0.5% (≥73 mẫu)
- **Phương pháp**: Gom các tỉnh/thành có tần suất < 0.5% vào "other"
- **Features**: 
  - Top cities: `city_ho_chi_minh`, `city_ha_noi`, `city_binh_duong`, `city_dong_nai`, `city_da_nang`, `city_hai_phong`, `city_can_tho`, `city_ba_ria`, `city_lam_dong`, `city_thanh_hoa`, `city_bac_ninh`, `city_dak_lak`, `city_gia_lai`, `city_phu_tho`, `city_vinh_phuc`
  - Special: `city_khac`, `city_unknow`, `city_other` (nhóm rare)

**i) `brand` → `brand_*` (24 features)**
- **Threshold**: 0.5% (≥73 mẫu)
- **Phương pháp**: Gom các hãng có tần suất < 0.5% vào "other"
- **Features**:
  - Popular brands: `brand_toyota`, `brand_honda`, `brand_mazda`, `brand_ford`, `brand_hyundai`, `brand_kia`, `brand_mitsubishi`, `brand_nissan`, `brand_suzuki`, `brand_vinfast`, `brand_mercedes_benz`, `brand_bmw`, `brand_lexus`, `brand_audi`, `brand_porsche`, `brand_volvo`, `brand_volkswagen`, `brand_chevrolet`, `brand_peugeot`, `brand_landrover`, `brand_mg`, `brand_isuzu`, `brand_daewoo`
  - Rare: `brand_other`

#### 6.3 Target Encoding

**`model` → `model_encoded`**
- **Phương pháp**: K-Fold Target Encoding (5 folds)
- **Công thức**: 
  ```
  smoothing_factor = 1 / (1 + exp(-(count - min_samples_leaf) / smoothing))
  model_encoded = global_mean × (1 - smoothing_factor) + category_mean × smoothing_factor
  ```
- **Tham số**:
  - `n_splits=5`: 5 folds để tránh data leakage
  - `min_samples_leaf=1`: Minimum samples cho smoothing
  - `smoothing=1`: Hệ số smoothing
  - Fallback: Global mean của `price_million`
- **Ý nghĩa**: Encode model bằng giá trung bình của model đó (với smoothing)
- **Lý do**: Model có 600+ unique values → One-hot không khả thi

### Phase VII: Finalization (car_features.csv)

#### 7.1 Xóa Cột Không Cần Thiết
Xóa các cột đã được encode:
- `brand`, `model`, `transmission`, `fuel_type`, `body_type`, `origin`, `condition`, `city`, `source`
- `bobanh_binary` (thông tin nguồn gốc, không cần cho prediction)

#### 7.2 Chuyển Đổi Kiểu Dữ Liệu
Chuyển các cột sang `int64`:
- `age`, `km`, `seats`, `price_million`

#### 7.3 Dataset Cuối Cùng
- **Số mẫu**: 14,585 xe (sau loại bỏ duplicates và outliers)
- **Số features**: 71 (70 features + 1 target)
- **Kiểu dữ liệu**: 
  - Integer: 67 features (binary và one-hot encoded)
  - Float: 4 features (engine, km_per_year, model_encoded, price_million)
- **Missing values**: 0%

---

## 📋 Mô Tả Chi Tiết Features

### 🎯 Target Variable

| Feature | Type | Description | Range | Mean |
|---------|------|-------------|-------|------|
| `price_million` | int64 | Giá xe (triệu VNĐ) | 50 - ~15,000 | ~700-800 |

### 🔢 Numerical Features (6)

| Feature | Type | Description | Range | Notes |
|---------|------|-------------|-------|-------|
| `km` | int64 | Số km đã đi | 0 - 500,000 | Xe mới = 0 |
| `seats` | int64 | Số chỗ ngồi | 2 - 16 | Phổ biến: 4, 5, 7 |
| `engine` | float64 | Dung tích động cơ (lít) | 0 - 6.0 | 0 = missing |
| `age` | int64 | Tuổi xe (năm) | 0 - 30 | 2025 - year |
| `km_per_year` | float64 | Km trung bình/năm | 0 - 100,000 | km / age |
| `model_encoded` | float64 | Target encoding của model | ~300 - ~3,000 | Giá trung bình |

### 🔘 Binary Features (6)

| Feature | Type | Description | Values | Notes |
|---------|------|-------------|--------|-------|
| `engine_missing` | int64 | Có missing engine không | 0 (có) / 1 (missing) | Chotot = 1 |
| `is_luxury` | int64 | Xe sang hay không | 0 (thường) / 1 (sang) | ~10% xe sang |
| `transmission_binary` | int64 | Loại hộp số | 0 (MT) / 1 (AT) | ~70% AT |
| `inland_binary` | int64 | Xuất xứ | 0 (NK) / 1 (TN) | ~60% trong nước |
| `new_binary` | int64 | Tình trạng | 0 (Cũ) / 1 (Mới) | ~15% xe mới |

### 🏷️ One-Hot Encoded Features (56)

#### Fuel Type (4 features)
- `fuel_gasoline`: Xăng (~70%)
- `fuel_diesel`: Dầu (~20%)
- `fuel_electric`: Điện (~3%)
- `fuel_hybrid`: Hybrid (~7%)

#### Body Type (10 features)
- `body_type_suv`: SUV/Crossover (~35%)
- `body_type_sedan`: Sedan (~30%)
- `body_type_hatchback`: Hatchback (~15%)
- `body_type_minivan`: MPV/Minivan (~10%)
- `body_type_pickup`: Pickup (~5%)
- `body_type_coupe`: Coupe (~2%)
- `body_type_convertible`: Convertible (~1%)
- `body_type_wagon`: Wagon (~1%)
- `body_type_truck`: Truck (<1%)
- `body_type_other`: Khác (~1%)

#### City (19 features)
**Top cities:**
- `city_ho_chi_minh`: TP HCM (~40%)
- `city_ha_noi`: Hà Nội (~25%)
- `city_binh_duong`: Bình Dương (~5%)
- `city_dong_nai`: Đồng Nai (~4%)
- `city_da_nang`: Đà Nẵng (~3%)
- `city_hai_phong`: Hải Phòng (~2%)
- `city_can_tho`: Cần Thơ (~1.5%)

**Medium cities:**
- `city_ba_ria`, `city_lam_dong`, `city_thanh_hoa`, `city_bac_ninh`, `city_dak_lak`, `city_gia_lai`, `city_phu_tho`, `city_vinh_phuc` (~0.5-1% mỗi city)

**Special:**
- `city_khac`: Khác
- `city_unknow`: Không xác định
- `city_other`: Nhóm các tỉnh rare (<0.5%)

#### Brand (24 features)
**Japanese brands (~50%):**
- `brand_toyota`: Toyota (~18%)
- `brand_honda`: Honda (~12%)
- `brand_mazda`: Mazda (~8%)
- `brand_mitsubishi`: Mitsubishi (~5%)
- `brand_nissan`: Nissan (~3%)
- `brand_suzuki`: Suzuki (~2%)
- `brand_isuzu`: Isuzu (~1%)

**Korean brands (~20%):**
- `brand_hyundai`: Hyundai (~10%)
- `brand_kia`: Kia (~8%)

**European luxury brands (~15%):**
- `brand_mercedes_benz`: Mercedes-Benz (~5%)
- `brand_bmw`: BMW (~4%)
- `brand_audi`: Audi (~2%)
- `brand_lexus`: Lexus (~1.5%)
- `brand_porsche`: Porsche (~1%)
- `brand_volvo`: Volvo (~0.8%)
- `brand_volkswagen`: Volkswagen (~0.7%)
- `brand_landrover`: Land Rover (~0.5%)

**American brands (~5%):**
- `brand_ford`: Ford (~3%)
- `brand_chevrolet`: Chevrolet (~2%)

**Vietnamese brand (~3%):**
- `brand_vinfast`: VinFast (~3%)

**Other brands:**
- `brand_peugeot`: Peugeot (~1%)
- `brand_mg`: MG (~0.8%)
- `brand_daewoo`: Daewoo (~0.5%)
- `brand_other`: Nhóm hãng rare (<0.5%)

---

## 📊 Thống Kê Mô Tả

### Numerical Features Statistics

| Feature         | Min | Q1     | Median  | Q3       | Max       | Mean     | Std     |
|-----------------|-----|--------|---------|----------|-----------|----------|---------|
| `price_million` | 50  | 380    | 580     | 950      | ~15,000   | ~750     | ~600    |
| `km`            | 0   | 15,000 | 35,000  | 70,000   | 500,000   | ~45,000  | ~40,000 |
| `seats`         | 2   | 5      | 5       | 7        | 16        | 5.5      | 1.2     |
| `engine`        | 0   | 0      | 1.5     | 2.0      | 6.0       | 1.2      | 1.0     |
| `age`           | 0   | 3      | 6       | 10       | 30        | 7        | 5       |
| `km_per_year`   | 0   | 3,000  | 6,000   | 12,000   | ~80,000   | ~8,000   | ~7,000  |

### Categorical Features Distribution

**Transmission:**
- AT (Automatic): ~70%
- MT (Manual): ~30%

**Fuel Type:**
- Gasoline: ~70%
- Diesel: ~20%
- Hybrid: ~7%
- Electric: ~3%

**Origin:**
- Trong nước: ~60%
- Nhập khẩu: ~40%

**Condition:**
- Cũ: ~85%
- Mới: ~15%

**Body Type:**
- SUV/Crossover: ~35%
- Sedan: ~30%
- Hatchback: ~15%
- Minivan: ~10%
- Pickup: ~5%
- Others: ~5%

**Luxury:**
- Non-luxury: ~90%
- Luxury: ~10%

---

## 🎯 Mục Đích Sử Dụng

Dataset này được thiết kế để:

1. **Dự đoán giá xe** (Regression)
   - Target: `price_million`
   - Features: 67 features đã được xử lý và encode

2. **Phân tích thị trường ô tô Việt Nam**
   - Xu hướng giá theo hãng, model, năm sản xuất
   - Phân bố địa lý của thị trường xe
   - So sánh xe nhập khẩu vs trong nước

3. **Research & Education**
   - Học tập về data preprocessing pipeline
   - Thực hành feature engineering
   - So sánh các phương pháp encoding

---

## ⚠️ Lưu Ý Quan Trọng

### 1. Data Quality
- ✅ **Không có missing values** sau xử lý
- ✅ **Không có outliers bất thường** sau lọc
- ✅ **Chuẩn hóa đồng nhất** giữa 2 nguồn dữ liệu
- ⚠️ **Engine missing** cho ~30% samples (Chotot không có dữ liệu)

### 2. Feature Engineering
- ✅ **Tránh data leakage**: Target encoding dùng K-Fold
- ✅ **Tránh multicollinearity**: Xóa `year` (đã có `age`)
- ✅ **Domain knowledge**: Imputation dựa trên kiến thức thực tế
- ⚠️ **Imbalanced**: Xe sang chỉ ~10%, một số hãng rare <1%

### 3. Encoding Strategy
- **One-hot**: Cho features có ít categories (<20)
- **Group + One-hot**: Cho features có nhiều categories nhưng có thể gom nhóm (city, brand)
- **Target encoding**: Cho features có quá nhiều categories (model: 600+)

### 4. Sử Dụng Dataset
```python
import pandas as pd

# Load dataset
df = pd.read_csv('data/processed/car_features.csv')

# Split features and target
X = df.drop('price_million', axis=1)
y = df['price_million']

# Train-test split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

### 5. Potential Issues
- **Highly skewed target**: Giá xe phân phối lệch phải → Có thể cần log transform
- **Rare categories**: Một số brand/city rất ít mẫu → Đã gom vào "other"
- **Missing engine**: 30% samples thiếu dữ liệu engine → Đã dùng indicator variable

---

## 📚 Tài Liệu Tham Khảo

- **Notebook xử lý**: `notebooks/01_data_preprocessing.ipynb`
- **Raw data**: `data/raw/raw_chotot_car_features.csv`, `data/raw/raw_bonbanh_car_features.csv`
- **Interim data**: `data/interim/` (5 files theo từng phase)
- **Final data**: `data/processed/car_features.csv`
