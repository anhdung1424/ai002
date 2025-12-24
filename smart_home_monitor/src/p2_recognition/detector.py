# src/p2_recognition/detector.py

from ultralytics import YOLO
import numpy as np
from typing import List
from src.utils.helpers import DetectionResult  # Sử dụng Class đã định nghĩa ở Bước 1

class ObjectDetector:
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Khởi tạo Module P2: Nhận diện vật thể.
        :param model_path: Đường dẫn tới trọng số YOLOv8.
        :param confidence_threshold: Ngưỡng tin cậy để lọc các nhận diện nhiễu (Node P2.2).
        """
        # Node P2.1: Load model YOLOv8 (Trang 11, 22)
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"[Error] Không thể tải model: {e}")
            raise

        self.conf_threshold = confidence_threshold

    def _classify_position(self, y1: float, y2: float, frame_height: int) -> str:
        """
        Node P2.3: Phân loại vị trí đồ vật dựa trên Heuristic (Trang 18, 22).
        Công thức: relative_y = y_center / frame_height
        """
        y_center = (y1 + y2) / 2
        relative_y = y_center / frame_height

        # Logic phân ngưỡng theo tài liệu (Trang 22)
        if relative_y > 0.8:
            return "floor"
        elif relative_y > 0.5:
            return "low"
        elif relative_y > 0.3:
            return "mid"
        else:
            return "high"

    def detect_objects(self, data_packet: dict) -> List[DetectionResult]:
        """
        Thực hiện nhận diện và phân loại vị trí.
        :param data_packet: Packet từ Module P1 chứa processed_frame và metadata.
        :return: Danh sách các đối tượng DetectionResult.
        """
        # Đầu vào là processed_frame (640x640) từ P1
        img = data_packet["processed_frame"]
        frame_h = data_packet["metadata"]["frame_height"]
        frame_w = data_packet["metadata"]["frame_width"]

        # 1. Chạy Inference (Dự đoán)
        # Chúng ta chạy trên ảnh 640x640 đã chuẩn hóa
        results = self.model.predict(source=img, conf=self.conf_threshold, verbose=False)
        
        detections = []
        
        # 2. Xử lý kết quả trả về từ YOLOv8
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Lấy tọa độ bbox (định dạng xyxy)
                # Lưu ý: YOLOv8 trả về tọa độ tương ứng với ảnh đầu vào (640x640)
                # Để phân loại vị trí chính xác, ta dùng tọa độ pixel chuẩn hóa
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Tính toán vị trí (Node P2.3)
                # Dùng y1, y2 trên khung hình 640 để tính tỉ lệ relative_y
                position = self._classify_position(y1, y2, 640) 

                # Chuyển đổi tọa độ ngược lại kích thước raw_frame để vẽ sau này
                scale_x = frame_w / 640
                scale_y = frame_h / 640
                original_bbox = [
                    int(x1 * scale_x), int(y1 * scale_y), 
                    int(x2 * scale_x), int(y2 * scale_y)
                ]

                # Tạo đối tượng DetectionResult (Trang 3)
                obj = DetectionResult(
                    class_name=self.model.names[int(box.cls)],
                    confidence=float(box.conf),
                    bbox=original_bbox,
                    position=position,
                    metadata=data_packet["metadata"]
                )
                
                detections.append(obj)

        return detections

# --- Đoạn mã chạy thử nghiệm (Unit Test cho Module P2) ---
if __name__ == "__main__":
    from src.p1_acquisition.data_reader import DataAcquisition
    import cv2

    # Giả lập pipeline P1 -> P2
    acquisition = DataAcquisition(source=0, camera_id="CAM_001")
    detector = ObjectDetector()

    for packet in acquisition.get_stream():
        results = detector.detect_objects(packet)
        
        raw_img = packet["raw_frame"]
        for res in results:
            x1, y1, x2, y2 = res.bbox
            # Vẽ bounding box và thông tin vị trí
            color = (0, 255, 0) # Mặc định xanh lá
            cv2.rectangle(raw_img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(raw_img, f"{res.class_name} ({res.position})", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow("Module P2 Test - Press Q to exit", raw_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()