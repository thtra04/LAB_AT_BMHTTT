# LAB 3 – Nhận diện và ứng phó các mối đe dọa đến an toàn thông tin (Identifying and Responding to Information Security Threats)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | Thực hành An toàn Bảo mật Hệ thống thông tin – Năm học 2026–2027 |
| Giảng viên biên soạn | Phạm Trọng Huynh – Bộ môn An toàn Thông tin |
| Repository | https://github.com/thtra04/LAB_AT_BMHTTT |
| Link video YouTube | *(dán link video quay quá trình thực hiện nếu lớp yêu cầu)* |
| Đề bài | [LAB3_CacMoiDeDoa_ATTT_2026.pdf](LAB3_CacMoiDeDoa_ATTT_2026.pdf) |

## 2. Tên bài Lab

**Lab 3: Nhận diện và ứng phó các mối đe dọa đến an toàn thông tin** – Thực hành An toàn Hệ thống thông tin.

### Mục tiêu
- Phân biệt đúng bốn khái niệm: **lỗ hổng (Vulnerability)**, **mối đe dọa (Threat)**, **rủi ro (Risk)** và **tấn công (Attack)**, liên hệ chúng với tài sản cụ thể trên một máy trạm Windows.
- Nhận diện **năm nhóm nguồn đe dọa**: hành động vô ý, hành động cố ý, thảm họa tự nhiên, lỗi kỹ thuật và lỗi quản lý.
- Quan sát và thu thập bằng chứng cho các nhóm kỹ thuật: mã độc, tấn công mật khẩu, keylogging, backdoor/persistence, DoS/DDoS, mail bombing, sniffing, man-in-the-middle, spoofing và social engineering/phishing.
- Sử dụng **Microsoft Defender, Windows Event Log, Sysmon, Autoruns, Process Explorer và Wireshark** để thu thập bằng chứng từ endpoint và mạng.
- Thực hiện quy trình **Baseline → Observe → Detect → Contain → Recover → Verify** bằng dữ liệu thử nghiệm thuộc phạm vi bài LAB.
- Tạo báo cáo có thể tái lập: ghi rõ phiên bản, lệnh đã chạy, kết quả quan sát, ảnh chụp trực tiếp từ VM/PC, log và SHA-256 của bằng chứng.

## 3. Kiến thức nền

### 3.1. Bốn khái niệm cốt lõi

| Khái niệm | Định nghĩa dùng trong bài lab |
|---|---|
| Lỗ hổng (Vulnerability) | Điểm yếu của tổ chức, hệ thống CNTT hoặc mạng có thể bị một mối đe dọa khai thác. |
| Mối đe dọa (Threat) | Yếu tố hoặc sự kiện có khả năng gây thiệt hại cho tổ chức, hệ thống CNTT hoặc mạng. |
| Rủi ro (Risk) | Khả năng mối đe dọa khai thác lỗ hổng của tài sản và gây ra tổn thất. |
| Tấn công (Attack) | Hành động khai thác một điểm yếu đã xác định nhằm gây thiệt hại hoặc đánh cắp thông tin. |

### 3.2. Năm nhóm nguồn đe dọa cần phân loại
1. Hành động vô ý
2. Hành động cố ý
3. Thảm họa tự nhiên
4. Lỗi kỹ thuật (phần cứng/phần mềm)
5. Lỗi quản lý

Bài thực hành không cố gắng "tạo" mọi loại sự cố; sinh viên thu thập bằng chứng ở những tình huống có thể tái lập an toàn và dùng **risk register** để phân loại các trường hợp còn lại.

## 4. Kịch bản

Một máy trạm **Windows 11** thuộc mạng đào tạo xuất hiện nhiều dấu hiệu cần đánh giá:
- cảnh báo của endpoint protection;
- các lần đăng nhập thất bại;
- một mục tự khởi động không được phê duyệt;
- một tiến trình lắng nghe cổng cục bộ;
- lưu lượng HTTP có dữ liệu đọc được và lưu lượng HTTPS được mã hóa;
- một thông điệp có dấu hiệu lừa đảo.

Sinh viên đóng vai nhân sự An toàn và Bảo mật HTTT: thực hiện **triage, thu thập bằng chứng, phân loại mối đe dọa, đánh giá rủi ro và khôi phục** máy trạm về trạng thái chấp nhận được. Mục tiêu là làm rõ mối quan hệ giữa khái niệm trong bài học và dấu vết quan sát được trên hệ thống, **không** khai thác máy bên ngoài hoặc né cơ chế bảo vệ.

## 5. Môi trường và phiên bản chuẩn hóa

| Thành phần | Phiên bản / cấu hình | Vai trò |
|---|---|---|
| Ảo hóa | VMware Workstation Pro 26H1 | Dùng snapshot; mạng **Host-only** là mặc định |
| Máy ảo | Windows 11 25H2 x64, OS build 26200.9445 (KB5124008) | Pro/Education/Enterprise; cập nhật bảo mật tháng 09/2026 |
| Endpoint protection | Microsoft Defender Antivirus tích hợp Windows 11 | Real-time protection và Tamper Protection **giữ bật** |
| Shell | Windows PowerShell 5.1 | Run as administrator cho các bước cần quyền quản trị |
| Sysmon | 15.22 (schema cấu hình 4.90) | Microsoft Sysinternals |
| Autoruns | 14.3 | Microsoft Sysinternals |
| Process Explorer | 17.14 | Microsoft Sysinternals |
| Wireshark | 4.6.8 Stable + Npcap | Loopback capture và NIC của VM |
| Python | 3.14.7 | Chỉ dùng làm HTTP server cục bộ và tải thử giới hạn trên 127.0.0.1 |
| Gói dữ liệu bài lab | `LAB3_Threats_Assets.zip` | SHA-256: `96236f95ce59d0cc37f9b7ab8fbb04522f21870cd0b53aad6e52da5a23655439` |

Phiên bản thực tế trên máy sinh viên: *(điền sau khi chạy lệnh kiểm tra version ở Bước 5 mục 6)*

## 6. Cách dựng môi trường

### Bước 1. Tạo VM Windows 11 25H2 x64
- Tối thiểu 2 vCPU, 6 GB RAM, 64 GB đĩa.
- VMware Workstation Pro 26H1: **VM > Settings > Network Adapter > Host-only**.
- Cài Windows, cập nhật KB5124008, tạo snapshot tên `LAB3_CLEAN_20260914`.
- Ảnh H1: cửa sổ VMware hiển thị VM với Network Adapter = Host-only và `winver` xác nhận Windows 11 25H2 build 26200.9445 → `H1_VM_WindowsVersion.png`.

### Bước 2. Tạo cấu trúc thư mục bài lab (PowerShell – Administrator)
```powershell
$Lab = 'C:\LAB3'
New-Item -ItemType Directory -Force `
  "$Lab\Evidence", "$Lab\Tools", "$Lab\Downloads", "$Lab\Assets" | Out-Null
Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz' | Out-File "$Lab\Evidence\start_time.txt"
```

### Bước 3. Kiểm tra hash và giải nén gói dữ liệu
Sao chép `LAB3_Threats_Assets.zip` do giảng viên cung cấp vào `C:\LAB3\Downloads`, kiểm tra hash **trước** khi giải nén (phải trùng manifest của bài).
```powershell
Get-FileHash C:\LAB3\Downloads\LAB3_Threats_Assets.zip -Algorithm SHA256
Expand-Archive C:\LAB3\Downloads\LAB3_Threats_Assets.zip -DestinationPath C:\LAB3 -Force
```

### Bước 4. Cài Python 3.14.7 và Wireshark 4.6.8
Nếu phòng máy đã có đúng phiên bản thì không cài lại. Khi trình cài Wireshark hỏi Npcap, **giữ Npcap**.
```powershell
winget install --id Python.Python.3.14 --exact --version 3.14.7 `
  --accept-package-agreements --accept-source-agreements
winget install --id WiresharkFoundation.Wireshark --exact --version 4.6.8 `
  --accept-package-agreements --accept-source-agreements
python --version
& 'C:\Program Files\Wireshark\tshark.exe' --version | Select-Object -First 1
```

### Bước 5. Tải bộ Sysinternals từ máy chủ Microsoft
Chỉ dùng ba URL `download.sysinternals.com` bên dưới; **không** dùng mirror hoặc executable do người khác chia sẻ.
```powershell
$D='C:\LAB3\Downloads'; $T='C:\LAB3\Tools'
Invoke-WebRequest 'https://download.sysinternals.com/files/Sysmon.zip' -OutFile "$D\Sysmon.zip"
Invoke-WebRequest 'https://download.sysinternals.com/files/Autoruns.zip' -OutFile "$D\Autoruns.zip"
Invoke-WebRequest 'https://download.sysinternals.com/files/ProcessExplorer.zip' -OutFile "$D\ProcessExplorer.zip"
Expand-Archive "$D\Sysmon.zip" -DestinationPath "$T\Sysmon" -Force
Expand-Archive "$D\Autoruns.zip" -DestinationPath "$T\Autoruns" -Force
Expand-Archive "$D\ProcessExplorer.zip" -DestinationPath "$T\ProcessExplorer" -Force
(Get-Item "$T\Sysmon\Sysmon64.exe").VersionInfo | Select FileVersion,ProductVersion
(Get-Item "$T\Autoruns\Autoruns64.exe").VersionInfo | Select FileVersion,ProductVersion
(Get-Item "$T\ProcessExplorer\procexp64.exe").VersionInfo | Select FileVersion,ProductVersion
```
- Ảnh H2: cửa sổ PowerShell hiển thị Python 3.14.7, Wireshark 4.6.8, Sysmon 15.22, Autoruns 14.3, Process Explorer 17.14 → `H2_ToolVersions.png`.
- Nếu một version khác xuất hiện: **dừng và báo giảng viên** trước khi thực hành.

## 7. Quy ước bằng chứng (bắt buộc tuân thủ)

- Mọi ảnh giao diện trong báo cáo phải là **ảnh chụp trực tiếp từ VM/PC của sinh viên** sau khi thực hiện bước tương ứng. Các khung "VỊ TRÍ HÌNH" trong đề chỉ là chỉ dẫn vị trí, không phải ảnh minh họa.
- Mọi lệnh phải chạy trong shell được nêu ở bước hướng dẫn; lưu output bằng `Tee-Object`/`Out-File` hoặc ảnh chụp cửa sổ lệnh.
- **Không** nhập tài khoản thật, mật khẩu thật, token, cookie/session, email cá nhân hoặc dữ liệu riêng tư vào VM.
- Defender/Tamper Protection **giữ bật**; không tạo exclusion, không phục hồi tệp bị quarantine chỉ để tiếp tục kịch bản.
- Traffic gây tải chỉ được tạo bởi script đi kèm, hard-code `127.0.0.1:8080`. Không sửa script để chỉ tới IP/hostname/dịch vụ khác.

## 8. Nội dung đã thực hiện

Bảng ánh xạ nội dung bài học ↔ tình huống thực hành:

| Nội dung bài học | Tình huống | Bằng chứng / chức năng chính |
|---|---|---|
| Vulnerability – Threat – Risk – Attack | TH1 | Risk register: phân loại tài sản, điểm yếu, mối đe dọa, rủi ro |
| Hành động vô ý/cố ý; thảm họa; lỗi kỹ thuật; lỗi quản lý | TH1 | Phân loại 5 nguồn đe dọa bằng tình huống |
| Malware | TH2 | EICAR + Defender detection/quarantine |
| Password: brute force, dictionary, keylogger | TH3 | Event 4624/4625/4648, password rotation, phân tích keylogging |
| Backdoor | TH4 | Persistence lành tính + dịch vụ lắng nghe loopback; Autoruns/Sysmon/Process Explorer |
| Sniffing / MITM / Spoofing | TH5 | Capture HTTP loopback, so sánh TLS; phân tích các biến thể MITM |
| DoS / DDoS | TH6 | Tải cục bộ giới hạn + dataset TEST-NET |
| Mail bombing | TH6 | Phân tích log email offline, không gửi thư |
| Social Engineering / Phishing / Spear phishing | TH7 | Phân tích mẫu offline và phân loại tình huống |

### 8.0. Baseline trước khi tạo tình huống
Baseline là trạng thái tham chiếu để phân biệt thay đổi do bài lab với trạng thái đã tồn tại. Chạy **trước** khi tạo EICAR, tài khoản thử nghiệm, persistence hoặc HTTP server.
```powershell
$E='C:\LAB3\Evidence'
Get-ComputerInfo | Select WindowsProductName,WindowsVersion,OsBuildNumber,OsArchitecture |
  Format-List | Tee-Object "$E\baseline_os.txt"
Get-MpComputerStatus | Select AntivirusEnabled,RealTimeProtectionEnabled,IsTamperProtected,AntivirusSignatureVersion |
  Format-List | Tee-Object "$E\baseline_defender.txt"
Get-NetFirewallProfile | Select Name,Enabled,DefaultInboundAction,DefaultOutboundAction |
  Format-Table -Auto | Tee-Object "$E\baseline_firewall.txt"
Get-NetIPConfiguration | Format-List | Out-File "$E\baseline_network.txt" -Width 220
Get-Process | Sort ProcessName | Select ProcessName,Id,Path | Out-File "$E\baseline_processes.txt" -Width 220
```
- [ ] Ảnh H3: output `Get-MpComputerStatus` có `RealTimeProtectionEnabled = True` và trạng thái firewall → `H3_Baseline_Defender_Firewall.png`.

### 8.1. Tình huống 1 – Xác định tài sản, lỗ hổng, mối đe dọa và rủi ro
Lập **risk register** trước khi thao tác kỹ thuật. Mỗi hàng gắn với một tài sản của chính VM lab theo quan hệ **Asset → Vulnerability → Threat → Risk → Control**.

| Tài sản | Lỗ hổng | Mối đe dọa | Rủi ro | Biện pháp |
|---|---|---|---|---|
| Thông tin xác thực tài khoản lab | Mật khẩu ngắn hoặc bị nhập vào phần mềm không tin cậy | Dò mật khẩu / keylogging / phishing | Mất quyền truy cập hoặc chiếm tài khoản | Mật khẩu dài, MFA ở hệ thống hỗ trợ, endpoint protection, audit log |
| Dữ liệu trong `C:\LAB3` | Thiếu backup / kiểm soát thay đổi | Xóa nhầm, mã độc, lỗi đĩa | Mất hoặc thay đổi dữ liệu | Backup, least privilege, hash, logging |
| Dịch vụ nghiệp vụ giả lập | Cổng lắng nghe ngoài dự kiến, thiếu giám sát | Backdoor / DoS | Gián đoạn hoặc truy cập trái phép | Firewall, process/network monitoring, allow-list |
| Email / người dùng | Thiếu xác minh domain / người gửi | Phishing / Spear phishing | Lộ thông tin xác thực | Awareness, email filtering, MFA, verify out-of-band |
| *(bổ sung tối thiểu thêm 1 tài sản, ví dụ: cấu hình Sysmon/Defender, snapshot VM…)* | | | | |

**Bài tập phân loại nguồn đe dọa** (điền một trong 5 nhóm và giải thích ngắn):

| ID | Tình huống cần phân loại | Nhóm | Giải thích |
|---|---|---|---|
| 1 | Nhân viên xóa nhầm tệp cấu hình đang dùng | Hành động vô ý | Người dùng hợp lệ gây thiệt hại nhưng không có chủ đích |
| 2 | Người có ác ý cài phần mềm thu thập dữ liệu | Hành động cố ý | Có chủ đích gây hại/đánh cắp thông tin |
| 3 | Mất điện kéo dài làm dịch vụ dừng và file chưa ghi bị mất | Thảm họa tự nhiên | Sự kiện môi trường bên ngoài, không do con người hay hệ thống |
| 4 | Ổ đĩa hỏng hoặc dịch vụ treo do lỗi phần mềm | Lỗi kỹ thuật | Lỗi phần cứng/phần mềm của chính hệ thống |
| 5 | Tổ chức không áp dụng chính sách backup/patching dù đã có yêu cầu | Lỗi quản lý | Thiếu sót trong quy trình, chính sách, kiểm soát của tổ chức |

**Điều kiện đạt TH1:** risk register có tối thiểu 5 tài sản/nguy cơ; 5 tình huống được phân loại kèm giải thích dựa trên định nghĩa trong bài học.

### 8.2. Tình huống 2 – Mã độc: kiểm chứng chu trình phát hiện bằng EICAR
EICAR là chuỗi kiểm thử an toàn được các sản phẩm chống mã độc nhận biết. Tình huống này chỉ kiểm tra detection/quarantine, **không** chứng minh VM có malware thật.

- [ ] Bước 1. Xác minh Defender đang bảo vệ theo thời gian thực:
```powershell
Get-MpComputerStatus | Select AntivirusEnabled,RealTimeProtectionEnabled,IsTamperProtected
```
- [ ] Bước 2. Tạo tệp EICAR trong `Evidence`. Defender có thể chặn ngay khi `Set-Content` ghi tệp – đó là kết quả mong đợi:
```powershell
$eicar='X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
try {
  Set-Content -Path C:\LAB3\Evidence\eicar.com.txt -Value $eicar -NoNewline -Encoding Ascii
} catch {
  $_ | Out-File C:\LAB3\Evidence\eicar_write_error.txt
}
Start-Sleep -Seconds 5
Get-MpThreatDetection | Sort InitialDetectionTime -Descending | Select -First 5 `
  ThreatID,InitialDetectionTime,Resources,ActionSuccess |
  Format-List | Tee-Object C:\LAB3\Evidence\defender_eicar.txt
```
- [ ] Bước 3. Mở **Windows Security > Virus & threat protection > Protection history**, mở thẻ detection EICAR, ghi thời gian, tên detection, resource, action. **Không** chọn *Allow on device*.
- [ ] Ảnh H4: Protection history hiển thị detection EICAR (có thời gian/detection/action đối chiếu với output PowerShell) → `H4_ProtectionHistory_EICAR.png`.

**PASS TH2:** `RealTimeProtectionEnabled = True`; có detection EICAR trong Protection history hoặc `Get-MpThreatDetection`; không tắt bảo vệ, không tạo exclusion.

### 8.3. Tình huống 3 – Tấn công mật khẩu và nguy cơ keylogging
Bài học phân biệt brute force, dictionary attack và key logger. Trong lab **không** chạy phần mềm dò mật khẩu hay keylogger; thay vào đó tạo tài khoản cục bộ riêng, sinh sự kiện đăng nhập hợp lệ/không hợp lệ, đổi credential và dùng log để chứng minh phục hồi.

- [ ] Bước 1. Bật Audit Logon success/failure và tạo tài khoản `lab3user` (PowerShell – Administrator):
```powershell
auditpol /set /subcategory:{0CCE9215-69AE-11D9-BED3-505054503030} /success:enable /failure:enable
$pw = Read-Host 'Nhap mat khau chi dung cho LAB3' -AsSecureString
New-LocalUser -Name 'lab3user' -Password $pw -FullName 'LAB3 Test User' `
  -Description 'Temporary account for authentication logging lab'
Get-LocalUser -Name 'lab3user'
```
- [ ] Bước 2. Sinh lần đăng nhập **thành công**: chạy `runas /user:.\lab3user cmd.exe`, nhập đúng mật khẩu, trong cửa sổ mới chạy `whoami` rồi đóng.
- [ ] Bước 3. Sinh **hai** lần đăng nhập **thất bại** có kiểm soát: chạy lại `runas` hai lần và cố ý nhập sai mật khẩu. Không tự động hóa số lần thử.
- [ ] Bước 4. Thu Security log 20 phút gần nhất (Event ID 4624/4625/4648):
```powershell
$start=(Get-Date).AddMinutes(-20)
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625,4648; StartTime=$start} |
  Where-Object { $_.Message -match 'lab3user' } |
  Select TimeCreated,Id,Message |
  Out-File C:\LAB3\Evidence\auth_events_before_rotation.txt -Width 260
```
- [ ] Bước 5. Kiểm tra bằng Event Viewer: `Win+R > eventvwr.msc > Windows Logs > Security > Filter Current Log...` nhập `4624,4625,4648`, đối chiếu timestamp các event có `lab3user`.
- [ ] Ảnh H5: Event Viewer Security log với một Event ID 4625 liên quan `lab3user` (phần General thấy account và thời gian) → `H5_Event4625.png`.
- [ ] Bước 6. Đổi mật khẩu `lab3user` và kiểm chứng: `runas` với mật khẩu cũ **phải thất bại**, mật khẩu mới **phải thành công**:
```powershell
$newPw = Read-Host 'Nhap mat khau LAB3 sau khi doi' -AsSecureString
Set-LocalUser -Name 'lab3user' -Password $newPw
runas /user:.\lab3user cmd.exe
```
- [ ] Phân tích keylogging: giải thích vì sao độ dài/độ phức tạp mật khẩu không ngăn được việc mật khẩu bị thu trực tiếp khi gõ; vai trò của endpoint protection, kiểm soát phần mềm, MFA/passkey, phishing resistance và credential rotation.

**PASS TH3:** có bằng chứng 4624/4648 cho credential hợp lệ, 4625 cho lần nhập sai; sau khi đổi mật khẩu thì credential cũ không còn dùng được.

### 8.4. Tình huống 4 – Backdoor: nhận diện persistence và dịch vụ lắng nghe không được phê duyệt
Lab **không** cài backdoor. Sinh viên tạo hai artefact lành tính tên `LAB3_*` và một HTTP listener chỉ bind `127.0.0.1` để học cách phát hiện bằng nhiều nguồn telemetry.

#### 8.4.1. Cài Sysmon và thu baseline Autoruns (PowerShell – Administrator)
```powershell
C:\LAB3\Tools\Sysmon\Sysmon64.exe -accepteula -i C:\LAB3\lab3_assets\sysmon-lab.xml
C:\LAB3\Tools\Sysmon\Sysmon64.exe -c
C:\LAB3\Tools\Autoruns\autorunsc64.exe -a * -c -h -s > C:\LAB3\Evidence\autoruns_before.csv
```
- [ ] Bước 1. Event Viewer: `Applications and Services Logs > Microsoft > Windows > Sysmon > Operational`. Mở Notepad rồi refresh; phải thấy **Event ID 1** (Process Create).
- [ ] Ảnh H6: Event Viewer tại `Microsoft-Windows-Sysmon/Operational` với một Event ID 1 → `H6_Sysmon_Event1.png`.

#### 8.4.2. Tạo persistence lành tính và kiểm tra sau logon
```powershell
$run='HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
New-ItemProperty -Path $run -Name 'LAB3_Run_Demo' -PropertyType String -Value 'notepad.exe' -Force | Out-Null
$action=New-ScheduledTaskAction -Execute 'cmd.exe' `
  -Argument '/c echo LAB3_TASK_OK>>C:\LAB3\Evidence\task_ran.txt'
$trigger=New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
Register-ScheduledTask -TaskName 'LAB3_Persistence_Demo' -Action $action -Trigger $trigger `
  -Description 'Benign LAB3 persistence demonstration' -Force | Out-Null
Get-ItemProperty $run -Name LAB3_Run_Demo
Get-ScheduledTask -TaskName LAB3_Persistence_Demo
```
- [ ] Lưu công việc, **restart VM**, đăng nhập đúng tài khoản đã tạo task. Sau logon: xác minh Notepad tự mở hoặc Run value còn tồn tại; `C:\LAB3\Evidence\task_ran.txt` có chuỗi `LAB3_TASK_OK`.
- [ ] Bước 2. Mở `Autoruns64.exe` (Run as administrator) > tab **Logon**, tìm `LAB3_Run_Demo`; kiểm tra cột Entry, Description, Publisher, Image Path, Timestamp. **Không xóa** mục khác.
- [ ] Ảnh H7: Autoruns 14.3 tab Logon hiển thị `LAB3_Run_Demo` với Image Path = `notepad.exe` → `H7_Autoruns_LAB3_Run_Demo.png`.
- [ ] Bước 3. Truy vấn Sysmon cho Registry và process liên quan:
```powershell
$ids=1,11,12,13,14
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';Id=$ids;StartTime=(Get-Date).AddMinutes(-30)} |
  Where-Object { $_.Message -match 'LAB3_Run_Demo|LAB3_Persistence_Demo|notepad.exe|task_ran.txt' } |
  Select TimeCreated,Id,Message | Out-File C:\LAB3\Evidence\sysmon_persistence.txt -Width 300
```

#### 8.4.3. Tạo listener chỉ trên loopback và ánh xạ về tiến trình
- [ ] Bước 4. PowerShell (không cần admin) chạy HTTP server cục bộ; **giữ cửa sổ này mở trong TH4–TH6**:
```powershell
Set-Location C:\LAB3\lab3_assets\www
python -m http.server 8080 --bind 127.0.0.1
```
- [ ] Bước 5. Ở cửa sổ PowerShell khác, xác minh cổng lắng nghe và PID:
```powershell
$tcp=Get-NetTCPConnection -LocalPort 8080 -State Listen
$tcp | Format-Table LocalAddress,LocalPort,State,OwningProcess -Auto
Get-Process -Id $tcp.OwningProcess | Select Id,ProcessName,Path
```
- [ ] Bước 6. Mở Process Explorer 17.14 (Run as administrator), tìm PID vừa xác định, mở Properties ghi Image, Command line, User, Verified Signer. Kết luận listener này là **dịch vụ LAB được phê duyệt** vì bind 127.0.0.1, có lệnh khởi chạy xác định và do chính sinh viên tạo; **không** kết luận chỉ dựa vào "có cổng mở".
- [ ] Ảnh H8: Process Explorer tại `python.exe` có PID khớp `OwningProcess` → `H8_ProcessExplorer_Python.png`.

**PASS TH4:** phát hiện được `LAB3_Run_Demo` và `LAB3_Persistence_Demo`; Sysmon/Autoruns/Process Explorer cung cấp dấu vết tương quan; listener 8080 chỉ ở 127.0.0.1 và được ánh xạ đúng PID.

### 8.5. Tình huống 5 – Sniffing, MITM và Spoofing: quan sát HTTP so với HTTPS
Chỉ capture traffic của chính VM. **Không** thực hiện ARP poisoning, DNS spoofing, Wi-Fi giả mạo, session hijacking hoặc chèn chứng chỉ.

- [ ] Bước 1. Mở Wireshark 4.6.8, chọn interface loopback (*Adapter for loopback traffic capture*), bắt đầu capture.
- [ ] Bước 2. Tạo HTTP request có chuỗi huấn luyện trong URL (không dùng dữ liệu thật):
```powershell
curl.exe "http://127.0.0.1:8080/?lab_user=lab3_student&lab_code=TRAINING_ONLY"
```
- [ ] Bước 3. Display Filter trong GUI Wireshark (không phải lệnh shell), chọn packet HTTP GET và xem Request URI trong Packet Details:
```
http.request || tcp.port == 8080
```
- [ ] Ảnh H9: Wireshark có packet HTTP GET tới 127.0.0.1:8080, Request URI thể hiện chuỗi `TRAINING_ONLY` → `H9_HTTP_Plaintext.png`.
- [ ] Bước 4. So sánh với HTTPS: tạm chuyển VM sang **NAT** nếu cần Internet, capture trên NIC hoạt động, chạy lệnh dưới; sau khi capture xong **chuyển VM về Host-only**:
```powershell
curl.exe -I "https://example.com/?lab_user=lab3_student&lab_code=TRAINING_ONLY"
```
```
tls || tcp.port == 443
```
- [ ] Phân tích: metadata vẫn quan sát được (IP, cổng, kích thước, thời gian, một số thông tin handshake tùy phiên bản TLS) và những gì không còn đọc trực tiếp (HTTP payload/Request URI). Liên hệ biện pháp: HTTPS, HSTS, cập nhật hệ thống, thận trọng với Wi-Fi, VPN. Nêu giới hạn: mã hóa đường truyền không tự giải quyết phishing, endpoint compromise hoặc người dùng tự cung cấp credential cho trang giả mạo.
- [ ] Ảnh H10: Wireshark có TLS traffic sau `curl.exe` tới example.com → `H10_TLS_443.png`.

**PASS TH5:** có một capture HTTP loopback đọc được chuỗi huấn luyện và một capture TLS/443 để so sánh; không thực hiện kỹ thuật chặn/chuyển hướng lưu lượng chủ động.

### 8.6. Tình huống 6 – DoS, DDoS và Mail Bombing
Bài lab **không** tạo DDoS và **không** gửi email hàng loạt. Phần thực hành gồm tải cục bộ giới hạn và phân tích dataset offline.

#### 8.6.1. DoS – tải cục bộ có giới hạn
- [ ] Bước 1. Đảm bảo HTTP server 127.0.0.1:8080 của TH4 vẫn chạy; quan sát `python.exe` bằng Task Manager/Process Explorer.
- [ ] Bước 2. Chạy script giới hạn 50 request, 5 worker (hard-code 127.0.0.1:8080, không nhận URL từ tham số):
```powershell
python C:\LAB3\lab3_assets\scripts\local_load_test.py | Tee-Object C:\LAB3\Evidence\local_load_test.txt
```
- [ ] Ghi `requests`, `workers`, `ok/failures`, `elapsed_s`, `avg_latency_s`. Giải thích đây là minh họa tải quy mô nhỏ trên localhost, không phải DoS thực tế.

#### 8.6.2. DDoS – phân tích dataset nguồn phân tán
```powershell
Import-Csv C:\LAB3\lab3_assets\data\ddos_sample.csv |
  Group-Object SourceIP | Sort-Object Count -Descending |
  Select-Object Count,Name |
  Tee-Object C:\LAB3\Evidence\ddos_sources.txt
```
- [ ] Dataset dùng dải TEST-NET (RFC 5737). So sánh dấu hiệu "một nguồn tạo tải" của TH6.1 với "nhiều SourceIP" trong dataset; giải thích vì sao chặn một IP không đủ trong DDoS.

#### 8.6.3. Mail bombing – phân tích log email offline (không gửi email)
```powershell
$log=Import-Csv C:\LAB3\lab3_assets\data\mailbomb_sample.csv
$log | Group-Object Sender | Sort-Object Count -Descending | Select Count,Name |
  Tee-Object C:\LAB3\Evidence\mail_sender_counts.txt
$log | Measure-Object SizeBytes -Sum -Average |
  Tee-Object C:\LAB3\Evidence\mail_volume.txt
```
- [ ] Ảnh H10: PowerShell có kết quả `local_load_test` và thống kê DDoS/mail log; ảnh phải thể hiện target local 127.0.0.1:8080 → `H10_Load_and_Log_Analysis.png`.

**PASS TH6:** không có traffic gây tải ra ngoài; `local_load_test` chỉ nhắm 127.0.0.1; phân biệt DoS/DDoS và xác định sender/volume bất thường trong `mailbomb_sample.csv`.

### 8.7. Tình huống 7 – Social Engineering, Phishing và Spear Phishing
Bài học nêu Phishing, Watering Hole, Pretexting, Baiting, Quid Pro Quo; Spear Phishing là phishing được cá nhân hóa cho một người/tổ chức cụ thể. Tình huống này **hoàn toàn offline**.

- [ ] Bước 1. Mở mẫu email huấn luyện:
```powershell
notepad.exe C:\LAB3\lab3_assets\samples\phishing_email.txt
```
  Đánh dấu tối thiểu **5 chỉ dấu**: tạo cảm giác khẩn cấp; display name có vẻ đáng tin; domain cần xác minh; Reply-To khác From; yêu cầu truy cập link/cung cấp thông tin xác thực. **Không** truy cập domain trong mẫu (`.example`/`.invalid` chỉ phục vụ tài liệu/kiểm thử).
- [ ] Bước 2. Phân loại 6 tình huống Social Engineering:
```powershell
Import-Csv C:\LAB3\lab3_assets\samples\social_engineering_cases.csv | Format-Table -Wrap
```
  Trong báo cáo lập bảng **CaseID → loại tấn công → dấu hiệu → biện pháp phòng tránh**. Với Spear Phishing, chỉ ra yếu tố cá nhân hóa khiến thông điệp thuyết phục hơn.

| CaseID | Loại tấn công | Dấu hiệu | Biện pháp phòng tránh |
|---|---|---|---|
| *(điền)* | | | |

- [ ] Ảnh H10: Notepad mở `phishing_email.txt` và PowerShell hiển thị `social_engineering_cases.csv`; ảnh không chứa email/tài khoản thật → `H10_Phishing_Offline.png`.

**PASS TH7:** nhận diện tối thiểu 5 chỉ dấu phishing và phân loại đúng 6 case Social Engineering kèm biện pháp giảm thiểu.

### 8.8. Cô lập, cleanup, phục hồi và kiểm tra lại
**Chỉ cleanup sau khi đã thu đủ bằng chứng.** Các lệnh chỉ loại bỏ artefact do bài lab tạo, không xóa entry hệ thống khác (PowerShell – Administrator):
```powershell
# 1) Xoa persistence LAB3
Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' `
  -Name 'LAB3_Run_Demo' -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName 'LAB3_Persistence_Demo' -Confirm:$false -ErrorAction SilentlyContinue

# 2) Dung HTTP server dung PID dang listen tren 8080
$serverPid=(Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue).OwningProcess
if ($serverPid) { Stop-Process -Id $serverPid -Force }

# 3) Xoa tai khoan lab
Get-Process -IncludeUserName -ErrorAction SilentlyContinue | Out-Null
Remove-LocalUser -Name 'lab3user' -ErrorAction SilentlyContinue

# 4) Kiem tra lai
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'LAB3_Run_Demo' -ErrorAction SilentlyContinue
Get-ScheduledTask -TaskName 'LAB3_Persistence_Demo' -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
Get-MpComputerStatus | Select AntivirusEnabled,RealTimeProtectionEnabled,IsTamperProtected
```
- [ ] Bước 1. Thu baseline Autoruns sau cleanup và so sánh:
```powershell
C:\LAB3\Tools\Autoruns\autorunsc64.exe -a * -c -h -s > C:\LAB3\Evidence\autoruns_after.csv
Compare-Object (Get-Content C:\LAB3\Evidence\autoruns_before.csv) `
  (Get-Content C:\LAB3\Evidence\autoruns_after.csv) |
  Out-File C:\LAB3\Evidence\autoruns_diff.txt -Width 240
```
- [ ] Bước 2. Tính SHA-256 cho toàn bộ bằng chứng:
```powershell
Get-ChildItem C:\LAB3\Evidence -File |
  Get-FileHash -Algorithm SHA256 |
  Export-Csv C:\LAB3\Evidence\evidence_sha256.csv -NoTypeInformation -Encoding UTF8
```
- [ ] Bước 3. Sau khi nộp đủ Evidence, revert VM về snapshot `LAB3_CLEAN_20260914` (hoặc snapshot sạch do giảng viên quy định).
- [ ] Ảnh H11: kết quả verify sau cleanup – không còn `LAB3_Run_Demo`, `LAB3_Persistence_Demo`, listener 8080; Defender vẫn bật → `H11_Recovery_Verification.png`.

**Điều kiện hoàn thành toàn bài:** artefact thử nghiệm đã được loại bỏ; endpoint protection vẫn hoạt động; bằng chứng đã được hash; sinh viên mô tả rõ mối quan hệ giữa dấu vết kỹ thuật, rủi ro và biện pháp phòng chống.

## 9. Danh sách ảnh chụp bằng chứng

| Hình | Nội dung cần chụp | Tên tệp đề nghị |
|---|---|---|
| H1 | VMware: VM + Network Adapter = Host-only; `winver` Windows 11 25H2 build 26200.9445 | `H1_VM_WindowsVersion.png` |
| H2 | PowerShell hiển thị version Python/Wireshark/Sysmon/Autoruns/Process Explorer | `H2_ToolVersions.png` |
| H3 | `Get-MpComputerStatus` (RealTimeProtectionEnabled = True) + trạng thái firewall | `H3_Baseline_Defender_Firewall.png` |
| H4 | Windows Security > Protection history: detection EICAR | `H4_ProtectionHistory_EICAR.png` |
| H5 | Event Viewer Security: Event ID 4625 của `lab3user` | `H5_Event4625.png` |
| H6 | Event Viewer Sysmon/Operational: Event ID 1 | `H6_Sysmon_Event1.png` |
| H7 | Autoruns tab Logon: `LAB3_Run_Demo`, Image Path = notepad.exe | `H7_Autoruns_LAB3_Run_Demo.png` |
| H8 | Process Explorer: `python.exe` với PID khớp OwningProcess | `H8_ProcessExplorer_Python.png` |
| H9 | Wireshark: HTTP GET tới 127.0.0.1:8080 có `TRAINING_ONLY` | `H9_HTTP_Plaintext.png` |
| H10 | Wireshark: TLS traffic tới example.com | `H10_TLS_443.png` |
| H10 | PowerShell: kết quả local_load_test + thống kê DDoS/mail log | `H10_Load_and_Log_Analysis.png` |
| H10 | Notepad `phishing_email.txt` + PowerShell `social_engineering_cases.csv` | `H10_Phishing_Offline.png` |
| H11 | Verify sau cleanup: không còn artefact LAB3, Defender vẫn bật | `H11_Recovery_Verification.png` |

## 10. Kết quả PASS/FAIL

| Tình huống | Điều kiện PASS | Kết quả | Ghi chú |
|---|---|---|---|
| Baseline | Đủ 5 tệp baseline_*.txt trong Evidence, Defender/Firewall bật | *(PASS/FAIL)* | |
| TH1 – Risk register & phân loại | ≥ 5 tài sản/nguy cơ; 5 tình huống phân loại có giải thích | *(PASS/FAIL)* | |
| TH2 – EICAR | RealTimeProtection = True; có detection EICAR; không tắt bảo vệ/exclusion | *(PASS/FAIL)* | |
| TH3 – Password/keylogging | Có 4624/4648 hợp lệ, 4625 thất bại; mật khẩu cũ không dùng được sau khi đổi | *(PASS/FAIL)* | |
| TH4 – Backdoor/persistence | Phát hiện LAB3_Run_Demo & LAB3_Persistence_Demo; listener 8080 chỉ 127.0.0.1, đúng PID | *(PASS/FAIL)* | |
| TH5 – Sniffing/MITM/Spoofing | Capture HTTP loopback đọc được chuỗi huấn luyện + capture TLS/443 | *(PASS/FAIL)* | |
| TH6 – DoS/DDoS/Mail bombing | Tải chỉ nhắm 127.0.0.1; phân biệt DoS/DDoS; xác định sender/volume bất thường | *(PASS/FAIL)* | |
| TH7 – Social Engineering | ≥ 5 chỉ dấu phishing; phân loại đúng 6 case + biện pháp | *(PASS/FAIL)* | |
| Cleanup & Verify | Không còn artefact LAB3; Defender bật; có evidence_sha256.csv | *(PASS/FAIL)* | |

## 11. Lỗi gặp phải và cách khắc phục

| # | Lỗi / hiện tượng | Nguyên nhân | Cách khắc phục |
|---|---|---|---|
| 1 | Version công cụ khác với chuẩn (Python 3.14.7, Wireshark 4.6.8, Sysmon 15.22, Autoruns 14.3, Process Explorer 17.14) | Cài sai phiên bản hoặc winget lấy bản mới hơn | Dừng lại, báo giảng viên trước khi thực hành; cài đúng bằng `--exact --version` |
| 2 | `Set-Content` ghi tệp EICAR báo lỗi / tệp biến mất | Defender chặn ngay khi ghi – **đây là kết quả mong đợi** | Không tắt Defender, không tạo exclusion; lưu lỗi vào `eicar_write_error.txt` và dùng `Get-MpThreatDetection` làm bằng chứng |
| 3 | Hash gói `LAB3_Threats_Assets.zip` không trùng manifest | Tải sai file hoặc file bị sửa | Không giải nén; xin lại gói từ giảng viên |
| 4 | Không thấy Event 4625 trong Security log | Chưa bật audit Logon failure | Chạy lại `auditpol /set ...` với `/failure:enable` rồi sinh lại đăng nhập sai |
| 5 | Wireshark không có interface loopback | Chưa cài Npcap (bỏ chọn khi cài Wireshark) | Cài lại Wireshark và giữ thành phần Npcap |
| 6 | Scheduled task không chạy sau logon | Đăng nhập bằng tài khoản khác với `$env:USERNAME` lúc tạo task | Đăng nhập đúng tài khoản đã đăng ký task |
| … | *(bổ sung lỗi thực tế gặp phải khi thực hành)* | | |

## 12. Câu hỏi cần trả lời trong báo cáo

1. Dùng một ví dụ từ VM để phân biệt Asset, Vulnerability, Threat, Risk và Attack (không dùng cùng một câu mô tả cho Threat và Risk).
2. Phân loại năm tình huống ở TH1 thành: hành động vô ý, hành động cố ý, thảm họa tự nhiên, lỗi kỹ thuật, lỗi quản lý. Giải thích tiêu chí phân loại.
3. EICAR trong TH2 chứng minh được điều gì về Defender và không chứng minh được điều gì về việc có malware thật?
4. Vì sao không được tắt Microsoft Defender/EDR để "cho mẫu chạy"? Nếu phần mềm hợp lệ bị chặn trong doanh nghiệp, quy trình xử lý đúng gồm những bước nào?
5. So sánh Brute Force Attack, Dictionary Attack và Key Logger Attack về dữ liệu đầu vào, cách phát hiện và biện pháp giảm thiểu.
6. Dùng Event ID 4624, 4625, 4648 của chính VM để giải thích trạng thái xác thực trước và sau khi đổi mật khẩu `lab3user`.
7. Vì sao mật khẩu dài/phức tạp không tự ngăn được keylogging? Phân tích vai trò và giới hạn của MFA, push MFA và FIDO2/passkey.
8. Dựa trên TH4, một cổng đang Listen có đủ để kết luận có backdoor không? Nêu tối thiểu bốn bằng chứng phải tương quan trước khi kết luận.
9. Run value và Scheduled Task trong TH4 tạo persistence như thế nào? Vì sao phải kiểm tra tên, đường dẫn, publisher, command line và context thay đổi trước khi xóa một entry?
10. So sánh DoS và DDoS bằng kết quả `local_load_test.py` và `ddos_sample.csv`. Vì sao DDoS khó chặn chỉ bằng một rule IP đơn giản?
11. Mail bombing ảnh hưởng chủ yếu tới thuộc tính nào của hệ thống? Từ `mailbomb_sample.csv`, nêu hai chỉ số phù hợp để phát hiện hành vi bất thường.
12. Sniffing có thể được dùng hợp pháp và bất hợp pháp như thế nào? Dùng hai capture của TH5 để minh họa khác biệt HTTP và HTTPS.
13. Trình bày Email Hijacking, Wi-Fi Eavesdropping, Session Hijacking và IP/DNS/HTTPS Spoofing trong bối cảnh Man-in-the-Middle. Kỹ thuật nào không được thực hiện chủ động trong lab và vì sao?
14. HTTPS, HSTS và VPN giảm rủi ro MITM theo những cơ chế nào? Nêu ít nhất hai loại rủi ro mà các biện pháp này không tự giải quyết.
15. Phân biệt spoofing ở lớp IP, DNS và website/domain. Với mỗi loại, nêu một nguồn bằng chứng hoặc kiểm soát phù hợp.
16. Từ `social_engineering_cases.csv`, phân biệt Phishing, Spear Phishing, Watering Hole, Pretexting, Baiting và Quid Pro Quo.
17. Trong `phishing_email.txt`, những chỉ dấu nào liên quan tới "uy tín giả", "khẩn cấp", "domain", "Reply-To" và "yêu cầu credential"?
18. Xây dựng quy trình incident response ngắn cho endpoint nghi có keylogger/backdoor: triage → preserve evidence → contain → credential action → eradicate → recover → monitor.
19. SHA-256 trong bài giúp chứng minh điều gì về tính toàn vẹn của file Evidence và không chứng minh điều gì về nguồn gốc hay tính đúng đắn của nội dung?
20. Đề xuất defense-in-depth cho một máy phòng kế toán hoặc máy quản trị: endpoint protection, least privilege, application control, logging, network control, backup và credential protection.

## 13. Yêu cầu nộp bài và cấu trúc thư mục LAB3

### Yêu cầu nộp bài
- Báo cáo Word (.docx) đặt tên `[MãLớp]-LAB3_MSSV-HoTen.docx`; đầu báo cáo ghi phiên bản môi trường thực hành và link video (nếu lớp yêu cầu).
- Repository GitHub cá nhân `LAB_AT_BMHTTT` ở chế độ **Public**, có thư mục `LAB3` riêng.
- `LAB3/` tối thiểu gồm: `README.md`, báo cáo, các tệp output/log đã làm sạch và `evidence_sha256.csv`.
- **Không** đưa installer, executable Sysinternals/Wireshark/Python hoặc file bị Defender quarantine vào repo.
- **Không** upload mật khẩu, token/API key, cookie/session, dữ liệu cá nhân, email thật, log chưa làm sạch hoặc thông tin định danh hệ thống thật.
- Không chỉnh `local_load_test.py` để chỉ tới mục tiêu khác 127.0.0.1:8080; không tạo mail bomb, DDoS, spoofing hoặc MITM chủ động trên mạng ngoài VM lab.
- Trước hạn nộp: commit/push toàn bộ, mở URL repo trong trình duyệt không đăng nhập để kiểm tra quyền truy cập, dán URL vào Google Classroom.

### Cấu trúc thư mục dự kiến
```
LAB3/
├── README.md                                  # file này
├── LAB3_CacMoiDeDoa_ATTT_2026.pdf             # đề bài
├── Lab3_CNPM2_1150080120_HoangThanhTra.docx   # báo cáo Word
├── Evidence/                                  # output/log đã làm sạch
│   ├── start_time.txt
│   ├── baseline_os.txt, baseline_defender.txt, baseline_firewall.txt,
│   │   baseline_network.txt, baseline_processes.txt
│   ├── defender_eicar.txt
│   ├── auth_events_before_rotation.txt
│   ├── autoruns_before.csv, autoruns_after.csv, autoruns_diff.txt
│   ├── sysmon_persistence.txt, task_ran.txt
│   ├── local_load_test.txt, ddos_sources.txt
│   ├── mail_sender_counts.txt, mail_volume.txt
│   └── evidence_sha256.csv
└── Images/                                    # ảnh chụp H1 … H11
```

### Cấu trúc gói `LAB3_Threats_Assets.zip` (tham khảo, không đưa vào repo)

| Tệp | Mục đích |
|---|---|
| `lab3_assets/sysmon-lab.xml` | Cấu hình Sysmon schema 4.90 |
| `lab3_assets/www/index.html` | Trang HTTP cục bộ |
| `lab3_assets/scripts/local_load_test.py` | 50 request / 5 worker, chỉ 127.0.0.1:8080 |
| `lab3_assets/data/ddos_sample.csv` | Dataset offline, địa chỉ TEST-NET |
| `lab3_assets/data/mailbomb_sample.csv` | Log email offline, domain `.invalid` |
| `lab3_assets/samples/phishing_email.txt` | Mẫu phishing offline |
| `lab3_assets/samples/social_engineering_cases.csv` | 6 case phân loại Social Engineering |
| `lab3_assets/README.txt` | Mô tả phạm vi và nội dung gói |

## 14. Tài liệu tham khảo

1. Microsoft. *Windows 11, version 25H2 – September 8, 2026, KB5124008 (OS Build 26200.9445)*. https://support.microsoft.com/vi-vn/servicing/os/windows-11/2026/09/kb5124008-windows-11-24h2-25h2-security-update
2. VMware Cloud Foundation. *VMware Workstation and Fusion 26H1*. https://blogs.vmware.com/cloud-foundation/2026/05/14/announcing-vmware-workstation-and-fusion-26h1/
3. Microsoft Sysinternals. *Sysmon v15.22*. https://learn.microsoft.com/sysinternals/downloads/sysmon
4. Microsoft Learn. *Enable and configure Sysmon in Windows – minimal schema 4.90*. https://learn.microsoft.com/windows/security/operating-system-security/sysmon/how-to-enable-sysmon
5. Microsoft Sysinternals. *Autoruns v14.3*. https://learn.microsoft.com/sysinternals/downloads/autoruns
6. Microsoft Sysinternals. *Process Explorer v17.14*. https://learn.microsoft.com/sysinternals/downloads/process-explorer
7. Wireshark Foundation. *Wireshark 4.6.8 Stable*. https://www.wireshark.org/download.html
8. Wireshark Foundation. *Wireshark User's Guide*. https://www.wireshark.org/docs/wsug_html/
9. Python Software Foundation. *Python 3.14.7*. https://www.python.org/downloads/release/python-3147/
10. Microsoft Support. *Protection History in the Windows Security app*. https://support.microsoft.com/vi-vn/windows/security/windows-security/protection-history-in-the-windows-security-app
11. Microsoft Learn. *Validate Microsoft Defender Antivirus with the EICAR test file*. https://learn.microsoft.com/defender-endpoint/validate-antimalware
12. EICAR. *Anti-Malware Test File*. https://www.eicar.org/download-anti-malware-testfile/
13. Microsoft Learn. *Audit Logon events 4624, 4625, 4648*. https://learn.microsoft.com/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-logon
14. IETF RFC 5737. *IPv4 Address Blocks Reserved for Documentation*. https://www.rfc-editor.org/rfc/rfc5737
15. IETF RFC 2606. *Reserved Top Level DNS Names*. https://www.rfc-editor.org/rfc/rfc2606
