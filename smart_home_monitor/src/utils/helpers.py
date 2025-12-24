# src/utils/helpers.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import datetime

@dataclass
class DetectionResult:
    """
    Cấu trúc dữ liệu lưu trữ kết quả nhận diện của một vật thể.
    Bám sát định nghĩa chi tiết bài toán tại Trang 3 và Trang 18.
    """
    class_name: str           # Tên lớp vật thể (e.g., 'knife', 'bottle')
    confidence: float         # Độ tin cậy từ model AI (0.0 - 1.0)
    bbox: List[int]           # Tọa độ khung hình gốc [x1, y1, x2, y2]
    position: str             # Vị trí phân loại: floor, low, mid, high (Trang 22)
    
    # Metadata chứa ngữ cảnh hệ thống (Trang 7)
    metadata: Dict[str, Any] = field(default_factory=dict) 

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi dữ liệu sang Dictionary để phục vụ ghi Log JSON (Trang 20)"""
        return {
            "class": self.class_name,
            "confidence": round(self.confidence, 2),
            "bbox": self.bbox,
            "position": self.position,
            "room_type": self.metadata.get("room_type"),
            "camera_id": self.metadata.get("camera_id"),
            "timestamp": self.metadata.get("timestamp").isoformat() if self.metadata.get("timestamp") else None
        }

@dataclass
class AlertMessage:
    """
    Cấu trúc một đối tượng cảnh báo đầy đủ (Node P4.1 - Trang 13, 19).
    Dùng để hiển thị lên giao diện Dashboard hoặc gửi thông báo.
    """
    alert_id: str
    timestamp: datetime.datetime
    room_name: str
    violation_type: str       # 'forbidden_object' hoặc 'forbidden_on_floor'
    severity: str             # 'CRITICAL', 'HIGH', 'MEDIUM'
    message: str
    image_path: Optional[str] = None

def calculate_iou(bbox1: List[int], bbox2: List[int]) -> float:
    """
    Hàm tính toán chỉ số Intersection over Union (IoU).
    Dùng cho thuật toán Lọc trùng cảnh báo (Node P4.2 - Trang 23, 24).
    
    :param bbox1: [x1, y1, x2, y2]
    :param bbox2: [x1, y1, x2, y2]
    :return: Giá trị IoU từ 0.0 đến 1.0
    """
    # Xác định tọa độ của hình chữ nhật giao nhau
    x_left = max(bbox1[0], bbox2[0])
    y_top = max(bbox1[1], bbox2[1])
    x_right = min(bbox1[2], bbox2[2])
    y_bottom = min(bbox1[3], bbox2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # Tính diện tích phần giao (Intersection)
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # Tính diện tích mỗi bbox
    bbox1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
    bbox2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])

    # Tính diện tích phần hợp (Union)
    union_area = float(bbox1_area + bbox2_area - intersection_area)

    return intersection_area / union_area if union_area > 0 else 0.0

def get_severity_color(severity: str) -> tuple:
    """
    Hàm bổ trợ trả về màu sắc BGR dựa trên mức độ nghiêm trọng.
    """
    if severity == "CRITICAL":
        return (0, 0, 255)    # Đỏ đậm
    elif severity == "HIGH":
        return (0, 165, 255)  # Cam
    return (0, 255, 255)      # Vàng