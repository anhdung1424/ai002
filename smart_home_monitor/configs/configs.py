# configs/config.py

# Định nghĩa các nhóm vật thể (Generalization - Trang 15)
OBJECT_CATEGORIES = {
    "DANGEROUS": ["knife", "scissors", "razor", "needle", "lighter"],
    "FRAGILE": ["glass", "cup", "plate", "vase"],
    "CHEMICAL": ["detergent", "bleach", "medicine"]
}

# Cấu hình Camera và Phòng (Room Metadata)
CAMERA_CONFIG = {
    "CAM_001": {
        "room_id": "kitchen_01",
        "room_type": "kitchen",
        "room_name": "Bếp tầng 1"
    },
    "CAM_002": {
        "room_id": "child_01",
        "room_type": "child_room",
        "room_name": "Phòng trẻ em"
    }
}

# Quy tắc an toàn (Safety Rules - Trang 2 & 16)
SAFETY_RULES = {
    "kitchen": {
        "forbidden_on_floor": ["knife", "glass", "hot_pan"],
        "forbidden_objects": [],
        "description": "Cảnh báo vật sắc nhọn hoặc đồ nóng dưới sàn bếp"
    },
    "child_room": {
        "forbidden_objects": ["knife", "scissors", "medicine", "lighter"],
        "forbidden_on_floor": ["any_sharp_object"],
        "description": "Cấm vật nguy hiểm trong phòng trẻ em"
    },
    "living_room": {
        "forbidden_on_floor": ["glass", "medicine"],
        "forbidden_objects": []
    }
}

# Cấu hình kỹ thuật
DETECTION_THRESHOLD = 0.5
DEDUPLICATION_TIME = 30  # Giây (Lọc trùng cảnh báo)