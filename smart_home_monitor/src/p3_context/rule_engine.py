# src/p3_context/rule_engine.py

from configs.config import SAFETY_RULES, OBJECT_CATEGORIES
from src.utils.helpers import DetectionResult
from typing import Tuple, Optional

class RuleEngine:
    def __init__(self):
        self.rules = SAFETY_RULES

    def validate_detection(self, det: DetectionResult) -> Tuple[bool, Optional[str], str, str]:
        """
        Node P3.2 & P3.3: Đối soát quy tắc an toàn.
        Trả về: (is_violation, violation_type, severity, message)
        """
        room_type = det.metadata.get("room_type")
        room_rules = self.rules.get(room_type, {})
        
        obj_name = det.class_name
        pos = det.position
        
        # 1. Kiểm tra vật thể bị cấm hoàn toàn trong phòng (Trang 2)
        if obj_name in room_rules.get("forbidden_objects", []):
            return True, "forbidden_object", "CRITICAL", f"Phát hiện {obj_name} trong {det.metadata.get('room_name')}!"

        # 2. Kiểm tra vật thể bị cấm để dưới sàn (Trang 2)
        if pos == "floor":
            forbidden_on_floor = room_rules.get("forbidden_on_floor", [])
            
            # Kiểm tra vật thể cụ thể hoặc nhóm vật thể nguy hiểm (Trang 15)
            if obj_name in forbidden_on_floor or (
                "any_sharp_object" in forbidden_on_floor and obj_name in OBJECT_CATEGORIES["DANGEROUS"]
            ):
                return True, "forbidden_on_floor", "HIGH", f"Phát hiện {obj_name} đặt sai vị trí (dưới sàn)!"

        return False, None, "INFO", ""