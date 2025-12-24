# src/p4_action/alert_manager.py

import time
from datetime import datetime
from typing import List, Dict
from src.utils.helpers import DetectionResult, AlertMessage
from configs.config import DEDUPLICATION_TIME

class AlertManager:
    def __init__(self):
        # Lưu trữ lịch sử cảnh báo để lọc trùng (Node P4.2)
        # Cấu trúc: {(room_id, object_class): last_alert_time}
        self.alert_history: Dict[tuple, float] = {}
        self.dedup_interval = DEDUPLICATION_TIME # 30 giây theo yêu cầu

    def _calculate_iou(self, bbox1, bbox2):
        """Hàm bổ trợ tính IoU để xác định độ trùng lắp vị trí (Trang 24)"""
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0

    def is_duplicate(self, det: DetectionResult) -> bool:
        """
        Node P4.2: Thuật toán lọc trùng cảnh báo (Trang 23).
        Kiểm tra nếu cùng vật thể, cùng phòng vi phạm trong khoảng thời gian ngắn.
        """
        current_time = time.time()
        key = (det.metadata.get("camera_id"), det.class_name, det.position)
        
        if key in self.alert_history:
            last_time = self.alert_history[key]
            if (current_time - last_time) < self.dedup_interval:
                return True
        
        # Cập nhật thời gian cảnh báo mới nhất
        self.alert_history[key] = current_time
        return False

    def trigger(self, det: DetectionResult, violation_info: tuple):
        """
        Node P4.1 & P4.3: Tạo và gửi cảnh báo.
        """
        is_violation, v_type, severity, msg = violation_info
        
        if is_violation and not self.is_duplicate(det):
            # 1. Tạo Alert Object (P4.1)
            timestamp_str = det.metadata.get("timestamp").strftime("%Y-%m-%d %H:%M:%S")
            
            # 2. In cảnh báo ra Console (P4.3)
            # Định dạng: [Severity] Message (Timestamp)
            print(f"[{severity}] {msg} ({timestamp_str})")
            
            # Trong thực tế, đây là nơi gọi API gửi SMS/Push Notification hoặc lưu DB
            return True
        return False