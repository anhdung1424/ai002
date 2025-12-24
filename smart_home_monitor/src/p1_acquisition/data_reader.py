# src/p1_acquisition/data_reader.py

import cv2
import datetime
import time
import numpy as np
from typing import Generator, Dict, Any, Union
from configs.config import CAMERA_CONFIG

class DataAcquisition:
    def __init__(self, source: Union[str, int], camera_id: str):
        """
        Khởi tạo module thu thập dữ liệu (P1).
        :param source: Đường dẫn file video hoặc ID camera (0 cho webcam).
        :param camera_id: Mã định danh camera để tra cứu metadata.
        """
        self.source = source
        self.camera_id = camera_id
        self.cap = None
        
        # Tra cứu room_type từ config (Node P1.3)
        cam_info = CAMERA_CONFIG.get(camera_id, {})
        self.room_type = cam_info.get("room_type", "unknown")
        self.room_name = cam_info.get("room_name", "Unknown Room")

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Node P1.2: Tiền xử lý khung hình (Resize + Normalization)
        """
        # 1. Resize về 640x640 (chuẩn đầu vào YOLOv8 - Trang 22)
        resized = cv2.resize(frame, (640, 640))
        
        # 2. Chuẩn hóa pixel về dải [0, 1] - Kiểu dữ liệu float32
        normalized = resized.astype(np.float32) / 255.0
        
        return normalized

    def get_stream(self) -> Generator[Dict[str, Any], None, None]:
        """
        Node P1.1: Đọc video stream sử dụng Generator để tối ưu bộ nhớ.
        Trả về một dictionary chứa đầy đủ dữ liệu và metadata.
        """
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            print(f"[Error] Không thể kết nối nguồn video: {self.source}")
            return

        print(f"[P1] Đang bắt đầu luồng dữ liệu từ: {self.room_name} ({self.camera_id})")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Ghi nhận timestamp hiện tại (Node P1.3 - Trang 7)
            timestamp = datetime.datetime.now()
            
            # Thực hiện tiền xử lý
            processed_frame = self._preprocess(frame)

            # Đóng gói dữ liệu đầu ra của P1
            data_packet = {
                "raw_frame": frame,          # Giữ frame gốc để hiển thị/vẽ cảnh báo
                "processed_frame": processed_frame,
                "metadata": {
                    "timestamp": timestamp,
                    "camera_id": self.camera_id,
                    "room_type": self.room_type,
                    "room_name": self.room_name,
                    "frame_height": frame.shape[0],
                    "frame_width": frame.shape[1]
                }
            }

            yield data_packet

        self.cap.release()

# --- Đoạn mã chạy thử nghiệm (Unit Test cho Module P1) ---
if __name__ == "__main__":
    # Test với Webcam (0) hoặc thay bằng đường dẫn file video
    acquisition = DataAcquisition(source=0, camera_id="CAM_001")
    
    for packet in acquisition.get_stream():
        frame = packet["raw_frame"]
        meta = packet["metadata"]
        
        # Hiển thị thông tin metadata lên frame
        cv2.putText(frame, f"{meta['room_name']} | {meta['timestamp'].strftime('%H:%M:%S')}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Module P1 Test - Press Q to exit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()